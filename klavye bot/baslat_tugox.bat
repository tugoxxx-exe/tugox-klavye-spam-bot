@echo off
title TUGOX // Discord Kontrol ve Klavye Terminal Motoru
color 0B
python tugox_terminal.py
if errorlevel 1 (
    echo.
    echo [!] Hata olustu.
    pause
)
