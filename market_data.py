import ccxt
import pandas as pd
import numpy as np

class MarketData:
    def __init__(self):
        # Zaman senkronizasyonu burada da önemli
        self.exchange = ccxt.binance({
            'options': {'adjustForTimeDifference': True}
        })

    def get_technical_analysis(self, symbol="BTC/USDT", timeframe="1h"):
        try:
            if "USDT" in symbol and "/" not in symbol:
                symbol = symbol.replace("USDT", "/USDT")

            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=200)
            if not ohlcv: return None, None

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            current_price = float(close.iloc[-1])

            # İndikatör Hesaplamaları
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            # MACD
            exp12 = close.ewm(span=12, adjust=False).mean()
            exp26 = close.ewm(span=26, adjust=False).mean()
            macd_line = exp12 - exp26
            macd_signal = macd_line.ewm(span=9, adjust=False).mean()

            # Bollinger
            sma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            upper = sma20 + (std20 * 2)
            lower = sma20 - (std20 * 2)
            width = (upper - lower) / sma20

            # Diğerleri
            ema200 = close.ewm(span=200, adjust=False).mean()
            sma50 = close.rolling(50).mean()
            
            # ATR
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()

            # OBV & Vol
            obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
            obv_trend = "Yükseliyor" if obv.iloc[-1] > obv.iloc[-5] else "Düşüyor"
            vol_sma = volume.rolling(20).mean()
            vol_status = "Yüksek" if volume.iloc[-1] > vol_sma.iloc[-1] else "Düşük"
            
            # Stoch K
            lowest = low.rolling(14).min()
            highest = high.rolling(14).max()
            stoch_k = 100 * ((close - lowest) / (highest - lowest))
            
            # Williams R
            will_r = -100 * ((highest - close) / (highest - lowest))

            # CCI
            tp = (high + low + close) / 3
            cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

            # ADX Proxy
            adx = (abs(close - close.shift(14)) / atr) * 10

            # FLOAT DÖNÜŞÜMÜ VE PAKETLEME
            indicators = {
                "Low_Risk_Trend": { 
                    "EMA_200": float(round(ema200.iloc[-1], 2)),
                    "MACD_Line": float(round(macd_line.iloc[-1], 2)),
                    "MACD_Signal": float(round(macd_signal.iloc[-1], 2)),
                    "ADX": float(round(adx.iloc[-1], 2)),
                    "RSI": float(round(rsi.iloc[-1], 2)),
                    "ATR": float(round(atr.iloc[-1], 2))
                },
                "Med_Risk_Reversion": {
                    "Bollinger_Upper": float(round(upper.iloc[-1], 2)),
                    "Bollinger_Lower": float(round(lower.iloc[-1], 2)),
                    "SMA_50": float(round(sma50.iloc[-1], 2)),
                    "Stochastic_K": float(round(stoch_k.iloc[-1], 2)),
                    "CCI": float(round(cci.iloc[-1], 2)),
                    "MFI": "N/A"
                },
                "High_Risk_Breakout": {
                    "Bollinger_Width": float(round(width.iloc[-1], 4)),
                    "Volume_SMA": vol_status,
                    "OBV": obv_trend,
                    "PSAR": "N/A",
                    "Williams_R": float(round(will_r.iloc[-1], 2))
                }
            }
            return current_price, indicators

        except Exception as e:
            print(f"❌ Market Veri Hatası: {e}")
            return None, None
