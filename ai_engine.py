import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ UYARI: GEMINI_API_KEY bulunamadı!")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=api_key)
                self.model_name = "gemini-3-flash-preview"
                print("✅ AI Motoru Hazır (v1.0)")
            except Exception as e:
                print(f"❌ AI Bağlantı Hatası: {e}")
                self.client = None

    # GÜNCELLEME: Artık bakiye bilgilerini de parametre olarak alıyor
    def analyze_and_select(self, symbol, price, all_indicators, risk_profile, usdt_bal, coin_bal):
        if not self.client:
            return {"karar": "BEKLE", "skor": 50, "neden": "AI Anahtarı Eksik", "secilen_indikatorler": []}

        # --- YENİ AKILLI PROMPT ---
        # Bakiyeyi ve kuralları yapay zekaya öğretiyoruz.
        prompt = f"""
        Sen Profesyonel Kripto Fon Yöneticisisin.
        
        DURUM RAPORU:
        - Coin: {symbol}
        - Fiyat: {price}
        - Risk Profili: {risk_profile}
        - MEVCUT CÜZDAN: {usdt_bal} USDT (Nakit) | {coin_bal} Adet Coin (Mal)
        
        PİYASA VERİLERİ (İndikatörler):
        {json.dumps(all_indicators)}
        
        KRİTİK CÜZDAN KURALLARI (BUNLARA KESİN UY):
        1. Eğer USDT bakiyesi 12 dolardan azsa, ASLA "AL" kararı verme. "BEKLE" de ve nedenine "Yetersiz Bakiye" yaz.
        2. Eğer Coin bakiyesi 0.0005'ten azsa, ASLA "SAT" kararı verme. "BEKLE" de ve nedenine "Satacak Coin Yok" yaz.
        
        GÖREV:
        1. Yukarıdaki bakiye kurallarını kontrol et. Bakiye yetmiyorsa teknik analize bakmadan BEKLE.
        2. Bakiye yetiyorsa, indikatörleri analiz et ve karar ver.
        
        YANIT FORMATI (Sadece JSON):
        {{
            "karar": "AL" veya "SAT" veya "BEKLE",
            "skor": 0-100,
            "neden": "Kısa ve net açıklama",
            "secilen_indikatorler": ["RSI", "MACD" vb.]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"⚠️ AI Analiz Hatası: {e}")
            return {"karar": "BEKLE", "skor": 50, "neden": "AI Yanıt Vermedi", "secilen_indikatorler": []}
