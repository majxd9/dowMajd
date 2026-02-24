"""
ملف الإعدادات الرئيسي للبوت
Main configuration file for the bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===== إعدادات البوت الأساسية =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # سيتم قراءته من متغيرات البيئة في المنصة السحابية

# ===== إعدادات التحميل =====
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "./downloads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))  # الحد الأقصى لحجم الملف بالميجابايت
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ===== إعدادات مكافحة السبام =====
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "3"))   # عدد الطلبات المسموح بها
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))       # النافذة الزمنية بالثواني
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "30"))         # وقت الانتظار بعد تجاوز الحد

# ===== إعدادات اللغة =====
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")
SUPPORTED_LANGUAGES = ["ar", "en"]

# ===== المنصات المدعومة =====
SUPPORTED_PLATFORMS = [
    "youtube.com", "youtu.be",
    "tiktok.com",
    "facebook.com", "fb.watch",
    "instagram.com",
    "twitter.com", "x.com",
    "dailymotion.com",
    "vimeo.com",
    "twitch.tv",
    "reddit.com",
    "soundcloud.com",
]

# ===== جودات الفيديو المتاحة =====
VIDEO_QUALITIES = {
    "144p":  {"height": 144,  "label": "144p  📱 (أقل جودة)"},
    "360p":  {"height": 360,  "label": "360p  📺 (جودة منخفضة)"},
    "480p":  {"height": 480,  "label": "480p  🖥️ (جودة متوسطة)"},
    "720p":  {"height": 720,  "label": "720p  🎬 (جودة عالية HD)"},
    "1080p": {"height": 1080, "label": "1080p 🎥 (جودة Full HD)"},
    "best":  {"height": 9999, "label": "أفضل جودة متاحة ⭐"},
}

# ===== إعدادات yt-dlp =====
YTDLP_BASE_OPTIONS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": False,
    "socket_timeout": 30,
    "retries": 3,
    "nocheckcertificate": True,
    "cookiefile": os.getenv("COOKIE_FILE"),  # خيار لإضافة ملف كوكيز لإنستغرام وغيره
}
