import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from gradio_client import Client

BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Running!"

edit_client = Client("Qwen/Qwen-Image-Edit", token=HF_TOKEN)

DRESSES = {
    "saree": "Kerala kasavu saree",
    "lehenga": "Red bridal lehenga",
    "gown": "Black long party gown",
    "casual": "Jeans and white top",
    "abaya": "Elegant black abaya"
}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👗 Photo ayakk, dress select cheyyam!")

def photo_handler(update: Update, context: CallbackContext):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    file.download("input.jpg")
    keyboard = [[InlineKeyboardButton("🥻 Saree", callback_data='saree'), InlineKeyboardButton("👗 Lehenga", callback_data='lehenga')],
                [InlineKeyboardButton("👘 Gown", callback_data='gown'), InlineKeyboardButton("👖 Casual", callback_data='casual')],
                [InlineKeyboardButton("🧕 Abaya", callback_data='abaya')]]
    update.message.reply_text("Etha dress? 👇", reply_markup=InlineKeyboardMarkup(keyboard))

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    dress = DRESSES[query.data]
    query.edit_message_text(f"⏳ {dress} try cheyyunnu... 20 sec...")
    try:
        result = edit_client.predict("input.jpg", f"Change outfit to {dress}, keep face same, modest fashion, realistic", 0, True, 1, api_name="/edit_image")
        # result list aanel first item edukkam
        image_path = result[0] if isinstance(result, (list, tuple)) else result
        context.bot.send_photo(chat_id=query.message.chat_id, photo=open(image_path, 'rb'), caption=f"{dress} Ready ✅")
    except Exception as e:
        context.bot.send_message(chat_id=query.message.chat_id, text=f"Error: {e}")

def run_bot():
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))
    updater.start_polling()
    updater.idle()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
