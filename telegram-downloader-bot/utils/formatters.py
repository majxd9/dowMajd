"""
وحدة تنسيق البيانات (الأحجام، المدد الزمنية، الأرقام)
Data formatting utilities
"""


def format_file_size(size_bytes: int | float | None) -> str:
    """تنسيق حجم الملف بشكل مقروء"""
    if not size_bytes or size_bytes <= 0:
        return "غير معروف / Unknown"
    size_bytes = float(size_bytes)
    if size_bytes < 1024:
        return f"{size_bytes:.0f} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_duration(seconds: int | float | None) -> str:
    """تنسيق المدة الزمنية"""
    if not seconds:
        return "غير معروف / Unknown"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_views(views: int | None) -> str:
    """تنسيق عدد المشاهدات"""
    if not views:
        return "غير معروف / Unknown"
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B"
    elif views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def format_date(date_str: str | None) -> str:
    """تنسيق تاريخ الرفع من صيغة YYYYMMDD"""
    if not date_str or len(date_str) != 8:
        return "غير معروف / Unknown"
    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{day}/{month}/{year}"
    except Exception:
        return date_str


def truncate_title(title: str, max_length: int = 60) -> str:
    """اختصار عنوان الفيديو إذا كان طويلاً جداً"""
    if not title:
        return "بدون عنوان / No title"
    if len(title) > max_length:
        return title[:max_length - 3] + "..."
    return title


def estimate_size_from_bitrate(duration_seconds: float, bitrate_kbps: float) -> int:
    """تقدير حجم الملف من معدل البت والمدة"""
    if not duration_seconds or not bitrate_kbps:
        return 0
    # الحجم بالبايت = (معدل البت بالكيلوبت/ثانية × المدة بالثواني × 1000) / 8
    return int((bitrate_kbps * 1000 * duration_seconds) / 8)
