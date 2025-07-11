#!/bin/bash

# Генератор лендингов - скрипт установки для Linux
# Версия 2.0 с кроссплатформенной поддержкой

echo "🐧 Установка Генератора Лендингов для Linux"
echo "=============================================="

# Определяем дистрибутив
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo "📊 Обнаружен дистрибутив: $PRETTY_NAME"
else
    echo "❌ Не удалось определить дистрибутив Linux"
    DISTRO="unknown"
fi

# Функция установки системных пакетов
install_system_packages() {
    echo ""
    echo "📦 Установка системных пакетов..."
    
    case $DISTRO in
        "ubuntu"|"debian"|"linuxmint"|"pop")
            echo "🔧 Установка пакетов для Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-tk python3-pil python3-pil.imagetk
            sudo apt install -y fonts-noto-color-emoji fonts-dejavu fonts-liberation
            sudo apt install -y curl wget
            ;;
        "fedora"|"centos"|"rhel")
            echo "🔧 Установка пакетов для Fedora/CentOS..."
            sudo dnf install -y python3 python3-pip python3-tkinter python3-pillow
            sudo dnf install -y google-noto-emoji-color-fonts dejavu-fonts liberation-fonts
            sudo dnf install -y curl wget
            ;;
        "arch"|"manjaro")
            echo "🔧 Установка пакетов для Arch Linux..."
            sudo pacman -S --noconfirm python python-pip tk python-pillow
            sudo pacman -S --noconfirm noto-fonts-emoji ttf-dejavu ttf-liberation
            sudo pacman -S --noconfirm curl wget
            ;;
        "opensuse"|"sles")
            echo "🔧 Установка пакетов для openSUSE..."
            sudo zypper install -y python3 python3-pip python3-tk python3-Pillow
            sudo zypper install -y noto-coloremoji-fonts dejavu-fonts liberation-fonts
            sudo zypper install -y curl wget
            ;;
        *)
            echo "⚠️ Неизвестный дистрибутив. Убедитесь что установлены:"
            echo "   - Python 3.6+"
            echo "   - python3-tk (tkinter)"
            echo "   - python3-pip"
            echo "   - Шрифты: Noto Color Emoji, DejaVu, Liberation"
            ;;
    esac
}

# Функция установки Python зависимостей
install_python_packages() {
    echo ""
    echo "🐍 Установка Python зависимостей..."
    
    # Проверяем наличие pip
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 не найден. Устанавливаем pip..."
        sudo apt install -y python3-pip 2>/dev/null || \
        sudo dnf install -y python3-pip 2>/dev/null || \
        sudo pacman -S --noconfirm python-pip 2>/dev/null
    fi
    
    # Устанавливаем минимальные зависимости
    echo "📋 Установка основных библиотек..."
    pip3 install --user requests beautifulsoup4 lxml Pillow numpy
    
    # Опционально устанавливаем pyautogui если пользователь хочет
    echo ""
    read -p "🤖 Установить pyautogui для автовставки промптов? (может требовать X11) [y/N]: " install_pyautogui
    if [[ $install_pyautogui =~ ^[Yy]$ ]]; then
        pip3 install --user pyautogui
        echo "✅ pyautogui установлен"
    else
        echo "ℹ️ pyautogui пропущен (автовставка промптов будет отключена)"
    fi
}

# Функция создания desktop файла
create_desktop_entry() {
    echo ""
    echo "🖥️ Создание ярлыка для рабочего стола..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
    DESKTOP_FILE="$HOME/.local/share/applications/landing-generator.desktop"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Генератор Лендингов
Comment=Генератор лендинг-страниц v2.0
Exec=python3 "$SCRIPT_DIR/main.py"
Icon=applications-development
Path=$SCRIPT_DIR
Terminal=false
Categories=Development;Office;
EOF
    
    chmod +x "$DESKTOP_FILE"
    echo "✅ Ярлык создан: $DESKTOP_FILE"
}

# Функция создания скрипта запуска
create_launcher() {
    echo ""
    echo "🚀 Создание скрипта запуска..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
    LAUNCHER="$SCRIPT_DIR/run_linux.sh"
    
    cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# Скрипт запуска Генератора Лендингов в Linux

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Запуск Генератора Лендингов..."
echo "Директория: $SCRIPT_DIR"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден!"
    exit 1
fi

# Запускаем приложение
python3 main.py

echo "👋 Генератор Лендингов завершен"
EOF
    
    chmod +x "$LAUNCHER"
    echo "✅ Скрипт запуска создан: $LAUNCHER"
}

# Функция проверки Cursor AI
check_cursor() {
    echo ""
    echo "🔍 Проверка наличия Cursor AI..."
    
    if command -v cursor &> /dev/null; then
        echo "✅ Cursor найден в PATH: $(which cursor)"
        return 0
    fi
    
    # Проверяем популярные места установки
    CURSOR_PATHS=(
        "$HOME/cursor.AppImage"
        "$HOME/Cursor.AppImage" 
        "$HOME/Downloads/cursor.AppImage"
        "$HOME/Downloads/Cursor.AppImage"
        "/usr/bin/cursor"
        "/usr/local/bin/cursor"
        "/opt/cursor/cursor"
        "/snap/cursor/current/cursor"
    )
    
    for path in "${CURSOR_PATHS[@]}"; do
        if [ -f "$path" ]; then
            echo "✅ Cursor найден: $path"
            return 0
        fi
    done
    
    echo "⚠️ Cursor AI не найден. Варианты установки:"
    echo "   1. AppImage: скачать с https://cursor.so"
    echo "   2. Snap: sudo snap install cursor"
    echo "   3. Flatpak: flatpak install flathub com.cursor.Cursor"
    echo "   4. Deb пакет: скачать .deb с официального сайта"
    echo ""
    echo "   Программа будет работать и без Cursor AI"
    echo "   (промпты будут копироваться в буфер обмена)"
}

# Главная функция
main() {
    echo ""
    echo "Этот скрипт установит:"
    echo "• Системные пакеты (Python, tkinter, шрифты)"
    echo "• Python библиотеки (requests, Pillow, и др.)"
    echo "• Ярлык на рабочем столе"
    echo "• Скрипт запуска"
    echo ""
    
    read -p "Продолжить установку? [Y/n]: " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "❌ Установка отменена"
        exit 0
    fi
    
    install_system_packages
    install_python_packages
    create_desktop_entry
    create_launcher
    check_cursor
    
    echo ""
    echo "🎉 УСТАНОВКА ЗАВЕРШЕНА!"
    echo "=============================="
    echo ""
    echo "📍 Как запустить:"
    echo "   1. Через ярлык в меню приложений"
    echo "   2. Командой: ./run_linux.sh"
    echo "   3. Напрямую: python3 main.py"
    echo ""
    echo "📂 Лендинги будут создаваться в: ~/Desktop"
    echo ""
    echo "🐛 При проблемах проверьте requirements_linux.txt"
    echo "   или установите зависимости вручную:"
    echo "   pip3 install -r requirements_linux.txt"
    echo ""
    echo "✨ Готово! Приятного использования!"
}

# Запускаем установку
main 