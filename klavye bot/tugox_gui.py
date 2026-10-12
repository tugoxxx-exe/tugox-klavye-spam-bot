#!/usr/bin/env python3
"""
TUGOX // Discord Automation Hub & Vowel Keyboard Hook
=====================================================
Geliştirici: aero (Red Team / Dev) & TUGOX
Açıklama: 
  - Modern CustomTkinter Grafik Arayüzü (GUI)
  - TUGOX Başlığı ve Neon Cyber Tasarım
  - Discord Token ile Kullanıcı / Bot Hesabı Bağlama & Doğrulama
  - Seçenek 1: Sistem Geneli Sesli Harf -> L33t Klavye Dönüştürücü Motoru (F8 Kısayolu)
  - Seçenek 2: Discord Kullanıcı Hesabından Kanal & DM Otomatik Mesaj Gönderici
"""

import sys
import os
import time
import random
import threading
import requests
import customtkinter as ctk
from tkinter import messagebox

# Yerel klavye motoru sınıfını içe aktar
try:
    from vowel_hook import VowelKeyboardHook, DEFAULT_VOWEL_MAP
except ImportError:
    # Eğer doğrudan bu dosya çalıştırılırsa aynı dizindeki vowel_hook'u bul
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vowel_hook import VowelKeyboardHook, DEFAULT_VOWEL_MAP

