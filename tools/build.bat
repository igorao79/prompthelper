@echo off
setlocal

REM Автономный сборщик PromptHelper (Windows)
REM 1) Скачивает ветку linux из igorao79/prompthelper
REM 2) Создаёт виртуальное окружение
REM 3) Устанавливает зависимости
REM 4) Собирает onefile EXE в release/

set REPO=https://github.com/igorao79/prompthelper
set BRANCH=linux
set SCRIPT_DIR=%~dp0

where python >nul 2>nul
if errorlevel 1 (
  echo Python не найден. Установите Python 3.10+ и повторите.
  pause
  exit /b 1
)

python -c "import sys;print(sys.version)" >nul 2>nul || (
  echo Python не запускается.
  pause
  exit /b 1
)

echo Запуск сборщика...
python "%SCRIPT_DIR%builder.py" --repo %REPO% --branch %BRANCH% --mode remote
if errorlevel 1 (
  echo Ошибка сборки.
  pause
  exit /b 1
)

echo Готово. Проверьте папку release\
pause
endlocal


