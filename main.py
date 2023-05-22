import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
import time

from transcribe import get_transcribtion

API_KEY = os.getenv('SHHH_API_KEY')
MY_CHAT_ID = os.getenv('SHHH_MY_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename="log.txt"
)

...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = '''
    👋 Welcome to the ATC Voice-to-Text Bot!

    I'm here to assist you in converting Air Traffic Control (ATC) voice data into text. Simply send me a voice message containing the ATC audio, and I'll transcribe it for you.

    Please ensure that you have the necessary permissions to share and process ATC voice data. Respect any applicable regulations and privacy considerations.

    To get started, follow these steps:
    1️⃣ Send me a voice message with the ATC audio.
    2️⃣ Wait a moment while I process the audio and convert it into text.
    3️⃣ Once the conversion is complete, I'll send you the transcribed text.

    Note: The accuracy of the transcription may vary depending on the audio quality and clarity.

    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def handle_message(update, context):
    username = str(update.message.chat.username)
    chat_id = update.message.chat_id
    start = time.time()
    try:
        file = await context.bot.get_file(update.message.effective_attachment.file_id)

        # File Size Check 50mb
        if file.file_size > 50*1024*1024:
            end = time.time()
            logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(chat_id) + ": FAIL SIZE : " + str(file.file_size) + "Message was too big for processing, there is a 50mb limit")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Message was too big for processing, there is a 50mb limit")
            return

        file_name = await file.download_to_drive()
        file_path = os.path.join(os.getcwd(), str(file_name))

        text = get_transcribtion(file_path)
        os.remove(file_path)
      
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
    except:
        end = time.time()
        logging.log(logging.ERROR,str(end-start) + " " + username + " : " + str(chat_id)  + " : FAIL UNKNOWN : Failed processing message")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure processing your message")

if __name__ == '__main__':
    exitt = False
    if API_KEY == None:
        print("SHHH_API_KEY must be defined")
        exitt = True
    if MY_CHAT_ID == None:
        print("SHHH_MY_CHAT_ID must be defined")
        exitt = True

    if not exitt:
        application = ApplicationBuilder().token(API_KEY).build()

        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        unknown_handler = MessageHandler(filters.COMMAND, unknown)
        application.add_handler(unknown_handler)

        application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))

        application.run_polling()
    else:
        print ("Failed to run, please resolve exports issue and run again")