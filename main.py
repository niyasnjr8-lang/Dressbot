import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from gradio_client import Client
from PIL import Image

BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Running!"

client = Client("yisol/IDM-VTON", token=HF_TOKEN)

def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text("👗 2 Photo Bot\n\n1️⃣ Aadyam NINTE photo ayakk\n2️⃣ Pinne DRESS photo ayakk")

def photo_handler(update: Update, context: CallbackContext):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    
    if 'person' not in context.user_data:
        file.download("person.jpg")
        context.user_data['person'] = True
        update.message.reply_text("✅ Person kitti! Ippo 2️⃣ DRESS photo ayakk!")
    else:
        file.download("dress.jpg")
        update.message.reply_text("⏳ Dress maati tharam... 50 sec wait...")
        try:
            result = client.predict(
                dict={"background": Image.open("person.jpg"), "layers": [], "composite": None},
                garm_img=Image.open("dress.jpg"),
                garment_des="dress",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon"
            )
            out_path = result[0] if isinstance(result, (list, tuple)) else result
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(out_path, 'rb'), caption="✅ Dress ready!")
            context.user_data.clear()
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")
            context.user_data.clear()

def run_bot():
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.start_polling()
    updater.idle()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
