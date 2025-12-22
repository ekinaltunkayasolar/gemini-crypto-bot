import asyncio, json, os, logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from binance.client import Client
from market_data import get_historical_data
from indicators import Indicators
from strategies import LowRiskStrategy, MediumRiskStrategy, HighRiskStrategy
from backtester import Backtester

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- DOSYA YÖNETİMİ ---
if not os.path.exists("config.json"):
    default_conf = { "symbol": "BTCUSDT", "active_strategy": "LOW_RISK", "timeframe": "1h", "check_interval": 10 }
    with open("config.json", "w") as f: json.dump(default_conf, f)

if not os.path.exists("users.json"):
    with open("users.json", "w") as f: json.dump({}, f)

# Global Durum
state = {
    "bakiye_usdt": 1000.0, "pozisyon": False, "giris_fiyati": 0.0, "en_yuksek_fiyat": 0.0,
    "eldeki_btc": 0.0, "aktif_strateji": "LOW_RISK",
    "son_analiz": {"fiyat":0, "karar":"Bekleniyor", "detay":"..."},
    "risk": {"puan":0, "seviye":"---"},
    "current_user": None
}

# Yardımcılar
def load_config():
    with open("config.json", "r") as f: return json.load(f)
def save_config(conf):
    with open("config.json", "w") as f: json.dump(conf, f)
def get_strat(name):
    conf = {} 
    if name == "HIGH_RISK": return HighRiskStrategy(conf)
    if name == "MEDIUM_RISK": return MediumRiskStrategy(conf)
    return LowRiskStrategy(conf)

# Başlangıç
try:
    initial_conf = load_config()
    if "timeframe" not in initial_conf: initial_conf["timeframe"] = "1h"; save_config(initial_conf)
    state["aktif_strateji"] = initial_conf.get("active_strategy", "LOW_RISK")
    bot_strategy = get_strat(state["aktif_strateji"])
except Exception as e: print(f"Config hatası: {e}")

# Modeller
class UserAuth(BaseModel): username: str; password: str
class UserData(BaseModel): username: str; settings: dict
class BacktestReq(BaseModel): gun_sayisi: int
class StratReq(BaseModel): yeni_strateji: str 

@app.post("/auth/register")
async def register(u: UserAuth):
    d = json.load(open("users.json"))
    if u.username in d: return JSONResponse(400, {"mesaj":"Kullanıcı adı dolu"})
    d[u.username] = {"password": u.password, "settings": {"symbol":"BTCUSDT", "risk_profile":"LOW_RISK"}}
    json.dump(d, open("users.json","w"))
    return {"mesaj":"Kayıt başarılı"}

@app.post("/auth/login")
async def login(u: UserAuth):
    d = json.load(open("users.json"))
    if u.username not in d or d[u.username]["password"] != u.password: return JSONResponse(401, {"mesaj":"Hatalı giriş"})
    s = d[u.username]["settings"]
    conf = load_config()
    conf["symbol"] = s.get("symbol", "BTCUSDT")
    conf["active_strategy"] = s.get("risk_profile", "LOW_RISK")
    save_config(conf)
    state["current_user"] = u.username
    state["aktif_strateji"] = conf["active_strategy"]
    global bot_strategy
    bot_strategy = get_strat(state["aktif_strateji"])
    return {"mesaj":"Giriş başarılı", "settings": s}

@app.post("/auth/save-data")
async def save_data(d: UserData):
    db = json.load(open("users.json"))
    if d.username not in db: return JSONResponse(404, {"mesaj":"User yok"})
    current_settings = db[d.username]["settings"]
    current_settings.update(d.settings)
    db[d.username]["settings"] = current_settings
    json.dump(db, open("users.json","w"))
    state["current_user"] = d.username
    conf = load_config()
    conf["symbol"] = d.settings.get("symbol", conf["symbol"])
    conf["active_strategy"] = d.settings.get("risk_profile", conf["active_strategy"])
    state["api_key"] = d.settings.get("api_key", "")
    state["api_secret"] = d.settings.get("api_secret", "")
    save_config(conf)
    state["aktif_strateji"] = conf["active_strategy"]
    global bot_strategy
    bot_strategy = get_strat(state["aktif_strateji"])
    return {"mesaj":"Kaydedildi"}

