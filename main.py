import os
import json
import ccxt
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from database import Database
from ai_engine import AIEngine
from market_data import MarketData 
from backtester import Backtester

load_dotenv()
app = FastAPI()

ai_brain = AIEngine()
market_analyst = MarketData()
backtester_engine = Backtester()

config = {
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "risk_profile": "LOW_RISK",
    "api_key": "",
    "api_secret": ""
}

class UserLogin(BaseModel):
    username: str
    password: str

# --- 1. BAKİYE ÇEKME ---
def get_wallet_balance(api_key, api_secret, symbol):
    if not api_key or not api_secret: return 0.0, 0.0
    try:
        exchange = ccxt.binance({
            'apiKey': api_key, 'secret': api_secret,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        exchange.set_sandbox_mode(True) # Testnet
        
        balance = exchange.fetch_balance()
        base = symbol.split('/')[0] if "/" in symbol else "BTC"
        quote = symbol.split('/')[1] if "/" in symbol else "USDT"

        return float(balance['total'].get(quote, 0.0)), float(balance['total'].get(base, 0.0))
    except Exception as e:
        print(f"Bakiye Hatası: {e}")
        return 0.0, 0.0

# --- 2. İŞLEM YAPMA ---
def execute_binance_trade(decision, symbol, api_key, api_secret):
    if not api_key or not api_secret: return "API Anahtarı Yok"
    try:
        exchange = ccxt.binance({
            'apiKey': api_key, 'secret': api_secret,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        exchange.set_sandbox_mode(True) # Testnet
        
        balance = exchange.fetch_balance()
        base = symbol.split('/')[0]
        quote = symbol.split('/')[1]
        
        usdt_bal = float(balance['total'].get(quote, 0.0))
        coin_bal = float(balance['total'].get(base, 0.0))

        if decision == "AL":
            if usdt_bal > 12: # Güvenli limit
                amount = usdt_bal * 0.98
                params = {'quoteOrderQty': amount}
                order = exchange.create_order(symbol, 'market', 'buy', None, params=params)
                return f"✅ ALIM: {order['amount']} {base}"
            return "Bakiye Yetersiz"
        
        elif decision == "SAT":
            if coin_bal > 0.0005:
                exchange.create_order(symbol, 'market', 'sell', coin_bal)
                return f"🔻 SATIŞ: {coin_bal} {base}"
            return "Satacak Coin Yok"
            
    except Exception as e:
        return f"Hata: {str(e)}"
    return ""

# --- ENDPOINTS ---
@app.get("/", response_class=HTMLResponse)
def landing(): return open("home.html", "r", encoding="utf-8").read()

@app.get("/panel", response_class=HTMLResponse)
def panel(): return open("index.html", "r", encoding="utf-8").read()

@app.post("/auth/register")
def register(user: UserLogin):
    success, msg = Database.register_user(user.username, user.password)
    return JSONResponse(content={"mesaj": msg}, status_code=200 if success else 400)

@app.post("/auth/login")
def login(user: UserLogin):
    success, _ = Database.login_user(user.username, user.password)
    if success:
        settings = Database.get_settings(user.username)
        if settings: config.update(settings)
        return JSONResponse(content={"mesaj": "Giriş Başarılı", "settings": settings})
    return JSONResponse(content={"mesaj": "Hata"}, status_code=401)

@app.post("/auth/save-data")
def save(data: dict):
    if Database.save_settings(data.get('username'), data.get('settings')):
        config.update(data.get('settings'))
        return {"status": "ok"}
    return {"status": "error"}

@app.get("/durum-oku")
def get_status():
    raw_symbol = config.get("symbol", "BTCUSDT")
    formatted_symbol = raw_symbol.replace("USDT", "/USDT") if "USDT" in raw_symbol and "/" not in raw_symbol else raw_symbol

    # 1. CANLI VERİ
    current_price, all_indicators = market_analyst.get_technical_analysis(formatted_symbol, config.get("timeframe", "1h"))
    if current_price is None: return {"analiz": {"fiyat": 0, "karar": "HATA", "detay": "Veri Yok"}}

    # 2. CANLI BAKİYE (ÖNCE BUNU ÇEKİYORUZ)
    usdt_bal, coin_bal = get_wallet_balance(config.get("api_key"), config.get("api_secret"), formatted_symbol)

    # 3. AI ANALİZİ (ARTIK BAKİYEYİ BİLİYOR)
    risk_mode = config.get("risk_profile", "LOW_RISK")
    
    # GÜNCELLEME: usdt_bal ve coin_bal parametrelerini buraya ekledik
    ai_result = ai_brain.analyze_and_select(
        symbol=formatted_symbol,
        price=current_price,
        all_indicators=all_indicators,
        risk_profile=risk_mode,
        usdt_bal=usdt_bal,  # <-- YENİ
        coin_bal=coin_bal   # <-- YENİ
    )
    
    karar = ai_result.get("karar", "BEKLE")

    # 4. İŞLEM YAP (Yine de son bir güvenlik kontrolü var)
    trade_log = ""
    if karar in ["AL", "SAT"]:
        trade_log = execute_binance_trade(karar, formatted_symbol, config.get("api_key"), config.get("api_secret"))
        if "Hata" not in trade_log and "Yok" not in trade_log:
             print(f"💰 İŞLEM YAPILDI: {trade_log}")

    return {
        "analiz": {
            "fiyat": current_price,
            "karar": karar,
            "detay": ai_result.get("neden", "..."),
            "secilenler": ai_result.get("secilen_indikatorler", []),
            "son_islem": trade_log
        },
        "bakiye_usdt": usdt_bal,
        "eldeki_kripto": coin_bal,
        "ayarlar": config,
        "strateji": {"kod": risk_mode},
        "risk": {"seviye": "AI Güven", "puan": int(ai_result.get("skor", 50) / 10)}
    }

@app.post("/backtest-yap")
def run_backtest(data: dict):
    days = data.get("gun_sayisi", 30)
    symbol = config.get("symbol", "BTC/USDT")
    timeframe = config.get("timeframe", "1h")
    result = backtester_engine.run_simulation(symbol, timeframe, days)
    return result if result else {"mesaj": "Hata"}

@app.post("/strateji-degistir")
def change_strat(data: dict): 
    if data.get("yeni_strateji"): config["risk_profile"] = data.get("yeni_strateji"); return {"durum": "OK"}
    return {"durum": "Fail"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
