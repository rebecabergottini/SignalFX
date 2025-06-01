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
        return None, data.get("message", "Error fetching data")
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
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    if (latest.EMA20 > latest.EMA50) and (previous.RSI < 30) and (latest.RSI > 30):
        return "BUY"
    elif (latest.EMA20 < latest.EMA50) and (previous.RSI > 70) and (latest.RSI < 70):
        return "SELL"
    else:
        return "HOLD"

def get_price_and_change(symbol, api_key):
    api_symbol = symbol 
    
    url = "https://api.twelvedata.com/quote"
    params = {
        "symbol": api_symbol,
        "apikey": api_key
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        print(f"API Response for {api_symbol}: {data}")
        
        if data.get("status") == "error":
            print(f"API error for {api_symbol}: {data.get('message')}")
            return None
        
        # 'close' es el precio; 'percent_change' es el cambio porcentual
        price = float(data.get("close", 0))
        change = float(data.get("percent_change", 0))
        
        return {
            "symbol": api_symbol,
            "price": price,
            "change": change,
            "display_symbol": api_symbol  # ya viene con "EUR/USD"
        }
    except Exception as e:
        print(f"Error obteniendo datos para {api_symbol}: {e}")
        return None



@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    # En tu ruta Flask (/)
    MAJOR_CURRENCY_PAIRS = [
    "EUR/USD",
    "USD/JPY",
    "GBP/JPY",
    ]


    ticker_data = []
    for symbol in MAJOR_CURRENCY_PAIRS:
        data = get_price_and_change(symbol, API_KEY)
        if data:
            ticker_data.append(data)
        else:
            print(f"No data for {symbol}")


    if request.method == "POST":
        symbol = request.form.get("symbol", "EUR/USD").upper()
        interval = request.form.get("interval", "15min")
        df, error = get_forex_data(symbol, interval, API_KEY)
        if df is not None:
            df = calculate_indicators(df)
            signal = generate_signal(df)
            last_close = df["close"].iloc[-1]
            result = {
                "symbol": symbol.replace("/", ""),
                "interval": interval,
                "last_close": last_close,
                "signal": signal
            }
        else:
            # Aquí el error ya tiene el mensaje recibido de la API
            print("API error:", error)  # También ver en consola
    return render_template("index.html", result=result, error=error, ticker_data=ticker_data)


if __name__ == "__main__":
    app.run(debug=True)
