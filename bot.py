import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8708611740:AAFqaQIm-mz_bEuOKMmngxEk7PXaGwzuh-E"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавіатура вибору мови
def lang_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🇺🇦 Українська"), KeyboardButton(text="🇬🇧 English")],
        [KeyboardButton(text="🇷🇺 Русский")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    # Саме ця команда видає вибір мови
    await message.answer("🌍 Будь ласка, оберіть мову / Please choose a language:", reply_markup=lang_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
