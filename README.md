# ⚡ AI Trader Pro (V1.1)

**Yapay Zeka Destekli, Çoklu Stratejili ve Web Arayüzlü Kripto Ticaret Terminali**

Bu proje, 7/24 piyasayı izleyen, teknik indikatörlere (RSI, Bollinger, MACD) göre otomatik al-sat kararı veren ve kullanıcısına Telegram üzerinden anlık bildirim gönderen profesyonel bir ticaret botudur.

![Bot Dashboard](https://img.shields.io/badge/Status-Live-green) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Binance](https://img.shields.io/badge/Integration-Binance-yellow)

---

## 🚀 Öne Çıkan Özellikler

* **🛡️ Çoklu Risk Yönetimi:** Piyasa koşullarına göre 3 farklı mod (Low, Medium, High Risk).
* **🧠 Akıllı Karar Mekanizması:** Sadece fiyatı değil; trendi, hacmi ve volatiliteyi analiz eder.
* **📱 Telegram Entegrasyonu:** Alım veya satım yapıldığı saniye cebinize bildirim gelir.
* **📊 Backtest (Geçmiş Test) Motoru:** "Geçen ay bu botu kullansaydım ne kadar kazanırdım?" sorusunun cevabını verir.
* **🖥️ Canlı Web Terminali:** TradingView grafikleri, anlık bakiye ve bot kararlarını içeren modern arayüz.

---

## ⚙️ Sistem Mimarisi

Botun çalışma mantığı, karar verme süreçleri ve kullanıcı etkileşimi aşağıdaki şemada özetlenmiştir:

![Sistem Algoritması](https://mermaid.ink/img/pako:eNp1kstuwyAQRX9FaNZWEchDvapS9aO6q4oLBxg1sHEwTlLlf--A80hZycW9MzB3OCAzsUQW4shfyucKNk5W0Pj40qgOngs2gjXew93ROb5cdUKJRtuTQefhjbPGa9bquILW_lird_3f_fYPmqf9CNYu179X--PuDvL8yesMvYEn8AEcwA6cwAIcwB5cQjsHa_BovWENPqEfwRam4AvMoIMluAQuLMASZv9gLfAZvYGpHz6E6T_YwCIUw1ws4Blm4w0m4w18AB9gB0c4wglOYGEDT7CHJ3iBK9zgBnewMISXUAwTWMA91HAPu3iAR3iCYmjhGV7gBb7gG77hB35hCT-hGObwAr8QwxJ-I4bfqOEPjPAPzPAHMfyJGP5CDH8jhn8Qw9-I4R_E8C9i-A8x_IkY_kIMe_gDL8tBjg?type=png)

---

## 📈 Strateji Modları

Bot, yatırımcının risk algısına göre 3 farklı karakterde çalışabilir:

### 1. LOW RISK (Trend Pullback)
* **Mantık:** "Trend dostundur."
* **Giriş:** Fiyat yükseliş trendindeyken (EMA200 üstü) yaşanan kısa vadeli düşüşlerde (RSI < 45) alım yapar.
* **Hedef:** Güvenli ve istikrarlı büyüme.

### 2. MEDIUM RISK (Mean Reversion)
* **Mantık:** "Fiyat her zaman ortalamaya döner."
* **Giriş:** Fiyat Bollinger Alt Bandını delip tekrar içeri girdiğinde alım yapar.
* **Hedef:** Yatay piyasalarda dalgalanmaları yakalamak.

### 3. HIGH RISK (Volatility Breakout)
* **Mantık:** "Sıkışan fiyat patlama yapar."
* **Giriş:** Bollinger bantları daraldıktan sonra yukarı yönlü hacimli bir kırılım (Breakout) olduğunda girer.
* **Hedef:** Sert yükselişleri yakalamak (Trailing Stop kullanır).

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için:

1. **Repoyu İndirin:**
    ```bash
    git clone https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git
    cd crypto-bot
    ```

2. **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Botu Başlatın:**
    ```bash
    uvicorn main:app --reload
    ```

4. **Web Arayüzüne Girin:**
    Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

---

## 📲 Telegram Bildirimleri Kurulumu

Botun size mesaj atması için:
1. Telegram'da **@BotFather** ile yeni bir bot oluşturun ve `Token` alın.
2. Kendi `Chat ID`nizi öğrenin.
3. Web arayüzündeki **"Ayarlar"** butonuna basarak bu bilgileri girin.

---

## ⚠️ Yasal Uyarı

*Bu yazılım deneysel amaçlı geliştirilmiş bir algoritmik ticaret aracıdır. Geçmiş performans, gelecekteki sonuçların garantisi değildir. Kripto para piyasaları yüksek risk içerir. Yazar, bu yazılımın kullanımından doğabilecek maddi kayıplardan sorumlu tutulamaz.*

---
*Developed by Ekin Altunkaya*
