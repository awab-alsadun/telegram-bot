from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.filters import Command
from yt_dlp import YoutubeDL
import asyncio
import os

BOT_TOKEN = '7931007070:AAGnswiBQ2ewPLmp5SSGp2cHlAx1QNC4E-Y'  # Replace with your real token
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ensure category folders exist
CATEGORIES = {
    "yassir": "Yassir Al-Dosri",
    "anas": "Anas Al-3made",
    "lhedaan": "Mohamed Al-Lhedaan",
    "others": "Others"
}

# Store file lists temporarily to avoid long callback data
file_cache = {}

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
for folder in CATEGORIES:
    os.makedirs(os.path.join(DOWNLOADS_DIR, folder), exist_ok=True)


# /sheikh command - Show categories
@dp.message(Command("sheikh"))
async def sheikh_handler(message: Message):
    # Create inline keyboard with categories
    buttons = []
    for key, name in CATEGORIES.items():
        button = InlineKeyboardButton(text=name, callback_data=f"cat_{key}")
        buttons.append([button])  # Each button on its own row

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply("📚 Choose a sheikh category:", reply_markup=keyboard)


# Handle category selection and file selection
@dp.callback_query(lambda c: c.data.startswith("cat_") or c.data.startswith("file_") or c.data == "back_to_categories")
async def handle_callback(call: CallbackQuery):
    print(f"🔁 Button clicked with data: {call.data}")

    if call.data.startswith("cat_"):
        # Handle category selection
        cat_key = call.data.replace("cat_", "")
        folder_path = os.path.join(DOWNLOADS_DIR, cat_key)

        if not os.path.exists(folder_path):
            await call.message.edit_text("⚠️ Category folder not found.")
            await call.answer()
            return

        files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.mp3', '.wav', '.m4a'))]
        if not files:
            await call.message.edit_text(f"📂 *{CATEGORIES[cat_key]}* folder is empty.", parse_mode="Markdown")
            await call.answer()
            return

        # Store files in cache with category key
        cache_key = f"{call.from_user.id}_{cat_key}"
        file_cache[cache_key] = files

        # Create buttons for each file using index
        file_buttons = []
        for i, file in enumerate(files[:10]):  # Limit to first 10 files
            # Remove file extension for cleaner display
            display_name = os.path.splitext(file)[0]
            if len(display_name) > 30:  # Truncate long names
                display_name = display_name[:27] + "..."
            button = InlineKeyboardButton(
                text=display_name,
                callback_data=f"file_{cat_key}_{i}"  # Use index instead of filename
            )
            file_buttons.append([button])

        # Add back button
        back_button = InlineKeyboardButton(text="🔙 Back", callback_data="back_to_categories")
        file_buttons.append([back_button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=file_buttons)
        await call.message.edit_text(
            f"🎬 *{CATEGORIES[cat_key]}* Recitations:\n\nChoose a recitation to play:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif call.data.startswith("file_"):
        # Handle file selection
        parts = call.data.replace("file_", "").split("_")
        cat_key = parts[0]
        file_index = int(parts[1])

        # Get filename from cache
        cache_key = f"{call.from_user.id}_{cat_key}"
        if cache_key not in file_cache or file_index >= len(file_cache[cache_key]):
            await call.message.edit_text("⚠️ File not found in cache.")
            await call.answer()
            return

        filename = file_cache[cache_key][file_index]
        file_path = os.path.join(DOWNLOADS_DIR, cat_key, filename)

        if os.path.exists(file_path):
            await call.message.edit_text(f"🎵 Playing: *{os.path.splitext(filename)[0]}*", parse_mode="Markdown")

            # Send the audio/video file using FSInputFile
            try:
                file_input = FSInputFile(file_path)
                if filename.endswith(('.mp3', '.wav', '.m4a')):
                    await call.message.answer_audio(file_input)
                else:
                    await call.message.answer_video(file_input)
            except Exception as e:
                await call.message.answer(f"❌ Error playing file: {e}")
        else:
            await call.message.edit_text("⚠️ File not found.")

    elif call.data == "back_to_categories":
        # Handle back button - show categories again
        buttons = []
        for key, name in CATEGORIES.items():
            button = InlineKeyboardButton(text=name, callback_data=f"cat_{key}")
            buttons.append([button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await call.message.edit_text("📚 Choose a sheikh category:", reply_markup=keyboard)

    await call.answer()


# /download command
def download_tiktok_video(url, category_folder):
    folder_path = os.path.join(DOWNLOADS_DIR, category_folder)
    ydl_opts = {
        'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
        'format': 'mp4/best',  # Try mp4 first, then best available
        'extract_flat': False,
        'no_warnings': False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.abspath(ydl.prepare_filename(info))


@dp.message(Command("download"))
async def download_handler(message: Message):
    # Parse command arguments
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if not args:
        await message.reply("⚠️ Please provide a TikTok link.\nUsage:\n/download https://tiktok.com/...")
        return

    url = args[0].strip()
    if "tiktok.com" not in url:
        await message.reply("⚠️ That doesn't look like a valid TikTok link.")
        return

    # Show category selection for download
    buttons = []
    for key, name in CATEGORIES.items():
        button = InlineKeyboardButton(text=name, callback_data=f"download_{key}_{url}")
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply("📂 Choose which sheikh folder to save to:", reply_markup=keyboard)


# Handle download category selection
@dp.callback_query(lambda c: c.data.startswith("download_"))
async def handle_download_callback(call: CallbackQuery):
    parts = call.data.split("_", 2)
    cat_key = parts[1]
    url = parts[2]

    await call.message.edit_text("⏳ Downloading video...")

    try:
        video_path = download_tiktok_video(url, cat_key)
        filename = os.path.basename(video_path)
        await call.message.edit_text(
            f"✅ Video downloaded successfully!\n"
            f"📁 Saved to: *{CATEGORIES[cat_key]}*\n"
            f"📄 File: {filename}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await call.message.edit_text(f"❌ Error during download:\n{str(e)}")

    await call.answer()


# Start command for help
@dp.message(Command("start"))
async def start_handler(message: Message):
    help_text = """
🎵 *Sheikh Recitation Bot*

*Commands:*
• `/sheikh` - Browse and play recitations by category
• `/download [tiktok_url]` - Download a TikTok video to a category folder

*Categories:*
• Yassir Al-Dosri
• Anas Al-3made  
• Mohamed Al-Lhedaan
• Others

Use `/sheikh` to browse existing recitations or `/download` to add new ones!
    """
    await message.reply(help_text, parse_mode="Markdown")


async def main():
    print("✅ Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())