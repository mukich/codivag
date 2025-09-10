import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from collections import Counter
import io

TOKEN = os.getenv("BOT_TOKEN")

STATS = {
    "total": 0,
    "success": 0,
    "fail": 0,
    "queries": Counter(),
    "by_lang": Counter(),
    "success_queries": [],
    "fail_queries": []
}

def load_dataframe(path: str = "all-in-one.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except Exception:
        df = pd.DataFrame(columns=["Article", "Version", "Dataset", "Model", "Year", "Region"])
    for col in ["Article", "Version", "Dataset", "Model", "Year", "Region"]:
        if col not in df.columns:
            df[col] = ""
    try:
        df["Year"] = df["Year"].apply(lambda x: int(x) if pd.notna(x) and str(x).strip() != "" else "")
    except Exception:
        pass
    for col in ["Article", "Version", "Dataset", "Model", "Region"]:
        try:
            df[col] = df[col].astype(str)
        except Exception:
            pass
    return df

df = load_dataframe("all-in-one.xlsx")

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
            "main": "🏠 Головне меню"
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
        "search_ok": "✅ Знайдено результати!",
        "page_info": "📖 Сторінка {cur} з {total}"
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
            "main": "🏠 Main menu"
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
        "search_ok": "✅ Results found!",
        "page_info": "📖 Page {cur} of {total}"
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
            "main": "🏠 Hauptmenü"
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
        "search_ok": "✅ Ergebnisse gefunden!",
        "page_info": "📖 Seite {cur} von {total}"
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
            "main": "🏠 Menu principal"
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
        "search_ok": "✅ Résultats trouvés!",
        "page_info": "📖 Page {cur} sur {total}"
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
            "main": "🏠 Menú principal"
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
        "search_ok": "✅ ¡Resultados encontrados!",
        "page_info": "📖 Página {cur} de {total}"
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
            "main": "🏠 Menu principale"
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
        "search_ok": "✅ Risultati trovati!",
        "page_info": "📖 Pagina {cur} di {total}"
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
            "main": "🏠 Menu principal"
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
        "search_ok": "✅ Resultados encontrados!",
        "page_info": "📖 Página {cur} de {total}"
    }
}  # ⚠️ вставити повний словник з 7 мовами

def main_menu_keyboard(lang="uk"):
    t = LANGUAGES[lang]["menu"]
    keyboard = [
        [InlineKeyboardButton(t["search"], callback_data="search")],
        [InlineKeyboardButton(t["contacts"], callback_data="contacts")],
        [InlineKeyboardButton(t["help"], callback_data="help")],
        [InlineKeyboardButton(t["language"], callback_data="language")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard(lang="uk"):
    t = LANGUAGES[lang]["menu"]
    return InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="menu")]])

def language_menu_keyboard():
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

def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "uk")

def clean(value):
    if pd.isna(value) or str(value).strip() == "" or str(value).lower() == "nan":
        return "---"
    return str(value)

def render_result(row, lang="uk"):
    labels = LANGUAGES[lang]["labels"]
    return (
        f"{labels['article']} {clean(row['Article'])}\n"
        f"{labels['version']} {clean(row['Version'])}\n"
        f"{labels['dataset']} {clean(row['Dataset'])}\n"
        f"{labels['model']} {clean(row['Model'])}\n"
        f"{labels['year']} {clean(row['Year'])}\n"
        f"{labels['region']} {clean(row['Region'])}"
    )

def render_page(results: pd.DataFrame, page: int, lang="uk", per_page: int = 5) -> str:
    start = page * per_page
    end = min(start + per_page, len(results))
    subset = results.iloc[start:end]
    parts = []
    for i, (_, row) in enumerate(subset.iterrows(), start=start+1):
        parts.append(f"🔹 *{i}*\n{render_result(row, lang)}")
    text = "\n\n".join(parts)
    total_pages = (len(results) + per_page - 1) // per_page
    text += f"\n\n{LANGUAGES[lang]['page_info'].format(cur=page+1, total=total_pages)}"
    return text

