import logging
from database import write_to_db, get_stat
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler, MessageHandler, filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
START_ROUTES, INPUT_ROUTES, SHOW_ROUTES = range(3)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Создать запись", callback_data=str(ONE)),
            InlineKeyboardButton("Отчет продаж", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что вы хотите сделать?",
                                    reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def start_over(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Создать запись", callback_data=str(ONE)),
            InlineKeyboardButton("Список продаж", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Что вы хотите сделать?",
                                  reply_markup=reply_markup)
    return START_ROUTES


async def one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="Введите данные продажи в формате: \nДата (yyyy-MM-dd)\n"
             "Название товара \nЦена за единицу \nКоличество"
    )
    return INPUT_ROUTES


async def two(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="Введите дату начала и дату конца учетного периода в формате: "
             "\nДата налача (yyyy-MM-dd)\nДата конца")
    return SHOW_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


async def write_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # await update.message.reply_text(update.message.text)
    data = update.message.text.split("\n")
    if not insert_input_checker(data):
        result = "Произошла ошибка записи, проверьте формат данных"
    else:
        result = write_to_db(data)

    keyboard = [
        [
            InlineKeyboardButton("Создать запись", callback_data=str(ONE)),
            InlineKeyboardButton("Отчет продаж", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text(result)
    await update.message.reply_text("Что вы хотите сделать?",
                                    reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def show_stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # await update.message.reply_text(update.message.text)
    data = update.message.text.split("\n")
    if not stats_input_checker(data):
        result = "Произошла ошибка чтения, проверьте формат данных"
    else:
        result = get_stat(data)

    keyboard = [
        [
            InlineKeyboardButton("Создать запись", callback_data=str(ONE)),
            InlineKeyboardButton("Отчет продаж", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text(result)
    await update.message.reply_text("Что вы хотите сделать?",
                                    reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


def insert_input_checker(data):
    if len(data) == 4:
        return True


def stats_input_checker(data):
    if len(data) == 2:
        return True


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6204437005:AAF28-Lep02stJ7BQ8auXy-xXsR8hAg2Vco").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(two, pattern="^" + str(TWO) + "$")

            ],
            INPUT_ROUTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, write_data),
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            ],
            SHOW_ROUTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_stat),

            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application
    # that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()