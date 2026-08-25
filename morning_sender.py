import json
import os
import requests
from datetime import datetime, date

# =========================================================
# تنظیمات
# =========================================================

TOKEN = os.environ.get("EITAA_TOKEN", "")

# Chat ID گروه ایتا
CHAT_ID = "11234919"

# فایل پیام‌های صبح‌بخیر
MORNING_MESSAGES_FILE = "morning_messages.json"

# فایل‌های متنی که بعد از پیام صبح‌بخیر ارسال می‌شوند
FILES_TO_SEND = [
    "مرحله_۱_۳۰۰_متن_فرزندپروری_و_روانشناسی_کودک.txt",
    "200_poems_children_shokoofehaye_mahdavi.txt",
    "300_texts_parenting_children.txt"
]

# تاریخ شروع انتخاب پیام‌ها
START_DATE = date(2026, 8, 19)


# =========================================================
# ارسال پیام به ایتا
# =========================================================

def send_message(text):

    if not TOKEN:
        print("❌ EITAA_TOKEN تنظیم نشده است.")
        return False

    if not CHAT_ID:
        print("❌ CHAT_ID تنظیم نشده است.")
        return False

    if not text or not text.strip():
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
            print("❌ پاسخ JSON معتبر نیست.")
            return False

        if result.get("ok") is True:
            return True

        print("❌ ارسال ناموفق بود.")
        return False

    except Exception as e:

        print("❌ خطا در ارسال پیام:")
        print(e)

        return False


# =========================================================
# خواندن پیام صبح‌بخیر
# =========================================================

def load_morning_message():

    if not os.path.exists(MORNING_MESSAGES_FILE):

        print(
            f"❌ فایل پیدا نشد: "
            f"{MORNING_MESSAGES_FILE}"
        )

        return None

    try:

        with open(
            MORNING_MESSAGES_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            messages = json.load(f)

        if not messages:

            print(
                "❌ فایل morning_messages.json خالی است."
            )

            return None

        today = datetime.now().date()

        days_passed = (
            today - START_DATE
        ).days

        if days_passed < 0:

            print(
                "⚠️ تاریخ شروع پیام‌های صبح‌بخیر "
                "هنوز نرسیده است."
            )

            return None

        index = (
            days_passed %
            len(messages)
        )

        message = messages[index]

        # اگر پیام به صورت متن ساده باشد
        if isinstance(message, str):

            text = message.strip()

        # اگر پیام به صورت object باشد
        elif isinstance(message, dict):

            if not message.get(
                "enabled",
                True
            ):

                print(
                    "⚠️ پیام انتخاب‌شده "
                    "غیرفعال است."
                )

                return None

            text = message.get(
                "text",
                ""
            ).strip()

        else:

            print(
                "❌ فرمت پیام صبح‌بخیر نامعتبر است."
            )

            return None

        if not text:

            print(
                "⚠️ پیام صبح‌بخیر خالی است."
            )

            return None

        print(
            f"🌅 پیام صبح‌بخیر "
            f"شماره {index + 1} "
            f"از {len(messages)}"
        )

        return text

    except Exception as e:

        print(
            "❌ خطا در خواندن "
            "morning_messages.json:"
        )

        print(e)

        return None


# =========================================================
# خواندن فایل TXT
# =========================================================

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
        ) as f:

            content = f.read()

        # یکسان‌سازی خط‌ها
        content = content.replace(
            "\r\n",
            "\n"
        )

        content = content.replace(
            "\r",
            "\n"
        )

        # جدا کردن متن‌ها
        parts = content.split("\n\n")

        messages = []

        for part in parts:

            text = part.strip()

            if text:

                messages.append(text)

        return messages

    except Exception as e:

        print(
            f"❌ خطا در خواندن فایل "
            f"{filename}:"
        )

        print(e)

        return []


# =========================================================
# انتخاب متن روزانه
# =========================================================

def get_daily_index(count):

    if count <= 0:

        return 0

    today = datetime.now().date()

    days_passed = (
        today - START_DATE
    ).days

    if days_passed < 0:

        return 0

    return days_passed % count


# =========================================================
# ارسال فایل‌های TXT
# =========================================================

def send_txt_file(filename):

    print()
    print("=" * 60)
    print(f"📄 فایل: {filename}")
    print("=" * 60)

    messages = load_txt_messages(
        filename
    )

    if not messages:

        print(
            "⚠️ هیچ متنی در این فایل پیدا نشد."
        )

        return False

    index = get_daily_index(
        len(messages)
    )

    text = messages[index]

    print(
        f"📝 متن شماره "
        f"{index + 1} "
        f"از {len(messages)}"
    )

    print(
        "📤 در حال ارسال..."
    )

    success = send_message(text)

    if success:

        print(
            f"✅ متن فایل "
            f"{filename} "
            f"با موفقیت ارسال شد."
        )

        return True

    print(
        f"❌ ارسال فایل "
        f"{filename} "
        f"ناموفق بود."
    )

    return False


# =========================================================
# برنامه اصلی
# =========================================================

def main():

    print()
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
        "🆔 Chat ID:",
        CHAT_ID
    )

    print("=" * 60)

    # -----------------------------------------------------
    # بررسی Token
    # -----------------------------------------------------

    if not TOKEN:

        print(
            "❌ EITAA_TOKEN پیدا نشد."
        )

        print(
            "Secret مربوط به EITAA_TOKEN "
            "را در GitHub Actions بررسی کن."
        )

        return

    print(
        "✅ EITAA_TOKEN دریافت شد."
    )

    # -----------------------------------------------------
    # مرحله ۱
    # پیام صبح‌بخیر
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("🌅 مرحله ۱: پیام صبح‌بخیر")
    print("=" * 60)

    morning_message = (
        load_morning_message()
    )

    if morning_message:

        success = send_message(
            morning_message
        )

        if success:

            print(
                "✅ پیام صبح‌بخیر ارسال شد."
            )

        else:

            print(
                "❌ ارسال پیام صبح‌بخیر ناموفق بود."
            )

    else:

        print(
            "⚠️ پیام صبح‌بخیر ارسال نشد."
        )

    # -----------------------------------------------------
    # مرحله ۲
    # فایل‌های TXT
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("📚 مرحله ۲: فایل‌های متنی")
    print("=" * 60)

    for filename in FILES_TO_SEND:

        send_txt_file(
            filename
        )

    # -----------------------------------------------------
    # پایان
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("✅ عملیات امروز تمام شد.")
    print("=" * 60)


# =========================================================
# اجرای برنامه
# =========================================================

if __name__ == "__main__":

    main()
