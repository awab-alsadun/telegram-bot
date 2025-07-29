from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import asyncio

TOKEN = "7931007070:AAGnswiBQ2ewPLmp5SSGp2cHlAx1QNC4E-Y"  # Replace with your real token
bot = Bot(token=TOKEN)
dp = Dispatcher()

choice1 = "tea"
choice2 = "coffee"  # Fixed spelling
button1 = InlineKeyboardButton(text=choice1, callback_data="tea_like")
button2 = InlineKeyboardButton(text=choice2, callback_data="coffee_like")  # Fixed spelling
keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])


@dp.message(Command("like"))
async def like_handler(message: Message):
    await message.reply("What drink do you like?", reply_markup=keyboard_inline)


@dp.callback_query(lambda c: c.data in ["tea_like", "coffee_like"])  # Removed extra space
async def response(call: types.CallbackQuery):
    if call.data == "tea_like":
        await call.message.answer("I like " + choice1 + " too")
    elif call.data == "coffee_like":  # Changed to elif for better practice
        await call.message.answer("I like " + choice2 + " too")

    # Answer the callback query to remove the loading state
    await call.answer()


async def main():
    await dp.start_polling(bot)  # Pass bot instance, not token


if __name__ == "__main__":
    asyncio.run(main())