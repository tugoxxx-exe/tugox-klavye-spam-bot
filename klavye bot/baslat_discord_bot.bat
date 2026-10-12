@echo off
title Tugox KORKMAZ - Discord Bot Kontrolcusu
color 0D
echo ===================================================
echo   Tugox KORKMAZ // Discord Bot Baslatiliyor
echo ===================================================
set /p TOKEN="Discord Bot Tokeninizi Girin: "
python discord_bot.py --token %TOKEN%
pause
