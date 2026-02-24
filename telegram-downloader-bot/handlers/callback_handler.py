"""
معالج الأزرار التفاعلية (Inline Keyboard Callbacks)
Handles quality selection, download type, and download execution
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from locales import get_message
from utils import (
    get_user_lang, get_user_url, get_user_video_info,
    set_user_state, clear_user_session, rate_limiter,
    format_file_size,
)
from utils.downloader import download_video, download_audio, cleanup_file
from config.settings import MAX_FILE_SIZE_MB, MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المعالج الرئيسي لجميع الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    lang = get_user_lang(user.id)
    data = query.data

    # ===== إلغاء العملية =====
    if data == "action:cancel":
        clear_user_session(user.id)
        await query.edit_message_text(
            get_message("cancelled", lang),
            parse_mode="Markdown"
        )
        return

    # ===== اختيار نوع التحميل (فيديو/صوت) =====
    if data.startswith("type:"):
        download_type = data.split(":")[1]
        await _show_quality_options(query, user.id, lang, download_type)
        return

    # ===== اختيار جودة الفيديو =====
    if data.startswith("quality:"):
        parts = data.split(":", 2)
        quality_index = int(parts[1])
        await _start_video_download(query, context, user.id, lang, quality_index)
        return

    # ===== اختيار جودة الصوت =====
    if data.startswith("audio:"):
        parts = data.split(":", 2)
        quality_index = int(parts[1])
        await _start_audio_download(query, context, user.id, lang, quality_index)
        return

    # ===== الرجوع =====
    if data == "action:back":
        video_info = get_user_video_info(user.id)
        if not video_info:
            await query.edit_message_text(
                get_message("error_general", lang),
                parse_mode="Markdown"
            )
            return

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
        await query.edit_message_text(
            get_message("choose_type", lang),
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def _show_quality_options(query, user_id: int, lang: str, download_type: str):
    """عرض خيارات الجودة المتاحة"""
    video_info = get_user_video_info(user_id)
    if not video_info:
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
        return

    keyboard = []

    if download_type == "video":
        qualities = video_info.get("video_qualities", [])
        if not qualities:
            await query.edit_message_text(
                get_message("error_video_unavailable", lang),
                parse_mode="Markdown"
            )
            return

        for i, q in enumerate(qualities):
            label = q["quality_label"]
            size_str = q["filesize_str"]
            # تمييز الملفات الكبيرة جداً
            if q["filesize"] > MAX_FILE_SIZE_BYTES:
                btn_text = f"⚠️ {label} ({size_str} — كبير جداً)"
            else:
                btn_text = f"🎬 {label} — {size_str}"

            keyboard.append([
                InlineKeyboardButton(btn_text, callback_data=f"quality:{i}")
            ])

        header = get_message("choose_quality", lang)

    else:  # audio
        qualities = video_info.get("audio_qualities", [])
        for i, q in enumerate(qualities):
            label = q["quality_label"]
            size_str = q["filesize_str"]
            btn_text = f"🎵 {label} — {size_str}"
            keyboard.append([
                InlineKeyboardButton(btn_text, callback_data=f"audio:{i}")
            ])

        header = get_message("choose_audio_quality", lang)

    # زر الرجوع
    keyboard.append([
        InlineKeyboardButton(
            get_message("btn_back", lang),
            callback_data="action:back"
        ),
        InlineKeyboardButton(
            get_message("btn_cancel", lang),
            callback_data="action:cancel"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        header,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    set_user_state(user_id, f"choosing_{download_type}_quality")


async def _start_video_download(
    query, context: ContextTypes.DEFAULT_TYPE,
    user_id: int, lang: str, quality_index: int
):
    """بدء تحميل الفيديو بالجودة المحددة"""
    video_info = get_user_video_info(user_id)
    url = get_user_url(user_id)

    if not video_info or not url:
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
        return

    qualities = video_info.get("video_qualities", [])
    if quality_index >= len(qualities):
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
        return

    selected = qualities[quality_index]
    height = selected["height"]
    format_id = selected.get("format_id")
    filesize = selected.get("filesize", 0)

    # التحقق من الحجم
    if filesize and filesize > MAX_FILE_SIZE_BYTES:
        await query.edit_message_text(
            get_message("error_file_too_large", lang, max_size=MAX_FILE_SIZE_MB),
            parse_mode="Markdown"
        )
        return

    # تحديث الرسالة لإظهار حالة التحميل
    await query.edit_message_text(
        get_message("downloading", lang),
        parse_mode="Markdown"
    )
    set_user_state(user_id, "downloading")

    # مؤشر التحميل
    await context.bot.send_chat_action(
        chat_id=query.message.chat_id,
        action=ChatAction.UPLOAD_VIDEO
    )

    file_paths = None
    try:
        # تحميل الفيديو (قد يكون قائمة ملفات في حال إنستغرام Carousel)
        file_paths = await download_video(url, height=height, format_id=format_id)

        if not file_paths:
            await query.edit_message_text(
                get_message("error_download_failed", lang),
                parse_mode="Markdown"
            )
            return

        # التحقق من الأحجام
        total_size = sum(os.path.getsize(fp) for fp in file_paths if os.path.exists(fp))
        if total_size > MAX_FILE_SIZE_BYTES and len(file_paths) == 1:
            await query.edit_message_text(
                get_message("error_file_too_large", lang, max_size=MAX_FILE_SIZE_MB),
                parse_mode="Markdown"
            )
            cleanup_file(file_paths)
            return

        # تحديث الرسالة لإظهار حالة الرفع
        await query.edit_message_text(
            get_message("uploading", lang),
            parse_mode="Markdown"
        )

        # إرسال الفيديو (أو الفيديوهات)
        caption = (
            f"🎬 *{video_info['title']}*\n"
            f"📊 الجودة: `{selected['quality_label']}`\n"
            f"📦 الحجم: `{format_file_size(total_size)}`\n"
            f"⏱️ المدة: `{video_info['duration_str']}`"
        )

        if len(file_paths) == 1:
            with open(file_paths[0], "rb") as video_file:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=video_file,
                    caption=caption,
                    parse_mode="Markdown",
                    supports_streaming=True,
                    read_timeout=120,
                    write_timeout=120,
                )
        else:
            # إرسال كألبوم (Media Group) للمنشورات المتعددة
            from telegram import InputMediaVideo
            media_group = []
            for i, fp in enumerate(file_paths):
                # ملاحظة: إنستغرام قد يحتوي على صور وفيديوهات مختلطة، yt-dlp يحملها كفيديو عادة
                media_group.append(InputMediaVideo(
                    open(fp, "rb"), 
                    caption=caption if i == 0 else "" ,
                    parse_mode="Markdown"
                ))
            await context.bot.send_media_group(
                chat_id=query.message.chat_id,
                media=media_group,
                read_timeout=180,
                write_timeout=180,
            )

        # رسالة الاكتمال
        await query.edit_message_text(
            get_message("done", lang),
            parse_mode="Markdown"
        )

        logger.info(
            f"User {user_id} downloaded video: {video_info['title']} "
            f"[{selected['quality_label']}] — {format_file_size(actual_size)}"
        )

    except TelegramError as e:
        logger.error(f"Telegram error sending video to user {user_id}: {e}")
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in video download for user {user_id}: {e}")
        error_str = str(e).lower()
        if "too large" in error_str or "file too big" in error_str:
            msg = get_message("error_file_too_large", lang, max_size=MAX_FILE_SIZE_MB)
        elif "timeout" in error_str:
            msg = get_message("error_timeout", lang)
        else:
            msg = get_message("error_download_failed", lang)
        try:
            await query.edit_message_text(msg, parse_mode="Markdown")
        except Exception:
            pass
    finally:
        if file_paths:
            cleanup_file(file_paths)
        clear_user_session(user_id)


async def _start_audio_download(
    query, context: ContextTypes.DEFAULT_TYPE,
    user_id: int, lang: str, quality_index: int
):
    """بدء تحميل الصوت بالجودة المحددة"""
    video_info = get_user_video_info(user_id)
    url = get_user_url(user_id)

    if not video_info or not url:
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
        return

    qualities = video_info.get("audio_qualities", [])
    if quality_index >= len(qualities):
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
        return

    selected = qualities[quality_index]
    quality_kbps = selected.get("abr", 192)

    # تحديث الرسالة
    await query.edit_message_text(
        get_message("downloading", lang),
        parse_mode="Markdown"
    )
    set_user_state(user_id, "downloading")

    await context.bot.send_chat_action(
        chat_id=query.message.chat_id,
        action=ChatAction.UPLOAD_DOCUMENT
    )

    file_paths = None
    try:
        # تحميل الصوت (دائماً ملف واحد عادة، لكن نستخدم القائمة للاتساق)
        path = await download_audio(url, quality_kbps=quality_kbps)
        file_paths = [path] if path else None

        if not file_paths or not os.path.exists(file_paths[0]):
            await query.edit_message_text(
                get_message("error_download_failed", lang),
                parse_mode="Markdown"
            )
            return

        actual_size = os.path.getsize(file_paths[0])
        if actual_size > MAX_FILE_SIZE_BYTES:
            await query.edit_message_text(
                get_message("error_file_too_large", lang, max_size=MAX_FILE_SIZE_MB),
                parse_mode="Markdown"
            )
            cleanup_file(file_paths)
            return

        await query.edit_message_text(
            get_message("uploading", lang),
            parse_mode="Markdown"
        )

        caption = (
            f"🎵 *{video_info['title']}*\n"
            f"🎶 الجودة: `{selected['quality_label']}`\n"
            f"📦 الحجم: `{format_file_size(actual_size)}`\n"
            f"⏱️ المدة: `{video_info['duration_str']}`"
        )

        with open(file_paths[0], "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_file,
                caption=caption,
                parse_mode="Markdown",
                title=video_info["title"],
                read_timeout=120,
                write_timeout=120,
            )

        await query.edit_message_text(
            get_message("done", lang),
            parse_mode="Markdown"
        )

        logger.info(
            f"User {user_id} downloaded audio: {video_info['title']} "
            f"[{selected['quality_label']}] — {format_file_size(actual_size)}"
        )

    except TelegramError as e:
        logger.error(f"Telegram error sending audio to user {user_id}: {e}")
        await query.edit_message_text(
            get_message("error_general", lang),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in audio download for user {user_id}: {e}")
        error_str = str(e).lower()
        if "too large" in error_str:
            msg = get_message("error_file_too_large", lang, max_size=MAX_FILE_SIZE_MB)
        elif "timeout" in error_str:
            msg = get_message("error_timeout", lang)
        else:
            msg = get_message("error_download_failed", lang)
        try:
            await query.edit_message_text(msg, parse_mode="Markdown")
        except Exception:
            pass
    finally:
        if file_paths:
            cleanup_file(file_paths)
        clear_user_session(user_id)
