import json
import os
import requests
from datetime import datetime, date


# ============================================================
# تنظیمات
# ============================================================

TOKEN = os.getenv("EITAA_TOKEN")

# Chat ID گروه جدید
CHAT_ID = "11234919"

# تاریخ شروع
START_DATE = date(2026, 8, 19)

# فایل پیام صبح بخیر
MORNING_FILE = "morning_messages.json"

# فایل‌هایی که بعد از صبح بخیر ارسال می‌شوند
TXT_FILES = [
    "مرحله_۱_۳۰۰_متن_فرزندپروری_و_روانشناسی_کودک.txt",
    "200_poems_children_shokoofehaye_mahdavi.txt",
    "300_texts_parenting_children.txt"
]


# ============================================================
# ارسال پیام
# ============================================================

def send_message(text):

    if not TOKEN:
        print("❌ EITAA_TOKEN پیدا نشد.")
        return False

    if not text or not text.strip():
        print("⚠️ پیام خالی است.")
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

            print("❌ پاسخ JSON معتبر نیست.")
            return False

        if result.get("ok") is True:

            print("✅ پیام ارسال شد.")
            return True

        print("❌ ارسال ناموفق بود.")

        return False

    except Exception as error:

        print("❌ خطا در ارسال:")

        print(error)

        return False


# ============================================================
# شماره روز
# ============================================================

def get_day_number():

    today = datetime.now().date()

    days_passed = (
        today - START_DATE
    ).days

    if days_passed < 0:
        return 0

    return days_passed


# ============================================================
# خواندن پیام صبح بخیر
# ============================================================

def get_morning_message():

    if not os.path.exists(MORNING_FILE):

        print(
            f"❌ فایل پیدا نشد: {MORNING_FILE}"
        )

        return None

    try:

        with open(
            MORNING_FILE,
            "r",
            encoding="utf-8-sig"
        ) as file:

            messages = json.load(file)

        if not messages:

            print(
                "❌ morning_messages.json خالی است."
            )

            return None

        day_number = get_day_number()

        index = (
            day_number %
            len(messages)
        )

        message = messages[index]

        if isinstance(message, str):

            text = message.strip()

        elif isinstance(message, dict):

            if not message.get(
                "enabled",
                True
            ):

                print(
                    "⚠️ پیام صبح بخیر غیرفعال است."
                )

                return None

            text = message.get(
                "text",
                ""
            ).strip()

        else:

            print(
                "❌ فرمت پیام صبح بخیر نامعتبر است."
            )

            return None

        if not text:

            return None

        print(
            f"🌅 پیام صبح بخیر "
            f"شماره {index + 1} "
            f"از {len(messages)}"
        )

        return text

    except Exception as error:

        print(
            "❌ خطا در خواندن پیام صبح بخیر:"
        )

        print(error)

        return None


# ============================================================
# خواندن متن‌های TXT
# ============================================================

def load_txt_messages(filename):

    if not os.path.exists(filename):

        print(
            f"❌ فایل پیدا نشد: {filename}"
        )

        return []

    try:

        with open(
            filename,
            "r",
            encoding="utf-8-sig"
        ) as file:

            content = file.read()

        content = content.replace(
            "\r\n",
            "\n"
        )

        content = content.replace(
            "\r",
            "\n"
        )

        # ----------------------------------------------------
        # جداکننده اصلی فایل‌ها
        # ----------------------------------------------------

        separator = (
            "========================================================================"
        )

        if separator in content:

            parts = content.split(
                separator
            )

        else:

            parts = content.split(
                "\n\n"
            )

        messages = []

        for part in parts:

            text = part.strip()

            if text:

                messages.append(text)

        return messages

    except Exception as error:

        print(
            f"❌ خطا در خواندن {filename}:"
        )

        print(error)

        return []


# ============================================================
# گرفتن متن مربوط به امروز
# ============================================================

def get_today_text(filename):

    messages = load_txt_messages(
        filename
    )

    if not messages:

        return None

    day_number = get_day_number()

    # هر روز فقط یک متن
    index = (
        day_number %
        len(messages)
    )

    print(
        f"📝 فایل: {filename}"
    )

    print(
        f"📝 متن امروز: "
        f"{index + 1}/{len(messages)}"
    )

    return messages[index]


# ============================================================
# ارسال متن روزانه از فایل
# ============================================================

def send_today_text(filename):

    print("")
    print("-" * 60)

    text = get_today_text(
        filename
    )

    if text is None:

        print(
            "⚠️ متنی برای ارسال پیدا نشد."
        )

        return False

    return send_message(text)


# ============================================================
# برنامه اصلی
# ============================================================

def main():

    print("")
    print("=" * 60)
    print("🌸 Eitaa Automatic Message Sender")
    print("=" * 60)

    print(
        "📅 تاریخ:",
        datetime.now().strftime(
            "%Y-%m-%d"
        )
    )

    print(
        "⏰ ساعت:",
        datetime.now().strftime(
            "%H:%M:%S"
        )
    )

    print(
        "📌 شماره روز:",
        get_day_number() + 1
    )

    print("=" * 60)

    # --------------------------------------------------------
    # بررسی Token
    # --------------------------------------------------------

    if not TOKEN:

        print(
            "❌ EITAA_TOKEN پیدا نشد."
        )

        return

    print(
        "✅ Token دریافت شد."
    )

    # ========================================================
    # 1. پیام صبح بخیر
    # ========================================================

    print("")
    print("🌅 مرحله 1: پیام صبح بخیر")

    morning_message = (
        get_morning_message()
    )

    if morning_message:

        success = send_message(
            morning_message
        )

        if not success:

            print(
                "❌ پیام صبح بخیر ارسال نشد."
            )

            return

    else:

        print(
            "⚠️ پیام صبح بخیر پیدا نشد."
        )

    # ========================================================
    # 2. فایل اول
    # ========================================================

    print("")
    print(
        "📚 مرحله 2: "
        "فرزندپروری و روانشناسی کودک"
    )

    if not send_today_text(
        TXT_FILES[0]
    ):

        print(
            "❌ ارسال فایل اول ناموفق بود."
        )

    # ========================================================
    # 3. فایل دوم
    # ========================================================

    print("")
    print(
        "📚 مرحله 3: شعرهای کودکانه"
    )

    if not send_today_text(
        TXT_FILES[1]
    ):

        print(
            "❌ ارسال فایل دوم ناموفق بود."
        )

    # ========================================================
    # 4. فایل سوم
    # ========================================================

    print("")
    print(
        "📚 مرحله 4: متن‌های فرزندپروری"
    )

    if not send_today_text(
        TXT_FILES[2]
    ):

        print(
            "❌ ارسال فایل سوم ناموفق بود."
        )

    # ========================================================
    # پایان
    # ========================================================

    print("")
    print("=" * 60)
    print("✅ ارسال‌های امروز تمام شد.")
    print("=" * 60)


if __name__ == "__main__":

    main()
