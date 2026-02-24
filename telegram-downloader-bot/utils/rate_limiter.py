"""
وحدة مكافحة السبام وتحديد معدل الطلبات
Anti-spam and rate limiting module
"""

import time
import logging
from collections import defaultdict
from config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, COOLDOWN_SECONDS

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    نظام تحديد معدل الطلبات لكل مستخدم
    Tracks request counts per user within a time window
    """

    def __init__(self):
        # {user_id: [timestamps]}
        self._requests: dict[int, list[float]] = defaultdict(list)
        # {user_id: cooldown_until_timestamp}
        self._cooldowns: dict[int, float] = {}

    def is_allowed(self, user_id: int) -> tuple[bool, int]:
        """
        التحقق من إمكانية قبول طلب المستخدم.
        Returns: (is_allowed: bool, wait_seconds: int)
        """
        now = time.time()

        # التحقق من وجود فترة تهدئة نشطة
        if user_id in self._cooldowns:
            cooldown_until = self._cooldowns[user_id]
            if now < cooldown_until:
                wait_time = int(cooldown_until - now)
                logger.warning(f"User {user_id} is in cooldown for {wait_time}s")
                return False, wait_time
            else:
                del self._cooldowns[user_id]

        # تنظيف الطلبات القديمة خارج النافذة الزمنية
        self._requests[user_id] = [
            ts for ts in self._requests[user_id]
            if now - ts < RATE_LIMIT_WINDOW
        ]

        # التحقق من عدد الطلبات
        if len(self._requests[user_id]) >= RATE_LIMIT_REQUESTS:
            # تفعيل فترة التهدئة
            self._cooldowns[user_id] = now + COOLDOWN_SECONDS
            logger.warning(f"Rate limit exceeded for user {user_id}, cooldown: {COOLDOWN_SECONDS}s")
            return False, COOLDOWN_SECONDS

        # تسجيل الطلب الجديد
        self._requests[user_id].append(now)
        return True, 0

    def reset_user(self, user_id: int):
        """إعادة تعيين حالة المستخدم (للمشرفين)"""
        self._requests.pop(user_id, None)
        self._cooldowns.pop(user_id, None)

    def get_user_stats(self, user_id: int) -> dict:
        """الحصول على إحصائيات المستخدم"""
        now = time.time()
        recent_requests = [
            ts for ts in self._requests.get(user_id, [])
            if now - ts < RATE_LIMIT_WINDOW
        ]
        cooldown_remaining = max(
            0,
            int(self._cooldowns.get(user_id, 0) - now)
        )
        return {
            "requests_in_window": len(recent_requests),
            "max_requests": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW,
            "cooldown_remaining": cooldown_remaining,
        }


# مثيل عام واحد للاستخدام في جميع أنحاء البوت
rate_limiter = RateLimiter()
