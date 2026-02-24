"""
معالجات الأوامر الأساسية: /start، /help، /lang، /cancel
Basic command handlers: /start, /help, /lang, /cancel
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from locales import get_message
from utils import get_user_lang, set_user_lang, clear_user_session, init_user

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    user = update.effective_user
    init_user(user.id)
    lang = get_user_lang(user.id)

    welcome_text = get_message("welcome", lang)
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} ({user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    user = update.effective_user
    lang = get_user_lang(user.id)

    help_text = get_message("help", lang)
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown"
    )


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /lang — تغيير اللغة"""
    user = update.effective_user
    lang = get_user_lang(user.id)

    keyboard = [
        [
            InlineKeyboardButton(
                get_message("btn_ar", lang),
                callback_data="lang:ar"
            ),
            InlineKeyboardButton(
                get_message("btn_en", lang),
                callback_data="lang:en"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        get_message("choose_language", lang),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /cancel — إلغاء العملية الحالية"""
    user = update.effective_user
    lang = get_user_lang(user.id)
    clear_user_session(user.id)

    await update.message.reply_text(
        get_message("cancelled", lang),
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} cancelled their session")


async def handle_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج callback لتغيير اللغة"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    _, lang_code = query.data.split(":")

    set_user_lang(user.id, lang_code)
    confirmation = get_message("language_changed", lang_code)

    await query.edit_message_text(
        confirmation,
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} changed language to: {lang_code}")
