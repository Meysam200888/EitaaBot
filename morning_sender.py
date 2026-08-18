import json
import os
import requests
from datetime import datetime, date

TOKEN = os.getenv("EITAA_TOKEN")
CHAT_ID = "11229751"

MESSAGES_FILE = "morning_messages.json"

START_DATE = date(2026, 8, 19)


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

    try:
        return response.json()
    except Exception:
        return {
            "ok": False,
            "error": response.text
        }


def main():

    today = datetime.now().date()

    print("Today:", today)

    # تعداد روزهای گذشته از تاریخ شروع
    days_passed = (today - START_DATE).days

    if days_passed < 0:
        print("Morning messages have not started yet.")
        return

    with open(
        MESSAGES_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:

        messages = json.load(f)

    if not messages:
        print("No messages found.")
        return

    # انتخاب خودکار پیام
    index = days_passed % len(messages)

    message = messages[index]

    # اگر پیام به صورت متن ساده باشد
    if isinstance(message, str):
        text = message.strip()

    # اگر پیام به صورت object باشد
    elif isinstance(message, dict):
        if not message.get("enabled", True):
            print("Selected message is disabled.")
            return

        text = message.get("text", "").strip()

    else:
        print("Invalid message format.")
        return

    if not text:
        print("Message is empty.")
        return

    print(
        f"Sending message #{index + 1} "
        f"of {len(messages)}"
    )

    result = send_message(text)

    if result.get("ok") is True:
        print("✅ Message sent successfully.")
    else:
        print("❌ Message was not sent.")


if __name__ == "__main__":
    main()
