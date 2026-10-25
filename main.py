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
# 2. BOT VA GEMINI MANTIQIY QISMI
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Google GenAI mijozini ishga tushirish
ai_client = genai.Client()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # Gemini orqali javob generatsiya qilish
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! Render'da Environment Variables bo'limiga BOT_TOKEN qo'shganingizni tekshiring.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Foydalanuvchidan kelgan matnli xabarlarni qayta ishlash
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("JARVIS Bot muvaffaqiyatli ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
