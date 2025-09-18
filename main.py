import telebot
import yfinance as yf
import ta
import pandas as pd

# 🔑 Your bot token
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiFIb8HpzsppERpAWzk"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔍 Function to get predictive signal
def get_signal(symbol, interval, entry_minutes):
    try:
        data = yf.download(symbol, period="1d", interval=interval)
        close = data["Close"]

        # Indicators
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Moving Averages
        ma_fast = close.rolling(window=9).mean().iloc[-1]
        ma_slow = close.rolling(window=21).mean().iloc[-1]

        # Candle pattern (simple check: last two candles)
        last = close.iloc[-1]
        prev = close.iloc[-2]
        candle = "Bullish engulfing 🟢" if last > prev else "Bearish engulfing 🔴"

        # Predictive logic
        if rsi < 30 and macd_val > signal_val and ma_fast > ma_slow:
            return f"{symbol} → BUY 📈\nEntry: in {entry_minutes}m\nRSI: {rsi:.2f}\nMACD: Bullish ✅\nMA: 9 > 21 ✅\nCandle: {candle}"
        elif rsi > 70 and macd_val < signal_val and ma_fast < ma_slow:
            return f"{symbol} → SELL 📉\nEntry: in {entry_minutes}m\nRSI: {rsi:.2f}\nMACD: Bearish ❌\nMA: 9 < 21 ❌\nCandle: {candle}"
        else:
            return f"{symbol} → No strong signal ⚠️\nEntry: in {entry_minutes}m\nRSI: {rsi:.2f}\nMACD: Neutral\nMA Trend: Mixed\nCandle: {candle}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📊 Welcome to your Forex Signal Bot!\n\nUse /signal to request predictive signals.")

# /signal command
@bot.message_handler(commands=['signal'])
def signal(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("EURUSD", "GBPUSD", "AUDUSD")
    markup.add("USDJPY", "XAUUSD")
    bot.send_message(message.chat.id, "💱 Choose a pair:", reply_markup=markup)

# Handle pair selection
@bot.message_handler(func=lambda msg: msg.text in ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "XAUUSD"])
def choose_time(message):
    symbol = message.text
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("30s", "1m", "5m")
    bot.send_message(message.chat.id, f"⏳ Choose entry time for {symbol}:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_request(symbol, msg))

# Handle final signal request
def handle_request(symbol, message):
    entry_time = message.text
    if entry_time == "30s":
        interval = "1m"
        entry_minutes = 1
    elif entry_time == "1m":
        interval = "1m"
        entry_minutes = 1
    elif entry_time == "5m":
        interval = "5m"
        entry_minutes = 5
    else:
        bot.reply_to(message, "⚠️ Invalid time.")
        return

    # Map symbols to Yahoo tickers
    mapping = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "AUDUSD": "AUDUSD=X",
        "USDJPY": "JPY=X",
        "XAUUSD": "XAUUSD=X"
    }

    result = get_signal(mapping[symbol], interval, entry_minutes)
    bot.send_message(message.chat.id, result)

print("🤖 Bot is running...")
bot.infinity_polling()
