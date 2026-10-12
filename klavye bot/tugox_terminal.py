#!/usr/bin/env python3
"""
TUGOX // Terminal Kontrol & Discord Otomasyon Hub
=================================================
Geliştirici: aero (Red Team / Dev) & TUGOX
Açıklama:
  - CMD / Terminal Arayüzü (CLI Hub)
  - TUGOX ASCII Banner
  - Discord Token Doğrulama & Hesap Bağlama
  - 1. Seçenek: Sesli Harf -> L33t Klavye Motoru (F8 Kısayollu)
  - 2. Seçenek: Kanal veya DM Otomatik Mesaj Gönderici:
      * Cümle Tekrarı (Spam/Flood), Kelime Kelime, Satır Satır
      * Font & Boyut Biçimlendirme (Discord 36pt H1 Devasa Başlık, Unicode Bold, Gothic, ANSI Renk)
      * Sansür & Spoiler Seçenekleri (||spoiler|| ve AutoMod / Bot Filtresi Bypass)
"""

import sys
import os
import time
import random
import requests
import colorama
from colorama import Fore, Style

# Renkleri Windows CMD'de etkinleştir
colorama.init(autoreset=True)

# Klavye motorunu içe aktar
try:
    from vowel_hook import VowelKeyboardHook, DEFAULT_VOWEL_MAP
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from vowel_hook import VowelKeyboardHook, DEFAULT_VOWEL_MAP

import keyboard

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner(account_text="Bağlantı Yok"):
    clear_screen()
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
  ████████╗██╗   ██╗ ██████╗  ██████╗ ██╗  ██╗
  ╚══██╔══╝██║   ██║██╔════╝ ██╔═══██╗╚██╗██╔╝
     ██║   ██║   ██║██║  ███╗██║   ██║ ╚███╔╝ 
     ██║   ██║   ██║██║   ██║██║   ██║ ██╔██╗ 
     ██║   ╚██████╔╝╚██████╔╝╚██████╔╝██╔╝ ██╗
     ╚═╝    ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
{Fore.WHITE}      [ DISCORD AUTOMATION & HARDWARE HOOK HUB // v2.0 ]
      {Fore.YELLOW}Geliştirici: aero & TUGOX
{Fore.BLUE}══════════════════════════════════════════════════════════════
{Fore.MAGENTA}  [HESAP]: {Fore.GREEN}{account_text}
{Fore.BLUE}══════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
    print(banner)

# =========================================================================
# FONT, BOYUT VE SANSÜR DÖNÜŞTÜRÜCÜLERİ
# =========================================================================
def to_unicode_bold(text):
    """Metni kalın matematiksel Unicode karakterlerine çevirir (𝗕𝗢𝗟𝗗)."""
    res = []
    for c in text:
        if 'A' <= c <= 'Z':
            res.append(chr(ord(c) - ord('A') + 0x1D400))
        elif 'a' <= c <= 'z':
            res.append(chr(ord(c) - ord('a') + 0x1D41A))
        elif '0' <= c <= '9':
            res.append(chr(ord(c) - ord('0') + 0x1D7CE))
        else:
            res.append(c)
    return "".join(res)

def to_unicode_gothic(text):
    """Metni Fraktur / Gothic Unicode karakterlerine çevirir (𝕲𝖔𝖙𝖍𝖎𝖈)."""
    res = []
    for c in text:
        if 'A' <= c <= 'Z':
            res.append(chr(ord(c) - ord('A') + 0x1D56C))
        elif 'a' <= c <= 'z':
            res.append(chr(ord(c) - ord('a') + 0x1D586))
        else:
            res.append(c)
    return "".join(res)

def apply_font_and_size(text, font_choice):
    """
    Discord üzerinde font boyutu ve kalınlık uygular.
    Discord'da 36pt en büyük boyut `# **Metin**` (Header 1) ile elde edilir.
    """
    if font_choice == "1":
        # 36pt Devasa & Kalın Başlık
        return f"# **{text}**"
    elif font_choice == "2":
        # 24pt Büyük Başlık
        return f"## **{text}**"
    elif font_choice == "3":
        # 18pt Orta Başlık
        return f"### {text}"
    elif font_choice == "4":
        # Standart Kalın Metin
        return f"**{text}**"
    elif font_choice == "5":
        # Unicode Kalın Font (𝗕𝗢𝗟𝗗)
        return to_unicode_bold(text)
    elif font_choice == "6":
        # Unicode Gothic Font (𝕲𝖔𝖙𝖍𝖎𝖈)
        return to_unicode_gothic(text)
    elif font_choice == "7":
        # Kırmızı ANSI / Diff Renk Bloğu
        return f"```diff\n- {text}\n```"
    elif font_choice == "8":
        # Yeşil ANSI / Diff Renk Bloğu
        return f"```diff\n+ {text}\n```"
    return text

def apply_censorship_bypass(text, censor_choice):
    """
    Sansürleme ve filtre bypass modları:
    1: Discord Spoiler (||metin|| - Tıklandığında açılan siyah kutu)
    2: Anti-AutoMod / Bot Filtresi Bypass (Harflerin arasına görünmez Zero-Width Space ekler)
    3: Her ikisi birden (Hem spoiler hem filtre bypass)
    """
    if censor_choice == "1":
        return f"||{text}||"
    elif censor_choice == "2":
        # Görünmez karakter (\u200b) harflerin arasına eklenir. Botlar küfrü yakalayamaz ama gözle normal okunur.
        bypassed = "\u200b".join(list(text))
        return bypassed
    elif censor_choice == "3":
        bypassed = "\u200b".join(list(text))
        return f"||{bypassed}||"
    return text

# =========================================================================
# DISCORD API VE KANAL İŞLEMLERİ
# =========================================================================
def verify_discord_token(token):
    token = token.strip().replace('"', '').replace("'", "")
    if not token:
        return None, None, "Token boş olamaz."

    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://discord.com/api/v9/users/@me"

    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            return res.json(), headers, None
        
        bot_headers = {
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0)"
        }
        res_bot = requests.get(url, headers=bot_headers, timeout=8)
        if res_bot.status_code == 200:
            return res_bot.json(), bot_headers, None

        return None, None, f"Geçersiz Token (HTTP {res.status_code})"
    except Exception as e:
        return None, None, f"Bağlantı Hatası: {e}"

