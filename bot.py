import os
import yt_dlp
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- البيانات الرسمية الخاصة بك (لا تغيرها) ---
TOKEN = "8571508914:AAHH-8KTOhiRBMRdv1cAD7fBU0qZcFbbpgQ"
CH_ID = "@dopamine_waleed" 
CH_URL = "https://t.me/dopamine_waleed"
INSTA_URL = "https://www.instagram.com/waleedokde"
FB_URL = "https://www.facebook.com/share/14U29fpr4Rc/"
BOT_URL = "https://t.me/zxw_down_2026_bot"

DB_FILE = "stats.json"

# دالة الإحصائيات
def get_stats():
    if not os.path.exists(DB_FILE): return {"users": [], "downloads": 0}
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {"users": [], "downloads": 0}

def update_stats(user_id, is_download=False):
    stats = get_stats()
    if str(user_id) not in stats["users"]: stats["users"].append(str(user_id))
    if is_download: stats["downloads"] += 1
    with open(DB_FILE, "w") as f: json.dump(stats, f)

# --- محرك التحميل الشامل (الحل النهائي) ---
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferredformat': 'mp4'}]
}

async def download_video(url, update, context):
    chat_id = update.effective_chat.id
    status = await context.bot.send_message(chat_id=chat_id, text="🔍 جاري جلب الفيديو بأفضل جودة... انتظر قليلاً.")
    
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # التحميل في خلفية منفصلة لعدم تجميد البوت
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            if not info: raise Exception("Error")
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as v:
                await context.bot.send_video(
                    chat_id=chat_id, 
                    video=v, 
                    caption=f"✅ تم التحميل بنجاح!\n📌 {info.get('title', 'فيديو')}\n👤 المطور: @waleedokde"
                )
            os.remove(filename)
            update_stats(update.effective_user.id, is_download=True)
            await status.delete()
    except Exception as e:
        await status.edit_text("❌ فشل التحميل! تأكد أن الرابط عام وصحيح.\nإذا استمرت المشكلة، جرب رابطاً آخر.")

# --- فحص الاشتراك ورسالة الترحيب ---
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CH_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **أهلاً بك في بوت التحميل الذكي!**\n\n"
        "🎥 **يدعم البوت التحميل من:**\n"
        "• يوتيوب - إنستغرام - تيك توك - فيسبوك\n\n"
        "✨ **أرسل رابط الفيديو الآن وسأقوم بمهمتي فوراً!**\n\n"
        "⚠️ يجب الاشتراك في القناة أولاً لتفعيل الخدمة."
    )
    update_stats(update.effective_user.id)
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if not text or "http" not in text:
        if text == "إحصائيات":
            stats = get_stats()
            await update.message.reply_text(f"📊 إحصائيات البوت:\n👥 المستخدمين: {len(stats['users'])}\n📥 التحميلات: {stats['downloads']}")
        return

    context.user_data['url'] = text
    if await is_subscribed(user_id, context):
        await download_video(text, update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في القناة", url=CH_URL)],
            [InlineKeyboardButton("📸 تابعني على إنستا", url=INSTA_URL)],
            [InlineKeyboardButton("🔄 تحقق من الاشتراك للتحميل", callback_data="check")]
        ]
        await update.message.reply_text("⚠️ عفواً! يجب أن تشترك في قناتنا أولاً لتفعيل البوت.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(query.from_user.id, context):
        url = context.user_data.get('url')
        if url:
            await query.edit_message_text("✅ تم التحقق! جاري التحميل...")
            await download_video(url, update, context)
    else:
        await query.answer("⚠️ لم تشترك في القناة بعد!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="check"))
    app.run_polling()

if __name__ == '__main__':
    main()
