import json
import time
import os
import random
import requests
from datetime import datetime


# =========================
# تنظیمات
# =========================

TOKEN = os.getenv("EITAA_TOKEN")
CHAT_ID = "11229751"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POSTS_FILE = os.path.join(
    BASE_DIR,
    "posts.json"
)

MORNING_MESSAGES_FILE = os.path.join(
    BASE_DIR,
    "morning_messages.json"
)

MORNING_STATE_FILE = os.path.join(
    BASE_DIR,
    "morning_state.json"
)

MORNING_CONFIG_FILE = os.path.join(
    BASE_DIR,
    "morning_config.json"
)


# جلوگیری از ارسال دوباره پست‌های معمولی
sent_posts = set()


# =========================
# ارسال پیام متنی
# =========================

def send_message(text):

    url = f"https://eitaayar.ir/api/{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(
        url,
        data=data
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    try:
        return response.json()

    except:
        return {
            "ok": False
        }


# =========================
# ارسال عکس
# =========================

def send_photo(file_path, caption=""):

    url = f"https://eitaayar.ir/api/{TOKEN}/sendFile"

    full_path = os.path.join(
        BASE_DIR,
        file_path
    )

    if not os.path.exists(full_path):

        print(
            "❌ عکس پیدا نشد:",
            full_path
        )

        return {
            "ok": False
        }


    with open(
        full_path,
        "rb"
    ) as photo:

        files = {
            "file": photo
        }

        data = {
            "chat_id": CHAT_ID,
            "title": "عکس کودکستان",
            "caption": caption
        }

        response = requests.post(
            url,
            files=files,
            data=data
        )


    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.text
    )


    try:

        return response.json()

    except:

        return {
            "ok": False
        }


# =========================
# ارسال فایل
# =========================

def send_file(file_path, caption=""):

    url = f"https://eitaayar.ir/api/{TOKEN}/sendFile"

    full_path = os.path.join(
        BASE_DIR,
        file_path
    )

    if not os.path.exists(full_path):

        print(
            "❌ فایل پیدا نشد:",
            full_path
        )

        return {
            "ok": False
        }


    with open(
        full_path,
        "rb"
    ) as file:

        files = {
            "file": file
        }

        data = {
            "chat_id": CHAT_ID,
            "title": "فایل کودکستان",
            "caption": caption
        }

        response = requests.post(
            url,
            files=files,
            data=data
        )


    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.text
    )


    try:

        return response.json()

    except:

        return {
            "ok": False
        }


# =========================
# خواندن posts.json
# =========================

