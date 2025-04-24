async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"Ваш chat_id: {chat_id}")
    await update.message.reply_text(f"Ваш chat_id: {chat_id}")