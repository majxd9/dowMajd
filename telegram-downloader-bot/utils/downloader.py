"""
وحدة تحميل الفيديو والصوت باستخدام yt-dlp
Video and audio downloader module using yt-dlp
"""

import os
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp

from config.settings import (
    DOWNLOAD_PATH, MAX_FILE_SIZE_BYTES, YTDLP_BASE_OPTIONS
)
from utils.formatters import format_file_size, format_duration, format_views, format_date, truncate_title

logger = logging.getLogger(__name__)

# إنشاء مجلد التحميل إذا لم يكن موجوداً
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


class VideoInfo:
    """كلاس لتخزين معلومات الفيديو"""
    def __init__(self, raw_info: dict):
        self.title = truncate_title(raw_info.get("title", ""))
        self.duration = raw_info.get("duration", 0)
        self.duration_str = format_duration(self.duration)
        self.views = format_views(raw_info.get("view_count"))
        self.upload_date = format_date(raw_info.get("upload_date"))
        self.platform = raw_info.get("extractor_key", "Unknown")
        self.url = raw_info.get("webpage_url", "")
        self.thumbnail = raw_info.get("thumbnail", "")
        self.formats = raw_info.get("formats", [])
        self.raw = raw_info

    def get_available_video_qualities(self) -> list[dict]:
        """
        استخراج الجودات المتاحة للفيديو مع تقدير الأحجام.
        Returns list of dicts: {quality_label, height, format_id, filesize, filesize_str}
        """
        seen_heights = set()
        qualities = []

        for fmt in self.formats:
            # تجاهل الصيغ الصوتية فقط
            if fmt.get("vcodec") == "none":
                continue
            height = fmt.get("height")
            if not height:
                continue
            if height in seen_heights:
                continue
            seen_heights.add(height)

            # تقدير الحجم
            filesize = fmt.get("filesize") or fmt.get("filesize_approx") or 0
            if not filesize and self.duration:
                tbr = fmt.get("tbr", 0) or 0
                filesize = int((tbr * 1000 * self.duration) / 8) if tbr else 0

            qualities.append({
                "height": height,
                "quality_label": f"{height}p",
                "format_id": fmt.get("format_id", ""),
                "filesize": filesize,
                "filesize_str": format_file_size(filesize) if filesize else "غير معروف",
                "ext": fmt.get("ext", "mp4"),
                "fps": fmt.get("fps", 0),
                "vcodec": fmt.get("vcodec", ""),
                "acodec": fmt.get("acodec", ""),
            })

        # ترتيب تصاعدي حسب الجودة
        qualities.sort(key=lambda x: x["height"])

        # إضافة خيار "أفضل جودة"
        if qualities:
            best = max(qualities, key=lambda x: x["height"])
            qualities.append({
                "height": 9999,
                "quality_label": "best",
                "format_id": "bestvideo+bestaudio/best",
                "filesize": best["filesize"],
                "filesize_str": best["filesize_str"],
                "ext": "mp4",
                "fps": best.get("fps", 0),
                "vcodec": best.get("vcodec", ""),
                "acodec": best.get("acodec", ""),
            })

        return qualities

    def get_available_audio_qualities(self) -> list[dict]:
        """استخراج الجودات الصوتية المتاحة"""
        seen_abr = set()
        audio_formats = []

        for fmt in self.formats:
            # الصيغ الصوتية فقط
            if fmt.get("vcodec") != "none" and fmt.get("acodec") == "none":
                continue
            abr = fmt.get("abr", 0) or 0
            if not abr:
                continue
            abr_rounded = round(abr / 32) * 32  # تقريب لأقرب 32
            if abr_rounded in seen_abr:
                continue
            seen_abr.add(abr_rounded)

            filesize = fmt.get("filesize") or fmt.get("filesize_approx") or 0
            if not filesize and self.duration:
                filesize = int((abr * 1000 * self.duration) / 8)

            audio_formats.append({
                "abr": abr_rounded,
                "quality_label": f"{abr_rounded}kbps",
                "format_id": fmt.get("format_id", ""),
                "filesize": filesize,
                "filesize_str": format_file_size(filesize) if filesize else "غير معروف",
                "ext": fmt.get("ext", "m4a"),
            })

        audio_formats.sort(key=lambda x: x["abr"])

        # إضافة خيارات افتراضية إذا لم تُوجد
        if not audio_formats:
            audio_formats = [
                {"abr": 128, "quality_label": "128kbps", "format_id": "bestaudio/best",
                 "filesize": 0, "filesize_str": "غير معروف", "ext": "mp3"},
                {"abr": 192, "quality_label": "192kbps", "format_id": "bestaudio/best",
                 "filesize": 0, "filesize_str": "غير معروف", "ext": "mp3"},
                {"abr": 320, "quality_label": "320kbps", "format_id": "bestaudio/best",
                 "filesize": 0, "filesize_str": "غير معروف", "ext": "mp3"},
            ]

        return audio_formats


