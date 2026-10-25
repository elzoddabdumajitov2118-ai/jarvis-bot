import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ==========================================
# 1. RENDER PORT TALABINI QONDIRUVCHI SERVER
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"JARVIS Bot is active and running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Veb-serverni fonda alohida oqimda ishga tushiramiz
threading.Thread(target=run_web_server, daemon=True).start()

# ==========================================
# 2. BEARER TOKEN ROTATION TIZIMI
# ==========================================
BOT_TOKEN = "8878852882:AAHoEcCIG7LtqQvzRobwp8zhwtYu3nfpkLQ"

# Siz bergan 10 ta standartsiz access tokenlar
API_TOKENS = [
    "AQ.Ab8RN6IyY3m_t3xPVlIngvwms6CU-5qV6uOwD409R3nRqI4QTA",
    "AQ.Ab8RN6Iht85MbHgRRGJptRURcXp-V1t1xsDVOaOw-ZtKMCBPWA",
    "AQ.Ab8RN6IuwuzQATJUu0Rwy8dIXOwT8E4jGj2FchEmGgBgWFwcDQ",
    "AQ.Ab8RN6ImhhHnQo34_Ud1zwPV5VSHGiMK25jlSYFpA4MXpyZgmA",
    "AQ.Ab8RN6Kc_twXMVBNIfnzcRmYWNAN4XpwxjLWHdcy5UmhwjBnDQ",
    "AQ.Ab8RN6IIf7xmUSscnjnKsX10rg4nmF4WFW_9H3-P7UUsT0-1uQ",
    "AQ.Ab8RN6KueQp89q_gvJFhrJWC_t4hM-gDDr-YYDfAMuASrKHvlw",
    "AQ.Ab8RN6KhIn-OWLkaVRUWdJyCx5ftzVOBqaQ6RCl1EpCJoDebsw",
    "AQ.Ab8RN6JhPlh2rkt8_42qwjJu7469Vd-Zn1wxyiaekIuNyY5-eg",
    "AQ.Ab8RN6LFwGjQ9yHh1lgSW_oK-ZdDP9WNJlw1Qur1ohqwQ0X7Xw"
]

current_token_index = 0

def get_next_token():
    global current_token_index
    token = API_TOKENS[current_token_index]
    current_token_index = (current_token_index + 1) % len(API_TOKENS)
    return token

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    attempts = len(API_TOKENS)
    for _ in range(attempts):
        token = get_next_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Javob topilmadi.")
                await update.message.reply_text(text)
                return
            else:
                # Agar token yaroqsiz (401) yoki limit tugagan bo'lsa (429/403), keyingi tokenga o'tamiz
                if response.status_code in [401, 429, 403]:
                    continue
                else:
                    # Boshqa turdagi xatolik chiqsa
                    continue
        except Exception:
            continue

    await update.message.reply_text("Barcha tokenlarning limiti tugagan yoki yaroqsiz.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("JARVIS Bot (Bearer Token Rotation) bilan ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