# CustomTkinter Tema Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TugoxApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TUGOX // Discord Control & Keyboard Automation Hub")
        self.geometry("960x780")
        self.minsize(880, 700)
        self.configure(fg_color="#0d1117")

        # Durum Değişkenleri
        self.token = ""
        self.auth_header = {}
        self.account_info = None
        self.is_bot_token = False

        # Klavye Motoru
        self.keyboard_engine = VowelKeyboardHook(hotkey="f8")

        # Otomatik Mesajlaşma Durumu
        self.auto_msg_running = False
        self.auto_msg_thread = None

        self._build_ui()
        self._setup_hotkey_listener()

    def _setup_hotkey_listener(self):
        """Klavye F8 tuşuna basıldığında GUI arayüzündeki buton durumunu senkronize eder."""
        import keyboard
        try:
            keyboard.add_hotkey("f8", self._on_f8_pressed)
        except Exception as e:
            self._log(f"F8 kısayolu bağlanırken uyarı: {e}")

    def _on_f8_pressed(self):
        self.keyboard_engine.toggle()
        self.after(0, self._update_keyboard_ui_status)

    def _build_ui(self):
        # 1. ÜST BAŞLIK (TUGOX HEADER)
        header_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=12, border_width=1, border_color="#30363d")
        header_frame.pack(fill="x", padx=18, pady=(15, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ TUGOX",
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
            text_color="#58a6ff"
        )
        title_label.pack(side="left", padx=20, pady=12)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="// CONTROL HUB: DISCORD & KEYBOARD ENGINE",
            font=ctk.CTkFont(family="Consolas", size=13, weight="normal"),
            text_color="#8b949e"
        )
        subtitle_label.pack(side="left", padx=(0, 20), pady=12)

        self.system_status_badge = ctk.CTkLabel(
            header_frame,
            text="● ÇEVRİMDIŞI",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#f85149",
            fg_color="#21262d",
            corner_radius=6,
            padx=12,
            pady=4
        )
        self.system_status_badge.pack(side="right", padx=20, pady=12)

        # 2. DISCORD TOKEN BAĞLANTI PANELİ
        token_card = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=12, border_width=1, border_color="#30363d")
        token_card.pack(fill="x", padx=18, pady=(0, 10))

        token_top_frame = ctk.CTkFrame(token_card, fg_color="transparent")
        token_top_frame.pack(fill="x", padx=15, pady=(12, 6))

        token_icon_label = ctk.CTkLabel(
            token_top_frame,
            text="🔑 Discord Token:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#c9d1d9"
        )
        token_icon_label.pack(side="left")

        self.token_entry = ctk.CTkEntry(
            token_top_frame,
            placeholder_text="Hesap Tokeninizi buraya girin (User Token veya Bot Token)",
            show="•",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=36,
            fg_color="#0d1117",
            border_color="#30363d"
        )
        self.token_entry.pack(side="left", fill="x", expand=True, padx=12)

        self.show_token_var = ctk.BooleanVar(value=False)
        self.show_token_btn = ctk.CTkCheckBox(
            token_top_frame,
            text="Göster",
            variable=self.show_token_var,
            command=self._toggle_token_visibility,
            width=65,
            font=ctk.CTkFont(size=12)
        )
        self.show_token_btn.pack(side="left", padx=(0, 10))

        self.connect_btn = ctk.CTkButton(
            token_top_frame,
            text="⚡ Hesabı Bağla",
            command=self._connect_discord_account,
            fg_color="#238636",
            hover_color="#2ea043",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=130
        )
        self.connect_btn.pack(side="left")

        # Hesap Profil Durum Alanı
        self.profile_status_label = ctk.CTkLabel(
            token_card,
            text="Durum: Token girilmedi. Lütfen hesabınızı bağlayın.",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#8b949e"
        )
        self.profile_status_label.pack(anchor="w", padx=15, pady=(0, 10))

        # 3. SEÇENEKLER SEKME ALANI (TABVIEW)
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#161b22",
            segmented_button_fg_color="#0d1117",
            segmented_button_selected_color="#1f6feb",
            segmented_button_selected_hover_color="#388bfd",
            corner_radius=12
        )
        self.tabview.pack(fill="both", expand=True, padx=18, pady=(0, 15))

        self.tab_keyboard = self.tabview.add("1. Seçenek: ⌨️ Klavye Botu (L33t)")
        self.tab_automessage = self.tabview.add("2. Seçenek: ✉️ Kanal & DM Oto Mesaj")

        self._build_keyboard_tab()
        self._build_automessage_tab()

    # =========================================================================
    # 1. SEÇENEK: KLAVYE BOTU
    # =========================================================================
    def _build_keyboard_tab(self):
        tab = self.tab_keyboard

        info_box = ctk.CTkFrame(tab, fg_color="#0d1117", corner_radius=8, border_width=1, border_color="#30363d")
        info_box.pack(fill="x", padx=12, pady=10)

        info_text = (
            "📌 Sistem Geneli Klavye Dinleyici Motoru:\n"
            "Klavyede nereye yazarsanız yazın (Not Defteri, Discord, Oyunlar, Tarayıcı),\n"
            "tüm sesli harfler anında sayılara çevrilir (Örn: 'rat' ➡️ 'r4t', 'araba' ➡️ '4r4b4').\n"
            "Kısayol: İstediğiniz an [F8] tuşuna basarak anında durdurabilir veya açabilirsiniz."
        )
        ctk.CTkLabel(
            info_box,
            text=info_text,
            justify="left",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#c9d1d9"
        ).pack(anchor="w", padx=14, pady=10)

        # Kontrol Butonları & Durum
        ctrl_frame = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=12, pady=5)

        self.kb_toggle_btn = ctk.CTkButton(
            ctrl_frame,
            text="▶ Motoru Başlat (F8)",
            command=self._toggle_keyboard_engine,
            fg_color="#238636",
            hover_color="#2ea043",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=200
        )
        self.kb_toggle_btn.pack(side="left", padx=(0, 15))

        self.kb_status_badge = ctk.CTkLabel(
            ctrl_frame,
            text="DURUM: DEVRE DIŞI",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#f85149",
            fg_color="#21262d",
            corner_radius=6,
            padx=14,
            pady=8
        )
        self.kb_status_badge.pack(side="left")

        # Harita Tablosu Önizleme
        map_title = ctk.CTkLabel(
            tab,
            text="Aktif Harf Dönüşüm Kuralları:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#58a6ff"
        )
        map_title.pack(anchor="w", padx=12, pady=(15, 5))

        rules_card = ctk.CTkFrame(tab, fg_color="#0d1117", corner_radius=8, border_width=1, border_color="#30363d")
        rules_card.pack(fill="x", padx=12, pady=5)

        rules_str = (
            "  a, A ➡️ 4    |    e, E ➡️ 3    |    i, ı, İ, I ➡️ 1    |    o, ö, O, Ö ➡️ 0    |    u, ü, U, Ü ➡️ 7"
        )
        ctk.CTkLabel(
            rules_card,
            text=rules_str,
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#7ee787"
        ).pack(pady=10)

        # Hızlı Test Giriş Kutusu
        test_title = ctk.CTkLabel(
            tab,
            text="Canlı Test Alanı (Klavye motorunu açıp burada yazı yazın):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c9d1d9"
        )
        test_title.pack(anchor="w", padx=12, pady=(15, 5))

        self.kb_test_entry = ctk.CTkEntry(
            tab,
            placeholder_text="Motoru başlattıktan sonra buraya 'araba', 'rat', 'okul' yazarak test edin...",
            font=ctk.CTkFont(family="Consolas", size=13),
            height=38,
            fg_color="#0d1117",
            border_color="#30363d"
        )
        self.kb_test_entry.pack(fill="x", padx=12, pady=5)

    def _toggle_keyboard_engine(self):
        self.keyboard_engine.toggle()
        self._update_keyboard_ui_status()

    def _update_keyboard_ui_status(self):
        if self.keyboard_engine.is_active:
            self.kb_toggle_btn.configure(
                text="⏹ Motoru Durdur (F8)",
                fg_color="#da3633",
                hover_color="#f85149"
            )
            self.kb_status_badge.configure(
                text="DURUM: AKTİF ÇALIŞIYOR",
                text_color="#3fb950"
            )
        else:
            self.kb_toggle_btn.configure(
                text="▶ Motoru Başlat (F8)",
                fg_color="#238636",
                hover_color="#2ea043"
            )
            self.kb_status_badge.configure(
                text="DURUM: DEVRE DIŞI",
                text_color="#f85149"
            )

    # =========================================================================
    # 2. SEÇENEK: OTO MESAJ (KANAL & DM)
    # =========================================================================
    def _build_automessage_tab(self):
        tab = self.tab_automessage

        # Hedef Seçimi (Kanal mı DM mi)
        target_frame = ctk.CTkFrame(tab, fg_color="transparent")
        target_frame.pack(fill="x", padx=12, pady=(10, 5))

        target_label = ctk.CTkLabel(
            target_frame,
            text="Hedef Türü:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c9d1d9"
        )
        target_label.pack(side="left", padx=(0, 15))

        self.msg_target_type = ctk.StringVar(value="channel")
        self.radio_channel = ctk.CTkRadioButton(
            target_frame,
            text="📌 Sunucu Kanalı (Kanal ID)",
            variable=self.msg_target_type,
            value="channel",
            font=ctk.CTkFont(size=12)
        )
        self.radio_channel.pack(side="left", padx=(0, 15))

        self.radio_dm = ctk.CTkRadioButton(
            target_frame,
            text="💬 Direkt Mesaj / DM (Kullanıcı ID)",
            variable=self.msg_target_type,
            value="dm",
            font=ctk.CTkFont(size=12)
        )
        self.radio_dm.pack(side="left")

        # Hedef ID Girişi
        id_frame = ctk.CTkFrame(tab, fg_color="transparent")
        id_frame.pack(fill="x", padx=12, pady=5)

        ctk.CTkLabel(
            id_frame,
            text="Hedef ID:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c9d1d9"
        ).pack(side="left", padx=(0, 20))

        self.target_id_entry = ctk.CTkEntry(
            id_frame,
            placeholder_text="Kanal ID veya DM atılacak Kişinin Kullanıcı ID'sini girin (örn: 112233445566778899)",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=34,
            fg_color="#0d1117",
            border_color="#30363d"
        )
        self.target_id_entry.pack(side="left", fill="x", expand=True)

        # Mesaj İçeriği
        msg_label = ctk.CTkLabel(
            tab,
            text="Mesaj İçeriği:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c9d1d9"
        )
        msg_label.pack(anchor="w", padx=12, pady=(10, 3))

        self.message_textbox = ctk.CTkTextbox(
            tab,
            height=75,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#0d1117",
            border_width=1,
            border_color="#30363d"
        )
        self.message_textbox.pack(fill="x", padx=12, pady=(0, 10))
        self.message_textbox.insert("1.0", "TUGOX Otomasyon Mesajı Testi")

        # Ayarlar Satırı (Gecikme & Tekrar)
        settings_frame = ctk.CTkFrame(tab, fg_color="#0d1117", corner_radius=8, border_width=1, border_color="#30363d")
        settings_frame.pack(fill="x", padx=12, pady=5)

        ctk.CTkLabel(
            settings_frame,
            text="Gönderim Aralığı (Saniye):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#c9d1d9"
        ).pack(side="left", padx=(12, 6), pady=8)

        self.delay_entry = ctk.CTkEntry(
            settings_frame,
            width=65,
            height=30,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#161b22",
            border_color="#30363d"
        )
        self.delay_entry.insert(0, "3.0")
        self.delay_entry.pack(side="left", padx=(0, 15), pady=8)

        ctk.CTkLabel(
            settings_frame,
            text="Tekrar Adedi (0 = Sonsuz):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#c9d1d9"
        ).pack(side="left", padx=(0, 6), pady=8)

        self.count_entry = ctk.CTkEntry(
            settings_frame,
            width=65,
            height=30,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#161b22",
            border_color="#30363d"
        )
        self.count_entry.insert(0, "5")
        self.count_entry.pack(side="left", padx=(0, 15), pady=8)

        self.random_jitter_var = ctk.BooleanVar(value=True)
        self.random_jitter_cb = ctk.CTkCheckBox(
            settings_frame,
            text="Anti-Spam (±0.5s Rastgele Gecikme)",
            variable=self.random_jitter_var,
            font=ctk.CTkFont(size=12)
        )
        self.random_jitter_cb.pack(side="left", padx=10, pady=8)

        # Aksiyon Butonları
        action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        action_frame.pack(fill="x", padx=12, pady=10)

        self.send_once_btn = ctk.CTkButton(
            action_frame,
            text="✉ Tek Sefer Gönder",
            command=self._send_single_message_action,
            fg_color="#1f6feb",
            hover_color="#388bfd",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=160
        )
        self.send_once_btn.pack(side="left", padx=(0, 12))

        self.start_auto_btn = ctk.CTkButton(
            action_frame,
            text="▶ Otomasyonu Başlat",
            command=self._start_automessage_action,
            fg_color="#238636",
            hover_color="#2ea043",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=180
        )
        self.start_auto_btn.pack(side="left", padx=(0, 12))

        self.stop_auto_btn = ctk.CTkButton(
            action_frame,
            text="⏹ Durdur",
            command=self._stop_automessage_action,
            fg_color="#da3633",
            hover_color="#f85149",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=120,
            state="disabled"
        )
        self.stop_auto_btn.pack(side="left")

        # Canlı Log / Konsol Çıktı Kutusu
        log_label = ctk.CTkLabel(
            tab,
            text="İşlem & Gönderim Günlüğü (Canlı Log):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8b949e"
        )
        log_label.pack(anchor="w", padx=12, pady=(8, 3))

        self.log_textbox = ctk.CTkTextbox(
            tab,
            height=110,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0d1117",
            text_color="#7ee787",
            border_width=1,
            border_color="#30363d"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    # =========================================================================
    # DISCORD API VE BAĞLANTI İŞLEMLERİ
    # =========================================================================
    def _toggle_token_visibility(self):
        if self.show_token_var.get():
            self.token_entry.configure(show="")
        else:
            self.token_entry.configure(show="•")

    def _log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}\n"
        self.log_textbox.insert("end", line)
        self.log_textbox.see("end")

    def _connect_discord_account(self):
        raw_token = self.token_entry.get().strip().replace('"', '').replace("'", "")
        if not raw_token:
            messagebox.showwarning("Eksik Bilgi", "Lütfen geçerli bir Discord Tokeni girin!")
            return

        self.connect_btn.configure(text="Doğrulanıyor...", state="disabled")
        self.profile_status_label.configure(text="Hesap doğrulanıyor, lütfen bekleyin...", text_color="#d29922")

        # Arka planda sorgula ki arayüz donmasın
        threading.Thread(target=self._verify_token_worker, args=(raw_token,), daemon=True).start()

    def _verify_token_worker(self, token):
        # 1. Önce Kullanıcı Tokeni (User Token) olarak dene
        headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = "https://discord.com/api/v9/users/@me"

        try:
            res = requests.get(url, headers=headers, timeout=8)
            is_bot = False

            if res.status_code == 401:
                # 2. Belki Bot Tokenidir, "Bot " prefixi ile dene
                bot_headers = {
                    "Authorization": f"Bot {token}",
                    "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0)"
                }
                res_bot = requests.get(url, headers=bot_headers, timeout=8)
                if res_bot.status_code == 200:
                    res = res_bot
                    headers = bot_headers
                    is_bot = True

            if res.status_code == 200:
                data = res.json()
                self.token = token
                self.auth_header = headers
                self.is_bot_token = is_bot
                self.account_info = data

                username = data.get("username", "Bilinmiyor")
                discriminator = data.get("discriminator", "0")
                user_id = data.get("id", "0")
                tag = f"{username}#{discriminator}" if discriminator != "0" else username
                account_type = "BOT HESABI" if is_bot else "KULLANICI HESABI"

                self.after(0, lambda: self._on_token_verified_success(tag, user_id, account_type))
            else:
                err_msg = f"Geçersiz Token (HTTP {res.status_code}). Tokeninizi kontrol edin."
                self.after(0, lambda: self._on_token_verified_fail(err_msg))

        except Exception as e:
            self.after(0, lambda: self._on_token_verified_fail(f"Bağlantı Hatası: {str(e)}"))

    def _on_token_verified_success(self, tag, user_id, account_type):
        self.connect_btn.configure(text="✅ Bağlandı", fg_color="#238636", state="normal")
        self.profile_status_label.configure(
            text=f"🟢 Bağlı: {tag} (ID: {user_id}) [{account_type}]",
            text_color="#3fb950"
        )
        self.system_status_badge.configure(text="● BAĞLI", text_color="#3fb950")
        self._log(f"Discord bağlantısı başarılı: {tag} ({account_type})")

    def _on_token_verified_fail(self, error):
        self.connect_btn.configure(text="⚡ Hesabı Bağla", fg_color="#238636", state="normal")
        self.profile_status_label.configure(
            text=f"🔴 Hata: {error}",
            text_color="#f85149"
        )
        self.system_status_badge.configure(text="● BAĞLANTI HATASI", text_color="#f85149")
        self._log(f"HATA: {error}")

    # =========================================================================
    # MESAJ GÖNDERME ÇEKİRDEĞİ (KANAL VEYA DM)
    # =========================================================================
    def _send_discord_message(self, target_type, target_id, content):
        """
        Belirtilen Kanal veya Kullanıcı DM'ine mesaj yollar.
        HTTP 200/201 döndüğünde başarılıdır.
        """
        if not self.auth_header:
            return False, "Önce Discord Token ile bağlanmalısınız!"

        target_channel_id = target_id

        # Eğer hedef bir kullanıcı ID ise (DM ise), önce DM kanalı oluştur veya bul
        if target_type == "dm":
            create_dm_url = "https://discord.com/api/v9/users/@me/channels"
            payload = {"recipient_id": target_id}
            try:
                dm_res = requests.post(create_dm_url, headers=self.auth_header, json=payload, timeout=8)
                if dm_res.status_code in (200, 201):
                    target_channel_id = dm_res.json().get("id")
                else:
                    return False, f"DM Kanalı açılamadı (HTTP {dm_res.status_code}): {dm_res.text}"
            except Exception as e:
                return False, f"DM isteği hatası: {str(e)}"

        # Mesajı kanala ilet
        send_url = f"https://discord.com/api/v9/channels/{target_channel_id}/messages"
        payload = {"content": content}

        try:
            res = requests.post(send_url, headers=self.auth_header, json=payload, timeout=8)
            if res.status_code in (200, 201):
                return True, "Başarılı"
            elif res.status_code == 429:
                retry_after = res.json().get("retry_after", 1.5)
                return False, f"Rate Limit (Hız Sınırı)! {retry_after}s sonra tekrar deneyin."
            else:
                return False, f"HTTP {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"İstek Hatası: {str(e)}"

    def _send_single_message_action(self):
        target_id = self.target_id_entry.get().strip()
        content = self.message_textbox.get("1.0", "end-1c").strip()
        target_type = self.msg_target_type.get()

        if not target_id:
            messagebox.showwarning("Eksik Hedef", "Lütfen Hedef Kanal ID veya Kullanıcı ID girin!")
            return
        if not content:
            messagebox.showwarning("Eksik Mesaj", "Gönderilecek mesaj kutusu boş olamaz!")
            return

        threading.Thread(target=self._single_send_worker, args=(target_type, target_id, content), daemon=True).start()

    def _single_send_worker(self, target_type, target_id, content):
        self._log(f"Tek mesaj gönderiliyor ➡️ Hedef: {target_id} ({target_type.upper()})...")
        ok, msg = self._send_discord_message(target_type, target_id, content)
        if ok:
            self._log(f"✅ Mesaj başarıyla iletildi.")
        else:
            self._log(f"❌ Gönderim başarısız: {msg}")

    def _start_automessage_action(self):
        target_id = self.target_id_entry.get().strip()
        content = self.message_textbox.get("1.0", "end-1c").strip()
        target_type = self.msg_target_type.get()

        if not self.auth_header:
            messagebox.showwarning("Giriş Yapılmadı", "Önce Discord Tokeninizi bağlamalısınız!")
            return
        if not target_id:
            messagebox.showwarning("Eksik Hedef", "Lütfen Hedef Kanal ID veya Kullanıcı ID girin!")
            return
        if not content:
            messagebox.showwarning("Eksik Mesaj", "Gönderilecek mesaj kutusu boş olamaz!")
            return

        try:
            delay = float(self.delay_entry.get().strip())
            if delay < 0.5:
                delay = 0.5
        except ValueError:
            delay = 3.0

        try:
            count = int(self.count_entry.get().strip())
        except ValueError:
            count = 0

        self.auto_msg_running = True
        self.start_auto_btn.configure(state="disabled")
        self.stop_auto_btn.configure(state="normal")
        self.send_once_btn.configure(state="disabled")

        self.auto_msg_thread = threading.Thread(
            target=self._automessage_loop_worker,
            args=(target_type, target_id, content, delay, count),
            daemon=True
        )
        self.auto_msg_thread.start()

    def _stop_automessage_action(self):
        self.auto_msg_running = False
        self._log("⏹ Otomasyon durduruluyor...")
        self.start_auto_btn.configure(state="normal")
        self.stop_auto_btn.configure(state="disabled")
        self.send_once_btn.configure(state="normal")

    def _automessage_loop_worker(self, target_type, target_id, content, delay, count):
        sent = 0
        self._log(f"▶ Otomasyon başlatıldı: {target_id} | Aralık: {delay}s | Adet: {'Sonsuz' if count == 0 else count}")

        while self.auto_msg_running:
            sent += 1
            ok, msg = self._send_discord_message(target_type, target_id, content)

            if ok:
                self._log(f"[{sent}] ✅ Mesaj başarıyla iletildi.")
            else:
                self._log(f"[{sent}] ❌ Hata: {msg}")

            if count > 0 and sent >= count:
                self._log(f"🎉 Belirtilen adet tamamlandı ({count}/{count}).")
                break

            # Gecikme hesapla
            wait_time = delay
            if self.random_jitter_var.get():
                jitter = random.uniform(-0.5, 0.7)
                wait_time = max(0.5, delay + jitter)

            # Uyku döngüsü (anlık durdurmaya yanıt vermesi için küçük parçalarla uyu)
            step = 0.1
            elapsed = 0.0
            while elapsed < wait_time and self.auto_msg_running:
                time.sleep(step)
                elapsed += step

        self.auto_msg_running = False
        self.after(0, self._on_automessage_finished)

    def _on_automessage_finished(self):
        self.start_auto_btn.configure(state="normal")
        self.stop_auto_btn.configure(state="disabled")
        self.send_once_btn.configure(state="normal")
        self._log("Otomasyon döngüsü sona erdi.")

if __name__ == "__main__":
    app = TugoxApp()
    app.mainloop()
