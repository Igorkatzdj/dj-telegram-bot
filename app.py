import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "8594966820:AAFGMwhblnOvpIMMe-xluba3SGUpNxozS7c"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Временное хранилище
user_chats = {}
chat_tracks = {}

def send_message(chat_id, text):
    url = BASE_URL + "/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, json=data)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200
    
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        
        if text == "/start":
            send_message(chat_id, "🎧 Бот готов. Добавь меня в группу и напиши /connect")
        
        elif text == "/connect" and msg["chat"]["type"] in ["group", "supergroup"]:
            user_id = msg["from"]["id"]
            group_id = msg["chat"]["id"]
            if user_id not in user_chats:
                user_chats[user_id] = []
            if group_id not in user_chats[user_id]:
                user_chats[user_id].append(group_id)
            send_message(group_id, "✅ Группа подключена!")
        
        elif "audio" in msg:
            group_id = msg["chat"]["id"]
            file_id = msg["audio"]["file_id"]
            file_name = msg["audio"].get("file_name", "track.mp3")
            if group_id not in chat_tracks:
                chat_tracks[group_id] = []
            chat_tracks[group_id].append({"file_id": file_id, "name": file_name})
            send_message(group_id, f"🎵 Сохранён: {file_name}")
    
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)