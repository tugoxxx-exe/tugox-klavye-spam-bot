#!/usr/bin/env python3
"""
Tugox KORKMAZ // Sesli Harf L33t Klavye Dönüştürücü Motoru
=========================================================
Açıklama: Windows klavye girdilerini CMD üzerinden dinler ve değiştirir.
          Yazılan tüm sesli harfleri anında l33tspeak sayı karşılıklarıyla değiştirir.
          Örnek: "rat" -> "r4t", "discord" -> "d1sc0rd", "araba" -> "4r4b4", "okul" -> "0k7l".

Yazar: aero (Red Team / Dev)
Geliştirici: Tugox KORKMAZ
"""

import sys
import os
import time
import argparse
import keyboard

# CMD Renk Kodları
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Varsayılan Türkçe ve İngilizce Sesli Harf Haritası
DEFAULT_VOWEL_MAP = {
    # Küçük sesli harfler
    'a': '4',
    'e': '3',
    'i': '1',
    'ı': '1',
    'o': '0',
    'ö': '0',
    'u': '7',
    'ü': '7',

    # Büyük sesli harfler
    'A': '4',
    'E': '3',
    'I': '1',
    'İ': '1',
    'O': '0',
    'Ö': '0',
    'U': '7',
    'Ü': '7',
}

