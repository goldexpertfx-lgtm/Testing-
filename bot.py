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

# Temporary storage for active users
all_users = set()

# ================= FUNCTIONS =================

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Mon-Fri: Professional Daily Setup Reminder"""
    today = datetime.datetime.now().weekday()
    
    # 0=Mon, 4=Fri. (Auto-stop on Sat/Sun)
    if today >= 5:
        return

    text = (
        "<b>⚠️ DON'T MISS TODAY'S GOLD SETUP!</b>\n\n"
        "<b>JOIN NOW & COPY OUR PROFESSIONAL TRADES:</b>\n"
        "<b>👇👇👇</b>"
    )
    join_kb = [[InlineKeyboardButton("✅ JOIN WHATSAPP NOW", url=WHATSAPP_LINK)]]
    
    chat_id = context.job.chat_id
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(join_kb)
        )
    except:
        pass

async def send_sunday_offer(context: ContextTypes.DEFAULT_TYPE):
    """Sunday: Automatic Premium Weekend Offer"""
    text = (
        "<b>🎁 WEEKEND SPECIAL OFFER 🎁</b>\n\n"
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
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    all_users.add(user_id)
    
    # Bottom Keyboard Setup
    keyboard = [["🎁 Claim Your FREE Premium Gold VIP Access Now"]]
    
    # Show Admin Button ONLY to the Admin
    if user_id == ADMIN_ID:
        keyboard.append(["📢 ADMIN: BROADCAST / WEEKLY REPORT"])
        
    reply_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # 1. Professional Greeting
    await update.message.reply_text(
        text=f"<b>HEY, {user_name.upper()}! ⚡</b>\n\n<b>WELCOME TO THE ELITE GOLD TRADING HUB.</b>", 
        parse_mode='HTML',
        reply_markup=reply_kb
    )
    
    # 2. Join Message
    join_kb = [[InlineKeyboardButton("✅ JOIN WHATSAPP CHANNEL", url=WHATSAPP_LINK)]]
    await update.message.reply_text(
        text="<b>Join Whatsapp Channel 👇👇: 👇</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(join_kb)
    )

    # --- MON-FRI REMINDER SETUP (Every 15 Minutes) ---
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_repeating(send_daily_reminder, interval=900, first=900, chat_id=chat_id, name=str(chat_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # User Request Access
    if text == "🎁 Claim Your FREE Premium Gold VIP Access Now":
        response_text = f"<b>🚀 Unlock Your FREE Premium Gold VIP Membership</b>"
        website_button = [[InlineKeyboardButton("✅ ACCESS NOW", url=WEBSITE_LINK)]]
        await update.message.reply_text(
            text=response_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(website_button)
        )

    # Admin Broadcast Trigger
    elif text == "📢 ADMIN: BROADCAST / WEEKLY REPORT" and user_id == ADMIN_ID:
        await update.message.reply_text(
            "<b>🛠 BROADCAST MODE ACTIVATED!</b>\n\n"
            "<b>TYPE YOUR WEEKLY REPORT OR ANY MESSAGE BELOW. IT WILL BE SENT TO ALL SUBSCRIBERS.</b>",
            parse_mode='HTML'
        )
        context.user_data['state'] = 'BROADCASTING'

    # Admin Sending Message to Everyone
    elif context.user_data.get('state') == 'BROADCASTING' and user_id == ADMIN_ID:
        count = 0
        for uid in all_users:
            try:
                # We send exactly what the admin typed (supports bold/formatting if admin uses it)
                await context.bot.send_message(chat_id=uid, text=f"<b>{text}</b>", parse_mode='HTML')
                count += 1
            except:
                pass
        
        await update.message.reply_text(f"<b>✅ BROADCAST SUCCESSFUL! SENT TO {count} USERS.</b>", parse_mode='HTML')
        context.user_data['state'] = None

# ================= MAIN =================

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Automatic Sunday Offer at 12:00 PM
    app.job_queue.run_daily(send_sunday_offer, time=datetime.time(hour=12, minute=0), days=(6,))
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is LIVE (Elite Admin Version)...")
    app.run_polling(drop_pending_updates=True)
    
