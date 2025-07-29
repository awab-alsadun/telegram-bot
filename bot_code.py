from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os

BOT_TOKEN = '7931007070:AAGnswiBQ2ewPLmp5SSGp2cHlAx1QNC4E-Y'

# Categories
CATEGORIES = {
    "yassir": "Yassir Al-Dosri",
    "anas": "Anas Al-3made",
    "lhedaan": "Mohamed Al-Lhedaan",
    "others": "Others"
}

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
for folder in CATEGORIES:
    os.makedirs(os.path.join(DOWNLOADS_DIR, folder), exist_ok=True)


# /sheikh command
async def sheikh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"cat_{key}")]
        for key, name in CATEGORIES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📚 Choose a sheikh:", reply_markup=reply_markup)


# /download command
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /download <tiktok_url>")
        return

    url = context.args[0].strip()
    if "tiktok.com" not in url:
        await update.message.reply_text("⚠️ Please provide a valid TikTok link.")
        return

    # Show category selection for download
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"dl_{key}_{url}")]
        for key, name in CATEGORIES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 Choose folder to download to:", reply_markup=reply_markup)


# Download function
def download_tiktok_video(url, category):
    folder_path = os.path.join(DOWNLOADS_DIR, category)
    ydl_opts = {
        'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4]/best',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.basename(ydl.prepare_filename(info))


# Handle all button clicks
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    print(f"DEBUG: Button clicked with data: {query.data}")

    # Handle sheikh category selection
    if query.data.startswith("cat_"):
        cat_key = query.data.replace("cat_", "")
        folder_path = os.path.join(DOWNLOADS_DIR, cat_key)

        if not os.path.exists(folder_path):
            await query.edit_message_text("⚠️ Folder not found.")
            return

        files = [f for f in os.listdir(folder_path) if f.endswith(('.mp3', '.mp4', '.m4a'))]

        if not files:
            await query.edit_message_text(f"📂 {CATEGORIES[cat_key]} folder is empty.")
            return

        # Create buttons for each file
        keyboard = [
            [InlineKeyboardButton(f[:30] + "..." if len(f) > 30 else f, callback_data=f"play_{cat_key}_{f}")]
            for f in files
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"🎬 {CATEGORIES[cat_key]} files:", reply_markup=reply_markup)

    # Handle file playback
    elif query.data.startswith("play_"):
        parts = query.data.split("_", 2)
        cat_key = parts[1]
        filename = parts[2]
        file_path = os.path.join(DOWNLOADS_DIR, cat_key, filename)

        if os.path.exists(file_path):
            await query.edit_message_text(f"🎵 Playing: {filename}")
            with open(file_path, 'rb') as f:
                if filename.endswith('.mp4'):
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f)
                else:
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f)
        else:
            await query.edit_message_text("⚠️ File not found.")

    # Handle download
    elif query.data.startswith("dl_"):
        parts = query.data.split("_", 2)
        cat_key = parts[1]
        url = parts[2]

        await query.edit_message_text(f"⏳ Downloading to {CATEGORIES[cat_key]}...")
        try:
            filename = download_tiktok_video(url, cat_key)
            await query.edit_message_text(f"✅ Downloaded: {filename}")
        except Exception as e:
            await query.edit_message_text(f"❌ Download failed: {str(e)}")

    # Handle back button
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"cat_{key}")]
            for key, name in CATEGORIES.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📚 Choose a sheikh:", reply_markup=reply_markup)


# Setup bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("sheikh", sheikh))
app.add_handler(CommandHandler("download", download))
app.add_handler(CallbackQueryHandler(handle_callback))

print("✅ Bot running...")
app.run_polling()