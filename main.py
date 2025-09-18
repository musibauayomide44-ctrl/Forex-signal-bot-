import telebot
import yfinance as yf
import ta

# 🔑 Your bot token
BOT_TOKEN = "8208622897:AAH23ayuurLtjjUWBiFIb8HpzsppERpAWzk"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔍 Function to get signals
def get_signal(symbol, interval):
    try:
        data = yf.download(symbol, period="1d", interval=interval)
        close = data["Close"].squeeze()   # 🔥 FIXED: force 1D array

        # RSI
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

        # MACD
        macd = ta.trend.MACD(close)
        macd_val = macd.macd().iloc[-1]
        signal_val = macd.macd_signal().iloc[-1]

        # Trading logic
        if rsi < 30 and macd_val > signal_val:
            return f"{symbol} ({interval}) → BUY 📈\nRSI: {rsi:.2f}\nMACD: Bullish crossover ✅"
        elif rsi > 70 and macd_val < signal_val:
            return f"{symbol} ({interval}) → SELL 📉\nRSI: {rsi:.2f}\nMACD: Bearish crossover ❌"
        else:
            return f"{symbol} ({interval}) → No trade ⚠️\nRSI: {rsi:.2f}\nMACD: Neutral"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📊 Welcome to your Forex Signal Bot!\n\nUse /signal to request live signals.")

# Signal command
@bot.message_handler(commands=['signal'])
def signal(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("EURUSD 1m", "EURUSD 5m", "EURUSD 15m")
    markup.add("GBPUSD 1m", "GBPUSD 5m", "GBPUSD 15m")
    markup.add("AUDUSD 1m", "AUDUSD 5m", "AUDUSD 15m")
    bot.send_message(message.chat.id, "⏰ Choose a pair and timeframe:", reply_markup=markup)

# Handle chosen pair + timeframe
@bot.message_handler(func=lambda msg: True)
def handle_signal_request(message):
    try:
        text = message.text.split()
        if len(text) == 2:
            symbol, interval = text
            if symbol == "EURUSD":
                ticker = "EURUSD=X"
            elif symbol == "GBPUSD":
                ticker = "GBPUSD=X"
            elif symbol == "AUDUSD":
                ticker = "AUDUSD=X"
            else:
                bot.reply_to(message, "⚠️ Invalid pair.")
                return

            result = get_signal(ticker, interval)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, "⚠️ Please choose a valid option.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("🤖 Bot is running...")
bot.infinity_polling()
