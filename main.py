
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

ASK_NAME, ASK_PHONE = range(2)

# Токен і чат ID беруться з середовища
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Отримати прайс-лист", callback_data='price')],
        [InlineKeyboardButton("📩 Залишити заявку", callback_data='apply')]
    ]
    await update.message.reply_text("Привіт! Обери опцію:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'price':
        if os.path.exists("price_list.pdf"):
            await query.message.reply_document(document=open("price_list.pdf", "rb"))
        else:
            await query.message.reply_text("Файл прайсу ще не додано.")
    elif query.data == 'apply':
        await query.message.reply_text("Як вас звати?")
        return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Ваш номер телефону:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    name = context.user_data['name']
    phone = context.user_data['phone']

    msg = f"📥 Нова заявка:\n👤 Ім'я: {name}\n📞 Телефон: {phone}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await update.message.reply_text("Дякуємо! Ми зв'яжемось з вами.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявку скасовано.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='apply')],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='price'))
    app.add_handler(conv_handler)

    print("Бот запущено!")
    app.run_polling()

if __name__ == "__main__":
    main()
