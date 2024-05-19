import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from googletrans import Translator
from gtts import gTTS
from flask import Flask, request
import os
import time

server = Flask(__name__)

# Bot token
TOKEN = '7191614302:AAHzvVvYLngFpRUAoqm-TY8cv88fNxFwGrc'

bot = telebot.TeleBot(TOKEN)

translator = Translator()

user_language_choice = {}

# /start buyrug'iga javob beruvchi funksiya
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("UZ -> RU", callback_data="uz_ru"))
    markup.add(InlineKeyboardButton("UZ -> EN", callback_data="uz_en"))
    bot.reply_to(message, "Salom! Tarjima tilini tanlang:", reply_markup=markup)

# Callback so'rovlariga javob beruvchi funksiya
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "uz_ru":
        user_language_choice[call.from_user.id] = 'ru'
        bot.answer_callback_query(call.id, "Tarjima: O'zbek -> Rus")
        bot.send_message(call.message.chat.id, "Matnni yuboring:")
    elif call.data == "uz_en":
        user_language_choice[call.from_user.id] = 'en'
        bot.answer_callback_query(call.id, "Tarjima: O'zbek -> Ingliz")
        bot.send_message(call.message.chat.id, "Matnni yuboring:")

# Xabarlarni ushlab olish va tarjima qilish
@bot.message_handler(func=lambda message: True)
def translate_message(message):
    user_id = message.from_user.id
    if user_id in user_language_choice:
        dest_lang = user_language_choice[user_id]
        try:
            # Matnni tarjima qilish
            translation = translator.translate(message.text, src='uz', dest=dest_lang).text
            time.sleep(5)
            
            # Tarjima qilingan matnni audio formatga o'girish
            # tts = gTTS(text=translation, lang=dest_lang)
            # audio_file = f'translation_{user_id}.mp3'
            # tts.save(audio_file)

            # Tarjima qilingan matn va audio faylni yuborish
            bot.reply_to(message, f"Tarjima ({'Rus' if dest_lang == 'ru' else 'Ingliz'}): {translation}")
            # with open(audio_file, 'rb') as audio:
            #     bot.send_audio(message.chat.id, audio)
        except Exception as e:
            bot.reply_to(message, f"Tarjima qilishda xatolik: {str(e)}")
    else:
        bot.reply_to(message, "Avval tarjima tilini tanlang. /start buyrug'ini yuboring.")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://tg-translate-bot.onrender.com/' + TOKEN)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

# bot.polling(none_stop=True, timeout=60, port=8443)