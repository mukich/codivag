import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен зберігається у секретах Fly.io
TOKEN = os.getenv("BOT_TOKEN")

# Завантажуємо Excel-таблицю
df = pd.read_excel("data.xlsx")

# Функція головного меню
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

# Обробка кнопок меню
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
    elif query.data.startswith("page_"):
        _, page = query.data.split("_")
        page = int(page)
        results = context.user_data.get("search_results", [])
        await send_results(update, results, page)

# Функція виводу результатів блоками
async def send_results(update, results, page=0):
    per_page = 10
    start = page * per_page
    end = start + per_page
    chunk = results[start:end]

    if not chunk:
        await update.callback_query.message.reply_text("⚠️ Немає результатів для відображення.", reply_markup=main_menu_keyboard())
        return

    text = ""
    for _, row in chunk.iterrows():
        text += f"🆔 *Article:* {row.get('Article','N/A')}\n"
        text += f"🔢 *Version:* {row.get('Version','N/A')}\n"
        text += f"📊 *Dataset:* {row.get('Dataset','N/A')}\n"
        text += f"💻 *Model:* {row.get('Model','N/A')}\n"
        text += f"📅 *Year:* {row.get('Year','N/A')}\n"
        text += f"🌍 *Region:* {row.get('Region','N/A')}\n"
        text += "---------------------\n"

    # Кнопки пагінації
    keyboard = []
    if page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    if end < len(results):
        keyboard.append(InlineKeyboardButton("➡️ Далі", callback_data=f"page_{page+1}"))
    keyboard.append(InlineKeyboardButton("🏠 Головне меню", callback_data="menu"))

    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.callback_query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# Пошук у базі
async def search_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    mask = (
        df['Article'].str.contains(query, case=False, na=False) |
        df['Dataset'].str.contains(query, case=False, na=False)
    )
    results = df[mask]

    if not results.empty:
        context.user_data["search_results"] = results
        # Стартуємо з першої сторінки
        dummy = type("obj", (object,), {"callback_query": update})
        await send_results(dummy, results, page=0)
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