def resolve_target_channel(auth_headers, target_type, target_id):
    if target_type == "channel":
        return target_id, None

    target_id = target_id.strip()
    create_dm_url = "https://discord.com/api/v9/users/@me/channels"

    # User token standardı
    try:
        res = requests.post(create_dm_url, headers=auth_headers, json={"recipients": [target_id]}, timeout=8)
        if res.status_code in (200, 201):
            return res.json().get("id"), None
    except Exception:
        pass

    # Bot token standardı
    try:
        res = requests.post(create_dm_url, headers=auth_headers, json={"recipient_id": target_id}, timeout=8)
        if res.status_code in (200, 201):
            return res.json().get("id"), None
    except Exception:
        pass

    # Doğrudan DM Kanal ID'si olma ihtimali
    try:
        check_url = f"https://discord.com/api/v9/channels/{target_id}"
        res = requests.get(check_url, headers=auth_headers, timeout=8)
        if res.status_code == 200:
            return target_id, None
    except Exception:
        pass

    return target_id, "Uyarı: DM kanalı API ile açılamadı, doğrudan ID kanal olarak denenecek."

def send_message_api(auth_headers, channel_id, content):
    send_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {"content": content}

    try:
        res = requests.post(send_url, headers=auth_headers, json=payload, timeout=8)
        if res.status_code in (200, 201):
            return True, "Başarılı (HTTP 200)"
        elif res.status_code == 429:
            retry_after = res.json().get("retry_after", 2.0)
            return False, f"Rate Limit (Hız Sınırı)! {retry_after}s beklenmeli."
        else:
            return False, f"HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"İstek Hatası: {e}"

