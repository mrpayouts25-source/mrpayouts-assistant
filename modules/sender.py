import requests
from config import BOT_TOKEN, CHAT_ID

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)
    print(response.text)