def results_nav_keyboard(lang, page, total_items, per_page: int = 5):
    total_pages = (total_items + per_page - 1) // per_page
    nav = LANGUAGES[lang]["nav"]
    keyboard = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(nav["prev"], callback_data=f"res_{page-1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton(nav["next"], callback_data=f"res_{page+1}"))
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(nav["main"], callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(LANGUAGES[lang]["start"], reply_markup=main_menu_keyboard(lang))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = get_lang(context)
    await query.answer()
    data = query.data

    if data.startswith("res_"):
        page = int(data.split("_")[1])
        results = context.user_data.get("search_results")
        if results is not None and not results.empty:
            context.user_data["page"] = page
            page_text = render_page(results, page, lang)
            await query.message.edit_text(
                page_text,
                reply_markup=results_nav_keyboard(lang, page, len(results))
            )
        return

    if data == "language":
        await query.message.reply_text(LANGUAGES[lang]["choose_lang"], reply_markup=language_menu_keyboard())
    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await query.message.reply_text(
            LANGUAGES[lang]["changed"].format(lang=LANGUAGES[lang]["name"]),
            reply_markup=main_menu_keyboard(lang)
        )
    elif data == "search":
        await query.message.reply_text(LANGUAGES[lang]["enter_search"])
    elif data == "contacts":
        await query.message.reply_text(LANGUAGES[lang]["contacts"], reply_markup=back_to_menu_keyboard(lang))
    elif data == "help":
        await query.message.reply_text(LANGUAGES[lang]["help"], reply_markup=back_to_menu_keyboard(lang))
    elif data == "menu":
        await query.message.reply_text(LANGUAGES[lang]["back_menu"], reply_markup=main_menu_keyboard(lang))
        await query.message.reply_text(LANGUAGES[lang]["start"], reply_markup=main_menu_keyboard(lang))

async def search_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text(LANGUAGES[lang]["empty_query"])
        return
    if len(text) < 3:
        await update.message.reply_text(LANGUAGES[lang]["short_query"])
        return
    
    # Оновлення статистики
    STATS["total"] += 1
    STATS["by_lang"][lang] += 1
    STATS["queries"][text.lower()] += 1

    mask = (
        df["Article"].str.contains(text, case=False, na=False) |
        df["Dataset"].str.contains(text, case=False, na=False)
    )
    results = df[mask].reset_index(drop=True)
    
    if not results.empty:
        # Успішний пошук
        STATS["success"] += 1
        STATS["success_queries"].append({
            "query": text,
            "lang": lang,
            "timestamp": pd.Timestamp.now(),
            "results_count": len(results)
        })
        
        context.user_data["search_results"] = results
        context.user_data["page"] = 0
        page_text = render_page(results, 0, lang)
        await update.message.reply_text(
            LANGUAGES[lang]["search_ok"] + "\n\n" + page_text,
            reply_markup=results_nav_keyboard(lang, 0, len(results))
        )
    else:
        # Неуспішний пошук
        STATS["fail"] += 1
        STATS["fail_queries"].append({
            "query": text,
            "lang": lang,
            "timestamp": pd.Timestamp.now()
        })
        await update.message.reply_text(LANGUAGES[lang]["not_found"], reply_markup=main_menu_keyboard(lang))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /stats"""
    lang = get_lang(context)
    
    if not STATS["total"]:
        await update.message.reply_text("📊 Статистика ще порожня", reply_markup=back_to_menu_keyboard(lang))
        return
    
    # Створення клавіатури для експорту
    keyboard = [
        [InlineKeyboardButton("📈 Експорт успішних запитів (Excel)", callback_data="export_success_excel")],
        [InlineKeyboardButton("📈 Експорт неуспішних запитів (Excel)", callback_data="export_fail_excel")],
        [InlineKeyboardButton(LANGUAGES[lang]["menu"]["main"], callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формування статистики
    msg = (
        f"📊 *Статистика пошуку:*\n\n"
        f"🔎 Всього пошуків: {STATS['total']}\n"
        f"✅ Успішних: {STATS['success']}\n"
        f"⚠️ Неуспішних: {STATS['fail']}\n\n"
        f"🌐 За мовами:\n"
    )
    
    for lang_code, count in STATS["by_lang"].items():
        lang_name = LANGUAGES.get(lang_code, {}).get("name", lang_code)
        msg += f"   • {lang_name}: {count}\n"
    
    msg += f"\n🔥 Топ-10 запитів:\n"
    for query, count in STATS["queries"].most_common(10):
        msg += f"   • `{query}` — {count}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE, data_type: str):
    """Експорт даних у Excel"""
    query = update.callback_query
    await query.answer()
    
    lang = get_lang(context)
    
    if data_type == "success":
        data = STATS["success_queries"]
        filename = "successful_queries"
        title = "Успішні запити"
    else:
        data = STATS["fail_queries"]
        filename = "failed_queries"
        title = "Неуспішні запити"
    
    if not data:
        await query.message.reply_text(f"⚠️ Немає даних для {title.lower()}", reply_markup=back_to_menu_keyboard(lang))
        return
    
    # Створення DataFrame
    df_export = pd.DataFrame(data)
    
    # Експорт у Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name=title)
    excel_buffer.seek(0)
    
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=excel_buffer,
        filename=f"{filename}.xlsx",
        caption=f"📈 {title} (Excel)",
        reply_markup=back_to_menu_keyboard(lang)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = get_lang(context)
    await query.answer()
    data = query.data

    if data.startswith("res_"):
        page = int(data.split("_")[1])
        results = context.user_data.get("search_results")
        if results is not None and not results.empty:
            context.user_data["page"] = page
            page_text = render_page(results, page, lang)
            await query.message.edit_text(
                page_text,
                reply_markup=results_nav_keyboard(lang, page, len(results))
            )
        return

    # Обробка експорту даних
    elif data == "export_success_excel":
        await export_data(update, context, "success")
    elif data == "export_fail_excel":
        await export_data(update, context, "fail")

    elif data == "language":
        await query.message.reply_text(LANGUAGES[lang]["choose_lang"], reply_markup=language_menu_keyboard())
    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await query.message.reply_text(
            LANGUAGES[lang]["changed"].format(lang=LANGUAGES[lang]["name"]),
            reply_markup=main_menu_keyboard(lang)
        )
    elif data == "search":
        await query.message.reply_text(LANGUAGES[lang]["enter_search"])
    elif data == "contacts":
        await query.message.reply_text(LANGUAGES[lang]["contacts"], reply_markup=back_to_menu_keyboard(lang))
    elif data == "help":
        await query.message.reply_text(LANGUAGES[lang]["help"], reply_markup=back_to_menu_keyboard(lang))
    elif data == "menu":
        await query.message.reply_text(LANGUAGES[lang]["back_menu"], reply_markup=main_menu_keyboard(lang))

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))  # Додано команду /stats
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_database))
    app.run_polling()

if __name__ == "__main__":
    main()