class VowelKeyboardHook:
    def __init__(self, mapping=None, hotkey="f8"):
        self.mapping = mapping if mapping else DEFAULT_VOWEL_MAP.copy()
        self.hotkey = hotkey.lower()
        self.is_active = False
        self.remap_handles = []

    def enable(self):
        """Windows klavye taranan kodlarında harf değişimini etkinleştirir."""
        if self.is_active:
            return

        self.disable()
        self.remap_handles.clear()

        for src_key, dst_key in self.mapping.items():
            try:
                handle = keyboard.remap_key(src_key, dst_key)
                self.remap_handles.append(handle)
            except Exception as err:
                print(f"{Colors.RED}[!] Harf dönüştürme hatası '{src_key}' -> '{dst_key}': {err}{Colors.RESET}")

        self.is_active = True
        print(f"{Colors.GREEN}[+] Klavye Dönüştürücü : ETKİN [ÇALIŞIYOR]{Colors.RESET}")

    def disable(self):
        """Harf değişimini devre dışı bırakır ve standart klavyeyi geri yükler."""
        if not self.is_active and not self.remap_handles:
            return

        for handle in self.remap_handles:
            try:
                keyboard.unremap_key(handle)
            except Exception:
                pass

        self.remap_handles.clear()
        self.is_active = False
        print(f"{Colors.YELLOW}[-] Klavye Dönüştürücü : DEVRE DIŞI [DURDURULDU]{Colors.RESET}")

    def toggle(self):
        """Kısayol tuşu ile durumu değiştirir (AÇIK / KAPALI)."""
        if self.is_active:
            self.disable()
        else:
            self.enable()

    def print_banner(self):
        banner = f"""{Colors.CYAN}{Colors.BOLD}
================================================================================================
 ████████╗██╗   ██╗██████╗  ██████╗ ██╗  ██╗    ██╗  ██╗██████╗ ██████╗ ██╗  ██╗███╗   ███╗██████╗ ███████╗
 ╚══██╔══╝██║   ██║██╔════╝ ██╔═══██╗╚██╗██╔╝    ██║ ██╔╝██╔═══██╗██╔══██╗██║ ██╔╝████╗ ████║██╔══██╗╚══███╔╝
    ██║   ██║   ██║██║  ███╗██║   ██║ ╚███╔╝     █████═╝ ██║   ██║██████╔╝█████═╝ ██╔████╔██║███████║  ███╔╝ 
    ██║   ██║   ██║██║   ██║██║   ██║ ██╔██╗     ██╔═██╗ ██║   ██║██╔══██╗██╔═██╗ ██║╚██╔╝██║██╔══██║ ███╔╝  
    ██║   ╚██████╔╝╚██████╔╝╚██████╔╝██╔╝ ██╗    ██║  ██╗╚██████╔╝██║  ██║██║  ██╗██║ ╚═╝ ██║██║  ██║███████╗
    ╚═╝    ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
================================================================================================{Colors.RESET}
{Colors.MAGENTA}[*] Proje Sahibi     : Tugox KORKMAZ{Colors.RESET}
{Colors.MAGENTA}[*] Çalışma Modu     : Bağımsız CMD Klavye Motoru{Colors.RESET}
{Colors.CYAN}[+] Aç/Kapat Tuşu    : [{self.hotkey.upper()}] (Sistem genelinde istediğiniz yerde basın){Colors.RESET}
{Colors.GREEN}[+] Çıkış Tuşu       : [ESC] veya [CTRL+C] (bu CMD penceresinde){Colors.RESET}
{Colors.YELLOW}[+] Hedef Harfler    : {', '.join(sorted(set(self.mapping.keys())))}
================================================================================================
{Colors.BOLD}Aktif Harf Dönüşüm Kuralları:{Colors.RESET}"""
        print(banner)

        distinct_map = {}
        for k, v in self.mapping.items():
            if k.lower() not in distinct_map:
                distinct_map[k.lower()] = v

        for vowel, num in distinct_map.items():
            print(f"  - '{Colors.BOLD}{vowel}{Colors.RESET}' -> '{Colors.GREEN}{num}{Colors.RESET}'")

        print(f"{Colors.CYAN}================================================================================================{Colors.RESET}\n")

    def run(self):
        """CMD ana dinleme döngüsünü başlatır."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

        try:
            keyboard.add_hotkey(self.hotkey, self.toggle)
        except Exception as e:
            print(f"{Colors.RED}[!] Kısayol tuşu atanamadı [{self.hotkey}]: {e}{Colors.RESET}")

        self.enable()

        print(f"\n{Colors.GREEN}[*] Tüm sistem tuşları dinleniyor... Herhangi bir metin kutusunda veya CMD'de yazmayı deneyin!{Colors.RESET}\n")

        try:
            keyboard.wait('esc')
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        """Klavye bağlantılarını temizler ve klavyeyi orijinal haline getirir."""
        print(f"\n{Colors.YELLOW}[*] Tugox KORKMAZ Klavye Motoru kapatılıyor...{Colors.RESET}")
        self.disable()
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        print(f"{Colors.GREEN}[+] Klavye bağlantıları temizlendi. Standart klavye düzeni yüklendi.{Colors.RESET}")


def parse_custom_map(map_str):
    custom_map = {}
    pairs = map_str.split(',')
    for pair in pairs:
        if '=' in pair:
            k, v = pair.split('=', 1)
            k = k.strip()
            v = v.strip()
            if k and v:
                custom_map[k.lower()] = v
                custom_map[k.upper()] = v
    return custom_map


def main():
    parser = argparse.ArgumentParser(
        description="Tugox KORKMAZ // CMD Sesli Harf L33t Klavye Dönüştürücü",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  python vowel_hook.py
  python vowel_hook.py --hotkey f12
  python vowel_hook.py --custom "a=4,e=3,i=1,o=0,u=7,ü=7,ö=0"
"""
    )
    parser.add_argument("--hotkey", type=str, default="f8", help="Dönüştürücüyü duraklatma/başlatma tuşu (Varsayılan: f8)")
    parser.add_argument("--custom", type=str, default="", help="Özel harf değiştirme kuralı ('a=4,e=3' şeklinde)")

    args = parser.parse_args()

    vowel_map = DEFAULT_VOWEL_MAP.copy()
    if args.custom:
        parsed = parse_custom_map(args.custom)
        if parsed:
            vowel_map.update(parsed)

    engine = VowelKeyboardHook(mapping=vowel_map, hotkey=args.hotkey)
    engine.run()

if __name__ == "__main__":
    main()
