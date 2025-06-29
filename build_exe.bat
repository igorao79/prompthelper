@echo off
chcp 65001 > nul
echo ====================================
echo 🔥 Компактная сборка без DLL ошибок
echo ====================================

echo.
echo 🧹 Полная очистка перед сборкой...
taskkill /f /im "Генератор_Лендингов.exe" 2>nul
taskkill /f /im "python.exe" 2>nul
timeout /t 2 /nobreak >nul

if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "*.spec" del "*.spec" 2>nul

echo.
echo 📦 Установка чистого PyInstaller...
python -m pip uninstall pyinstaller -y 2>nul
python -m pip install pyinstaller==6.11.1

echo.
echo 🚀 Создание компактного EXE...

python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name="Генератор_Лендингов" ^
    --exclude-module=PIL ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    --exclude-module=tkinter.test ^
    --exclude-module=test ^
    --exclude-module=unittest ^
    --hidden-import=pyautogui ^
    --hidden-import=requests ^
    --distpath="dist" ^
    --workpath="build" ^
    --clean ^
    --noconfirm ^
    main.py

echo.
if exist "dist\Генератор_Лендингов.exe" (
    echo ✅ EXE файл создан успешно!
    
    echo.
    echo 🗂️ Размер файла:
    dir "dist\Генератор_Лендингов.exe" | find ".exe"
    
    echo.
    echo 🧹 Очистка временных файлов...
    if exist "build" rmdir /s /q "build" 2>nul
    if exist "*.spec" del "*.spec" 2>nul
    
    echo.
    echo 🎉 Готово! Запускаю программу...
    start "" "dist\Генератор_Лендингов.exe"
) else (
    echo ❌ Ошибка создания EXE файла!
)

pause 