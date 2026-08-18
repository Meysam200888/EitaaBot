import json
import os
import requests
from datetime import datetime

TOKEN = os.getenv("EITAA_TOKEN")
CHAT_ID = "11229751"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(
    BASE_DIR,
    "morning_messages.json"
)


def send_message(text):
    url = f"https://eitaayar.ir/api/{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    return response.json()


def main():

    today = datetime.now().strftime("%Y-%m-%d")

    print("Today:", today)

    with open(
        MESSAGES_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:
        messages = json.load(f)

    for message in messages:

        if not message.get("enabled", True):
            continue

        if message.get("date") != today:
            continue

        text = message.get("text", "").strip()

        if not text:
            continue

        result = send_message(text)

        if result.get("ok") is True:
            print("Message sent successfully.")
        else:
            print("Message was not sent.")

        break


if __name__ == "__main__":
    main()
