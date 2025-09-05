import os
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен зберігається у секретах fly.io
TOKEN = os.getenv("BOT_TOKEN")

# Завантажуємо Excel-таблицю (має бути в цій же папці)
df = pd.read_excel("data.xlsx")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли слово, і я знайду його в таблиці 📊")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    result = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
    
    if not result.empty:
        text = result.to_string(index=False)
        await update.message.reply_text(f"🔎 Знайшов:\n{text}")
    else:
        await update.message.reply_text("Нічого не знайшов 😔")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.run_polling()

if __name__ == "__main__":
    main()
