from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# Load environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
HF_API_TOKEN = os.environ["HF_API_TOKEN"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    print("Request body:", body)  # Log the incoming webhook

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook error:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    print("Received message:", user_input)

    HF_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.1"
    HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    prompt = f"User: {user_input}\nBot:"
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt}
        )
        print("HF response:", response.text)

        if response.status_code == 200:
            result = response.json()
            reply_text = result[0]["generated_text"].split("Bot:")[-1].strip()
        else:
            reply_text = "🤖 Bot error: HF status code " + str(response.status_code)

    except Exception as e:
        reply_text = "🤖 Bot crashed. Check logs."
        print("Error in HF request:", e)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

