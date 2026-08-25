import json
import os
import requests
from datetime import datetime, date

TOKEN = os.environ.get("bot515886:d4de9ae0-e0f2-44d6-b57b-98605f81a7cf", "")

CHAT_ID = "11234919"

MORNING_MESSAGES_FILE = "morning_messages.json"

FILES_TO_SEND = [
    "مرحله_۱_۳۰۰_متن_فرزندپروری_و_روانشناسی_کودک.txt",
    "200_poems_children_shokoofehaye_mahdavi.txt",
    "300_texts_parenting_children.txt"
]

START_DATE = date(2026, 8, 19)


def send_message(text):
    if not TOKEN:
        print("❌ EITAA_TOKEN تنظیم نشده است.")
        return False

    if not text.strip():
        print("⚠️ متن خالی است.")
        return False

    url = f"https://eitaayar.ir/api/{TOKEN}/sendMessage"

    try:
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
            result = response.json()
        except Exception:
            return False

        return result.get("ok") is True

    except Exception as e:
        print("❌ Error:", e)
        return False


def load_morning_message():
    if not os.path.exists(MORNING_MESSAGES_FILE):
        print("❌ morning_messages.json پیدا نشد.")
        return None

    try:
        with open(
            MORNING_MESSAGES_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:
            messages = json.load(f)

        if not messages:
            print("❌ فایل morning_messages.json خالی است.")
            return None

        today = datetime.now().date()
        days_passed = (today - START_DATE).days

        if days_passed < 0:
            return None

        index = days_passed % len(messages)

        message = messages[index]

        if isinstance(message, str):
            text = message.strip()

        elif isinstance(message, dict):
            if not message.get("enabled", True):
                print("⚠️ پیام انتخاب‌شده غیرفعال است.")
                return None

            text = message.get("text", "").strip()

        else:
            print("❌ فرمت پیام نامعتبر است.")
            return None

        if not text:
            return None

        print(
            f"🌅 Morning message #{index + 1} "
            f"of {len(messages)}"
        )

        return text

    except Exception as e:
        print("❌ Error loading morning message:", e)
        return None


def load_txt_messages(filename):
    if not os.path.exists(filename):
        print(f"❌ فایل پیدا نشد: {filename}")
        return []

    try:
        with open(
            filename,
            "r",
            encoding="utf-8-sig"
        ) as f:
            content = f.read()

        content = content.replace("\r\n", "\n")
        content = content.replace("\r", "\n")

        parts = content.split("\n\n")

        messages = []

        for part in parts:
            text = part.strip()

            if text:
                messages.append(text)

        return messages

    except Exception as e:
        print(f"❌ خطا در خواندن {filename}: {e}")
        return []


def get_daily_index(count):
    today = datetime.now().date()
    days_passed = (today - START_DATE).days

    if days_passed < 0:
        return 0

    return days_passed % count


def main():

    print("=" * 50)
    print("Eitaa Automatic Message Sender")
    print("=" * 50)

    print("📅 Today:", datetime.now().date())
    print("⏰ Time:", datetime.now().strftime("%H:%M:%S"))

    if not TOKEN:
        print("❌ EITAA_TOKEN موجود نیست.")
        return

    # ---------------------------------------------------------
    # 1. پیام صبح بخیر
    # ---------------------------------------------------------

    morning_message = load_morning_message()

    if morning_message:

        print("📤 ارسال پیام صبح‌بخیر...")

        success = send_message(morning_message)

        if success:
            print("✅ پیام صبح‌بخیر ارسال شد.")
        else:
            print("❌ ارسال پیام صبح‌بخیر ناموفق بود.")

    # ---------------------------------------------------------
    # 2. فایل‌های TXT
    # ---------------------------------------------------------

    for filename in FILES_TO_SEND:

        print()
        print("=" * 50)
        print("📄 فایل:", filename)
        print("=" * 50)

        messages = load_txt_messages(filename)

        if not messages:
            print("⚠️ هیچ متنی در فایل پیدا نشد.")
            continue

        index = get_daily_index(len(messages))

        text = messages[index]

        print(
            f"📝 متن شماره {index + 1} "
            f"از {len(messages)}"
        )

        print("📤 در حال ارسال...")

        success = send_message(text)

        if success:
            print(f"✅ متن فایل {filename} ارسال شد.")
        else:
            print(f"❌ ارسال فایل {filename} ناموفق بود.")

    print()
    print("=" * 50)
    print("✅ عملیات امروز تمام شد.")
    print("=" * 50)


if __name__ == "__main__":
    main()
