import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен зберігається у секретах Fly.io
TOKEN = os.getenv("BOT_TOKEN")

# Завантажуємо Excel-таблицю (має бути в тій же папці)
df = pd.read_excel("data.xlsx")

# Функція створює головне меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Пошук у базі", callback_data="search")],
        [InlineKeyboardButton("Контакти", callback_data="contacts")],
        [InlineKeyboardButton("Довідка", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Стартове меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Це бот із пошуку датасетів. Для початку, виберіть розділ:",
        reply_markup=main_menu_keyboard()
    )

# Обробка натискань кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.message.reply_text("Введіть артикул блоку чи назву датасету для пошуку:")
    elif query.data == "contacts":
        await query.message.reply_text(
            "📞 Контакти:\nEmail: datenflash@proton.me\nТелеграм: @mukich1",
            reply_markup=main_menu_keyboard()
        )
    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Довідка:\n"
            "1️⃣ Пошук у базі — знайти інформацію.\n"
            "2️⃣ Контакти — зв'язок з адміністрацією.\n"
            "3️⃣ Довідка — ця інструкція.",
            reply_markup=main_menu_keyboard()
        )

# Пошук у базі з гарним форматуванням
async def search_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    mask = (
        df['Article'].str.contains(query, case=False, na=False) |
        df['Dataset'].str.contains(query, case=False, na=False)
    )
    result = df[mask]

    if not result.empty:
        text = ""
        for _, row in result.iterrows():
            text += f"🆔 *Article:* {row['Article']}\n"
            text += f"📊 *Dataset:* {row['Dataset']}\n"
            text += "---------------------\n"
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("Нічого не знайдено 😔", reply_markup=main_menu_keyboard())

# Основна функція
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_database))
    app.run_polling()

if __name__ == "__main__":
    main()