# =========================================================================
# MENÜLER
# =========================================================================
def run_keyboard_bot():
    """1. Seçenek: Terminal üzerinde Klavye Dönüştürücü Motoru"""
    clear_screen()
    print(f"""{Fore.CYAN}{Style.BRIGHT}
  ╔══════════════════════════════════════════════════════════╗
  ║           ⌨️  TUGOX SESLİ HARF KLAVYE MOTORU            ║
  ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}

  {Fore.YELLOW}Motor Mantığı:{Fore.WHITE}
  Klavyede yazdığınız tüm sesli harfler anında sayılara çevrilir:
    a, A ➡️ 4  |  e, E ➡️ 3  |  i, ı, İ, I ➡️ 1  |  o, ö ➡️ 0  |  u, ü ➡️ 7
  Örnek: 'rat' ➡️ 'r4t', 'araba' ➡️ '4r4b4', 'discord' ➡️ 'd1sc0rd'

  {Fore.GREEN}[F8]{Fore.WHITE} Tuşuna basarak istediğiniz an motoru AÇIP / KAPATABİLİRSİNİZ.
  {Fore.RED}[ESC]{Fore.WHITE} Tuşuna basarak ana menüye dönebilirsiniz.
""")

    engine = VowelKeyboardHook(hotkey="f8")
    engine.enable()
    print(f"{Fore.GREEN}[+] Klavye Motoru Başlatıldı! (Sistem genelinde aktif){Style.RESET_ALL}")
    print(f"{Fore.WHITE}[i] Şimdi herhangi bir yere yazı yazmayı deneyin.{Style.RESET_ALL}\n")

    try:
        while True:
            if keyboard.is_pressed("esc"):
                print(f"\n{Fore.YELLOW}[!] ESC algılandı, ana menüye dönülüyor...{Style.RESET_ALL}")
                engine.disable()
                time.sleep(1)
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        engine.disable()
        print(f"\n{Fore.YELLOW}[!] Motor durduruldu, menüye dönülüyor.{Style.RESET_ALL}")
        time.sleep(1)

