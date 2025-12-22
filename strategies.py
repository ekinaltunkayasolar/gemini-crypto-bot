import numpy as np

class Strategy:
    def __init__(self, config):
        self.config = config

    def get_market_regime(self, row):
        """
        Piyasanın o anki durumunu (Rejimini) tespit eder.
        """
        # 1. Trend Gücü (ADX)
        # ADX verisi bazen NaN gelebilir, kontrol edelim
        adx_val = row['ADX'] if not np.isnan(row['ADX']) else 20
        is_trending = adx_val > 25
        
        # 2. Volatilite (ATR / Fiyat)
        atr_val = row['ATR'] if not np.isnan(row['ATR']) else 0
        volatility = (atr_val / row['close']) * 100
        is_volatile = volatility > 2.0 # %2'den fazla oynaklık varsa
        
        if is_trending:
            return "TREND"
        elif is_volatile:
            return "VOLATILE"
        else:
            return "RANGING" 

class LowRiskStrategy(Strategy):
    """
    Muhafazakar Yapay Zeka:
    Sadece çok yüksek puan (80/100) ve güçlü trend onayı arar.
    """
    def check_entry(self, df):
        row = df.iloc[-1]
        regime = self.get_market_regime(row)
        
        # --- DİNAMİK AĞIRLIKLANDIRMA (YAPAY ZEKA KATMANI) ---
        weights = {
            'EMA_TREND': 0, 'RSI': 0, 'MACD': 0, 'ADX': 0, 'VOL': 0
        }
        
        if regime == "TREND":
            weights = {'EMA_TREND': 40, 'MACD': 30, 'ADX': 20, 'RSI': 5, 'VOL': 5}
        elif regime == "RANGING":
            weights = {'RSI': 50, 'EMA_TREND': 10, 'MACD': 10, 'ADX': 10, 'VOL': 20}
        else: # Volatile
            weights = {'VOL': 40, 'EMA_TREND': 30, 'RSI': 10, 'MACD': 10, 'ADX': 10}

        score = 0
        
        # 1. EMA 200
        if row['close'] > row['EMA_200']: score += weights['EMA_TREND']
        
        # 2. RSI (< 55)
        if row['RSI'] < 55: score += weights['RSI']
        
        # 3. MACD
        if row['MACD_HIST'] > 0: score += weights['MACD']
        
        # 4. ADX
        if row['ADX'] > 20: score += weights['ADX']
        
        # 5. Hacim
        if row['volume'] > row['VOL_SMA_20']: score += weights['VOL']

        threshold = 80
        if score >= threshold:
            return True, f"AI Skoru: {score}/100 (Rejim: {regime})"
            
        return False, ""

    def check_exit(self, df, entry_price):
        row = df.iloc[-1]
        if row['close'] < row['EMA_200']: return True, "Trend Bitti"
        if row['RSI'] > 75: return True, "RSI Aşırı Şişti"
        if row['close'] < entry_price * 0.98: return True, "Stop Loss %2"
        return False, ""


class MediumRiskStrategy(Strategy):
    """
    Dengeli Yapay Zeka:
    Eşik Puan: 70/100
    """
    def check_entry(self, df):
        row = df.iloc[-1]
        regime = self.get_market_regime(row)
        
        weights = {}
        if regime == "RANGING":
            weights = {'BB_LOW': 30, 'STOCH': 30, 'CCI': 20, 'MFI': 20, 'SMA': 0}
        else:
            weights = {'BB_LOW': 20, 'STOCH': 20, 'CCI': 20, 'MFI': 20, 'SMA': 20}

        score = 0
        
        # 1. Bollinger Alt Bant
        if row['close'] <= row['BB_LOWER'] * 1.01: score += weights.get('BB_LOW', 0)
        
        # 2. Stochastic
        if row['STOCH_K'] < 25: score += weights.get('STOCH', 0)
        
        # 3. CCI
        if row['CCI'] < -100: score += weights.get('CCI', 0)
        
        # 4. MFI
        if row['MFI'] < 30: score += weights.get('MFI', 0)
        
        # 5. SMA 50
        if row['close'] < row['SMA_50']: score += weights.get('SMA', 0)

        if score >= 70:
            return True, f"AI Skoru: {score}/100 (Rejim: {regime})"
        return False, ""

    def check_exit(self, df, entry_price):
        row = df.iloc[-1]
        if row['close'] > row['BB_MID']: return True, "Kar Al (Orta Bant)"
        if row['close'] < entry_price * 0.95: return True, "Stop Loss %5"
        return False, ""


class HighRiskStrategy(Strategy):
    """
    Agresif Yapay Zeka:
    Eşik Puan: 60/100
    """
    def check_entry(self, df):
        row = df.iloc[-1]
        
        weights = {
            'VOLUME_BREAK': 35,
            'OBV_UP': 25,
            'WILLR_MOMENTUM': 20,
            'PSAR_TREND': 10,
            'BB_SQUEEZE': 10
        }

        score = 0
        prev_row = df.iloc[-2]

        # 1. Hacim Patlaması
        if row['volume'] > (row['VOL_SMA_20'] * 1.2): score += weights['VOLUME_BREAK']
        
        # 2. OBV Artışı
        if row['OBV'] > prev_row['OBV']: score += weights['OBV_UP']
        
        # 3. Williams %R
        if row['WILLR'] > -50: score += weights['WILLR_MOMENTUM']
        
        # 4. Parabolic SAR
        # PSAR bazen NaN olabilir, kontrol edelim
        psar_val = row['PSAR'] if not np.isnan(row['PSAR']) else 0
        if psar_val > 0 and row['close'] > psar_val: score += weights['PSAR_TREND']
        
        # 5. Bollinger Sıkışması
        if row['BB_WIDTH'] < 0.15: score += weights['BB_SQUEEZE']

        if score >= 60:
            return True, f"AI Skoru: {score}/100 (Agresif Giriş)"
        return False, ""

    def check_exit(self, df, entry_price, highest_price):
        row = df.iloc[-1]
        psar_val = row['PSAR'] if not np.isnan(row['PSAR']) else 0
        
        # Trailing Stop
        if row['close'] < highest_price * 0.97: return True, "Trailing Stop %3"
        # PSAR Dönüşü
        if psar_val > 0 and row['close'] < psar_val: return True, "PSAR Dönüşü"
        return False, ""
