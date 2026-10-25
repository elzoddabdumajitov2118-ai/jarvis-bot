import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

API_KEYS = [
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

current_key_index = 0

def get_next_client():
    global current_key_index
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return genai.Client(api_key=key)

client = get_next_client()
user_chats = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global client
    user_id = update.effective_user.id
    user_message = update.message.text
    if not user_message:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    if user_id not in user_chats:
        user_chats[user_id] = client.chats.create(
            model="gemini-3.8-flash",
            config={
                "system_instruction": "You are JARVIS, a helpful, intelligent, and detailed personal AI assistant. Provide complete, clear, and thorough answers to the user.",
                "max_output_tokens": 1500
            }
        )
    
    chat = user_chats[user_id]
    
    for attempt in range(len(API_KEYS)):
        try:
            response = chat.send_message(user_message)
            await update.message.reply_text(response.text)
            return
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                client = get_next_client()
                user_chats[user_id] = client.chats.create(
                    model="gemini-3.8-flash",
                    config={
                        "system_instruction": "You are JARVIS. Provide complete and detailed answers.",
                        "max_output_tokens": 1500
                    }
                )
                chat = user_chats[user_id]
                continue
            else:
                await update.message.reply_text(f"Xatolik: {e}")
                return

    await update.message.reply_text("Barcha API kalitlarning limiti vaqtincha tugadi. Biroz kuting.")

if __name__ == "__main__":
    # Tokenni Render'dagi Environment Variables'dan avtomatik o'qiydi
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("--- Render JARVIS Online ---")
    app.run_polling()