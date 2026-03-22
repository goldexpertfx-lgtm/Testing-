import os
import asyncio
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5072932186
WHATSAPP_LINK = "https://whatsapp.com/channel/0029Vb5eRVjGzzKNnL7c050y"
WEBSITE_LINK = "https://www.brokeraccountguide.com"

# Temporary Storage for users
all_users = set()

# ================= FUNCTIONS =================

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """MON-FRI: Daily Gold Setup Reminder"""
    today = datetime.datetime.now().weekday()
    
    # 5=Saturday, 6=Sunday (Stop auto-reminders on weekend)
    if today >= 5:
        return

    text = (
        "<b>⚠️ DON'T MISS TODAY'S GOLD SETUP!</b>\n\n"
        "<b>JOIN NOW & COPY TRADES:</b>\n"
        "<b>👇👇</b>"
    )
    join_kb = [[InlineKeyboardButton("✅ JOIN WHATSAPP NOW", url=WHATSAPP_LINK)]]
    
    try:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(join_kb)
        )
    except:
        pass

async def sunday_offer_job(context: ContextTypes.DEFAULT_TYPE):
    """SUNDAY: Auto Weekend Offer"""
    text = (
        "<b>WEEKEND OFFER 🎁</b>\n\n"
        "<b>GET FREE VIP GOLD SIGNALS ACCESS 🚀</b>\n"
        "<b>LIMITED TIME ONLY!</b>\n\n"
        "<b>JOIN NOW:</b>\n"
        f"<b>{WEBSITE_LINK}</b>"
    )
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
        except:
            pass

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    chat_id = update.effective_message.chat_id
    all_users.add(user_id)
    
    # Keyboard Setup (User + Admin)
    reply_kb = [["🎁 CLAIM YOUR FREE PREMIUM GOLD VIP ACCESS NOW"]]
    if user_id == ADMIN_ID:
        reply_kb.append(["📢 ADMIN: BROADCAST / REPORT"])
        
    bottom_button = ReplyKeyboardMarkup(reply_kb, resize_keyboard=True)
    
    # 1. ORIGINAL Greeting Message
    await update.message.reply_text(
        text=f"HEY, <b>{user_name.upper()}</b> !", 
        parse_mode='HTML',
        reply_markup=bottom_button
    )
    
    # 2. ORIGINAL Join Whatsapp Message
    join_kb = [[InlineKeyboardButton("JOIN NOW 👇✅", url=WHATSAPP_LINK)]]
    await update.message.reply_text(
        text="<b>JOIN WHATSAPP CHANNEL 👇👇</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(join_kb)
    )

    # --- MON-FRI REMINDER SETUP (15 Minutes) ---
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_repeating(send_reminder, interval=900, first=900, chat_id=chat_id, name=str(chat_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    text = update.message.text

    # Claim Access Logic
    if text == "🎁 CLAIM YOUR FREE PREMIUM GOLD VIP ACCESS NOW":
        response_text = f"<b>{user_name.upper()}</b> 🚀 <b>UNLOCK YOUR FREE PREMIUM GOLD VIP MEMBERSHIP</b>"
        website_button = [[InlineKeyboardButton("JOIN NOW ✅", url=WEBSITE_LINK)]]
        await update.message.reply_text(
            text=response_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(website_button)
        )

    # ADMIN: Broadcast Mode Trigger
    elif text == "📢 ADMIN: BROADCAST / REPORT" and user_id == ADMIN_ID:
        await update.message.reply_text(
            "<b>🛠 BROADCAST MODE ACTIVE!</b>\n\n"
            "<b>TYPE YOUR WEEKLY REPORT OR ANY MESSAGE. IT WILL BE SENT TO ALL SUBSCRIBERS.</b>",
            parse_mode='HTML'
        )
        context.user_data['state'] = 'BROADCASTING'

    # ADMIN: Send to all logic
    elif context.user_data.get('state') == 'BROADCASTING' and user_id == ADMIN_ID:
        count = 0
        for uid in all_users:
            try:
                # Sends whatever admin types exactly (Weekly Report format)
                await context.bot.send_message(chat_id=uid, text=f"<b>{text}</b>", parse_mode='HTML')
                count += 1
            except:
                pass
        
        await update.message.reply_text(f"<b>✅ BROADCAST SUCCESSFUL! SENT TO {count} USERS.</b>")
        context.user_data['state'] = None

# ================= MAIN =================

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN IS MISSING!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # SUNDAY AUTO OFFER: Every Sunday at 12:00 PM (Days 6)
        app.job_queue.run_daily(sunday_offer_job, time=datetime.time(hour=12, minute=0), days=(6,))
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("BOT IS LIVE (ELITE ADMIN VERSION)...")
        app.run_polling(drop_pending_updates=True)
        