def run_auto_messenger(auth_headers, username):
    """2. Seçenek: Terminal Kanal & DM Otomatik Mesaj Gönderici"""
    clear_screen()
    print(f"""{Fore.CYAN}{Style.BRIGHT}
  ╔══════════════════════════════════════════════════════════╗
  ║       ✉️  TUGOX KANAL & DM OTOMATİK MESAJ GÖNDERİCİ      ║
  ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
  {Fore.GREEN}Aktif Gönderici Hesap:{Fore.WHITE} {username}
""")

    print(f"{Fore.YELLOW}[1]{Fore.WHITE} Sunucu Kanalına Mesaj Gönder (Kanal ID)")
    print(f"{Fore.YELLOW}[2]{Fore.WHITE} Kullanıcıya Özel Mesaj / DM Gönder (Kullanıcı ID veya DM Kanal ID)")
    print(f"{Fore.RED}[0]{Fore.WHITE} Geri Dön")

    sub_choice = input(f"\n{Fore.CYAN}Seçiminiz [1/2/0]: {Style.RESET_ALL}").strip()
    if sub_choice == "0":
        return

    if sub_choice == "1":
        target_type = "channel"
        target_prompt = "Hedef Kanal ID: "
    elif sub_choice == "2":
        target_type = "dm"
        target_prompt = "Hedef Kullanıcı ID veya DM Kanal ID: "
    else:
        print(f"{Fore.RED}[!] Geçersiz seçim.{Style.RESET_ALL}")
        time.sleep(1.5)
        return

    target_id = input(f"{Fore.CYAN}{target_prompt}{Style.RESET_ALL}").strip()
    if not target_id:
        print(f"{Fore.RED}[!] Hedef ID boş olamaz!{Style.RESET_ALL}")
        time.sleep(1.5)
        return

    # Hedef Kanalı Çözümle
    print(f"\n{Fore.YELLOW}[~] Hedef kanal çözümleniyor...{Style.RESET_ALL}")
    actual_channel_id, warn_msg = resolve_target_channel(auth_headers, target_type, target_id)
    if warn_msg:
        print(f"{Fore.YELLOW}[!] {warn_msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] Hedef Kanal Doğrulandı: {actual_channel_id}{Style.RESET_ALL}")

    # Mesaj Modu Seçimi
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ 1. GÖNDERİM MODU SEÇİN ═══{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[1]{Fore.WHITE} Cümle Tekrarı (Aynı Cümleyi Tekrar Tekrar Gönder / Flood)")
    print(f"  {Fore.GREEN}[2]{Fore.WHITE} Kelime Kelime Gönderim (Metni Kelimelere Bölüp Sırayla Gönder)")
    print(f"  {Fore.GREEN}[3]{Fore.WHITE} Satır Satır Gönderim (Metni Satırlara Bölüp Sırayla Gönder)")

    mode_choice = input(f"\n{Fore.CYAN}Mod Seçimi [1/2/3]: {Style.RESET_ALL}").strip()
    if mode_choice not in ["1", "2", "3"]:
        mode_choice = "1"

    # Font / Kalınlık / Boyut Seçimi
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ 2. FONT, BOYUT VE KALINLIK SEÇİN ═══{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[0]{Fore.WHITE} Normal Standart Yazı")
    print(f"  {Fore.GREEN}[1]{Fore.WHITE} 💥 36pt Devasa & Kalın Başlık (Discord H1: # **MESAJ**)")
    print(f"  {Fore.GREEN}[2]{Fore.WHITE} 📢 24pt Büyük Başlık (Discord H2: ## **MESAJ**)")
    print(f"  {Fore.GREEN}[3]{Fore.WHITE} 📌 18pt Orta Başlık (Discord H3: ### MESAJ)")
    print(f"  {Fore.GREEN}[4]{Fore.WHITE} ⚡ Kalın Yazı (**MESAJ**)")
    print(f"  {Fore.MAGENTA}[5]{Fore.WHITE} 🔤 Unicode Kalın Font (𝗕𝗢𝗟𝗗)")
    print(f"  {Fore.MAGENTA}[6]{Fore.WHITE} ⚔️ Unicode Gotik Font (𝕲𝖔𝖙𝖍𝖎𝖈)")
    print(f"  {Fore.RED}[7]{Fore.WHITE} 🔴 ANSI Kırmızı Blok (```diff\\n- MESAJ\\n```)")
    print(f"  {Fore.GREEN}[8]{Fore.WHITE} 🟢 ANSI Yeşil Blok (```diff\\n+ MESAJ\\n```)")

    font_choice = input(f"\n{Fore.CYAN}Font & Boyut Seçimi [0-8, Varsayılan 1]: {Style.RESET_ALL}").strip()
    if font_choice not in ["0", "1", "2", "3", "4", "5", "6", "7", "8"]:
        font_choice = "1"

    # Sansür / Spoiler Seçimi
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ 3. SANSÜR VE FİLTRE BYPASS SEÇENEĞİ ═══{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[0]{Fore.WHITE} Yok (Kapalı)")
    print(f"  {Fore.GREEN}[1]{Fore.WHITE} ⬛ Discord Spoiler Sansürü (||MESAJ|| - Tıklayınca Açılan Siyah Kutu)")
    print(f"  {Fore.GREEN}[2]{Fore.WHITE} 🛡️ Anti-AutoMod & Bot Sansür Bypass (Harflerin arasına görünmez boşluk koyar, filtreleri deler)")
    print(f"  {Fore.GREEN}[3]{Fore.WHITE} 💣 Her İkisi (Hem Spoiler Sansürü Hem Anti-Filtre Bypass)")

    censor_choice = input(f"\n{Fore.CYAN}Sansür / Bypass Seçimi [0/1/2/3, Varsayılan 0]: {Style.RESET_ALL}").strip()
    if censor_choice not in ["0", "1", "2", "3"]:
        censor_choice = "0"

    message_content = input(f"\n{Fore.CYAN}Gönderilecek Mesaj / Metin: {Style.RESET_ALL}").strip()
    if not message_content:
        print(f"{Fore.RED}[!] Mesaj içeriği boş olamaz!{Style.RESET_ALL}")
        time.sleep(1.5)
        return

    # Mesaj Parçalarını Hazırla
    if mode_choice == "1":
        raw_parts = [message_content]
        mode_desc = "Cümle Tekrarı (Spam)"
    elif mode_choice == "2":
        raw_parts = message_content.split()
        mode_desc = f"Kelime Kelime ({len(raw_parts)} Kelime)"
        if not raw_parts:
            raw_parts = [message_content]
    else:
        raw_parts = [line.strip() for line in message_content.splitlines() if line.strip()]
        mode_desc = f"Satır Satır ({len(raw_parts)} Satır)"
        if not raw_parts:
            raw_parts = [message_content]

    # Her parçaya font, boyut ve sansür/bypass uygula
    final_parts = []
    for p in raw_parts:
        formatted = apply_font_and_size(p, font_choice)
        formatted = apply_censorship_bypass(formatted, censor_choice)
        final_parts.append(formatted)

    delay_raw = input(f"\n{Fore.CYAN}Gönderim Aralığı / Saniye (Varsayılan 1.0): {Style.RESET_ALL}").strip()
    try:
        delay = float(delay_raw) if delay_raw else 1.0
        if delay < 0.2:
            delay = 0.2
    except ValueError:
        delay = 1.0

    count_raw = input(f"{Fore.CYAN}Tekrar Adedi (0 = Sonsuz Döngü, Varsayılan 0): {Style.RESET_ALL}").strip()
    try:
        count = int(count_raw) if count_raw else 0
    except ValueError:
        count = 0

    jitter_raw = input(f"{Fore.CYAN}Anti-Spam Rastgele Gecikme Eklensin mi? [E/h]: {Style.RESET_ALL}").strip().lower()
    use_jitter = jitter_raw == "e"

    print(f"\n{Fore.GREEN}═══ GÖNDERİM ÖZETİ ═══{Style.RESET_ALL}")
    print(f"Hedef Türü : {target_type.upper()}")
    print(f"Hedef Kanal: {actual_channel_id}")
    print(f"Mod        : {mode_desc}")
    print(f"Örnek Çıktı: '{final_parts[0]}'")
    print(f"Aralık     : {delay}s (+rastgele gecikme: {use_jitter})")
    print(f"Adet       : {'Sonsuz' if count == 0 else count}")
    print(f"{Fore.YELLOW}[Durdurmak için istediğiniz zaman CTRL+C yapabilirsiniz]{Style.RESET_ALL}\n")

    confirm = input(f"{Fore.YELLOW}Başlatılsın mı? [E/h]: {Style.RESET_ALL}").strip().lower()
    if confirm == "h":
        print(f"{Fore.RED}[!] İptal edildi.{Style.RESET_ALL}")
        time.sleep(1)
        return

    print(f"\n{Fore.GREEN}[+] Otomasyon Başlatıldı...{Style.RESET_ALL}\n")

    total_sent = 0

    try:
        while True:
            for part in final_parts:
                total_sent += 1
                timestamp = time.strftime("%H:%M:%S")
                
                preview = part if len(part) <= 40 else part[:37] + "..."
                preview_clean = preview.replace("\n", " ").replace("\u200b", "")
                ok, response_msg = send_message_api(auth_headers, actual_channel_id, part)

                if ok:
                    print(f"{Fore.GREEN}[{timestamp}] [#{total_sent}] [+] İletildi: '{preview_clean}' ➡️ {response_msg}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[{timestamp}] [#{total_sent}] [-] HATA: '{preview_clean}' ➡️ {response_msg}{Style.RESET_ALL}")

                if count > 0 and total_sent >= count:
                    print(f"\n{Fore.CYAN}[✓] Belirtilen gönderim adedi tamamlandı ({total_sent}/{count}).{Style.RESET_ALL}")
                    raise KeyboardInterrupt

                wait_time = delay
                if use_jitter:
                    wait_time = max(0.2, delay + random.uniform(-0.3, 0.5))

                time.sleep(wait_time)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Otomasyon kullanıcı tarafından CTRL+C ile durduruldu. Toplam iletilen: {total_sent}{Style.RESET_ALL}")

    input(f"\n{Fore.WHITE}Menüye dönmek için ENTER'a basın...{Style.RESET_ALL}")

def main():
    account_str = "Bağlantı Yok"
    auth_headers = None

    while not auth_headers:
        print_banner(account_str)
        print(f"{Fore.YELLOW}[ADIM 1] Discord Hesabını Bağlama:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Hesabından işlem yapabilmek için Discord Tokenini girmen gerekiyor.")
        token_input = input(f"\n{Fore.CYAN}[>] Discord Token: {Style.RESET_ALL}").strip()

        if not token_input:
            continue

        print(f"\n{Fore.YELLOW}[~] Token doğrulanıyor...{Style.RESET_ALL}")
        acc_info, headers, err = verify_discord_token(token_input)

        if acc_info:
            auth_headers = headers
            username = acc_info.get("username", "Bilinmiyor")
            discrim = acc_info.get("discriminator", "0")
            tag = f"{username}#{discrim}" if discrim != "0" else username
            account_str = f"{tag} (ID: {acc_info.get('id')})"
            print(f"{Fore.GREEN}[+] Giriş Başarılı: {account_str}{Style.RESET_ALL}")
            time.sleep(1.5)
        else:
            print(f"{Fore.RED}[-] {err}{Style.RESET_ALL}")
            retry = input(f"\n{Fore.WHITE}Tekrar denemek için ENTER, çıkmak için 'q' yazın: {Style.RESET_ALL}").strip().lower()
            if retry == 'q':
                sys.exit(0)

    while True:
        print_banner(account_str)
        print(f"{Fore.CYAN}{Style.BRIGHT}  LÜTFEN BİR SEÇENEK SEÇİN:{Style.RESET_ALL}\n")
        print(f"  {Fore.GREEN}[1]{Fore.WHITE} ⌨️  Klavye Botu (Sesli Harf L33t Dönüştürücü - F8 Kısayolu)")
        print(f"  {Fore.GREEN}[2]{Fore.WHITE} ✉️  Kanal veya DM Otomatik Mesaj Gönderici (Hesabından)")
        print(f"  {Fore.YELLOW}[3]{Fore.WHITE} 🔑  Token Değiştir / Yeniden Bağlan")
        print(f"  {Fore.RED}[0]{Fore.WHITE} 🚪  Çıkış")

        choice = input(f"\n{Fore.CYAN}Komut [1/2/3/0]: {Style.RESET_ALL}").strip()

        if choice == "1":
            run_keyboard_bot()
        elif choice == "2":
            run_auto_messenger(auth_headers, account_str)
        elif choice == "3":
            auth_headers = None
            account_str = "Bağlantı Yok"
            while not auth_headers:
                print_banner(account_str)
                token_input = input(f"{Fore.CYAN}[>] Yeni Discord Token: {Style.RESET_ALL}").strip()
                acc_info, headers, err = verify_discord_token(token_input)
                if acc_info:
                    auth_headers = headers
                    username = acc_info.get("username", "Bilinmiyor")
                    account_str = f"{username} (ID: {acc_info.get('id')})"
                    print(f"{Fore.GREEN}[+] Yeni token bağlandı: {account_str}{Style.RESET_ALL}")
                    time.sleep(1.2)
                else:
                    print(f"{Fore.RED}[-] {err}{Style.RESET_ALL}")
                    time.sleep(1.5)
        elif choice == "0":
            clear_screen()
            print(f"{Fore.CYAN}TUGOX Kapatılıyor. İyi günler.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}[!] Geçersiz seçim.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    main()
