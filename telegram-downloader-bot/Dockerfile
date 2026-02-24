# ===================================================
# Dockerfile — بوت تلغرام لتحميل الفيديوهات
# ===================================================

FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOWNLOAD_PATH=/app/downloads

# تثبيت ffmpeg والأدوات المطلوبة
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً (للاستفادة من cache)
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود المشروع
COPY . .

# إنشاء مجلد التحميل
RUN mkdir -p /app/downloads

# تشغيل البوت
CMD ["python", "main.py"]
