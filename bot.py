import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from mega import Mega
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define stages
EMAIL, PASSWORD = range(2)

# Define Mega instance
mega = Mega()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user for their email."""
    await update.message.reply_text('Hi! I am your MEGA.nz bot. Please send me your MEGA.nz email.')
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the email and asks for the password."""
    user = update.message.from_user
    logger.info("Email of %s: %s", user.first_name, update.message.text)
    context.user_data['email'] = update.message.text
    await update.message.reply_text('Got it! Now, please send me your MEGA.nz password.')
    return PASSWORD

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Logs the user in and renames all files."""
    user = update.message.from_user
    logger.info("Password of %s: %s", user.first_name, update.message.text)
    email = context.user_data['email']
    password = update.message.text

    try:
        m = mega.login(email, password)
        files = m.get_files()
        for file in files:
            if 'a' in files[file]:
                file_name = files[file]['a']['n']
                file_ext = os.path.splitext(file_name)[1]
                new_name = f"renamed_{file}{file_ext}"
                m.rename(file, new_name)
        await update.message.reply_text('All files have been renamed successfully!')
    except Exception as e:
        logger.error("Error: %s", e)
        await update.message.reply_text('There was an error renaming the files. Please try again.')

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add conversation handler with the states EMAIL and PASSWORD
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()