import telebot
import yfinance as yf
import ta
import pandas as pd

# 🔑 Your bot token
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiFIb8HpzsppERpAWzk"
bot = telebot.TeleBot(BOT_TOKEN)

# 📊 Get signal function
def get_signal(symbol, interval, future_minutes=1):
    try:
        data = yf.download(symbol, period="1d", interval=interval)

        # ✅ Prevent errors if no data
        if data.empty or "Close" not in data:
            return f"⚠️ No data for {symbol} ({interval}). Market may be closed."

        close = data["Close"]

        # ✅ Make sure at least 30 candles exist
        if len(close) < 30:
            return f"⚠️ Not enough data for {symbol} ({interval})."

        # RSI
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

        # MACD
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Moving Average crossover
        ma_fast = close.rolling(window=9).mean().iloc[-1]
        ma_slow = close.rolling(window=21).mean().iloc[-1]

        # 🔮 Predictive logic
        if rsi < 30 and macd_val > signal_val and ma_fast > ma_slow:
            return f"{symbol} ({interval}) → BUY 📈\nRSI: {rsi:.2f}\nMACD: Bullish ✅\nMA: Fast > Slow\nEntry: In next {future_minutes}m"
        elif rsi > 70 and macd_val < signal_val and ma_fast < ma_slow:
            return f"{symbol} ({interval}) → SELL 📉\nRSI: {rsi:.2f}\nMACD: Bearish ❌\nMA: Fast < Slow\nEntry: In next {future_minutes}m"
        else:
            return f"{symbol} ({interval}) → No trade ⚠️\nRSI: {rsi:.2f}\nMACD: Neutral\nMA: Flat"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🚀 Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📊 Welcome to Forex Signal Bot!\n\nUse /signal to request live signals.")

# 🎯 Signal request
@bot.message_handler(commands=['signal'])
def signal(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("EURUSD 1m", "EURUSD 5m", "EURUSD 15m")
    markup.add("GBPUSD 1m", "AUDUSD 1m", "USDJPY 1m", "XAUUSD 1m")
    bot.send_message(message.chat.id, "📌 Choose a pair & timeframe:", reply_markup=markup)

# 🖲 Handle selection
@bot.message_handler(func=lambda msg: True)
def handle_signal_request(message):
    try:
        text = message.text.split()
        if len(text) == 2:
            symbol, interval = text

            mapping = {
                "EURUSD": "EURUSD=X",
                "GBPUSD": "GBPUSD=X",
                "AUDUSD": "AUDUSD=X",
                "USDJPY": "JPY=X",
                "XAUUSD": "XAUUSD=X"
            }

            if symbol not in mapping:
                bot.reply_to(message, "⚠️ Invalid pair.")
                return

            ticker = mapping[symbol]
            result = get_signal(ticker, interval, future_minutes=1)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, "⚠️ Please choose a valid option.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("🤖 Bot is running...")
bot.infinity_polling()
