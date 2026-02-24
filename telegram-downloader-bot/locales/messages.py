"""
ملف الرسائل متعدد اللغات (العربية والإنجليزية)
Multilingual messages file (Arabic & English)
"""

MESSAGES = {
    "ar": {
        # ===== رسائل الترحيب =====
        "welcome": (
            "👋 *أهلاً بك في بوت تحميل الفيديوهات!*\n\n"
            "🎯 *ما يمكنني فعله:*\n"
            "• تحميل الفيديوهات من يوتيوب، تيك توك، فيسبوك، إنستغرام وأكثر\n"
            "• اختيار جودة الفيديو المناسبة لك\n"
            "• تحميل الصوت فقط بصيغة MP3\n"
            "• عرض حجم الملف قبل التحميل\n\n"
            "📌 *كيفية الاستخدام:*\n"
            "فقط أرسل رابط الفيديو وسأتولى الباقي!\n\n"
            "⚙️ الأوامر المتاحة:\n"
            "/start - بدء البوت\n"
            "/help - المساعدة\n"
            "/lang - تغيير اللغة\n"
            "/cancel - إلغاء العملية الحالية"
        ),
        "help": (
            "📖 *دليل الاستخدام*\n\n"
            "1️⃣ أرسل رابط الفيديو مباشرة\n"
            "2️⃣ اختر نوع التحميل (فيديو أو صوت)\n"
            "3️⃣ اختر الجودة المناسبة\n"
            "4️⃣ انتظر حتى يكتمل التحميل\n\n"
            "🌐 *المنصات المدعومة:*\n"
            "YouTube • TikTok • Facebook • Instagram\n"
            "Twitter/X • Dailymotion • Vimeo • وأكثر!\n\n"
            "⚠️ *ملاحظات:*\n"
            "• الحد الأقصى لحجم الملف: 50 ميجابايت\n"
            "• بعض الفيديوهات الخاصة لا يمكن تحميلها\n"
            "• لا تنتهك حقوق الملكية الفكرية"
        ),
        "choose_type": "🎬 *اختر نوع التحميل:*",
        "choose_quality": "📊 *اختر جودة الفيديو:*\n\n_(الأرقام تمثل الدقة العمودية للفيديو)_",
        "choose_audio_quality": "🎵 *اختر جودة الصوت:*",
        "downloading": "⏳ *جارٍ التحميل...*\nيرجى الانتظار، قد يستغرق هذا بعض الوقت.",
        "fetching_info": "🔍 *جارٍ جلب معلومات الفيديو...*",
        "uploading": "📤 *جارٍ الرفع إلى تلغرام...*",
        "done": "✅ *تم التحميل بنجاح!*",
        "cancelled": "❌ *تم إلغاء العملية.*",
        "language_changed": "✅ تم تغيير اللغة إلى العربية.",
        "choose_language": "🌐 *اختر اللغة / Choose Language:*",

        # ===== معلومات الفيديو =====
        "video_info": (
            "📹 *معلومات الفيديو:*\n\n"
            "📌 *العنوان:* {title}\n"
            "⏱️ *المدة:* {duration}\n"
            "👁️ *المشاهدات:* {views}\n"
            "📅 *تاريخ الرفع:* {upload_date}\n"
            "🌐 *المنصة:* {platform}"
        ),
        "quality_option": "🎬 {label} — الحجم التقريبي: {size}",
        "audio_option": "🎵 {label} — الحجم التقريبي: {size}",
        "size_unknown": "غير معروف",
        "quality_unavailable": "⚠️ هذه الجودة غير متاحة، سيتم استخدام أقرب جودة متاحة.",

        # ===== رسائل الأخطاء =====
        "error_invalid_url": (
            "❌ *الرابط غير صالح!*\n\n"
            "يرجى إرسال رابط صحيح من إحدى المنصات المدعومة.\n"
            "مثال: `https://www.youtube.com/watch?v=...`"
        ),
        "error_unsupported_platform": (
            "⚠️ *المنصة غير مدعومة حالياً*\n\n"
            "المنصات المدعومة: YouTube, TikTok, Facebook, Instagram, Twitter, Dailymotion, Vimeo"
        ),
        "error_video_unavailable": (
            "🚫 *الفيديو غير متاح!*\n\n"
            "قد يكون الفيديو:\n"
            "• محذوفاً أو خاصاً\n"
            "• محظوراً في منطقتك\n"
            "• يتطلب تسجيل دخول"
        ),
        "error_file_too_large": (
            "📦 *الملف كبير جداً!*\n\n"
            "حجم الملف يتجاوز الحد المسموح به ({max_size} ميجابايت).\n"
            "جرب اختيار جودة أقل."
        ),
        "error_download_failed": (
            "❌ *فشل التحميل!*\n\n"
            "حدث خطأ أثناء التحميل. يرجى المحاولة مرة أخرى.\n"
            "إذا استمرت المشكلة، جرب رابطاً آخر."
        ),
        "error_general": "❌ *حدث خطأ غير متوقع.* يرجى المحاولة مرة أخرى.",
        "error_timeout": "⏰ *انتهت مهلة الطلب.* يرجى المحاولة مرة أخرى.",

        # ===== مكافحة السبام =====
        "rate_limit_exceeded": (
            "⏳ *لقد تجاوزت الحد المسموح به من الطلبات!*\n\n"
            "يرجى الانتظار {seconds} ثانية قبل إرسال طلب جديد."
        ),

        # ===== أزرار =====
        "btn_video": "🎬 فيديو",
        "btn_audio": "🎵 صوت MP3",
        "btn_cancel": "❌ إلغاء",
        "btn_back": "🔙 رجوع",
        "btn_ar": "🇸🇦 العربية",
        "btn_en": "🇬🇧 English",

        # ===== جودات الصوت =====
        "audio_qualities": {
            "128": "128 kbps — جودة عادية",
            "192": "192 kbps — جودة جيدة",
            "320": "320 kbps — جودة ممتازة",
        },
    },

    "en": {
        # ===== Welcome Messages =====
        "welcome": (
            "👋 *Welcome to the Video Downloader Bot!*\n\n"
            "🎯 *What I can do:*\n"
            "• Download videos from YouTube, TikTok, Facebook, Instagram & more\n"
            "• Choose your preferred video quality\n"
            "• Download audio only in MP3 format\n"
            "• Show file size before downloading\n\n"
            "📌 *How to use:*\n"
            "Just send a video link and I'll handle the rest!\n\n"
            "⚙️ Available commands:\n"
            "/start - Start the bot\n"
            "/help - Help guide\n"
            "/lang - Change language\n"
            "/cancel - Cancel current operation"
        ),
        "help": (
            "📖 *User Guide*\n\n"
            "1️⃣ Send a video link directly\n"
            "2️⃣ Choose download type (video or audio)\n"
            "3️⃣ Select your preferred quality\n"
            "4️⃣ Wait for the download to complete\n\n"
            "🌐 *Supported Platforms:*\n"
            "YouTube • TikTok • Facebook • Instagram\n"
            "Twitter/X • Dailymotion • Vimeo • and more!\n\n"
            "⚠️ *Notes:*\n"
            "• Maximum file size: 50 MB\n"
            "• Private videos cannot be downloaded\n"
            "• Do not violate copyright laws"
        ),
        "choose_type": "🎬 *Choose download type:*",
        "choose_quality": "📊 *Choose video quality:*\n\n_(Numbers represent vertical resolution)_",
        "choose_audio_quality": "🎵 *Choose audio quality:*",
        "downloading": "⏳ *Downloading...*\nPlease wait, this may take a moment.",
        "fetching_info": "🔍 *Fetching video information...*",
        "uploading": "📤 *Uploading to Telegram...*",
        "done": "✅ *Download complete!*",
        "cancelled": "❌ *Operation cancelled.*",
        "language_changed": "✅ Language changed to English.",
        "choose_language": "🌐 *اختر اللغة / Choose Language:*",

        # ===== Video Info =====
        "video_info": (
            "📹 *Video Information:*\n\n"
            "📌 *Title:* {title}\n"
            "⏱️ *Duration:* {duration}\n"
            "👁️ *Views:* {views}\n"
            "📅 *Upload Date:* {upload_date}\n"
            "🌐 *Platform:* {platform}"
        ),
        "quality_option": "🎬 {label} — Est. size: {size}",
        "audio_option": "🎵 {label} — Est. size: {size}",
        "size_unknown": "Unknown",
        "quality_unavailable": "⚠️ This quality is unavailable, using the closest available quality.",

        # ===== Error Messages =====
        "error_invalid_url": (
            "❌ *Invalid URL!*\n\n"
            "Please send a valid link from a supported platform.\n"
            "Example: `https://www.youtube.com/watch?v=...`"
        ),
        "error_unsupported_platform": (
            "⚠️ *Unsupported platform*\n\n"
            "Supported platforms: YouTube, TikTok, Facebook, Instagram, Twitter, Dailymotion, Vimeo"
        ),
        "error_video_unavailable": (
            "🚫 *Video unavailable!*\n\n"
            "The video might be:\n"
            "• Deleted or private\n"
            "• Geo-restricted in your region\n"
            "• Requires login"
        ),
        "error_file_too_large": (
            "📦 *File too large!*\n\n"
            "The file size exceeds the allowed limit ({max_size} MB).\n"
            "Try selecting a lower quality."
        ),
        "error_download_failed": (
            "❌ *Download failed!*\n\n"
            "An error occurred during download. Please try again.\n"
            "If the problem persists, try a different link."
        ),
        "error_general": "❌ *An unexpected error occurred.* Please try again.",
        "error_timeout": "⏰ *Request timed out.* Please try again.",

        # ===== Anti-Spam =====
        "rate_limit_exceeded": (
            "⏳ *You've exceeded the request limit!*\n\n"
            "Please wait {seconds} seconds before sending a new request."
        ),

        # ===== Buttons =====
        "btn_video": "🎬 Video",
        "btn_audio": "🎵 Audio MP3",
        "btn_cancel": "❌ Cancel",
        "btn_back": "🔙 Back",
        "btn_ar": "🇸🇦 العربية",
        "btn_en": "🇬🇧 English",

        # ===== Audio Qualities =====
        "audio_qualities": {
            "128": "128 kbps — Standard quality",
            "192": "192 kbps — Good quality",
            "320": "320 kbps — Excellent quality",
        },
    }
}


def get_message(key: str, lang: str = "ar", **kwargs) -> str:
    """الحصول على رسالة بلغة محددة مع دعم المتغيرات"""
    messages = MESSAGES.get(lang, MESSAGES["ar"])
    message = messages.get(key, MESSAGES["ar"].get(key, f"[{key}]"))
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return message