def load_posts():

    try:

        with open(
            POSTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        print(
            "❌ خطا در خواندن posts.json:",
            e
        )

        return []


# =========================
# خواندن پیام‌های صبح بخیر
# =========================

def load_morning_messages():

    try:

        with open(
            MORNING_MESSAGES_FILE,
            "r",
            encoding="utf-8-sig"
        ) as file:

            messages = json.load(file)


        if not isinstance(messages, list):

            print(
                "❌ morning_messages.json باید یک لیست باشد."
            )

            return []


        messages = [
            str(message).strip()
            for message in messages
            if str(message).strip()
        ]


        return messages


    except Exception as e:

        print(
            "❌ خطا در خواندن morning_messages.json:",
            e
        )

        return []


# =========================
# خواندن تنظیمات صبح بخیر
# =========================

def load_morning_config():

    default_config = {

        "enabled": True,

        "time": "09:00"

    }


    try:

        with open(
            MORNING_CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)


        if not isinstance(config, dict):

            return default_config


        return config


    except:

        return default_config


# =========================
# خواندن وضعیت صبح بخیر
# =========================

def load_morning_state():

    default_state = {

        "used": [],

        "last_sent_date": ""

    }


    try:

        with open(
            MORNING_STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            state = json.load(file)


        if not isinstance(state, dict):

            return default_state


        if "used" not in state:

            state["used"] = []


        if "last_sent_date" not in state:

            state["last_sent_date"] = ""


        return state


    except:

        return default_state


# =========================
# ذخیره وضعیت صبح بخیر
# =========================

def save_morning_state(state):

    with open(
        MORNING_STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# انتخاب پیام بدون تکرار
# =========================

def get_random_morning_message():

    messages = load_morning_messages()

    if not messages:

        print(
            "❌ هیچ پیام صبح بخیری پیدا نشد."
        )

        return None


    state = load_morning_state()

    used = state.get(
        "used",
        []
    )


    # حذف شماره‌های نامعتبر
    used = [
        index
        for index in used
        if isinstance(index, int)
        and 0 <= index < len(messages)
    ]


    # اگر همه پیام‌ها استفاده شده‌اند
    if len(used) >= len(messages):

        print(
            "🔄 همه پیام‌های صبح بخیر استفاده شدند؛ "
            "چرخه جدید شروع شد."
        )

        used = []


    available = [
        index
        for index in range(len(messages))
        if index not in used
    ]


    selected_index = random.choice(
        available
    )


    selected_message = messages[
        selected_index
    ]


    used.append(
        selected_index
    )


    state["used"] = used

    save_morning_state(
        state
    )


    print(
        f"🌸 پیام صبح بخیر شماره "
        f"{selected_index + 1} "
        f"از {len(messages)} انتخاب شد."
    )


    return selected_message


# =========================
# ارسال صبح بخیر روزانه
# =========================

def check_morning_message():

    config = load_morning_config()

    if not config.get(
        "enabled",
        True
    ):

        return


    morning_time = str(
        config.get(
            "time",
            "09:00"
        )
    ).strip()


    now = datetime.now()

    current_date = now.strftime(
        "%Y-%m-%d"
    )

    current_time = now.strftime(
        "%H:%M"
    )


    state = load_morning_state()

    last_sent_date = state.get(
        "last_sent_date",
        ""
    )


    # اگر امروز قبلاً ارسال شده، دوباره ارسال نکن
    if last_sent_date == current_date:

        return


    if current_time != morning_time:

        return


    print(
        "☀️ زمان ارسال صبح بخیر رسید."
    )


    message = get_random_morning_message()


    if not message:

        return


    result = send_message(
        message
    )


    if result.get("ok") is True:

        state["last_sent_date"] = current_date

        save_morning_state(
            state
        )


        print(
            "✅ پیام صبح بخیر امروز با موفقیت ارسال شد."
        )

    else:

        print(
            "❌ ارسال صبح بخیر ناموفق بود."
        )


# =========================
# شروع ربات
# =========================

print(
    "🌸 ربات کودکستان شکوفه‌های مهدوی اجرا شد."
)

print(
    "☀️ سیستم صبح بخیر روزانه فعال است."
)


# =========================
# حلقه اصلی
# =========================

while True:

    try:

        now = datetime.now()

        current_date = now.strftime(
            "%Y-%m-%d"
        )

        current_time = now.strftime(
            "%H:%M"
        )


        print(
            "⏰ زمان فعلی:",
            current_date,
            current_time
        )


        # =========================
        # صبح بخیر روزانه
        # =========================

        check_morning_message()


        # =========================
        # پست‌های زمان‌بندی‌شده معمولی
        # =========================

        posts = load_posts()


        for index, post in enumerate(posts):

            post_id = (
                f"{index}_"
                f"{post.get('date', '')}_"
                f"{post.get('time', '')}"
            )


            if post_id in sent_posts:

                continue


            if (
                post.get("date")
                == current_date
                and
                post.get("time")
                == current_time
            ):


                print(
                    "📤 در حال ارسال..."
                )


                post_type = post.get(
                    "type",
                    "text"
                )


                # =========================
                # متن
                # =========================

                if post_type == "text":

                    result = send_message(
                        post.get(
                            "text",
                            ""
                        )
                    )


                # =========================
                # عکس
                # =========================

                elif post_type == "photo":

                    result = send_photo(
                        post.get(
                            "file",
                            ""
                        ),
                        post.get(
                            "caption",
                            ""
                        )
                    )


                # =========================
                # فایل
                # =========================

                elif post_type == "file":

                    result = send_file(
                        post.get(
                            "file",
                            ""
                        ),
                        post.get(
                            "caption",
                            ""
                        )
                    )


                else:

                    print(
                        "❌ نوع پست ناشناخته:",
                        post_type
                    )

                    result = {
                        "ok": False
                    }


                if result.get("ok") is True:

                    sent_posts.add(
                        post_id
                    )

                    print(
                        "✅ ارسال با موفقیت انجام شد."
                    )


        # بررسی هر 20 ثانیه

        time.sleep(20)


    except KeyboardInterrupt:

        print(
            "\n🛑 ربات متوقف شد."
        )

        break


    except Exception as e:

        print(
            "❌ خطا:",
            e
        )

        time.sleep(20)
