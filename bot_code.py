from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = '7931007070:AAGnswiBQ2ewPLmp5SSGp2cHlAx1QNC4E-Y'  # Replace this with your BotFather token

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

def download_tiktok_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.abspath(ydl.prepare_filename(info))

# /download command
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a TikTok link.\nUsage:\n/download https://...")
        return

    url = context.args[0].strip()
    if "tiktok.com" not in url:
        await update.message.reply_text("⚠️ That doesn't look like a valid TikTok link.")
        return

    await update.message.reply_text("⏳ Downloading...")
    try:
        video_path = download_tiktok_video(url)
        await update.message.reply_text(f"✅ Video downloaded locally:\n{video_path}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error during download:\n{e}")

# Set up the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("download", download))

print("✅ Bot is running...")
app.run_polling()
