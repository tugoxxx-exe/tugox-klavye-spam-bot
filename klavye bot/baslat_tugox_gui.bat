@echo off
title TUGOX // Discord Kontrol ve Klavye Arayuzu
color 0B
python tugox_gui.py
if errorlevel 1 (
    echo.
    echo [!] Hata olustu. Bagimliliklari kontrol edin (kurulum.bat calistirin).
    pause
)
