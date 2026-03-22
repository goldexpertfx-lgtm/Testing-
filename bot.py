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

USERS = set()

# ================= FUNCTIONS =================

async def save_user(update: Update):
    USERS.add(update.effective_chat.id)


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Har 15 mins baad reminder (Mon-Fri only)"""
    today = datetime.datetime.now().weekday()

    if today == 5:  # Saturday OFF
        return

    job = context.job
    join_kb = [[InlineKeyboardButton("JOIN NOW 👇✅", url=WHATSAPP_LINK)]]

    text = "<b>⚠️ Don't Miss Today's Gold Setup!</b>\n\nJoin now & copy trades:\n👇👇"

    try:
        await context.bot.send_message(
            chat_id=job.chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(join_kb)
        )
    except:
        pass


async def sunday_offer(context: ContextTypes.DEFAULT_TYPE):
    """Sunday auto promotion"""
    text = """<b>Weekend Offer 🎁</b>

Get FREE VIP Gold Signals Access 🚀  
Limited Time Only!

Join Now:
https://www.brokeraccountguide.com/"""

    for user in USERS:
        try:
            await context.bot.send_message(
                chat_id=user,
                text=text,
                parse_mode='HTML'
            )
        except:
            pass


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin broadcast (Saturday use)"""
    if update.effective_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)

    for user in USERS:
        try:
            await context.bot.send_message(
                chat_id=user,
                text=message,
                parse_mode='HTML'
            )
        except:
            pass


# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    chat_id = update.effective_message.chat_id

    await save_user(update)

    # Bottom Button
    reply_kb = [["🎁 Claim Your FREE Premium Gold VIP Access Now"]]
    bottom_button = ReplyKeyboardMarkup(reply_kb, resize_keyboard=True)

    await update.message.reply_text(
        text=f"Hey, <b>{user_name}</b> !",
        parse_mode='HTML',
        reply_markup=bottom_button
    )

    # WhatsApp Join Button
    join_kb = [[InlineKeyboardButton("JOIN NOW 👇✅", url=WHATSAPP_LINK)]]

    await update.message.reply_text(
        text="<b>Join Whatsapp Channel 👇👇</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(join_kb)
    )

    # Reminder setup
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_repeating(
        send_reminder,
        interval=900,
        first=900,
        chat_id=chat_id,
        name=str(chat_id)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    text = update.message.text

    if text == "🎁 Claim Your FREE Premium Gold VIP Access Now":
        response_text = f"<b>{user_name}</b> 🚀 Unlock Your FREE Premium Gold VIP Membership"

        website_button = [[InlineKeyboardButton("JOIN NOW ✅", url=WEBSITE_LINK)]]

        await update.message.reply_text(
            text=response_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(website_button)
        )


# ================= MAIN =================

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Sunday Auto Offer
        app.job_queue.run_daily(
            sunday_offer,
            time=datetime.time(hour=12, minute=0),
            days=(6,)
        )

        print("Bot is LIVE 🔥")
        app.run_polling(drop_pending_updates=True)
