"""
معالج الرسائل النصية — استقبال الروابط وعرض خيارات التحميل
Text message handler — receives URLs and shows download options
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from locales import get_message
from utils import (
    get_user_lang, extract_url_from_text, is_valid_url,
    is_supported_platform, detect_platform, clean_url,
    set_user_url, set_user_video_info, set_user_state,
    get_user_state, rate_limiter, init_user,
    format_duration, format_views, format_date,
)
from utils.downloader import fetch_video_info

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المعالج الرئيسي للرسائل النصية"""
    user = update.effective_user
    text = update.message.text.strip()
    init_user(user.id)
    lang = get_user_lang(user.id)

    # ===== التحقق من معدل الطلبات =====
    allowed, wait_seconds = rate_limiter.is_allowed(user.id)
    if not allowed:
        await update.message.reply_text(
            get_message("rate_limit_exceeded", lang, seconds=wait_seconds),
            parse_mode="Markdown"
        )
        return

    # ===== استخراج الرابط من النص =====
    url = extract_url_from_text(text)
    if not url:
        # ليس رابطاً — تجاهل أو إرسال رسالة مساعدة
        await update.message.reply_text(
            get_message("error_invalid_url", lang),
            parse_mode="Markdown"
        )
        return

    # ===== التحقق من صحة الرابط =====
    if not is_valid_url(url):
        await update.message.reply_text(
            get_message("error_invalid_url", lang),
            parse_mode="Markdown"
        )
        return

    # ===== التحقق من المنصة المدعومة =====
    if not is_supported_platform(url):
        await update.message.reply_text(
            get_message("error_unsupported_platform", lang),
            parse_mode="Markdown"
        )
        return

    # ===== تنظيف الرابط =====
    url = clean_url(url)

    # ===== إرسال مؤشر الكتابة =====
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # ===== إرسال رسالة "جارٍ جلب المعلومات" =====
    status_msg = await update.message.reply_text(
        get_message("fetching_info", lang),
        parse_mode="Markdown"
    )

    # ===== جلب معلومات الفيديو =====
    try:
        video_info = await fetch_video_info(url)
        if not video_info:
            await status_msg.edit_text(
                get_message("error_video_unavailable", lang),
                parse_mode="Markdown"
            )
            return

    except Exception as e:
        error_str = str(e).lower()
        if any(kw in error_str for kw in ["private", "unavailable", "not available", "removed"]):
            msg = get_message("error_video_unavailable", lang)
        elif "timeout" in error_str:
            msg = get_message("error_timeout", lang)
        else:
            msg = get_message("error_download_failed", lang)
        await status_msg.edit_text(msg, parse_mode="Markdown")
        logger.error(f"Error fetching info for {url}: {e}")
        return

    # ===== تخزين بيانات الجلسة =====
    set_user_url(user.id, url)
    set_user_video_info(user.id, {
        "title": video_info.title,
        "duration": video_info.duration,
        "duration_str": video_info.duration_str,
        "views": video_info.views,
        "upload_date": video_info.upload_date,
        "platform": video_info.platform,
        "url": url,
        "video_qualities": video_info.get_available_video_qualities(),
        "audio_qualities": video_info.get_available_audio_qualities(),
    })
    set_user_state(user.id, "choosing_type")

    # ===== عرض معلومات الفيديو =====
    info_text = get_message(
        "video_info", lang,
        title=video_info.title,
        duration=video_info.duration_str,
        views=video_info.views,
        upload_date=video_info.upload_date,
        platform=detect_platform(url),
    )

    # ===== أزرار اختيار نوع التحميل =====
    keyboard = [
        [
            InlineKeyboardButton(
                get_message("btn_video", lang),
                callback_data="type:video"
            ),
            InlineKeyboardButton(
                get_message("btn_audio", lang),
                callback_data="type:audio"
            ),
        ],
        [
            InlineKeyboardButton(
                get_message("btn_cancel", lang),
                callback_data="action:cancel"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await status_msg.edit_text(
        f"{info_text}\n\n{get_message('choose_type', lang)}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} sent URL: {url} — showing type selection")
