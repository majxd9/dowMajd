#!/bin/bash
# ===================================================
# سكريبت التثبيت التلقائي لبوت تلغرام
# Auto-setup script for Telegram Video Downloader Bot
# ===================================================

set -e  # إيقاف عند أي خطأ

echo "======================================================"
echo "  🤖 إعداد بوت تلغرام لتحميل الفيديوهات"
echo "======================================================"

# ===== التحقق من Python =====
echo ""
echo "📋 التحقق من المتطلبات..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت! يرجى تثبيته أولاً."
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# ===== التحقق من pip =====
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت!"
    exit 1
fi
echo "✅ pip3: $(pip3 --version)"

# ===== تثبيت ffmpeg =====
echo ""
echo "📦 تثبيت ffmpeg..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y ffmpeg
elif command -v brew &> /dev/null; then
    brew install ffmpeg
elif command -v yum &> /dev/null; then
    sudo yum install -y ffmpeg
else
    echo "⚠️  لم يتم التعرف على مدير الحزم. يرجى تثبيت ffmpeg يدوياً."
fi

if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "⚠️  ffmpeg غير مثبت — بعض الميزات قد لا تعمل"
fi

# ===== إنشاء البيئة الافتراضية =====
echo ""
echo "🐍 إنشاء البيئة الافتراضية..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ تم إنشاء البيئة الافتراضية"
else
    echo "✅ البيئة الافتراضية موجودة مسبقاً"
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# ===== تثبيت المكتبات =====
echo ""
echo "📚 تثبيت مكتبات Python..."
pip install --upgrade pip -q
pip install -r requirements.txt
echo "✅ تم تثبيت جميع المكتبات"

# ===== إعداد ملف .env =====
echo ""
echo "⚙️  إعداد ملف البيئة..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ تم إنشاء ملف .env من .env.example"
    echo ""
    echo "🔑 الآن أدخل توكن البوت:"
    read -p "   BOT_TOKEN: " bot_token
    if [ -n "$bot_token" ]; then
        sed -i "s/YOUR_BOT_TOKEN_HERE/$bot_token/" .env
        echo "✅ تم حفظ التوكن"
    else
        echo "⚠️  لم يتم إدخال التوكن. يرجى تعديل ملف .env يدوياً"
    fi
else
    echo "✅ ملف .env موجود مسبقاً"
fi

# ===== إنشاء مجلد التحميل =====
mkdir -p downloads
echo "✅ تم إنشاء مجلد downloads"

# ===== إنشاء سكريبت التشغيل =====
cat > start_bot.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python main.py
EOF
chmod +x start_bot.sh

echo ""
echo "======================================================"
echo "  ✅ اكتمل الإعداد بنجاح!"
echo "======================================================"
echo ""
echo "🚀 لتشغيل البوت:"
echo "   ./start_bot.sh"
echo ""
echo "🔄 للتشغيل في الخلفية (24/7):"
echo "   nohup ./start_bot.sh > bot.log 2>&1 &"
echo ""
echo "📊 لمتابعة السجلات:"
echo "   tail -f bot.log"
echo ""
