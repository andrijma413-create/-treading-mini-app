import os
import asyncio
import random
import yfinance as yf
import pandas_ta as ta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

# --- НАЛАШТУВАННЯ ---
# Встав свій токен сюди (отримай у @BotFather)
TOKEN = "ТВІЙ_ТОКЕН_ТУТ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Мапінг для Yahoo Finance
TICKERS = {
    "Apple": "AAPL", "Tesla": "TSLA", "Alibaba": "BABA", "McDonald's": "MCD",
    "AUD/NZD": "AUDNZD=X", "AUD/CHF": "AUDCHF=X", "AED/CNY": "AEDCNY=X"
}

# --- ЛОГІКА АНАЛІЗУ ---
def perform_real_analysis(asset):
    ticker = TICKERS.get(asset, "EURUSD=X")
    # Отримуємо дані за останній день з інтервалом 15 хв
    df = yf.download(ticker, period="2d", interval="15m", progress=False)
    
    if df.empty:
        return "❌ Дані недоступні", "Спробуйте пізніше або інший актив."

    # Розрахунок індикаторів
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA'] = ta.ema(df['Close'], length=20)
    
    last_rsi = df['RSI'].iloc[-1]
    last_close = df['Close'].iloc[-1]
    last_ema = df['EMA'].iloc[-1]
    
    if last_rsi < 30:
        return "📈 ВГОРУ (CALL)", f"RSI низький ({round(last_rsi, 1)}). Актив перепроданий, очікується ріст."
    elif last_rsi > 70:
        return "📉 ВНИЗ (PUT)", f"RSI високий ({round(last_rsi, 1)}). Актив перекуплений, очікується падіння."
    elif last_close > last_ema:
        return "📈 ВГОРУ (CALL)", "Ціна вище EMA(20). Тренд стабільно висхідний."
    else:
        return "📉 ВНИЗ (PUT)", "Ціна нижче EMA(20). Тренд стабільно низхідний."

# --- КЛАВІАТУРИ ---
def main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📈 Акції", callback_data="cat_stocks"))
    builder.row(types.InlineKeyboardButton(text="💱 Валюта", callback_data="cat_forex"))
    return builder.as_markup()

def asset_kb(cat):
    builder = InlineKeyboardBuilder()
    assets = ["AUD/NZD", "AUD/CHF", "AED/CNY"] if cat == "cat_forex" else ["Apple", "Tesla", "Alibaba", "McDonald's"]
    for a in assets:
        builder.row(types.InlineKeyboardButton(text=a, callback_data=f"asset_{a}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return builder.as_markup()

def trade_kb(asset):
    builder = InlineKeyboardBuilder()
    # Живий графік через WebApp
    symbol = TICKERS.get(asset).replace("=X", "")
    builder.row(types.InlineKeyboardButton(
        text="📊 Відкрити LIVE Графік", 
        web_app=WebAppInfo(url=f"https://s.tradingview.com/widgetembed/?symbol={symbol}&interval=1&theme=dark")
    ))
    builder.row(types.InlineKeyboardButton(text="🔍 ПРОВЕСТИ АНАЛІЗ", callback_data=f"calc_{asset}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ До вибору", callback_data="back"))
    return builder.as_markup()

# --- ОБРОБНИКИ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🏦 **Trading Terminal v3.0**\nОберіть ринок для торгівлі:", reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("cat_"))
async def select_cat(callback: types.CallbackQuery):
    await callback.message.edit_text("Оберіть актив:", reply_markup=asset_kb(callback.data))

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("Оберіть ринок:", reply_markup=main_kb())

@dp.callback_query(F.data.startswith("asset_"))
async def select_asset(callback: types.CallbackQuery):
    asset = callback.data.split("_")[1]
    await callback.message.answer(f"💹 Актив: **{asset}**\nТаймфрейм: 1-10 хв\n\nВідкрийте графік або запустіть ШІ-аналіз:", 
                                  reply_markup=trade_kb(asset), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("calc_"))
async def run_analysis(callback: types.CallbackQuery):
    asset = callback.data.split("_")[1]
    await callback.answer("Зчитую технічні дані...")
    
    direction, reason = perform_real_analysis(asset)
    
    await callback.message.answer(
        f"✅ **РЕЗУЛЬТАТ АНАЛІЗУ: {asset}**\n\nПрогноз: **{direction}**\n🧠 **Чому:** {reason}",
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
