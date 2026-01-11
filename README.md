# ⚡ AI Trader Pro V2.4 - Yapay Zeka Destekli Kripto Botu

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green) ![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

**AI Trader Pro**, Binance borsasında otomatik alım-satım yapan, gücünü Google Gemini 3 Flash yapay zeka modelinden alan gelişmiş bir ticaret botudur. Piyasa verilerini 15 farklı teknik indikatörle analiz eder, kullanıcının risk profiline göre karar verir ve işlemleri otomatik uygular.

---

## 📋 Proje Özeti

Bu proje, geleneksel algoritmik botların aksine sadece "RSI 30'un altındaysa al" demez. Piyasa verilerini, trendleri, hacmi ve volatiliteyi bir bütün olarak **Yapay Zeka (LLM)** motoruna sunar.

**Temel Özellikler:**
* 🧠 **Yapay Zeka Karar Mekanizması:** Google Gemini API ile piyasa yorumlama.
* 📊 **Gelişmiş Teknik Analiz:** RSI, MACD, Bollinger, EMA, ATR ve daha fazlası.
* 💰 **Akıllı Bakiye Yönetimi:** Cüzdan bakiyesine göre işlem büyüklüğü belirleme.
* ⚡ **Hızlı Web Arayüzü:** FastAPI ve Vanilla JS ile anlık veri takibi.
* 🧪 **Backtest (Simülasyon) Modu:** Geçmiş verilerle strateji testi.
* ☁️ **Bulut Uyumlu:** Render.com üzerinde 7/24 çalışmaya uygun.

---

## 🛠️ Teknoloji Yığını ve Bağımlılıklar

Proje aşağıdaki teknolojiler üzerine inşa edilmiştir:

* **Backend:** Python 3.10+, FastAPI, Uvicorn
* **Veri & Borsa:** CCXT (Binance API), Pandas, Numpy
* **Yapay Zeka:** Google Generative AI (Gemini 3 Flash)
* **Frontend:** HTML5, CSS3 (Modern Dark UI), JavaScript (Fetch API)
* **Araçlar:** Python-dotenv, Git

---

## 🚀 Kurulum ve Dağıtım (Deployment)

### 1. Ön Hazırlıklar (Gereksinimler)
* Bilgisayarınızda [Python](https://www.python.org/) yüklü olmalıdır.
* [Binance](https://testnet.binance.vision/) Testnet API anahtarları.
* [Google AI Studio](https://aistudio.google.com/) API anahtarı.

### 2. Yerel Kurulum (Local)

Projeyi bilgisayarınıza klonlayın ve klasöre gidin:

```bash
git clone [https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git)
cd PROJE_ADINIZ
