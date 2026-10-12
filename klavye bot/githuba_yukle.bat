@echo off
chcp 65001 >nul
title Tugox KORKMAZ // GitHub Repo Yükleme Aracı
color 0A

echo =======================================================
echo     Tugox KORKMAZ - GitHub Repo Otomatik Yükleme
echo     Hedef: tugoxxx-exe/tugox-klavye-spam-bot
echo =======================================================
echo.

set "GIT_EXE=git"
where git >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe" (
        set "GIT_EXE=C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"
    ) else (
        echo [!] Git bulunamadı.
        pause
        exit /b 1
    )
)

"%GIT_EXE%" branch -M main >nul 2>&1
"%GIT_EXE%" add .
"%GIT_EXE%" commit -m "feat: Tugox KORKMAZ Klavye Botu v1.0" >nul 2>&1

echo [*] Remote kontrol ediliyor...
"%GIT_EXE%" remote set-url origin https://github.com/tugoxxx-exe/tugox-klavye-spam-bot.git

echo.
echo [*] GitHub'a gönderiliyor (main branch)...
echo [i] Tarayici veya kimlik dogrulama penceresi acilirsa giris yapin.
echo.

"%GIT_EXE%" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo [✓] BAŞARILI! Kodlar GitHub'a yüklendi:
    echo     https://github.com/tugoxxx-exe/tugox-klavye-spam-bot
    echo =======================================================
) else (
    echo.
    echo [!] Hata oluştu. Eğer tarayıcı ile giriş yapamadıysan:
    echo [i] GitHub Token'ın (PAT) varsa şu formatta yükleyebilirsin.
)

echo.
pause
