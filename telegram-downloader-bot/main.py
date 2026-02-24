"""
╔══════════════════════════════════════════════════════════════╗
║          بوت تلغرام لتحميل الفيديوهات                        ║
║          Telegram Video Downloader Bot                        ║
║                                                              ║
║  المنصات المدعومة: YouTube, TikTok, Facebook, Instagram,     ║
║                   Twitter/X, Dailymotion, Vimeo, وأكثر       ║
║  المكتبات: python-telegram-bot v20+, yt-dlp                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import BOT_TOKEN, DOWNLOAD_PATH
from handlers import (
    start_command, help_command, lang_command, cancel_command,
    handle_lang_callback, handle_message, handle_callback,
)

# ===== إعداد نظام السجلات =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)

# تقليل ضوضاء مكتبات خارجية
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("yt_dlp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام — يمنع توقف البوت"""
    logger.error(
        "Exception while handling an update:",
        exc_info=context.error
    )

    # محاولة إبلاغ المستخدم بالخطأ
    if isinstance(update, Update) and update.effective_message:
        try:
            from locales import get_message
            from utils import get_user_lang
            user_id = update.effective_user.id if update.effective_user else 0
            lang = get_user_lang(user_id)
            await update.effective_message.reply_text(
                get_message("error_general", lang),
                parse_mode="Markdown"
            )
        except Exception:
            pass


async def setup_bot_commands(application: Application):
    """إعداد قائمة الأوامر في تلغرام"""
    commands_ar = [
        BotCommand("start", "🚀 بدء البوت"),
        BotCommand("help", "📖 دليل الاستخدام"),
        BotCommand("lang", "🌐 تغيير اللغة"),
        BotCommand("cancel", "❌ إلغاء العملية الحالية"),
    ]
    commands_en = [
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("help", "📖 User guide"),
        BotCommand("lang", "🌐 Change language"),
        BotCommand("cancel", "❌ Cancel current operation"),
    ]
    await application.bot.set_my_commands(commands_ar)
    logger.info("Bot commands set successfully")


def create_application() -> Application:
    """إنشاء وإعداد تطبيق البوت"""

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.critical(
            "❌ لم يتم تعيين BOT_TOKEN!\n"
            "يرجى تعيين متغير البيئة BOT_TOKEN أو تعديل ملف .env"
        )
        sys.exit(1)

    # إنشاء مجلد التحميل
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    # بناء التطبيق
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(120)
        .connect_timeout(30)
        .pool_timeout(60)
        .build()
    )

    # ===== تسجيل معالجات الأوامر =====
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CommandHandler("cancel", cancel_command))

    # ===== معالج الأزرار التفاعلية =====
    # معالج تغيير اللغة (له أولوية أعلى)
    application.add_handler(
        CallbackQueryHandler(handle_lang_callback, pattern=r"^lang:")
    )
    # المعالج العام للأزرار
    application.add_handler(
        CallbackQueryHandler(handle_callback)
    )

    # ===== معالج الرسائل النصية (الروابط) =====
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # ===== معالج الأخطاء العام =====
    application.add_error_handler(error_handler)

    return application


async def post_init(application: Application):
    """تنفيذ بعد تهيئة التطبيق"""
    await setup_bot_commands(application)
    bot_info = await application.bot.get_me()
    logger.info(
        f"✅ البوت يعمل بنجاح!\n"
        f"   الاسم: {bot_info.full_name}\n"
        f"   المعرف: @{bot_info.username}\n"
        f"   ID: {bot_info.id}"
    )


def main():
    """نقطة الدخول الرئيسية"""
    logger.info("=" * 60)
    logger.info("🚀 بدء تشغيل بوت تحميل الفيديوهات...")
    logger.info("=" * 60)

    application = create_application()
    application.post_init = post_init

    # تشغيل البوت بوضع Polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,   # تجاهل الرسائل القديمة عند الإعادة
        poll_interval=1.0,
    )


if __name__ == "__main__":
    main()
