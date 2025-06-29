@echo off
chcp 65001 >nul
echo =================================
echo  Генератор Лендингов - Сборка EXE
echo =================================
echo.

echo Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Ошибка: Python не найден!
    echo Установите Python с python.org
    pause
    exit /b 1
)

echo.
echo 📦 Установка зависимостей...
pip install -r requirements.txt

echo.
echo 🔨 Очистка предыдущих сборок...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

echo.
echo 🚀 Компиляция в .exe файл...
pyinstaller --onefile --windowed --name="Генератор_Лендингов" --icon=favicon.ico main.py 2>nul
if not exist favicon.ico (
    pyinstaller --onefile --windowed --name="Генератор_Лендингов" main.py
)

echo.
if exist "dist\Генератор_Лендингов.exe" (
    echo ✅ Успешно! EXE файл создан: dist\Генератор_Лендингов.exe
    echo.
    echo 📊 Размер файла:
    dir "dist\Генератор_Лендингов.exe" | find "Генератор_Лендингов.exe"
    echo.
    echo 🧹 Очистка временных файлов...
    if exist "build" rmdir /s /q "build"
    if exist "*.spec" del "*.spec"
    echo.
    echo ✨ Готово! Можете использовать файл: dist\Генератор_Лендингов.exe
    echo.
    echo 🚀 Хотите запустить программу? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" start "" "dist\Генератор_Лендингов.exe"
) else (
    echo ❌ Ошибка создания EXE файла!
    echo Проверьте логи выше для деталей
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul 