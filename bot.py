import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ====== Налаштування токена ======
# Задай BOT_TOKEN у змінних оточення (наприклад, у Fly.io secrets або локально)
TOKEN = os.getenv("BOT_TOKEN")


# ====== Завантаження даних ======
def load_dataframe(path: str = "data.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except Exception as e:
        # Порожня таблиця як fallback, щоб бот не падав
        df = pd.DataFrame(columns=["Article", "Version", "Dataset", "Model", "Year", "Region"])

    # Гарантуємо наявність потрібних колонок
    for col in ["Article", "Version", "Dataset", "Model", "Year", "Region"]:
        if col not in df.columns:
            df[col] = ""

    # Перетворюємо Year у int, якщо можливо
    try:
        df["Year"] = df["Year"].apply(lambda x: int(x) if pd.notna(x) and str(x).strip() != "" else "")
    except Exception:
        pass

    # Всі текстові — в str
    for col in ["Article", "Version", "Dataset", "Model", "Region"]:
        try:
            df[col] = df[col].astype(str)
        except Exception:
            pass

    return df


df = load_dataframe("data.xlsx")


# ====== Словник перекладів (7 мов) ======
LANGUAGES = {
    "uk": {
        "name": "Українська",
        "start": "Привіт!😉\nЦе телеграм-бот із пошуку датасетів.\nДля початку, виберіть розділ ⤵️",
        "menu": {
            "search": "🔍 Пошук у базі",
            "contacts": "📞 Контакти",
            "help": "ℹ️ Довідка",
            "language": "🌐 Мова",
            "back": "🏠 На головну",
            "main": "🏠 Головне меню"
        },
        "labels": {
            "article": "🆔 *Артикул:*",
            "version": "🔢 *Версія:*",
            "dataset": "📊 *Датасет:*",
            "model": "🚙 *Модель:*",
            "year": "📅 *Рік:*",
            "region": "🌍 *Регіон:*"
        },
        "nav": {
            "prev": "⬅️ Назад",
            "next": "➡️ Далі",
            "main": "🏠 Головне меню",
            "contacts": "📞 Контакти"
        },
        "help": "ℹ️ Довідка:\nЦей телеграм-бот створений для швидкого пошуку датасетів у нашій базі даних.\nДля пошуку просто введіть артикул блоку управління або назву датасету",
        "contacts": "📞 Контакти:\nEmail: datenflash@proton.me\nTelegram: @mukich1 або @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Оберіть мову:",
        "changed": "✅ Мову змінено на {lang}",
        "not_found": "⚠️ Нічого не знайдено.",
        "enter_search": "Введіть артикул блоку чи назву датасету для пошуку ⤵️",
        "empty_query": "⚠️ Ви нічого не ввели. Спробуйте ще раз ⤵️",
        "short_query": "⚠️ Запит занадто короткий. Введіть мінімум 3 символи ⤵️",
        "back_menu": "🏠 Ви повернулися в головне меню.",
        "page": "📖 _Сторінка {cur} з {total}_",
        "search_ok": "✅ Знайдено результати!",
        "page_info": "📖 Ви на сторінці {cur} з {total}"
    },
    "en": {
        "name": "English",
        "start": "Hello!😉\nThis is a dataset search bot.\nPlease choose a section ⤵️",
        "menu": {
            "search": "🔍 Search database",
            "contacts": "📞 Contacts",
            "help": "ℹ️ Help",
            "language": "🌐 Language",
            "back": "🏠 Back to menu",
            "main": "🏠 Main menu"
        },
        "labels": {
            "article": "🆔 *Article:*",
            "version": "🔢 *Version:*",
            "dataset": "📊 *Dataset:*",
            "model": "🚙 *Model:*",
            "year": "📅 *Year:*",
            "region": "🌍 *Region:*"
        },
        "nav": {
            "prev": "⬅️ Prev",
            "next": "➡️ Next",
            "main": "🏠 Main menu",
            "contacts": "📞 Contacts"
        },
        "help": "ℹ️ Help:\nThis Telegram bot is designed for quick dataset search in our database.\nTo search, simply enter the control unit article number or dataset name",
        "contacts": "📞 Contacts:\nEmail: datenflash@proton.me\nTelegram: @mukich1 or @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Choose language:",
        "changed": "✅ Language changed to {lang}",
        "not_found": "⚠️ Nothing found.",
        "enter_search": "Enter the article number or dataset name to search ⤵️",
        "empty_query": "⚠️ You didn't type anything. Try again ⤵️",
        "short_query": "⚠️ Query too short. Please enter at least 3 characters ⤵️",
        "back_menu": "🏠 You returned to the main menu.",
        "page": "📖 _Page {cur} of {total}_",
        "search_ok": "✅ Results found!",
        "page_info": "📖 You are on page {cur} of {total}"
    },
    "de": {
        "name": "Deutsch",
        "start": "Hallo!😉\nDies ist ein Datensatz-Suchbot.\nBitte wählen Sie einen Bereich ⤵️",
        "menu": {
            "search": "🔍 In Datenbank suchen",
            "contacts": "📞 Kontakte",
            "help": "ℹ️ Hilfe",
            "language": "🌐 Sprache",
            "back": "🏠 Zurück zum Menü",
            "main": "🏠 Hauptmenü"
        },
        "labels": {
            "article": "🆔 *Artikel:*",
            "version": "🔢 *Version:*",
            "dataset": "📊 *Datensatz:*",
            "model": "🚙 *Modell:*",
            "year": "📅 *Jahr:*",
            "region": "🌍 *Region:*"
        },
        "nav": {
            "prev": "⬅️ Zurück",
            "next": "➡️ Weiter",
            "main": "🏠 Hauptmenü",
            "contacts": "📞 Kontakte"
        },
        "help": "ℹ️ Hilfe:\nDieser Telegram-Bot wurde für die schnelle Suche von Datensätzen in unserer Datenbank entwickelt.\nZur Suche geben Sie einfach die Artikelnummer oder den Datensatznamen ein",
        "contacts": "📞 Kontakte:\nEmail: datenflash@proton.me\nTelegram: @mukich1 oder @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Sprache wählen:",
        "changed": "✅ Sprache geändert zu {lang}",
        "not_found": "⚠️ Nichts gefunden.",
        "enter_search": "Geben Sie die Artikelnummer oder den Datensatznamen ein ⤵️",
        "empty_query": "⚠️ Sie haben nichts eingegeben. Bitte erneut versuchen ⤵️",
        "short_query": "⚠️ Anfrage zu kurz. Bitte mindestens 3 Zeichen eingeben ⤵️",
        "back_menu": "🏠 Sie sind ins Hauptmenü zurückgekehrt.",
        "page": "📖 _Seite {cur} von {total}_",
        "search_ok": "✅ Ergebnisse gefunden!",
        "page_info": "📖 Sie sind auf Seite {cur} von {total}"
    },
    "fr": {
        "name": "Français",
        "start": "Salut!😉\nCeci est un bot de recherche de jeux de données.\nVeuillez choisir une section ⤵️",
        "menu": {
            "search": "🔍 Recherche dans la base",
            "contacts": "📞 Contacts",
            "help": "ℹ️ Aide",
            "language": "🌐 Langue",
            "back": "🏠 Retour au menu",
            "main": "🏠 Menu principal"
        },
        "labels": {
            "article": "🆔 *Article:*",
            "version": "🔢 *Version:*",
            "dataset": "📊 *Jeu de données:*",
            "model": "🚙 *Modèle:*",
            "year": "📅 *Année:*",
            "region": "🌍 *Région:*"
        },
        "nav": {
            "prev": "⬅️ Précédent",
            "next": "➡️ Suivant",
            "main": "🏠 Menu principal",
            "contacts": "📞 Contacts"
        },
        "help": "ℹ️ Aide:\nCe bot Telegram est conçu pour la recherche rapide de jeux de données dans notre base.\nPour rechercher, entrez simplement le numéro de l’article ou le nom du dataset",
        "contacts": "📞 Contacts:\nEmail: datenflash@proton.me\nTelegram: @mukich1 ou @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Choisissez une langue:",
        "changed": "✅ Langue changée en {lang}",
        "not_found": "⚠️ Rien trouvé.",
        "enter_search": "Entrez le numéro de l’article ou le nom du dataset ⤵️",
        "empty_query": "⚠️ Vous n’avez rien saisi. Essayez encore ⤵️",
        "short_query": "⚠️ Requête trop courte. Entrez au moins 3 caractères ⤵️",
        "back_menu": "🏠 Vous êtes retourné au menu principal.",
        "page": "📖 _Page {cur} sur {total}_",
        "search_ok": "✅ Résultats trouvés!",
        "page_info": "📖 Vous êtes sur la page {cur} sur {total}"
    },
    "es": {
        "name": "Español",
        "start": "¡Hola!😉\nEste es un bot de búsqueda de conjuntos de datos.\nElija una sección ⤵️",
        "menu": {
            "search": "🔍 Buscar en la base",
            "contacts": "📞 Contactos",
            "help": "ℹ️ Ayuda",
            "language": "🌐 Idioma",
            "back": "🏠 Volver al menú",
            "main": "🏠 Menú principal"
        },
        "labels": {
            "article": "🆔 *Artículo:*",
            "version": "🔢 *Versión:*",
            "dataset": "📊 *Conjunto de datos:*",
            "model": "🚙 *Modelo:*",
            "year": "📅 *Año:*",
            "region": "🌍 *Región:*"
        },
        "nav": {
            "prev": "⬅️ Anterior",
            "next": "➡️ Siguiente",
            "main": "🏠 Menú principal",
            "contacts": "📞 Contactos"
        },
        "help": "ℹ️ Ayuda:\nEste bot de Telegram está diseñado para la búsqueda rápida de conjuntos de datos en nuestra base de datos.\nPara buscar, simplemente ingrese el número de artículo o el nombre del dataset",
        "contacts": "📞 Contactos:\nEmail: datenflash@proton.me\nTelegram: @mukich1 o @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Elija un idioma:",
        "changed": "✅ Idioma cambiado a {lang}",
        "not_found": "⚠️ No se encontró nada.",
        "enter_search": "Ingrese el número de artículo o el nombre del dataset ⤵️",
        "empty_query": "⚠️ No escribiste nada. Intenta de nuevo ⤵️",
        "short_query": "⚠️ Consulta demasiado corta. Escribe al menos 3 caracteres ⤵️",
        "back_menu": "🏠 Has vuelto al menú principal.",
        "page": "📖 _Página {cur} de {total}_",
        "search_ok": "✅ ¡Resultados encontrados!",
        "page_info": "📖 Estás en la página {cur} de {total}"
    },
    "it": {
        "name": "Italiano",
        "start": "Ciao!😉\nQuesto è un bot per la ricerca di dataset.\nSeleziona una sezione ⤵️",
        "menu": {
            "search": "🔍 Cerca nel database",
            "contacts": "📞 Contatti",
            "help": "ℹ️ Guida",
            "language": "🌐 Lingua",
            "back": "🏠 Torna al menu",
            "main": "🏠 Menu principale"
        },
        "labels": {
            "article": "🆔 *Articolo:*",
            "version": "🔢 *Versione:*",
            "dataset": "📊 *Dataset:*",
            "model": "🚙 *Modello:*",
            "year": "📅 *Anno:*",
            "region": "🌍 *Regione:*"
        },
        "nav": {
            "prev": "⬅️ Indietro",
            "next": "➡️ Avanti",
            "main": "🏠 Menu principale",
            "contacts": "📞 Contatti"
        },
        "help": "ℹ️ Guida:\nQuesto bot Telegram è stato creato per cercare rapidamente dataset nel nostro database.\nPer cercare, inserisci semplicemente il numero dell’articolo o il nome del dataset",
        "contacts": "📞 Contatti:\nEmail: datenflash@proton.me\nTelegram: @mukich1 o @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Seleziona la lingua:",
        "changed": "✅ Lingua cambiata in {lang}",
        "not_found": "⚠️ Nessun risultato trovato.",
        "enter_search": "Inserisci il numero dell’articolo o il nome del dataset ⤵️",
        "empty_query": "⚠️ Non hai digitato nulla. Riprova ⤵️",
        "short_query": "⚠️ Query troppo corta. Inserisci almeno 3 caratteri ⤵️",
        "back_menu": "🏠 Sei tornato al menu principale.",
        "page": "📖 _Pagina {cur} di {total}_",
        "search_ok": "✅ Risultati trovati!",
        "page_info": "📖 Sei a pagina {cur} di {total}"
    },
    "pt": {
        "name": "Português",
        "start": "Olá!😉\nEste é um bot de pesquisa de conjuntos de dados.\nEscolha uma seção ⤵️",
        "menu": {
            "search": "🔍 Pesquisar na base",
            "contacts": "📞 Contatos",
            "help": "ℹ️ Ajuda",
            "language": "🌐 Idioma",
            "back": "🏠 Voltar ao menu",
            "main": "🏠 Menu principal"
        },
        "labels": {
            "article": "🆔 *Artigo:*",
            "version": "🔢 *Versão:*",
            "dataset": "📊 *Conjunto de dados:*",
            "model": "🚙 *Modelo:*",
            "year": "📅 *Ano:*",
            "region": "🌍 *Região:*"
        },
        "nav": {
            "prev": "⬅️ Anterior",
            "next": "➡️ Próximo",
            "main": "🏠 Menu principal",
            "contacts": "📞 Contatos"
        },
        "help": "ℹ️ Ajuda:\nEste bot do Telegram foi criado para pesquisa rápida de conjuntos de dados no nosso banco de dados.\nPara pesquisar, basta inserir o número do artigo ou o nome do dataset",
        "contacts": "📞 Contatos:\nEmail: datenflash@proton.me\nTelegram: @mukich1 ou @mr_muhich\nInstagram: @codiVAG",
        "choose_lang": "🌐 Escolha o idioma:",
        "changed": "✅ Idioma alterado para {lang}",
        "not_found": "⚠️ Nada encontrado.",
        "enter_search": "Digite o número do artigo ou o nome do dataset ⤵️",
        "empty_query": "⚠️ Você não digitou nada. Tente novamente ⤵️",
        "short_query": "⚠️ Consulta muito curta. Digite pelo menos 3 caracteres ⤵️",
        "back_menu": "🏠 Você voltou ao menu principal.",
        "page": "📖 _Página {cur} de {total}_",
        "search_ok": "✅ Resultados encontrados!",
        "page_info": "📖 Você está na página {cur} de {total}"
    }
}


# ====== Побудова меню ======
def main_menu_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    t = LANGUAGES[lang]["menu"]
    keyboard = [
        [InlineKeyboardButton(t["search"], callback_data="search")],
        [InlineKeyboardButton(t["contacts"], callback_data="contacts")],
        [InlineKeyboardButton(t["help"], callback_data="help")],
        [InlineKeyboardButton(t["language"], callback_data="language")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    t = LANGUAGES[lang]["menu"]
    return InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="menu")]])


def language_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("Français", callback_data="lang_fr")],
        [InlineKeyboardButton("Español", callback_data="lang_es")],
        [InlineKeyboardButton("Italiano", callback_data="lang_it")],
        [InlineKeyboardButton("Português", callback_data="lang_pt")],
        [InlineKeyboardButton("Українська", callback_data="lang_uk")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ====== Допоміжні ======
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "uk")


def clean(value) -> str:
    if pd.isna(value) or str(value).strip() == "" or str(value).lower() == "nan":
        return "---"
    return str(value)


# Формування тексту одного запису
def render_result(row: pd.Series, lang: str = "uk") -> str:
    labels = LANGUAGES[lang]["labels"]
    return (
        f"{labels['article']} {clean(row.get('Article', ''))}\n"
        f"{labels['version']} {clean(row.get('Version', ''))}\n"
        f"{labels['dataset']} {clean(row.get('Dataset', ''))}\n"
        f"{labels['model']} {clean(row.get('Model', ''))}\n"
        f"{labels['year']} {clean(row.get('Year', ''))}\n"
        f"{labels['region']} {clean(row.get('Region', ''))}"
    )


def results_nav_keyboard(lang: str, page: int, total: int) -> InlineKeyboardMarkup:
    nav = LANGUAGES[lang]["nav"]
    keyboard = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(nav["prev"], callback_data=f"res_{page-1}"))
    if page < total - 1:
        row.append(InlineKeyboardButton(nav["next"], callback_data=f"res_{page+1}"))
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(nav["main"], callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)


