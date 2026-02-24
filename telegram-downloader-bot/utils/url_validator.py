"""
وحدة التحقق من صحة الروابط وتحديد المنصة
URL validation and platform detection module
"""

import re
from urllib.parse import urlparse
from config.settings import SUPPORTED_PLATFORMS


def is_valid_url(url: str) -> bool:
    """التحقق من صحة الرابط"""
    url = url.strip()
    url_pattern = re.compile(
        r'^(https?://)'                          # البروتوكول
        r'(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})'   # النطاق
        r'(:\d+)?'                               # المنفذ (اختياري)
        r'(/[^\s]*)?$',                          # المسار
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def is_supported_platform(url: str) -> bool:
    """التحقق من أن الرابط من منصة مدعومة"""
    try:
        parsed = urlparse(url.strip())
        domain = parsed.netloc.lower()
        # إزالة www. من بداية النطاق
        if domain.startswith("www."):
            domain = domain[4:]
        return any(platform in domain for platform in SUPPORTED_PLATFORMS)
    except Exception:
        return False


def detect_platform(url: str) -> str:
    """تحديد اسم المنصة من الرابط"""
    url_lower = url.lower()
    platform_map = {
        "youtube.com": "YouTube",
        "youtu.be": "YouTube",
        "tiktok.com": "TikTok",
        "facebook.com": "Facebook",
        "fb.watch": "Facebook",
        "instagram.com/stories": "Instagram Story",
        "instagram.com/reels": "Instagram Reel",
        "instagram.com/p/": "Instagram Post",
        "instagram.com": "Instagram",
        "twitter.com": "Twitter/X",
        "x.com": "Twitter/X",
        "dailymotion.com": "Dailymotion",
        "vimeo.com": "Vimeo",
        "twitch.tv": "Twitch",
        "reddit.com": "Reddit",
        "soundcloud.com": "SoundCloud",
    }
    for domain, name in platform_map.items():
        if domain in url_lower:
            return name
    return "Unknown"


def extract_url_from_text(text: str) -> str | None:
    """استخراج أول رابط من النص"""
    url_pattern = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        re.IGNORECASE
    )
    match = url_pattern.search(text)
    return match.group(0) if match else None


def clean_url(url: str) -> str:
    """تنظيف الرابط من المعاملات الزائدة"""
    url = url.strip()
    # إزالة معاملات التتبع الشائعة من يوتيوب
    if "youtube.com/watch" in url or "youtu.be/" in url:
        # الاحتفاظ بمعامل v= فقط
        parsed = urlparse(url)
        if "youtu.be" in parsed.netloc:
            return url.split("?")[0]  # روابط youtu.be لا تحتاج معاملات
    return url
