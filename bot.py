import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен зберігається у секретах Fly.io
TOKEN = os.getenv("BOT_TOKEN")

# Завантажуємо Excel-таблицю
df = pd.read_excel("data.xlsx")

# Перетворюємо колонку Year у int або залишаємо порожньою
if "Year" in df.columns:
    df["Year"] = df["Year"].apply(lambda x: int(x) if pd.notna(x) else "")

# Функція головного меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Пошук у базі", callback_data="search")],
        [InlineKeyboardButton("📞 Контакти", callback_data="contacts")],
        [InlineKeyboardButton("ℹ️ Довідка", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавіатура для підменю (лише одна кнопка "На головну")
def back_to_menu_keyboard():
    keyboard = [[InlineKeyboardButton("🏠 На головну", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)

# Стартове меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт!😉\n"
        "Це телеграм-бот із пошуку датасетів.\n"
        "Для початку, виберіть розділ:⤵️",
        reply_markup=main_menu_keyboard()
    )

# Функція для очищення даних і заміни порожніх значень на ---
def clean(value):
    if pd.isna(value) or str(value).strip() == "":
        return "---"
    return str(value)

# Відправка результатів блоками
async def send_results(update_or_query, context, results, page=0):
    per_page = 5   # по 5 результатів на сторінку
    total_pages = (len(results) + per_page - 1) // per_page
    start = page * per_page
    end = start + per_page
    chunk = results[start:end]

    if not chunk.empty:
        text = ""
        for _, row in chunk.iterrows():
            text += f"🆔 *Article:* {clean(row.get('Article'))}\n"
            text += f"🔢 *Version:* {clean(row.get('Version'))}\n"
            text += f"📊 *Dataset:* {clean(row.get('Dataset'))}\n"
            text += f"🚙 *Model:* {clean(row.get('Model'))}\n"
            text += f"📅 *Year:* {clean(row.get('Year'))}\n"
            text += f"🌍 *Region:* {clean(row.get('Region'))}\n"
            text += "--------------------------------------\n"

        # Лічильник сторінок
        text += f"\n📖 _Сторінка {page+1} з {total_pages}_"

        # Кнопки навігації
        keyboard = []
        if page > 0:
            keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
        if end < len(results):
            keyboard.append(InlineKeyboardButton("➡️ Далі", callback_data=f"page_{page+1}"))
        keyboard.append(InlineKeyboardButton("🏠 Головне меню", callback_data="menu"))

        reply_markup = InlineKeyboardMarkup([keyboard])

        if hasattr(update_or_query, "message"):
            await update_or_query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await update_or_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        if hasattr(update_or_query, "message"):
            await update_or_query.message.reply_text("⚠️ Нічого не знайдено.", reply_markup=main_menu_keyboard())
        else:
            await update_or_query.edit_message_text("⚠️ Нічого не знайдено.", reply_markup=main_menu_keyboard())

# Обробка натискань кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.message.reply_text("Введіть артикул блоку чи назву датасету для пошуку:")
    elif query.data == "contacts":
        await query.message.reply_text(
            "📞 Контакти:\n"
            "Email: datenflash@proton.me\n"
            "Telegram: @mukich1 або @mr_muhich\n"
            "Instagram: @codiVAG",
            reply_markup=back_to_menu_keyboard()
        )
    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Довідка:\n"
            "Цей телеграм-бот створений для швидкого пошуку датасетів у нашій базі даних.\n"
            "Для пошуку просто введіть артикул блоку управління або назву датасету",
            reply_markup=back_to_menu_keyboard()
        )
    elif query.data == "menu":
        await query.message.reply_text(
            "🏠 Ви повернулися в головне меню.",
            reply_markup=main_menu_keyboard()
        )
    elif query.data.startswith("page_"):
        _, page = query.data.split("_")
        page = int(page)
        results = context.user_data.get("search_results", pd.DataFrame())
        if not results.empty:
            await send_results(query, context, results, page)

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
        await send_results(update, context, results, page=0)
    else:
        await update.message.reply_text("⚠️ Нічого не знайдено.", reply_markup=main_menu_keyboard())

# Основна функція
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_database))
    app.run_polling()

if __name__ == "__main__":
    main()
