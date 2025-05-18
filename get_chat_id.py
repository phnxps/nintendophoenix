from telegram.ext import ApplicationBuilder, MessageHandler, filters
import os

BOT_TOKEN = os.getenv("8161617520:AAEbrPy1U_pJ0-arpBIhkDic7elR0x8YReQ")  # o pon directamente tu token como string

async def print_chat_id(update, context):
    chat_id = update.effective_chat.id
    print(f"✅ chat_id del grupo: {chat_id}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, print_chat_id))

print("📡 Esperando mensajes...")
app.run_polling()
