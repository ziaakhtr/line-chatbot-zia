from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# Load environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv[LINE_CHANNEL_ACCESS_TOKEN]
LINE_CHANNEL_SECRET = os.environ[LINE_CHANNEL_SECRET]
HELPINGAI_API_KEY = os.environ[HELPINGAI_API_KEY]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook error:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    # Call Helping AI API
    headers = {
        "Authorization": f"Bearer {HELPINGAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",  # or whatever model HelpingAI provides
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(
            "https://api.helping.ai/v1/chat/completions",  # Replace with actual endpoint from Helping AI
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            reply_text = data["choices"][0]["message"]["content"]
        else:
            print("HelpingAI API error:", response.status_code, response.text)
            reply_text = "Sorry, the bot is not available right now."

    except Exception as e:
        print("API call failed:", e)
        reply_text = "Error connecting to AI service."

    # Reply via LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text.strip())
    )
