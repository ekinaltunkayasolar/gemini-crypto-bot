import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Şifreleri Yükle (Dosya tek başına çalışsa bile bulsun diye)
load_dotenv()

# 2. Şifreleri Oku
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# 3. Kontrol
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ HATA: .env dosyasında Supabase bilgileri eksik!")
    supabase = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"❌ Supabase Bağlantı Hatası: {e}")
        supabase = None

class Database:
    @staticmethod
    def register_user(username, password):
        if not supabase: return False, "Veritabanı bağlantısı yok."
        try:
            # Kullanıcı var mı?
            res = supabase.table("bot_users").select("*").eq("username", username).execute()
            if res.data: return False, "Bu kullanıcı adı dolu."
            
            # Kayıt et
            data = {"username": username, "password": password}
            user_res = supabase.table("bot_users").insert(data).execute()
            user_id = user_res.data[0]['id']
            
            # Varsayılan ayar
            default_config = {
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "risk_profile": "LOW_RISK",
                "api_key": "",
                "api_secret": ""
            }
            supabase.table("bot_settings").insert({"user_id": user_id, "config": default_config}).execute()
            return True, "Kayıt Başarılı!"
        except Exception as e: return False, str(e)

    @staticmethod
    def login_user(username, password):
        if not supabase: return False, "Veritabanı hatası."
        try:
            res = supabase.table("bot_users").select("*").eq("username", username).eq("password", password).execute()
            if res.data: return True, res.data[0]
            return False, "Kullanıcı adı veya şifre hatalı."
        except Exception as e: return False, str(e)

    @staticmethod
    def get_settings(username):
        if not supabase: return {}
        try:
            user_res = supabase.table("bot_users").select("id").eq("username", username).execute()
            if not user_res.data: return {}
            user_id = user_res.data[0]['id']
            
            res = supabase.table("bot_settings").select("config").eq("user_id", user_id).execute()
            if res.data: return res.data[0]['config']
            return {}
        except: return {}

    @staticmethod
    def save_settings(username, new_settings):
        if not supabase: return False
        try:
            user_res = supabase.table("bot_users").select("id").eq("username", username).execute()
            if not user_res.data: return False
            user_id = user_res.data[0]['id']
            supabase.table("bot_settings").update({"config": new_settings}).eq("user_id", user_id).execute()
            return True
        except: return False