async def fetch_video_info(url: str) -> Optional[VideoInfo]:
    """
    جلب معلومات الفيديو بدون تحميله (غير متزامن).
    Returns VideoInfo object or None on failure.
    """
    def _fetch():
        opts = {
            **YTDLP_BASE_OPTIONS,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _fetch)
        if info:
            return VideoInfo(info)
        return None
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError for {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching info for {url}: {e}")
        raise


async def download_video(
    url: str,
    height: int = 720,
    format_id: str = None,
    progress_callback=None
) -> Optional[list[str]]:
    """
    تحميل الفيديو وإرجاع مسار الملف أو قائمة مسارات للمنشورات المتعددة.
    Returns: list of file path strings or None on failure.
    """
    temp_dir = tempfile.mkdtemp(dir=DOWNLOAD_PATH)

    def _progress_hook(d):
        if progress_callback and d["status"] == "downloading":
            try:
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    percent = int(downloaded / total * 100)
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(percent, downloaded, total),
                        asyncio.get_event_loop()
                    )
            except Exception:
                pass

    def _download():
        if format_id and format_id != "bestvideo+bestaudio/best":
            fmt = f"{format_id}+bestaudio/bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        elif height == 9999:
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best[height<={height}]/best"

        opts = {
            **YTDLP_BASE_OPTIONS,
            "format": fmt,
            "outtmpl": os.path.join(temp_dir, "%(playlist_index)s_%(title).50s.%(ext)s"),
            "merge_output_format": "mp4",
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
            "progress_hooks": [_progress_hook],
            "max_filesize": MAX_FILE_SIZE_BYTES,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        # البحث عن الملفات المحمّلة (دعم المنشورات المتعددة)
        files = sorted(list(Path(temp_dir).glob("*")), key=os.path.getmtime)
        if files:
            return [str(f) for f in files if f.stat().st_size > 0]
        return None

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, _download)
        return file_path
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Video download error for {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error downloading video {url}: {e}")
        raise


async def download_audio(
    url: str,
    quality_kbps: int = 192,
    progress_callback=None
) -> Optional[str]:
    """
    تحميل الصوت فقط بصيغة MP3.
    Returns: file path string or None on failure.
    """
    temp_dir = tempfile.mkdtemp(dir=DOWNLOAD_PATH)

    def _progress_hook(d):
        if progress_callback and d["status"] == "downloading":
            try:
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    percent = int(downloaded / total * 100)
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(percent, downloaded, total),
                        asyncio.get_event_loop()
                    )
            except Exception:
                pass

    def _download():
        opts = {
            **YTDLP_BASE_OPTIONS,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "%(title).50s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(quality_kbps),
                },
                {
                    "key": "EmbedThumbnail",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
            ],
            "writethumbnail": True,
            "progress_hooks": [_progress_hook],
            "max_filesize": MAX_FILE_SIZE_BYTES,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        # البحث عن ملف MP3
        mp3_files = list(Path(temp_dir).glob("*.mp3"))
        if mp3_files:
            return str(mp3_files[0])

        # fallback: أي ملف صوتي
        audio_files = list(Path(temp_dir).glob("*"))
        if audio_files:
            return str(max(audio_files, key=lambda f: f.stat().st_size))
        return None

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, _download)
        return file_path
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Audio download error for {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error downloading audio {url}: {e}")
        raise


def cleanup_file(file_path: str | list[str]):
    """حذف الملف أو قائمة الملفات المؤقتة بعد الإرسال"""
    if not file_path:
        return
    
    paths = [file_path] if isinstance(file_path, str) else file_path
    
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                # حذف المجلد المؤقت إذا كان فارغاً
                parent = os.path.dirname(path)
                if os.path.exists(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                logger.info(f"Cleaned up: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up {path}: {e}")
