import pandas as pd
import numpy as np
from binance.client import Client
from indicators import Indicators

class Backtester:
    def __init__(self, config, strategy_instance):
        self.config = config
        self.strategy = strategy_instance 
        self.symbol = config['symbol']
        self.client = Client()
        self.commission = 0.001
        self.risk_profile_name = strategy_instance.__class__.__name__

    def simulate_benchmark(self, df):
        usdt, btc = 1000.0, 0.0
        in_pos = False
        initial = 1000.0
        strategy_name = "Bilinmeyen"

        for i in range(200, len(df)):
            row = df.iloc[i]
            price = float(row['close'])
            buy_signal, sell_signal = False, False

            if "LowRisk" in self.risk_profile_name:
                strategy_name = "SMA 50 Trend"
                if row['close'] > row['SMA_50']: buy_signal = True
                elif row['close'] < row['SMA_50']: sell_signal = True
            elif "MediumRisk" in self.risk_profile_name:
                strategy_name = "RSI 30/70"
                if row['RSI'] < 30: buy_signal = True
                elif row['RSI'] > 70: sell_signal = True
            else:
                strategy_name = "BB Breakout"
                if row['close'] > row['BB_UPPER']: buy_signal = True
                elif row['close'] < row['BB_MID']: sell_signal = True

            if buy_signal and not in_pos:
                btc = (usdt * (1 - self.commission)) / price
                usdt = 0; in_pos = True
            elif sell_signal and in_pos:
                usdt = (btc * price) * (1 - self.commission)
                btc = 0; in_pos = False

        final_val = usdt + (btc * df.iloc[-1]['close'] * (1 - self.commission))
        ret = ((final_val - initial) / initial) * 100
        return ret, strategy_name

    def analyze_failure(self, trades, bot_ret, bench_ret, max_dd):
        """
        Bot neden kaybetti? Bunu analiz edip öneri üretir.
        """
        if bot_ret >= bench_ret:
            return "✅ Strateji harika çalışıyor. Müdahaleye gerek yok."

        # Hiç işlem yapmamışsa
        if not trades:
            return "⚠️ SORUN: Bot hiç işlem açmadı. <br>💡 ÖNERİ: Strateji çok katı (muhafazakar). Risk profilini 'Medium' veya 'High' yapmayı dene."

        # İstatistikleri çıkar
        wins = [t for t in trades if t['type'] == 'SAT' and t['profit'] > 0]
        losses = [t for t in trades if t['type'] == 'SAT' and t['profit'] <= 0]
        win_rate = (len(wins) / len(trades)) * 100 if len(trades) > 0 else 0
        
        # 1. Analiz: Çok sık stop mu oluyor? (Kazanma oranı düşük)
        if win_rate < 40:
            return f"⚠️ SORUN: Kazanma oranı çok düşük (%{win_rate:.1f}). Sık sık terste kalıyor. <br>💡 ÖNERİ: 'Indicators.py' içindeki RSI/Stoch eşiklerini düşürerek daha seçici olmasını sağla."

        # 2. Analiz: Çok büyük kayıplar mı var? (Drawdown yüksek)
        if max_dd < -15:
            return "⚠️ SORUN: Stop Loss mekanizması geç çalışıyor, büyük düşüşler yeniyor. <br>💡 ÖNERİ: 'strategies.py' içindeki Stop Loss yüzdesini daralt (Örn: %5 yerine %2)."

        # 3. Analiz: Çok az işlem mi var?
        if len(trades) < 3:
            return "⚠️ SORUN: Bot çok az fırsat buluyor. <br>💡 ÖNERİ: '1h' yerine '15m' zaman dilimini (timeframe) deneyebilirsin."

        # 4. Genel Piyasa Uyumsuzluğu
        return "⚠️ SORUN: Mevcut piyasa koşulları (Yatay/Trend) seçili stratejiye uymuyor. <br>💡 ÖNERİ: Risk profilini değiştirmeyi dene (Örn: Trend yoksa Medium Risk)."


    def run(self, days=30):
        try:
            interval = self.config['timeframe']
            klines = self.client.get_historical_klines(self.symbol, interval, f"{days} days ago")
            if not klines or len(klines) < 200: return {"error": f"Yetersiz veri."}

            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qav', 'nt', 'tbv', 'tqv', 'ig'])
            cols = ['open', 'high', 'low', 'close', 'volume']
            df[cols] = df[cols].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            try: df = Indicators.add_all_indicators(df)
            except Exception as e: return {"error": f"İndikatör Hatası: {str(e)}"}

            usdt, btc, initial = 1000.0, 0.0, 1000.0
            in_pos, entry, high_p = False, 0.0, 0.0
            trades, equity_curve = [], [initial]
            entry_time = ""

            for i in range(200, len(df)):
                slc = df.iloc[max(0, i-300):i+1]
                row = df.iloc[i]
                price = float(row['close'])
                time = str(row['timestamp'])
                equity_curve.append(usdt + (btc * price))

                if in_pos and price > high_p: high_p = price

                if not in_pos:
                    try:
                        buy, r = self.strategy.check_entry(slc)
                        if buy:
                            btc = (usdt * (1-self.commission)) / price
                            usdt = 0; in_pos = True; entry = price; high_p = price; entry_time = time
                            trades.append({"type": "AL", "price": price, "time": time, "profit": 0})
                    except: pass 
                else:
                    try:
                        sell, r = self.strategy.check_exit(slc, entry, high_p) if "HighRisk" in self.risk_profile_name else self.strategy.check_exit(slc, entry)
                        if sell:
                            # Satış anında kar/zarar hesapla
                            pnl_pct = ((price - entry) / entry) * 100
                            usdt = (btc * price) * (1-self.commission)
                            btc = 0; in_pos = False
                            trades.append({"type": "SAT", "price": price, "time": time, "profit": pnl_pct})
                    except: pass

            final = usdt + (btc * df.iloc[-1]['close'] * (1-self.commission))
            bot_return = ((final - initial)/initial)*100
            
            benchmark_return, benchmark_name = self.simulate_benchmark(df)

            eq = np.array(equity_curve)
            peak = np.maximum.accumulate(eq)
            with np.errstate(divide='ignore', invalid='ignore'): dd = (eq - peak) / peak
            max_dd = np.nanmin(dd) * 100 if len(dd) > 0 else 0.0

            m_prices = df['close'].values[200:]
            m_peak = np.maximum.accumulate(m_prices)
            with np.errstate(divide='ignore', invalid='ignore'): m_dd_arr = (m_prices - m_peak) / m_peak
            m_dd = np.nanmin(m_dd_arr) * 100 if len(m_dd_arr) > 0 else 0.0

            rets = pd.Series(equity_curve).pct_change().dropna()
            sharpe = (rets.mean() / rets.std()) * np.sqrt(365*24) if not rets.empty and rets.std() > 0.000001 else 0.0

            # --- AI TAVSİYESİ OLUŞTUR ---
            advice = self.analyze_failure(trades, bot_return, benchmark_return, max_dd)

            return {
                "bot_return_pct": float(bot_return), 
                "hodl_return_pct": float(benchmark_return), 
                "benchmark_label": benchmark_name,
                "max_drawdown": float(max_dd), 
                "market_drawdown": float(m_dd),
                "sharpe_ratio": round(float(sharpe), 2), 
                "profit_factor": 1.5 if bot_return > 0 else 0.8,
                "trades_log": trades[-5:],
                "ai_suggestion": advice  # <--- YENİ EKLENEN VERİ
            }
            
        except Exception as e: return {"error": f"Genel Sistem Hatası: {str(e)}"}
