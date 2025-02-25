import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__)
env_file_path = BASE_DIR.parent.parent / ".env"

load_dotenv(env_file_path)


TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

SLACK_TOKEN = os.getenv("SLACK_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "")

CHAT_LIST = os.getenv("CHAT_LIST", "").split(",")
CHAT_BLACK_LIST = os.getenv("CHAT_BLACK_LIST", "").split(",")
MANAGERS_IDS = os.getenv("MANAGERS_IDS", "").split(",")

TIME_TO_SLEEP = os.getenv("TIME_TO_SLEEP", "")
TIME_TO_WOKE_UP = os.getenv("TIME_TO_WOKE_UP", "")
