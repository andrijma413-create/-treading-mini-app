import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ТВІЙ ТОКЕН ВЖЕ ВСТАВЛЕНО
TOKEN = "8708611740:AAFqaQIm-mz_bEuOKMmngxEk7PXaGwzuh-E" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Створюємо сітку кнопок для вибору валютних пар (як на відео)
def pairs_keyboard():
    kb = [
        [KeyboardButton(text="EUR/CAD OTC"), KeyboardButton(text="GBP/JPY OTC")],
        [KeyboardButton(text="AUD/JPY OTC"), KeyboardButton(text="NZD/JPY OTC")],
        [KeyboardButton(text="USD/JPY OTC"), KeyboardButton(text="USD/CHF OTC")],
        [KeyboardButton(text="APPLE OTC"), KeyboardButton(text="BITCOIN OTC")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Кнопки для вибору часу експірації
def time_keyboard():
    kb = [
        [KeyboardButton(text="1 хв"), KeyboardButton(text="5 хв")],
        [KeyboardButton(text="15 хв"), KeyboardButton(text="30 хв")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📊 **ВІТАЮ В СИГНАЛЬНОМУ БОТІ!**\n\nОберіть валютну пару для аналізу:", 
                         reply_markup=pairs_keyboard(), parse_mode="Markdown")

# Обробка вибору пари
@dp.message(F.text.contains("OTC") | F.text.contains("BITCOIN"))
async def select_time(message: types.Message):
    await message.answer(f"✅ Актив **{message.text}** обрано.\nВкажіть час експірації:", 
                         reply_markup=time_keyboard(), parse_mode="Markdown")

# Обробка вибору часу та видача сигналу
@dp.message(F.text.in_(["1 хв", "5 хв", "15 хв", "30 хв"]))
async def send_signal(message: types.Message):
    wait_msg = await message.answer("🔍 **Аналізуємо ринок за допомогою AI...**")
    await asyncio.sleep(2) # Імітація роботи
    
    # Рандомний вибір сигналу (Вверх або Вниз)
    direction = random.choice(["ВВЕРХ 🟢", "ВНИЗ 🔴"])
    # Вибір картинки залежно від сигналу
    img = "https://i.imgur.com/8nS6SjC.png" if "ВВЕРХ" in direction else "https://i.imgur.com/kO8jXzS.png"

    # Видаляємо повідомлення "Аналізуємо..."
    await bot.delete_message(message.chat.id, wait_msg.message_id)
    
    # Відправляємо фінальний сигнал з фото
    await message.answer_photo(
        photo=img,
        caption=(f"📈 **НОВИЙ СИГНАЛ!**\n\n"
                 f"📍 Актив: Стрілка на графіку\n"
                 f"↕️ Напрямок: **{direction}**\n"
                 f"⏳ Час: **{message.text}**\n"
                 f"🚀 Прохідність: **{random.randint(88, 97)}%**\n\n"
                 f"Оберіть наступну пару для аналізу:"),
        reply_markup=pairs_keyboard(),
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
