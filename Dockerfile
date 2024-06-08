FROM python:3.10

RUN pip3 install python-telegram-bot aiohttp

COPY config.json config.json
COPY monitoring.py monitoring.py

ENTRYPOINT ["python3", "monitoring.py"]
