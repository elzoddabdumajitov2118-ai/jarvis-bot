import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

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
# 2. MULTI-KEY (10 TA API) ROTATION TIZIMI
# ==========================================
BOT_TOKEN = os.environ.get("8878852882:AAHoEcCIG7LtqQvzRobwp8zhwtYu3nfpkLQ")
raw_keys = os.environ.get("GEMINI_API_KEYS", "AQ.Ab8RN6IyY3m_t3xPVlIngvwms6CU-5qV6uOwD409R3nRqI4QTA

AQ.Ab8RN6Iht85MbHgRRGJptRURcXp-V1t1xsDVOaOw-ZtKMCBPWA

AQ.Ab8RN6IuwuzQATJUu0Rwy8dIXOwT8E4jGj2FchEmGgBgWFwcDQ

AQ.Ab8RN6ImhhHnQo34_Ud1zwPV5VSHGiMK25jlSYFpA4MXpyZgmA

AQ.Ab8RN6Kc_twXMVBNIfnzcRmYWNAN4XpwxjLWHdcy5UmhwjBnDQ

AQ.Ab8RN6IIf7xmUSscnjnKsX10rg4nmF4WFW_9H3-P7UUsT0-1uQ

AQ.Ab8RN6KueQp89q_gvJFhrJWC_t4hM-gDDr-YYDfAMuASrKHvlw

AQ.Ab8RN6KhIn-OWLkaVRUWdJyCx5ftzVOBqaQ6RCl1EpCJoDebsw

AQ.Ab8RN6JhPlh2rkt8_42qwjJu7469Vd-Zn1wxyiaekIuNyY5-eg

AQ.Ab8RN6LFwGjQ9yHh1lgSW_oK-ZdDP9WNJlw1Qur1ohqwQ0X7Xw")

# Agar vergul bilan kiritilgan bo'lsa, ularni ro'yxatga ajratib olamiz
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Render'da BOT_TOKEN ni kiriting.")
if not API_KEYS:
    raise ValueError("GEMINI_API_KEYS topilmadi! Render'da kalitlarni vergul bilan kiriting.")

current_key_index = 0

def get_next_client():
    global current_key_index
    key = API_KEYS[current_key_index]
    # Keyingi safar ro'yxatdagi keyingi kalitga o'tamiz (aylana bo'ylab)
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return genai.Client(api_key=key)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Barcha kalitlarni sinab ko'ramiz (agar bittasi ishlamasa, keyingisiga o'tadi)
    attempts = len(API_KEYS)
    for _ in range(attempts):
        client = get_next_client()
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
            )
            await update.message.reply_text(response.text)
            return
        except Exception as e:
            error_str = str(e)
            # Agar limit tugagan bo'lsa (429 / Quota / ResourceExhausted), tsikl davom etib keyingi kalitni oladi
            if "429" in error_str or "ResourceExhausted" in error_str or "quota" in error_str.lower():
                continue
            else:
                await update.message.reply_text(f"Xatolik yuz berdi: {e}")
                return

    await update.message.reply_text("Barcha 10 ta API kalitlarning limiti vaqtincha tugadi. Iltimos, biroz kuting.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("JARVIS Bot (Multi-Key Rotation) bilan ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
