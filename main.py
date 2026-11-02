import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from huggingface_hub import InferenceClient
from PIL import Image

BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Running!"

hf_client = InferenceClient(provider="fal-ai", api_key=HF_TOKEN)

def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text("👗 **2 Photo Bot**\n\n1️⃣ Aadyam NINTE photo ayakk (dress idendavar)\n2️⃣ Pinne DRESS-nte photo ayakk\n\nAadyam ninte photo ayakk 👇")

def photo_handler(update: Update, context: CallbackContext):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    
    # First photo alla?
    if 'person' not in context.user_data:
        file.download("person.jpg")
        context.user_data['person'] = True
        update.message.reply_text("✅ Person photo kitti!\n\nIppo 2️⃣ DRESS photo ayakk - eth dress venamo athinte photo!")
    else:
        file.download("dress.jpg")
        update.message.reply_text("⏳ Dress maati tharam... 30 sec wait...")
        
        try:
            person_img = Image.open("person.jpg").convert("RGB")
            dress_img = Image.open("dress.jpg").convert("RGB")
            
            # Qwen dual image edit - 2 image kodukkum
            prompt = "Transfer the exact outfit from the second image (dress reference) onto the person in the first image. Keep the first person's face, body pose, background same. Realistic, modest fashion, high quality"
            
            # fal-ai provider 2 image support cheyyum
            edited = hf_client.image_to_image(
                image=[person_img, dress_img],
                prompt=prompt,
                model="Qwen/Qwen-Image-Edit"
            )
            edited.save("output.jpg")
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("output.jpg", 'rb'), caption="✅ Dress transfer ready!")
            context.user_data.clear()
            
        except Exception as e:
            # Single image fallback - first image mathi eduth try
            try:
                person_img = Image.open("person.jpg").convert("RGB")
                prompt2 = "Change outfit to match the dress in reference image, keep face same, realistic"
                edited = hf_client.image_to_image(image=person_img, prompt=prompt2, model="Qwen/Qwen-Image-Edit")
                edited.save("output.jpg")
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("output.jpg", 'rb'), caption="✅ Ready (single mode)!")
            except Exception as e2:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}\n{e2}")
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
