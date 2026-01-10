import os
import yt_dlp
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- البيانات الرسمية ---
TOKEN = "8571508914:AAHH-8KTOhiRBMRdv1cAD7fBU0qZcFbbpgQ"
CH_ID = "@dopamine_waleed" 
CH_URL = "https://t.me/dopamine_waleed"
INSTA_URL = "https://www.instagram.com/waleedokde"
FB_URL = "https://www.facebook.com/share/14U29fpr4Rc/"
BOT_URL = "https://t.me/zxw_down_2026_bot"

DB_FILE = "stats.json"

def get_stats():
    if not os.path.exists(DB_FILE): return {"users": [], "downloads": 0}
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {"users": [], "downloads": 0}

def update_stats(user_id, is_download=False):
    stats = get_stats()
    if user_id not in stats["users"]: stats["users"].append(user_id)
    if is_download: stats["downloads"] += 1
    with open(DB_FILE, "w") as f: json.dump(stats, f)

# --- رسالة الترحيب الاحترافية الجديدة ---
START_TEXT = (
    "👋 **أهلاً بك في بوت التحميل الذكي والاحترافي!**\n\n"
    "🚀 **أنا أدعم التحميل بجودة عالية من المنصات التالية:**\n"
    "• 🎥 **يوتيوب (YouTube)** - فيديوهات وشورتس\n"
    "• 📸 **إنستغرام (Instagram)** - ريلز وبوستات\n"
    "• 🎬 **تيك توك (TikTok)** - بدون علامة مائية\n"
    "• 💙 **فيسبوك (Facebook)** - فيديوهات عامة\n\n"
    "✨ **أرسل رابط الفيديو الآن وسأقوم بمهمتي فوراً!**\n\n"
    "⚠️ **ملاحظة:** يرجى التأكد من الاشتراك في قنواتنا لتفعيل الخدمة."
)

async def download_and_send(url, update, context, user_name):
    chat_id = update.effective_chat.id
    status = await context.bot.send_message(chat_id=chat_id, text="🔍 جاري تحليل الرابط وسحب الفيديو... انتظر قليلاً.")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'vid_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as v:
                await context.bot.send_video(
                    chat_id=chat_id, 
                    video=v, 
                    caption=f"✅ تم التحميل بنجاح!\n📌 العنوان: {info.get('title', 'فيديو')}\n👤 المطور: @waleedokde"
                )
            
            os.remove(filename)
            update_stats(update.effective_user.id, is_download=True)
            await status.delete()
            
            share_text = f"حمّل فيديوهات يوتيوب وإنستا وتيك توك بسهولة عبر بوت: {BOT_URL}"
            keyboard = [[InlineKeyboardButton("🚀 شارك البوت مع أصدقائك", url=f"https://t.me/share/url?url={BOT_URL}&text={share_text}")]]
            await context.bot.send_message(chat_id=chat_id, text="استمتع بالفيديو! أرسل رابطاً جديداً للتحميل 👇", reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        await status.edit_text("❌ فشل التحميل! تأكد أن الرابط عام وصحيح وليس فيديو خاص.")

async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CH_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    update_stats(user_id)
    
    if text == "إحصائيات":
        stats = get_stats()
        await update.message.reply_text(f"📊 إحصائيات البوت:\n👥 مستخدمين: {len(stats['users'])}\n📥 تحميلات: {stats['downloads']}")
        return

    if not text or not text.startswith("http"): return
    context.user_data['last_url'] = text

    if await is_subscribed(user_id, context):
        await download_and_send(text, update, context, update.effective_user.first_name)
    else:
        keyboard = [
            [InlineKeyboardButton("1️⃣ قناة التلجرام 📢", url=CH_URL)],
            [InlineKeyboardButton("2️⃣ حساب الإنستغرام 📸", url=INSTA_URL)],
            [InlineKeyboardButton("🔄 تم الاشتراك؟ اضغط هنا للتحميل", callback_data="check")]
        ]
        await update.message.reply_text(
            f"⚠️ **عذراً يا {update.effective_user.first_name}!**\nللاشتراك في خدمة التحميل، يجب عليك متابعة حساباتنا الرسمية أولاً.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(query.from_user.id, context):
        url = context.user_data.get('last_url')
        if url:
            await query.edit_message_text("✅ تم التحقق! جاري التحميل الآن...")
            await download_and_send(url, update, context, query.from_user.first_name)
    else:
        await query.answer("⚠️ لم تشترك في كافة الحسابات بعد!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(START_TEXT, parse_mode="Markdown")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="check"))
    app.run_polling()

if __name__ == '__main__':
    main()
