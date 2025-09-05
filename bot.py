import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен зберігається у секретах fly.io
TOKEN = os.getenv("BOT_TOKEN")

# Завантажуємо Excel-таблицю (має бути в цій же папці)
df = pd.read_excel("data.xlsx")

# Створюємо стартове меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Пошук у базі", callback_data="search")],
        [InlineKeyboardButton("Контакти", callback_data="contacts")],
        [InlineKeyboardButton("Довідка", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Виберіть розділ:", reply_markup=reply_markup)

# Обробка натискань кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.message.reply_text("Введіть артикул блоку чи назву датасету для пошуку:")
        # Наступний текст користувача буде оброблятися MessageHandler
    elif query.data == "contacts":
        await query.message.reply_text("📞 Контакти:\nEmail: datenflash@proton.me\nТелеграм: @mukich1")
    elif query.data == "help":
        await query.message.reply_text("ℹ️ Довідка:\n1️⃣ Пошук у базі — знайти інформацію.\n2️⃣ Контакти — зв'язок з адміністрацією.\n3️⃣ Довідка — ця інструкція.")

# Пошук у базі
async def search_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    mask = (
        df['Article'].str.contains(query, case=False, na=False) |
        df['Dataset'].str.contains(query, case=False, na=False)
    )
    result = df[mask]
    if not result.empty:
        await update.message.reply_text(result.to_string(index=False))
    else:
        await update.message.reply_text("Нічого не знайдено 😔")

# Основна функція
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_database))
    app.run_polling()

if __name__ == "__main__":
    main()
