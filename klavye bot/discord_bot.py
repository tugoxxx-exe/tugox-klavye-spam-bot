#!/usr/bin/env python3
"""
Tugox KORKMAZ // Discord Uzaktan Klavye Kontrolcüsü
===================================================
Açıklama: CMD Klavye Motorunu Discord Botuna bağlar.
          Discord sohbet komutlarıyla klavye harf dönüşümünü uzaktan yönetmeyi sağlar.

Geliştirici: Tugox KORKMAZ (aero Red Team / Dev)
"""

import sys
import os
import argparse
import asyncio
import discord
from discord.ext import commands

from vowel_hook import VowelKeyboardHook, DEFAULT_VOWEL_MAP, Colors

class DiscordVowelController(commands.Cog):
    def __init__(self, bot, hook_engine):
        self.bot = bot
        self.engine = hook_engine

    @commands.group(name="vowel", invoke_without_command=True)
    async def vowel_group(self, ctx):
        embed = discord.Embed(
            title="⚡ Tugox KORKMAZ // Klavye Sesli Harf Kontrolörü",
            description="Discord Üzerinden Uzaktan Klavye Dönüştürücü Yönetimi.",
            color=discord.Color.blue()
        )
        status_text = "🟢 ETKİN (Harf Değişimi AÇIK)" if self.engine.is_active else "🔴 DURAKLATILDI (Harf Değişimi KAPALI)"
        embed.add_field(name="Mevcut Klavye Durumu", value=f"`{status_text}`", inline=False)
        embed.add_field(
            name="Kullanılabilir Komutlar",
            value=(
                "`!vowel on` - Harf değişimini aç\n"
                "`!vowel off` - Harf değişimini kapat (normal klavye)\n"
                "`!vowel durum` - Durum ve harita bilgilerini gör\n"
                "`!vowel map <harf>=<sayı>` - Kural ekle/güncelle (Örn: `!vowel map a=4`)\n"
                "`!vowel yardım` - Yardım menüsü"
            ),
            inline=False
        )
        embed.set_footer(text="Tugox KORKMAZ // Red-Team & System Tools")
        await ctx.send(embed=embed)

    @vowel_group.command(name="on")
    async def vowel_on(self, ctx):
        self.engine.enable()
        embed = discord.Embed(
            title="✅ Klavye Dönüştürücü Etkinleştirildi",
            description="Tüm sesli harfler otomatik olarak sayılara dönüştürülüyor (Örn: `rat` ➡️ `r4t`, `araba` ➡️ `4r4b4`).",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @vowel_group.command(name="off")
    async def vowel_off(self, ctx):
        self.engine.disable()
        embed = discord.Embed(
            title="⏸️ Klavye Dönüştürücü Duraklatıldı",
            description="Standart klavye düzenine geri dönüldü.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @vowel_group.command(name="durum")
    async def vowel_status(self, ctx):
        status_str = "ETKİN (Harfler Sayıya Dönüşüyor)" if self.engine.is_active else "DURAKLATILDI (Normal Klavye)"
        
        mapping_lines = []
        distinct_map = {}
        for k, v in self.engine.mapping.items():
            if k.lower() not in distinct_map:
                distinct_map[k.lower()] = v
        
        for vowel, num in distinct_map.items():
            mapping_lines.append(f"• `{vowel}` ➡️ `{num}`")

        embed = discord.Embed(
            title="📊 Tugox KORKMAZ Klavye Motoru Teşhisi",
            color=discord.Color.purple()
        )
        embed.add_field(name="Motor Durumu", value=f"`{status_str}`", inline=False)
        embed.add_field(name="Aktif Harf Dönüşümleri", value="\n".join(mapping_lines), inline=False)
        embed.add_field(name="Yerel Kısayol Tuşu", value=f"`[{self.engine.hotkey.upper()}]`", inline=False)
        await ctx.send(embed=embed)

    @vowel_group.command(name="map")
    async def vowel_map(self, ctx, pair: str):
        if "=" not in pair:
            await ctx.send("❌ Kural biçimi `<harf>=<sayı>` şeklinde olmalıdır, örn: `!vowel map a=4`")
            return

        vowel, val = pair.split("=", 1)
        vowel = vowel.strip()
        val = val.strip()

        if not vowel or not val:
            await ctx.send("❌ Geçersiz harf çifti.")
            return

        self.engine.mapping[vowel.lower()] = val
        self.engine.mapping[vowel.upper()] = val

        if self.engine.is_active:
            self.engine.enable()

        await ctx.send(f"🔄 Kural güncellendi: `{vowel}` ➡️ `{val}`")

def main():
    parser = argparse.ArgumentParser(description="Tugox KORKMAZ Discord Uzaktan Klavye Kontrolcüsü")
    parser.add_argument("--token", type=str, help="Discord Bot Token")
    parser.add_argument("--prefix", type=str, default="!", help="Bot komut ön eki (varsayılan: !)")
    args = parser.parse_args()

    token = args.token or os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print(f"{Colors.RED}[!] Hata: Discord Bot tokeni sağlanmadı.{Colors.RESET}")
        print(f"Kullanım: python discord_bot.py --token DISCORD_BOT_TOKENIZ")
        sys.exit(1)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=args.prefix, intents=intents)
    hook_engine = VowelKeyboardHook()

    @bot.event
    async def on_ready():
        print(f"{Colors.GREEN}[+] Discord sunucusuna bağlandı: {bot.user.name}{Colors.RESET}")
        hook_engine.enable()

    bot.add_cog(DiscordVowelController(bot, hook_engine))

    try:
        bot.run(token)
    except Exception as err:
        print(f"{Colors.RED}[!] Discord Bot Hata: {err}{Colors.RESET}")
    finally:
        hook_engine.cleanup()

if __name__ == "__main__":
    main()
