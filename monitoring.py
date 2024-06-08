import asyncio
import telegram
import aiohttp
import json

CONFIGS = json.load(open("config.json"))
BOT = telegram.Bot(CONFIGS["bot_token"])
SITES = CONFIGS["sites"]
BAD_NEWS_CHAT_ID = CONFIGS["notification_chat_id"]

STATUS = dict()

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
            if is_ok:
                if not STATUS[site]["status"]:
                    message = "Site: " + site + "\n" + "is alive"
                    await BOT.send_message(text = message, chat_id=BAD_NEWS_CHAT_ID)
            else:
                message = "Site: " + site + "\n" + error
                await BOT.send_message(text = message, chat_id=BAD_NEWS_CHAT_ID)

            STATUS[site]["status"] = is_ok
        except Exception as e:
            print(e)

        await asyncio.sleep(60)

async def im_ok():
    while True:
        await BOT.send_message(text = "I'm alive", chat_id=BAD_NEWS_CHAT_ID)
        await asyncio.sleep(60*60*24)

for site in SITES:
    STATUS[site] = {"status": True}

if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()

    tasks = [ioloop.create_task(start_monitoring(site)) for site in SITES]
    tasks.append(ioloop.create_task(im_ok()))

    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()
