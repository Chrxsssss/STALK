from vercel_kv import KV
import os

KV_URL = os.environ.get("KV_URL")  # À configurer dans Vercel Dashboard

def get_kv():
    return KV(KV_URL)

def save_config(token, chat_id):
    kv = get_kv()
    kv.set("bot_token", token)
    kv.set("chat_id", chat_id)
    kv.set("active", "true")

def get_config():
    kv = get_kv()
    return {
        "token": kv.get("bot_token"),
        "chat_id": kv.get("chat_id"),
        "active": kv.get("active") == "true"
    }
