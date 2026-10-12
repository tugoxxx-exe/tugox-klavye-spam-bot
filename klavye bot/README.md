# TUGOX // Discord Kontrol & Klavye Otomasyon Merkezi (GUI Hub)

Modern CustomTkinter arayüzüne sahip, Discord hesabı bağlama, L33t sesli harf dönüştürücü ve Kanal/DM otomatik mesajlaşma motoru.

---

## 📁 Klasör Yapısı

- `baslat_tugox_gui.bat` — **[ÖNERİLEN]** TUGOX grafiksel arayüzünü (GUI) başlatır.
- `tugox_gui.py` — Ana modern arayüz ve Discord otomasyon motoru.
- `baslat_klavye.bat` — Sadece CMD klavye motorunu başlatır.
- `baslat_discord_bot.bat` — Discord Bot kontrolcüsünü başlatır.
- `kurulum.bat` — Gerekli tüm Python kütüphanelerini otomatik kurar.
- `vowel_hook.py` — Sistem geneli klavye dönüştürme motoru (F8 kısayollu).
- `discord_bot.py` — Discord sunucu botu entegrasyonu.
- `requirements.txt` — Gerekli Python kütüphaneleri.

---

## ⚡ Özellikler

1. **Üst Başlık (TUGOX Header & Bağlantı Paneli):**
   - Discord Token (Kullanıcı veya Bot Tokeni) ile hesabı bağlama ve profil doğrulama.
2. **1. Seçenek: Klavye Botu (L33t Sesli Harf Motoru):**
   - Sistem geneli tüm sesli harfleri (`a, e, i, o, u`) sayılara (`4, 3, 1, 0, 7`) dönüştürme.
   - [F8] kısayolu ile anında açma/kapama.
   - Dahili canlı test alanı.
3. **2. Seçenek: Kanal & DM Otomatik Mesaj Gönderici:**
   - Sunucu kanalı (Kanal ID) veya doğrudan kullanıcı (DM Kullanıcı ID) seçimi.
   - Ayarlanabilir gönderim aralığı (saniye), tekrar adedi (veya sonsuz) ve Anti-Spam jitter koruması.
   - Canlı HTTP durum ve log konsolu.

---

## 🚀 Hızlı Başlangıç

1. İlk çalıştırmada `kurulum.bat` dosyasına çift tıklayın.
2. `baslat_tugox_gui.bat` dosyasına çift tıklayarak arayüzü açın.
