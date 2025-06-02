from flask import Flask, render_template, request
import requests
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("TWELVEDATA_API_KEY")
app = Flask(__name__)

def get_forex_data(symbol, interval, api_key, outputsize=100):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": api_key,
        "format": "JSON",
        "outputsize": outputsize
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "values" not in data:
        return None, data.get("message", "Error al obtener datos.")
    df = pd.DataFrame(data["values"])
    df = df.iloc[::-1]
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df, None

def calculate_indicators(df):
    df["EMA20"] = ta.ema(df["close"], length=20)
    df["EMA50"] = ta.ema(df["close"], length=50)
    df["RSI"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"])
    if macd is not None:
        df["MACD"] = macd["MACD_12_26_9"]
        df["MACDh"] = macd["MACDh_12_26_9"]
    else:
        df["MACD"] = df["MACDh"] = None
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    signal = "HOLD"

    # Condición BUY
    if (
        latest["EMA20"] > latest["EMA50"] and
        prev["EMA20"] <= prev["EMA50"] and  # cruce reciente al alza
        prev["RSI"] < 30 and latest["RSI"] > 30 and  # RSI saliendo de sobreventa
        latest["close"] > latest["open"] and  # vela verde
        latest["MACDh"] > prev["MACDh"]  # impulso alcista creciente
    ):
        signal = "BUY"

    # Condición SELL
    elif (
        latest["EMA20"] < latest["EMA50"] and
        prev["EMA20"] >= prev["EMA50"] and  # cruce reciente a la baja
        prev["RSI"] > 70 and latest["RSI"] < 70 and  # RSI saliendo de sobrecompra
        latest["close"] < latest["open"] and  # vela roja
        latest["MACDh"] < prev["MACDh"]  # impulso bajista creciente
    ):
        signal = "SELL"

    return signal

def get_price_and_change(symbol, api_key):
    url = "https://api.twelvedata.com/quote"
    params = {"symbol": symbol, "apikey": api_key}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("status") == "error":
            return None
        return {
            "symbol": symbol,
            "price": float(data.get("close", 0)),
            "change": float(data.get("percent_change", 0))
        }
    except Exception:
        return None

def safe_format(value, fmt=".4f"):
    try:
        return format(float(value), fmt)
    except:
        return "N/A"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    PAIRS = ["EUR/USD", "USD/JPY", "GBP/JPY"]
    ticker_data = []
    for pair in PAIRS:
        data = get_price_and_change(pair, API_KEY)
        if data is not None:
            ticker_data.append(data)

    if request.method == "POST":
        symbol = request.form.get("symbol", "EUR/USD").upper()
        interval = request.form.get("interval", "15min")
        df, error = get_forex_data(symbol, interval, API_KEY)
        if df is not None:
            df = calculate_indicators(df)
            signal = generate_signal(df)
            last_close = df["close"].iloc[-1]
            latest = df.iloc[-1]
            result = {
                "symbol": symbol.replace("/", ""),
                "interval": interval,
                "last_close": safe_format(last_close),
                "signal": signal,
                "rsi": safe_format(latest["RSI"], ".2f"),
                "macd": safe_format(latest["MACD"], ".4f"),
                "macdh": safe_format(latest["MACDh"], ".4f")
            }
    return render_template("index.html", result=result, error=error, ticker_data=ticker_data)

if __name__ == "__main__":
    app.run(debug=True)
