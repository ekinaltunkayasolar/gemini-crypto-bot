import pandas as pd
import pandas_ta as ta
import numpy as np

class Indicators:
    @staticmethod
    def add_all_indicators(df):
        """
        15 Profesyonel İndikatör (Hata Korumalı Dinamik Sütun Seçimi ile)
        """
        df = df.copy()
        
        # --- 1. GRUP: LOW RISK ---
        # 1. EMA 200
        df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # 2. RSI 14
        df['RSI'] = df.ta.rsi(length=14)
        
        # 3. MACD (Dinamik Sütun Seçimi)
        try:
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            if macd is not None:
                # Sütun isimleri MACD_12_26_9 gibi olabilir, dinamik buluyoruz:
                macd_col = [c for c in macd.columns if c.startswith('MACD_') and not c.startswith('MACDh') and not c.startswith('MACDs')][0]
                hist_col = [c for c in macd.columns if c.startswith('MACDh')][0]
                
                df['MACD'] = macd[macd_col]
                df['MACD_HIST'] = macd[hist_col]
            else:
                df['MACD'] = 0; df['MACD_HIST'] = 0
        except:
             df['MACD'] = 0; df['MACD_HIST'] = 0
            
        # 4. ADX
        try:
            adx = df.ta.adx(length=14)
            if adx is not None:
                col_name = [c for c in adx.columns if c.startswith('ADX')][0]
                df['ADX'] = adx[col_name]
            else: df['ADX'] = 0
        except: df['ADX'] = 0
            
        # 5. ATR
        df['ATR'] = df.ta.atr(length=14)

        # --- 2. GRUP: MEDIUM RISK ---
        # 6. Bollinger Bands (HATA VEREN KISIM DÜZELTİLDİ)
        try:
            bb = df.ta.bbands(length=20, std=2.0)
            if bb is not None:
                # Sütun isimlerini ezbere yazmak yerine "BBL" ile başlayanı al diyoruz
                lower_col = [c for c in bb.columns if c.startswith('BBL')][0]
                mid_col   = [c for c in bb.columns if c.startswith('BBM')][0]
                upper_col = [c for c in bb.columns if c.startswith('BBU')][0]
                width_col = [c for c in bb.columns if c.startswith('BBB')][0]

                df['BB_LOWER'] = bb[lower_col]
                df['BB_MID']   = bb[mid_col]
                df['BB_UPPER'] = bb[upper_col]
                df['BB_WIDTH'] = bb[width_col]
            else:
                # Hata olursa varsayılan değerler
                df['BB_LOWER'] = df['close']; df['BB_MID'] = df['close']; df['BB_UPPER'] = df['close']; df['BB_WIDTH'] = 0
        except:
            df['BB_LOWER'] = df['close']; df['BB_MID'] = df['close']; df['BB_UPPER'] = df['close']; df['BB_WIDTH'] = 0

        # 7. Stochastic
        try:
            stoch = df.ta.stoch(k=14, d=3, smooth_k=3)
            if stoch is not None:
                k_col = [c for c in stoch.columns if c.startswith('STOCHk')][0]
                df['STOCH_K'] = stoch[k_col]
            else: df['STOCH_K'] = 50
        except: df['STOCH_K'] = 50
            
        # 8. MFI
        df['MFI'] = df.ta.mfi(length=14)
        
        # 9. SMA 50
        df['SMA_50'] = df.ta.sma(length=50)
        
        # 10. CCI
        df['CCI'] = df.ta.cci(length=20)

        # --- 3. GRUP: HIGH RISK ---
        # 11. BB_WIDTH (Yukarıda hesaplandı)
        
        # 12. Volume SMA
        df['VOL_SMA_20'] = df['volume'].rolling(window=20).mean()
        
        # 13. OBV
        df['OBV'] = df.ta.obv()
        
        # 14. Parabolic SAR
        try:
            psar = df.ta.psar()
            if psar is not None:
                # PSAR long ve short sütunlarını birleştir
                cols = psar.columns
                df['PSAR'] = psar[cols[0]].combine_first(psar[cols[1]])
            else: df['PSAR'] = df['close']
        except: df['PSAR'] = df['close']

        # 15. Williams %R
        df['WILLR'] = df.ta.willr(length=14)

        # NaN değerleri temizle
        df.dropna(inplace=True)
        return df
