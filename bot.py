import os
import asyncio
import datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5072932186
WHATSAPP_LINK = "https://whatsapp.com/channel/0029Vb5eRVjGzzKNnL7c050y"
WEBSITE_LINK = "https://www.brokeraccountguide.com"

# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# Initialize DB on script start
init_db()

# ================= FUNCTIONS =================

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """MON-FRI: Daily Gold Setup Reminder"""
    today = datetime.datetime.now().weekday()
    if today >= 5: return

    text = "<b>⚠️ DON'T MISS TODAY'S GOLD SETUP!</b>\n\n<b>JOIN NOW & COPY TRADES:</b>\n<b>👇👇</b>"
    join_kb = [[InlineKeyboardButton("✅ JOIN WHATSAPP NOW", url=WHATSAPP_LINK)]]
    
    try:
        await context.bot.send_message(chat_id=context.job.chat_id, text=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(join_kb))
    except: pass

async def sunday_offer_job(context: ContextTypes.DEFAULT_TYPE):
    """SUNDAY: Auto Weekend Offer"""
    users = get_all_users()
    text = (
        "<b>WEEKEND OFFER 🎁</b>\n\n"
        "<b>GET FREE VIP GOLD SIGNALS ACCESS 🚀</b>\n"
        "<b>LIMITED TIME ONLY!</b>\n\n"
        "<b>JOIN NOW:</b>\n"
        f"<b>{WEBSITE_LINK}</b>"
    )
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
        except: pass

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    chat_id = update.effective_message.chat_id
    
    # Save user permanently to Database
    add_user(user_id)
    
    reply_kb = [["🎁 CLAIM YOUR FREE PREMIUM GOLD VIP ACCESS NOW"]]
    if user_id == ADMIN_ID:
        reply_kb.append(["📢 ADMIN: BROADCAST / REPORT"])
        
    bottom_button = ReplyKeyboardMarkup(reply_kb, resize_keyboard=True)
    
    await update.message.reply_text(text=f"HEY, <b>{user_name.upper()}</b> !", parse_mode='HTML', reply_markup=bottom_button)
    
    join_kb = [[InlineKeyboardButton("JOIN NOW 👇✅", url=WHATSAPP_LINK)]]
    await update.message.reply_text(text="<b>JOIN WHATSAPP CHANNEL 👇👇</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(join_kb))

    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs: job.schedule_removal()
    context.job_queue.run_repeating(send_reminder, interval=900, first=900, chat_id=chat_id, name=str(chat_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🎁 CLAIM YOUR FREE PREMIUM GOLD VIP ACCESS NOW":
        btn = [[InlineKeyboardButton("JOIN NOW ✅", url=WEBSITE_LINK)]]
        await update.message.reply_text(text=f"<b>{update.effective_user.first_name.upper()}</b> 🚀 <b>UNLOCK VIP MEMBERSHIP</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

    elif text == "📢 ADMIN: BROADCAST / REPORT" and user_id == ADMIN_ID:
        await update.message.reply_text("<b>🛠 BROADCAST MODE ACTIVE! TYPE YOUR MESSAGE:</b>", parse_mode='HTML')
        context.user_data['state'] = 'BROADCASTING'

    elif context.user_data.get('state') == 'BROADCASTING' and user_id == ADMIN_ID:
        users = get_all_users()
        count = 0
        for uid in users:
            try:
                await context.bot.send_message(chat_id=uid, text=f"<b>{text}</b>", parse_mode='HTML')
                count += 1
            except: pass
        
        await update.message.reply_text(f"<b>✅ SENT TO {count} USERS PERMANENTLY.</b>")
        context.user_data['state'] = None

# ================= MAIN =================
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN MISSING")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.job_queue.run_daily(sunday_offer_job, time=datetime.time(hour=12, minute=0), days=(6,))
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("BOT LIVE WITH DATABASE...")
        app.run_polling(drop_pending_updates=True)
        
