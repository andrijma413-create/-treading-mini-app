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
TOKEN = "8595206641:AAHkbbTLEk_DzLod554rDSYun0E0TuW5kkg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Мапінг для Yahoo Finance (Тікери)
TICKERS = {
    "Apple": "AAPL", 
    "Tesla": "TSLA", 
    "Alibaba": "BABA", 
    "McDonald's": "MCD",
    "AUD/NZD": "AUDNZD=X", 
    "AUD/CHF": "AUDCHF=X", 
    "AED/CNY": "AEDCNY=X"
}

# --- ЛОГІКА РЕАЛЬНОГО АНАЛІЗУ ---
def perform_real_analysis(asset):
    ticker_sym = TICKERS.get(asset, "EURUSD=X")
    try:
        # Отримуємо дані за останні 2 дні з інтервалом 15 хв
        df = yf.download(ticker_sym, period="2d", interval="15m", progress=False)
        
        if df.empty:
            return "❌ Дані недоступні", "Не вдалося отримати котирування з ринку."

        # Технічні індикатори
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA'] = ta.ema(df['Close'], length=20)
        
        last_rsi = df['RSI'].iloc[-1]
        last_close = df['Close'].iloc[-1]
        last_ema = df['EMA'].iloc[-1]
        
        # Аналіз показників
        if last_rsi < 30:
            return "📈 ВГОРУ (CALL)", f"RSI низький ({round(last_rsi, 1)}). Актив сильно перепроданий, висока ймовірність розвороту вгору."
        elif last_rsi > 70:
            return "📉 ВНИЗ (PUT)", f"RSI високий ({round(last_rsi, 1)}). Актив перекуплений, очікується корекція вниз."
        elif last_close > last_ema:
            return "📈 ВГОРУ (CALL)", "Ціна впевнено тримається вище ковзної середньої EMA(20). Тренд висхідний."
        else:
            return "📉 ВНИЗ (PUT)", "Ціна знаходиться нижче лінії EMA(20). Переважає ведмежий тренд."
    except Exception as e:
        return "⚠️ Помилка аналізу", str(e)

# --- КЛАВІАТУРИ ---
def main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📈 Акції", callback_data="cat_stocks"))
    builder.row(types.InlineKeyboardButton(text="💱 Валюта", callback_data="cat_forex"))
    return builder.as_markup()

def asset_kb(cat):
    builder = InlineKeyboardBuilder()
    if cat == "cat_forex":
        assets = ["AUD/NZD", "AUD/CHF", "AED/CNY"]
    else:
        assets = ["Apple", "Tesla", "Alibaba", "McDonald's"]
    
    for a in assets:
        builder.row(types.InlineKeyboardButton(text=a, callback_data=f"asset_{a}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return builder.as_markup()

def trade_kb(asset):
    builder = InlineKeyboardBuilder()
    # Справжній графік через WebApp від TradingView
    symbol = TICKERS.get(asset, "EURUSD").replace("=X", "")
    builder.row(types.InlineKeyboardButton(
        text="📊 Відкрити LIVE Графік", 
        web_app=WebAppInfo(url=f"https://s.tradingview.com/widgetembed/?symbol={symbol}&interval=1&theme=dark")
    ))
    builder.row(types.InlineKeyboardButton(text="🔍 ПРОВЕСТИ АНАЛІЗ", callback_data=f"calc_{asset}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ До вибору", callback_data="back"))
    return builder.as_markup()

# --- ОБРОБНИКИ (HANDLERS) ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("💎 **Торговий Термінал v3.0**\n\nВітаю! Оберіть категорію активів для початку роботи:", 
                         reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("cat_"))
async def select_cat(callback: types.CallbackQuery):
    await callback.message.edit_text("Оберіть потрібний актив:", reply_markup=asset_kb(callback.data))

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("Оберіть ринок:", reply_markup=main_kb())

@dp.callback_query(F.data.startswith("asset_"))
async def select_asset(callback: types.CallbackQuery):
    asset = callback.data.split("_")[1]
    await callback.message.answer(
        f"💹 Обрано актив: **{asset}**\n\nНижче ви можете переглянути графік у реальному часі або запустити технічний аналіз ринку.", 
        reply_markup=trade_kb(asset), 
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("calc_"))
async def run_analysis(callback: types.CallbackQuery):
    asset = callback.data.split("_")[1]
    await callback.answer("Зчитую технічні індикатори...")
    
    # Виконуємо реальний аналіз
    direction, reason = perform_real_analysis(asset)
    
    await callback.message.answer(
        f"✅ **РЕЗУЛЬТАТ АНАЛІЗУ: {asset}**\n\n"
        f"Рекомендація: **{direction}**\n"
        f"🧠 **Аналіз:** {reason}\n\n"
        f"_Дані отримані в реальному часі через Yahoo Finance API
  
