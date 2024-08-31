import asyncio
import telegram
import aiohttp
import json
from dataclasses import dataclass

CONFIGS = json.load(open("config.json"))
BOT = telegram.Bot(CONFIGS["bot_token"])
SITES = CONFIGS["sites"]
BAD_NEWS_CHAT_ID = CONFIGS["notification_chat_id"]

@dataclass
class TSiteStatus:
    status: bool
    counter: int

STATUS: dict[str, TSiteStatus] = dict()

async def is_response_ok(response) -> bool:
    if response.status != 200:
        return False, "Status not 200"
    
    html = await response.text()
    if len(html) < 100:
        return False, "Too small html"
    
    return True, ""


async def start_monitoring(site: str):
    is_ok, error = False, "somethin wrong"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(site) as response:
                    is_ok, error = await is_response_ok(response)
        except Exception:
            is_ok = False
            error = "Can't request"

        try:
            if is_ok and not STATUS[site].status:
                STATUS[site].counter = max(0, min(5, STATUS[site].counter - 1))

                if STATUS[site].counter == 0:
                    STATUS[site].status = True
                    message = "Site: " + site + "\n" + "is alive"
                    await BOT.send_message(text = message, chat_id=BAD_NEWS_CHAT_ID)             
            elif not is_ok:
                STATUS[site].counter = min(STATUS[site].counter + 1, 100)

                if 3 <= STATUS[site].counter <= 13:
                    STATUS[site].status = False
                    message = "Site: " + site + "\n" + error
                    await BOT.send_message(text = message, chat_id=BAD_NEWS_CHAT_ID)

        except Exception as e:
            print(e)

        await asyncio.sleep(60)

async def im_ok():
    await asyncio.sleep(60*60*9)
    while True:
        message = "Bot is alive"
        for site, site_status in STATUS.items():
            if not site_status.status:
                message += '\nThe ' + site + " is dead"
        await BOT.send_message(text = message, chat_id=BAD_NEWS_CHAT_ID)
        await asyncio.sleep(60*60*24)

for site in SITES:
    STATUS[site] = TSiteStatus(True, 0)

if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()

    tasks = [ioloop.create_task(start_monitoring(site)) for site in SITES]
    tasks.append(ioloop.create_task(im_ok()))

    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()