@app.post("/strateji-degistir")
async def strateji_degistir(req: StratReq):
    conf = load_config()
    conf["active_strategy"] = req.yeni_strateji
    save_config(conf)
    state["aktif_strateji"] = req.yeni_strateji
    global bot_strategy
    bot_strategy = get_strat(req.yeni_strateji)
    if state["current_user"]:
        db = json.load(open("users.json"))
        if state["current_user"] in db:
            db[state["current_user"]]["settings"]["risk_profile"] = req.yeni_strateji
            json.dump(db, open("users.json", "w"))
    return {"mesaj": f"Strateji {req.yeni_strateji} olarak ayarlandı"}

@app.post("/backtest-yap")
async def backtest(r: BacktestReq):
    try:
        conf = load_config()
        if "timeframe" not in conf: conf["timeframe"] = "1h"
        strat_to_test = get_strat(state["aktif_strateji"])
        tester = Backtester(conf, strat_to_test)
        res = await asyncio.to_thread(tester.run, days=r.gun_sayisi)
        return res
    except Exception as e: return {"mesaj": str(e)}

@app.get("/durum-oku")
def durum():
    conf = load_config()
    return {
        "bakiye_usdt": state["bakiye_usdt"],
        "eldeki_kripto": state["eldeki_btc"], # <--- YENİ EKLENEN KISIM
        "analiz": state["son_analiz"],
        "risk": state["risk"],
        "strateji": {"kod": state["aktif_strateji"]},
        "ayarlar": {"symbol": conf.get("symbol", "BTCUSDT")}
    }

async def loop():
    while True:
        try:
            conf = load_config()
            if conf["active_strategy"] != state["aktif_strateji"]:
                state["aktif_strateji"] = conf["active_strategy"]
                global bot_strategy
                bot_strategy = get_strat(state["aktif_strateji"])
            
            client = Client(state.get("api_key"), state.get("api_secret")) if state.get("api_key") else Client()
            if state.get("api_key"):
                try: 
                    b = client.get_asset_balance(asset='USDT')
                    state["bakiye_usdt"] = float(b['free'])
                    # Base asset (örn: BTC) bakiyesini de çekebilirdik ama simülasyon karışmasın diye şimdilik manuel tutuyoruz
                except: pass

            df = get_historical_data(conf["symbol"], Client.KLINE_INTERVAL_1HOUR, "5 days ago")
            df = Indicators.add_all_indicators(df)
            row = df.iloc[-1]
            price = float(row['close'])
            
            vol = (row['ATR']/price)*100
            score = min(10, int(vol*3))
            state["risk"] = {"puan": score, "seviye": "Yüksek" if score>6 else "Düşük"}

            decision, detail = "BEKLE", f"Risk Puanı: {score}"
            
            if not state["pozisyon"]:
                buy, reason = bot_strategy.check_entry(df)
                if buy:
                    state["pozisyon"] = True; state["giris_fiyati"] = price
                    state["eldeki_btc"] = state["bakiye_usdt"]/price; state["bakiye_usdt"] = 0
                    decision = "ALIM"; detail = reason
            else:
                try: sell, reason = bot_strategy.check_exit(df, state["giris_fiyati"], state["en_yuksek_fiyat"])
                except: sell, reason = bot_strategy.check_exit(df, state["giris_fiyati"])
                if sell:
                    state["pozisyon"] = False; state["bakiye_usdt"] = state["eldeki_btc"]*price
                    state["eldeki_btc"] = 0
                    decision = "SATIŞ"; detail = reason
            
            state["son_analiz"] = {"fiyat": price, "karar": decision, "detay": detail}
        except Exception as e: print(f"Hata: {e}")
        await asyncio.sleep(10)

@app.on_event("startup")
async def start(): asyncio.create_task(loop())
@app.get("/", response_class=HTMLResponse)
def home(): return open("index.html", "r", encoding="utf-8").read()
