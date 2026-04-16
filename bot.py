import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# ВСТАВ СВІЙ ТОКЕН ТА ПОСИЛАННЯ
TOKEN = "ТВІЙ_ТОКЕН_ТУТ"
URL = "https://andrijma413-create.github.io/-treading-app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Головне меню з кнопкою Mini App
def main_kb():
    kb = [
        [KeyboardButton(text="🚀 Відкрити термінал", web_app=WebAppInfo(url=URL))]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Натисни кнопку нижче, щоб вибрати пару:", reply_markup=main_kb())

# ПРИЙОМ ДАНИХ З MINI APP (вибір пари)
@dp.message(F.web_app_data)
async def web_app_receive(message: types.Message):
    pair = message.web_app_data.data
    
    # Кнопки вибору часу
    time_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1 хв"), KeyboardButton(text="5 хв")],
        [KeyboardButton(text="15 хв"), KeyboardButton(text="30 хв")]
    ], resize_keyboard=True)
    
    await message.answer(f"✅ Ви вибрали пару: {pair}\nТепер обери час експірації:", reply_markup=time_kb)

# ОБРОБКА ВИБОРУ ЧАСУ
@dp.message(F.text.in_(["1 хв", "5 хв", "15 хв", "30 хв"]))
async def give_signal(message: types.Message):
    await message.answer(f"⏳ Аналізую ринок на {message.text}...")
    await asyncio.sleep(2) # Імітація аналізу
    await message.answer("📉 СИГНАЛ: ВНИЗ (SELL) 🔴")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
