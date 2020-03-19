import os
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ZEN_CONSUMER_KEY = os.getenv("ZEN_CONSUMER_KEY")
ZEN_CONSUMER_SECRET = os.getenv("ZEN_CONSUMER_SECRET")
