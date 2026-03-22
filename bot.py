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

# Users list (Memory mein save hogi, behtar hai isay file ya database mein save karein)
all_users = set()

# ================= FUNCTIONS =================

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Mon-Fri: Auto Reminder (15 mins interval)"""
    today = datetime.datetime.now().weekday()
    
    # 5 = Saturday, 6 = Sunday. Weekend par auto band.
    if today >= 5:
        return

    text = (
        "<b>⚠️ Don't Miss Today's Gold Setup!</b>\n\n"
        "Join now & copy trades:\n"
        "👇👇"
    )
    join_kb = [[InlineKeyboardButton("JOIN WHATSAPP NOW 👇✅", url=WHATSAPP_LINK)]]
    
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
    """Sunday: Auto Weekend Offer at 12:00 PM"""
    text = (
        "<b>Weekend Offer 🎁</b>\n\n"
        "Get <b>FREE VIP Gold Signals Access</b> 🚀\n"
        "Limited Time Only!\n\n"
        "<b>Join Now:</b>\n"
        f"{WEBSITE_LINK}"
    )
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
        except:
            pass

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    all_users.add(user_id)
    
    # Admin & User Buttons
    keyboard = [["🎁 Claim Your FREE Premium Gold VIP Access Now"]]
    if user_id == ADMIN_ID:
        keyboard.append(["📢 Admin: Broadcast / Report"])
    
    reply_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        text=f"Welcome, <b>{update.effective_user.first_name}</b>!", 
        parse_mode='HTML',
        reply_markup=reply_kb
    )

    # Mon-Fri Reminders Setup (900s = 15m)
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    
    context.job_queue.run_repeating(send_reminder, interval=900, first=900, chat_id=chat_id, name=str(chat_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # 1. User Claim Button
    if text == "🎁 Claim Your FREE Premium Gold VIP Access Now":
        btn = [[InlineKeyboardButton("JOIN NOW ✅", url=WEBSITE_LINK)]]
        await update.message.reply_text(
            text="🚀 Unlock Your FREE Premium Gold VIP Membership",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(btn)
        )

    # 2. Admin Broadcast Trigger
    elif text == "📢 Admin: Broadcast / Report" and user_id == ADMIN_ID:
        await update.message.reply_text(
            "<b>Broadcast Mode ON! 🛠</b>\n\nAb aap jo bhi type karke bhejenge, wo saare users ko send ho jayega.",
            parse_mode='HTML'
        )
        context.user_data['state'] = 'BROADCASTING'

    # 3. Sending the Broadcast
    elif context.user_data.get('state') == 'BROADCASTING' and user_id == ADMIN_ID:
        count = 0
        for uid in all_users:
            try:
                # Forwarding whatever admin typed
                await context.bot.send_message(chat_id=uid, text=text, parse_mode='HTML')
                count += 1
            except:
                pass
        
        await update.message.reply_text(f"✅ Broadcast Sent to {count} users.")
        context.user_data['state'] = None # Mode off

# ================= MAIN =================

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Schedule Sunday Auto Offer at 12:00 PM (Days 6 = Sunday)
        app.job_queue.run_daily(sunday_offer_job, time=datetime.time(hour=12, minute=0), days=(6,))

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot is LIVE (Premium Gold Machine)...")
        app.run_polling(drop_pending_updates=True)
    