# ====== Хендлери ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(LANGUAGES[lang]["start"], reply_markup=main_menu_keyboard(lang))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = get_lang(context)
    await query.answer()

    data = query.data or ""

    # Пагінація результатів: res_<page_index>
    if data.startswith("res_"):
        try:
            page = int(data.split("_")[1])
        except Exception:
            return

        results: pd.DataFrame = context.user_data.get("search_results")
        if results is None or results.empty:
            # Нема результатів — повертаємось у меню
            await query.message.edit_text(LANGUAGES[lang]["not_found"], reply_markup=main_menu_keyboard(lang))
            return

        total = len(results)
        if 0 <= page < total:
            context.user_data["page"] = page
            row = results.iloc[page]
            text = render_result(row, lang) + f"\n\n{LANGUAGES[lang]['page_info'].format(cur=page+1, total=total)}"
            await query.message.edit_text(text, reply_markup=results_nav_keyboard(lang, page, total))
        return

    # Меню вибору мови
    if data == "language":
        await query.message.reply_text(LANGUAGES[lang]["choose_lang"], reply_markup=language_menu_keyboard())
        return

    # Зміна мови: lang_<code>
    if data.startswith("lang_"):
        new_lang = data.split("_", 1)[1]
        if new_lang in LANGUAGES:
            context.user_data["lang"] = new_lang
            lang = new_lang
        await query.message.reply_text(
            LANGUAGES[lang]["changed"].format(lang=LANGUAGES[lang]["name"]),
            reply_markup=main_menu_keyboard(lang)
        )
        return

    # Пошук
    if data == "search":
        await query.message.reply_text(LANGUAGES[lang]["enter_search"])
        return

    # Контакти
    if data == "contacts":
        await query.message.reply_text(LANGUAGES[lang]["contacts"], reply_markup=back_to_menu_keyboard(lang))
        return

    # Довідка
    if data == "help":
        await query.message.reply_text(LANGUAGES[lang]["help"], reply_markup=back_to_menu_keyboard(lang))
        return

    # Повернення в меню
    if data == "menu":
        await query.message.reply_text(LANGUAGES[lang]["back_menu"], reply_markup=main_menu_keyboard(lang))
        await query.message.reply_text(LANGUAGES[lang]["start"], reply_markup=main_menu_keyboard(lang))
        return


async def search_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = (update.message.text or "").strip()

    if not text:
        await update.message.reply_text(LANGUAGES[lang]["empty_query"])
        return
    if len(text) < 3:
        await update.message.reply_text(LANGUAGES[lang]["short_query"])
        return

    # Маска пошуку по Article або Dataset
    try:
        mask = (
            df["Article"].str.contains(text, case=False, na=False) |
            df["Dataset"].str.contains(text, case=False, na=False)
        )
    except Exception:
        mask = pd.Series([False] * len(df), index=df.index)

    results = df[mask].reset_index(drop=True)

    if not results.empty:
        context.user_data["search_results"] = results
        context.user_data["page"] = 0
        row = results.iloc[0]
        text_msg = LANGUAGES[lang]["search_ok"] + "\n\n" + render_result(row, lang)
        await update.message.reply_text(
            text_msg,
            reply_markup=results_nav_keyboard(lang, 0, len(results))
        )
    else:
        await update.message.reply_text(LANGUAGES[lang]["not_found"], reply_markup=main_menu_keyboard(lang))


# ====== Запуск приложения ======
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Please set environment variable BOT_TOKEN.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_database))
    app.run_polling()


if __name__ == "__main__":
    main()
