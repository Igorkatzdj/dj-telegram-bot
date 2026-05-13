import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TOKEN = "8594966820:AAFGMwhblnOvpIMMe-xluba3SGUpNxozS7c"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Временное хранилище (для теста)
user_chats = {}
chat_tracks = {}

def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
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
            send_message(chat_id, "🎧 Привет! Я DJ-бот. Отправь /help.")
            
        elif text == "/help":
            send_message(chat_id, "📋 Команды:\n/connect — подключить группу\n/groups — список групп\n/tracks — треки в группе")
        
        elif text == "/connect" and msg["chat"]["type"] in ["group", "supergroup"]:
            user_id = msg["from"]["id"]
            chat_id = msg["chat"]["id"]
            if user_id not in user_chats:
                user_chats[user_id] = []
            if chat_id not in user_chats[user_id]:
                user_chats[user_id].append(chat_id)
            send_message(chat_id, "✅ Группа подключена! Кидайте треки.")
        
        elif "audio" in msg:
            chat_id = msg["chat"]["id"]
            file_id = msg["audio"]["file_id"]
            file_name = msg["audio"].get("file_name", "audio.mp3")
            if chat_id not in chat_tracks:
                chat_tracks[chat_id] = []
            chat_tracks[chat_id].append({"file_id": file_id, "name": file_name})
            send_message(chat_id, f"🎵 Трек сохранён: {file_name}")
    
    elif "callback_query" in update:
        callback = update["callback_query"]
        data = callback["data"]
        chat_id = callback["message"]["chat"]["id"]
        
        if data.startswith("track_"):
            parts = data.split("_")
            track_index = int(parts[1])
            deck = parts[2]
            tracks = chat_tracks.get(chat_id, [])
            if track_index < len(tracks):
                file_id = tracks[track_index]["file_id"]
                requests.post(BASE_URL + "/answerCallbackQuery", json={
                    "callback_query_id": callback["id"],
                    "text": f"Трек отправлен в Deck {deck}!",
                    "show_alert": False
                })
                send_message(chat_id, f"🎵 Трек для Deck {deck} готов. Откройте Mini App и нажмите 'Из Telegram'.")
    
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)