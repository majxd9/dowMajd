"""
وحدة إدارة بيانات المستخدمين (اللغة والحالة في الذاكرة)
In-memory user data management (language, state)
"""

import logging
from config.settings import DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)

# تخزين بيانات المستخدمين في الذاكرة
# {user_id: {"lang": "ar", "state": "idle", "current_url": None, "video_info": None}}
_user_data: dict[int, dict] = {}


def get_user_lang(user_id: int) -> str:
    """الحصول على لغة المستخدم"""
    return _user_data.get(user_id, {}).get("lang", DEFAULT_LANGUAGE)


def set_user_lang(user_id: int, lang: str):
    """تعيين لغة المستخدم"""
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id]["lang"] = lang
    logger.info(f"User {user_id} language set to: {lang}")


def get_user_state(user_id: int) -> str:
    """الحصول على حالة المستخدم الحالية"""
    return _user_data.get(user_id, {}).get("state", "idle")


def set_user_state(user_id: int, state: str):
    """تعيين حالة المستخدم"""
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id]["state"] = state


def get_user_url(user_id: int) -> str | None:
    """الحصول على الرابط الحالي للمستخدم"""
    return _user_data.get(user_id, {}).get("current_url")


def set_user_url(user_id: int, url: str):
    """تعيين الرابط الحالي للمستخدم"""
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id]["current_url"] = url


def get_user_video_info(user_id: int) -> dict | None:
    """الحصول على معلومات الفيديو المخزنة للمستخدم"""
    return _user_data.get(user_id, {}).get("video_info")


def set_user_video_info(user_id: int, info: dict):
    """تخزين معلومات الفيديو للمستخدم"""
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id]["video_info"] = info


def clear_user_session(user_id: int):
    """مسح جلسة المستخدم الحالية (مع الاحتفاظ باللغة)"""
    lang = get_user_lang(user_id)
    _user_data[user_id] = {
        "lang": lang,
        "state": "idle",
        "current_url": None,
        "video_info": None,
    }


def init_user(user_id: int, lang: str = None):
    """تهيئة بيانات مستخدم جديد"""
    if user_id not in _user_data:
        _user_data[user_id] = {
            "lang": lang or DEFAULT_LANGUAGE,
            "state": "idle",
            "current_url": None,
            "video_info": None,
        }
