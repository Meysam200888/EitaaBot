```python
import json
import os
import requests
from datetime import datetime, date


# =========================================================
# تنظیمات
# =========================================================

TOKEN = os.environ.get("bot515886:d4de9ae0-e0f2-44d6-b57b-98605f81a7cf", "").strip()

CHAT_ID = "11234919"

# تاریخ شروع ارسال
START_DATE = date(2026, 8, 19)

# فایل پیام‌های صبح‌بخیر
MORNING_MESSAGES_FILE = "morning_messages.json"

# فایل‌های بعد از صبح‌بخیر
TEXT_FILES = [
    "مرحله_۱_۳۰۰_متن_فرزندپروری_و_روانشناسی_کودک.txt",
    "200_poems_children_shokoofehaye_mahdavi.txt",
    "300_texts_parenting_children.txt"
]

# فایل ذخیره وضعیت
STATE_FILE = "send_state.json"


# =========================================================
# ارسال پیام به ایتا
# =========================================================

def send_message(text):

    if not TOKEN:
        print("❌ EITAA_TOKEN در GitHub Secrets تنظیم نشده است.")
        return False

    if not CHAT_ID:
        print("❌ CHAT_ID تنظیم نشده است.")
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
            print("✅ پیام با موفقیت ارسال شد.")
            return True

        print("❌ ارسال پیام ناموفق بود.")
        return False

    except Exception as ex:

        print("❌ خطا در اتصال به ایتا:")
        print(ex)

        return False


# =========================================================
# خواندن پیام‌های صبح‌بخیر
# =========================================================

def load_morning_messages():

    if not os.path.exists(MORNING_MESSAGES_FILE):
        print(
            f"❌ فایل {MORNING_MESSAGES_FILE} پیدا نشد."
        )
        return []

    try:

        with open(
            MORNING_MESSAGES_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            messages = json.load(f)

        if not isinstance(messages, list):
            print("❌ morning_messages.json باید یک آرایه باشد.")
            return []

        result = []

        for message in messages:

            if isinstance(message, str):

                text = message.strip()

                if text:
                    result.append(text)

            elif isinstance(message, dict):

                if not message.get("enabled", True):
                    continue

                text = message.get("text", "").strip()

                if text:
                    result.append(text)

        return result

    except Exception as ex:

        print("❌ خطا در خواندن پیام‌های صبح‌بخیر:")
        print(ex)

        return []


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

        # تبدیل خطوط مختلف به \n
        content = content.replace("\r\n", "\n")
        content = content.replace("\r", "\n")

        # جدا کردن متن‌ها با یک یا چند خط خالی
        blocks = content.split("\n\n")

        messages = []

        for block in blocks:

            text = block.strip()

            if text:
                messages.append(text)

        return messages

    except Exception as ex:

        print(
            f"❌ خطا در خواندن {filename}:"
        )

        print(ex)

        return []


# =========================================================
# خواندن وضعیت قبلی
# =========================================================

def load_state():

    default_state = {
        "morning_index": 0,
        "text_file_index": 0,
        "text_message_indexes": [
            0,
            0,
            0
        ]
    }

    if not os.path.exists(STATE_FILE):
        return default_state

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            state = json.load(f)

        if not isinstance(state, dict):
            return default_state

        state.setdefault(
            "morning_index",
            0
        )

        state.setdefault(
            "text_file_index",
            0
        )

        state.setdefault(
            "text_message_indexes",
            [0, 0, 0]
        )

        while len(
            state["text_message_indexes"]
        ) < len(TEXT_FILES):

            state["text_message_indexes"].append(0)

        return state

    except Exception as ex:

        print("⚠️ خطا در خواندن وضعیت:")
        print(ex)

        return default_state


# =========================================================
# ذخیره وضعیت
# =========================================================

def save_state(state):

    try:

        with open(
            STATE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                state,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("💾 وضعیت ذخیره شد.")

    except Exception as ex:

        print("❌ خطا در ذخیره وضعیت:")
        print(ex)


# =========================================================
# ساخت لیست کامل پیام‌ها
# =========================================================

def build_all_messages():

    all_messages = []

    # -----------------------------------------
    # مرحله اول: پیام‌های صبح‌بخیر
    # -----------------------------------------

    morning_messages = load_morning_messages()

    print(
        f"🌅 تعداد پیام‌های صبح‌بخیر: "
        f"{len(morning_messages)}"
    )

    for message in morning_messages:

        all_messages.append(
            {
                "type": "morning",
                "file": MORNING_MESSAGES_FILE,
                "text": message
            }
        )

    # -----------------------------------------
    # مرحله دوم: فایل‌های TXT
    # -----------------------------------------

    for filename in TEXT_FILES:

        messages = load_txt_messages(filename)

        print(
            f"📄 {filename}: "
            f"{len(messages)} پیام"
        )

        for message in messages:

            all_messages.append(
                {
                    "type": "text",
                    "file": filename,
                    "text": message
                }
            )

    return all_messages


# =========================================================
# ارسال روزانه
# =========================================================

def main():

    today = datetime.now().date()

    print("====================================")
    print("🌸 Eitaa Automatic Message Sender")
    print("====================================")

    print("📅 Today:", today)

    # -----------------------------------------
    # بررسی تاریخ شروع
    # -----------------------------------------

    days_passed = (
        today - START_DATE
    ).days

    if days_passed < 0:

        print(
            "⏳ زمان شروع ارسال هنوز نرسیده است."
        )

        return

    # -----------------------------------------
    # ساخت لیست پیام‌ها
    # -----------------------------------------

    all_messages = build_all_messages()

    if not all_messages:

        print(
            "❌ هیچ پیامی برای ارسال پیدا نشد."
        )

        return

    print(
        f"📦 مجموع پیام‌ها: "
        f"{len(all_messages)}"
    )

    # -----------------------------------------
    # وضعیت قبلی
    # -----------------------------------------

    state = load_state()

    # -----------------------------------------
    # انتخاب پیام روز
    #
    # برای اینکه هر روز فقط یک پیام ارسال شود،
    # از تعداد روزهای گذشته استفاده می‌کنیم.
    # -----------------------------------------

    index = days_passed % len(all_messages)

    selected = all_messages[index]

    message = selected["text"]

    filename = selected["file"]

    message_type = selected["type"]

    print("------------------------------------")

    print(
        f"📌 شماره پیام: "
        f"{index + 1} / {len(all_messages)}"
    )

    print(
        f"📂 فایل: {filename}"
    )

    print(
        f"📋 نوع: {message_type}"
    )

    print("------------------------------------")

    # -----------------------------------------
    # جلوگیری از پیام خالی
    # -----------------------------------------

    if not message.strip():

        print(
            "❌ پیام انتخاب‌شده خالی است."
        )

        return

    # -----------------------------------------
    # ارسال
    # -----------------------------------------

    success = send_message(message)

    # -----------------------------------------
    # فقط در صورت موفقیت وضعیت ذخیره شود
    # -----------------------------------------

    if success:

        state["last_sent_date"] = str(today)

        state["last_sent_index"] = index

        state["last_sent_file"] = filename

        state["last_sent_type"] = message_type

        state["last_sent_text"] = message

        save_state(state)

        print("------------------------------------")
        print("✅ عملیات امروز با موفقیت انجام شد.")
        print("------------------------------------")

    else:

        print("------------------------------------")
        print("❌ پیام ارسال نشد.")
        print("⚠️ وضعیت جلو برده نشد.")
        print("------------------------------------")


# =========================================================
# اجرای برنامه
# =========================================================

if __name__ == "__main__":
    main()
```
