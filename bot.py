import os
import asyncio
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5072932186  # Aapki ID
WHATSAPP_LINK = "https://whatsapp.com/channel/0029Vb5eRVjGzzKNnL7c050y"
WEBSITE_LINK = "https://www.brokeraccountguide.com"

# Temporary Storage for Users (Database use karna behtar hai long-term ke liye)
all_users = set()

# ================= HELPER FUNCTIONS =================

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Mon-Fri: Auto Reminder every 15 mins. Sat: OFF."""
    job = context.job
    today = datetime.datetime.now().weekday()
    
    # 5 = Saturday, 6 = Sunday. We stop auto-reminders on Saturday.
    if today == 5:
        return

    text = (
        "<b>🔥 DON'T MISS THE GOLDEN MOVE! 🔥</b>\n\n"
        "Join our <b>Official WhatsApp Channel</b> for real-time <b>XAUUSD Signals</b>, "
        "Market Analysis, and VIP Updates! 🚀📈\n\n"
        "<i>Success starts with the right signal.</i>"
    )
    join_kb = [[InlineKeyboardButton("✅ JOIN OFFICIAL CHANNEL NOW", url=WHATSAPP_LINK)]]
    
    try:
        await context.bot.send_message(
            chat_id=job.chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(join_kb)
        )
    except:
        pass

async def sunday_weekend_offer(context: ContextTypes.DEFAULT_TYPE):
    """Sunday: Automatic Special Offer"""
    text = (
        "<b>🎁 SPECIAL WEEKEND OFFER 🎁</b>\n\n"
        "Unlock your <b>FREE Premium Gold VIP Access</b> today! "
        "Get ready for the Monday market opening with our elite strategies. 🚀\n\n"
        "<b>Don't wait—Secure your spot now! 👇</b>"
    )
    offer_kb = [[InlineKeyboardButton("🚀 CLAIM FREE VIP ACCESS", url=WEBSITE_LINK)]]
    
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(offer_kb))
        except:
            pass

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    chat_id = update.effective_message.chat_id
    all_users.add(user_id)

    # Main Keyboard for Users
    keyboard = [["🎁 Claim Your FREE Premium Gold VIP Access Now"]]
    
    # Special Admin Button
    if user_id == ADMIN_ID:
        keyboard.append(["📢 Admin: Broadcast Message"])

    reply_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        text=f"<b>Welcome, {user_name}! ⚡</b>\n\nYour Professional Forex & Gold Trading Partner.",
        parse_mode='HTML',
        reply_markup=reply_kb
    )

    # --- JOB SCHEDULING ---
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    # Reminder every 15 mins (900 seconds)
    context.job_queue.run_repeating(send_reminder, interval=900, first=900, chat_id=chat_id, name=str(chat_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # User Claim Button
    if text == "🎁 Claim Your FREE Premium Gold VIP Access Now":
        response = (
            "<b>🚀 VIP ACCESS UNLOCKED 🚀</b>\n\n"
            "Congratulations! You are one step away from <b>Premium Gold Signals</b>.\n\n"
            "Click the button below to complete your setup: 👇"
        )
        btn = [[InlineKeyboardButton("✅ START VIP ACTIVATION", url=WEBSITE_LINK)]]
        await update.message.reply_text(text=response, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

    # Admin Broadcast Trigger
    elif text == "📢 Admin: Broadcast Message" and user_id == ADMIN_ID:
        await update.message.reply_text(
            "<b>Broadcast Mode Active! 🛠</b>\n\n"
            "Please type your message below and send it. I will forward it to all users.",
            parse_mode='HTML'
        )
        context.user_data['state'] = 'BROADCASTING'

    # Logic to send broadcast
    elif context.user_data.get('state') == 'BROADCASTING' and user_id == ADMIN_ID:
        count = 0
        for uid in all_users:
            try:
                await context.bot.send_message(chat_id=uid, text=f"<b>📢 ANNOUNCEMENT:</b>\n\n{text}", parse_mode='HTML')
                count += 1
            except:
                pass
        
        await update.message.reply_text(f"✅ <b>Broadcast Successful!</b> Sent to {count} users.", parse_mode='HTML')
        context.user_data['state'] = None

# ================= MAIN =================

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Schedule Sunday Auto-Post at 12:00 PM
        app.job_queue.run_daily(sunday_weekend_offer, time=datetime.time(hour=12, minute=0), days=(6,))

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot is LIVE (Premium Admin Version)...")
        app.run_polling(drop_pending_updates=True)
        
