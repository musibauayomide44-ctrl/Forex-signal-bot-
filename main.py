import telebot
import yfinance as yf
import ta
import pandas as pd

# === Bot Token ===
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiF"
bot = telebot.TeleBot(BOT_TOKEN)

# === Watchlist (main pairs only) ===
WATCHLIST = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "XAUUSD=X"]

# === Signal Generator ===
def get_signal(symbol):
    try:
        # Fetch last 200 candles (1m timeframe)
        data = yf.download(symbol, period="1d", interval="1m")

        if data.empty:
            return f"⚠️ No data for {symbol}. Market may be closed."

        close = data["Close"].dropna()

        # RSI
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

        # MACD
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Moving Averages (for trend confirmation)
        sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator().iloc[-1]

        # Candle pattern (very simple check: bullish/bearish close)
        last_candle = data.iloc[-1]
        candle_trend = "Bullish" if last_candle["Close"] > last_candle["Open"] else "Bearish"

        # === Prediction Logic ===
        if rsi < 30 and macd_val > signal_val and sma20 > sma50 and candle_trend == "Bullish":
            return f"{symbol} → 📈 BUY (next 1m)\nRSI={rsi:.2f}, MACD bullish, Trend=UP"
        elif rsi > 70 and macd_val < signal_val and sma20 < sma50 and candle_trend == "Bearish":
            return f"{symbol} → 📉 SELL (next 1m)\nRSI={rsi:.2f}, MACD bearish, Trend=DOWN"
        else:
            return f"{symbol} → ⏸️ NO CLEAR ENTRY\nRSI={rsi:.2f}, Trend={candle_trend}"
    except Exception as e:
        return f"⚠️ Error for {symbol}: {str(e)}"

# === Telegram Commands ===
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "📊 Welcome to MANBOY Signal Bot!\nUse /signal to get predictive entries.")

@bot.message_handler(commands=["signal"])
def signal(message):
    bot.send_message(message.chat.id, "🔍 Checking pairs, please wait...")
    results = []
    for pair in WATCHLIST:
        results.append(get_signal(pair))
    bot.send_message(message.chat.id, "\n\n".join(results))

# === Run Bot ===
print("✅ Bot is running...")
bot.polling(none_stop=True)
