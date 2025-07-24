# Установка Генератора Фавиконов на Linux 🐧

## Системные Требования

- **Python**: 3.8+ (рекомендуется 3.10+)
- **ОС**: Ubuntu 20.04+, Debian 11+, CentOS 8+, Fedora 35+, или любой современный дистрибутив Linux
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **Место на диске**: ~500MB для установки всех зависимостей

## Установка по Дистрибутивам

### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и системных зависимостей
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    qt5-default \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libxrender1 \
    libxkbcommon-x11-0 \
    libopencv-dev \
    python3-opencv \
    git \
    wget \
    curl
```

### CentOS/RHEL/Fedora

```bash
# Для CentOS/RHEL
sudo yum update -y
sudo yum install -y epel-release
sudo yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    python3-qt5 \
    qt5-qtbase-devel \
    opencv-devel \
    python3-opencv \
    git \
    wget \
    curl

# Для Fedora
sudo dnf update -y
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    python3-qt5 \
    qt5-qtbase-devel \
    opencv-devel \
    python3-opencv \
    git \
    wget \
    curl
```

### Arch Linux

```bash
sudo pacman -Syu
sudo pacman -S \
    python \
    python-pip \
    python-pyqt5 \
    qt5-base \
    opencv \
    python-opencv \
    git \
    wget \
    curl
```

## Установка Приложения

### 1. Скачивание проекта

```bash
# Если у вас есть git репозиторий
git clone <repository_url>
cd prompttest

# Или если у вас есть архив с проектом
wget <archive_url>
unzip archive.zip
cd prompttest
```

### 2. Создание виртуального окружения (Рекомендуется)

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Обновление pip
pip install --upgrade pip
```

### 3. Установка Python зависимостей

```bash
# Установка всех зависимостей из requirements.txt
pip install -r requirements.txt

# Если возникают проблемы, устанавливайте по частям:
pip install requests beautifulsoup4 lxml fake-useragent
pip install opencv-python Pillow numpy pyautogui
pip install PyQt5 PyQt5-tools
pip install rembg onnxruntime
pip install pyyaml pathlib2 chardet scikit-image imageio
```

### 4. Дополнительные настройки для некоторых дистрибутивов

#### Если возникают проблемы с PyQt5:

```bash
# Ubuntu/Debian
sudo apt install python3-pyqt5.qtquick python3-pyqt5.qtwebkit

# Установка через pip если системные пакеты не работают
pip uninstall PyQt5
pip install PyQt5==5.15.9
```

#### Если возникают проблемы с OpenCV:

```bash
# Переустановка OpenCV
pip uninstall opencv-python
pip install opencv-python-headless==4.8.0.76
```

## Запуск Приложения

### Через Python

```bash
# В корневой папке проекта
python3 main.py

# Или
python3 gui.py
```

### Создание ярлыка для рабочего стола

```bash
# Создание .desktop файла
cat > ~/Desktop/favicon-generator.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Генератор Фавиконов
Comment=Генератор тематических фавиконов
Exec=/usr/bin/python3 /путь/к/вашему/проекту/main.py
Icon=/путь/к/вашему/проекту/icon.png
Terminal=false
Categories=Graphics;Development;
EOF

# Сделать исполняемым
chmod +x ~/Desktop/favicon-generator.desktop
```

### Создание скрипта запуска

```bash
# Создание исполняемого скрипта
cat > run_favicon_generator.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python3 main.py
EOF

chmod +x run_favicon_generator.sh

# Теперь можно запускать через
./run_favicon_generator.sh
```

## Решение Возможных Проблем

### Проблема: "ModuleNotFoundError: No module named 'PyQt5'"

```bash
# Решение 1: Системная установка
sudo apt install python3-pyqt5
# или
sudo dnf install python3-qt5

# Решение 2: Через pip
pip install PyQt5==5.15.9
```

### Проблема: "qt.qpa.plugin: Could not load the Qt platform plugin"

```bash
# Установка дополнительных Qt плагинов
sudo apt install qt5-style-plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
```

### Проблема: OpenCV не может найти библиотеки

```bash
# Установка дополнительных библиотек
sudo apt install libgl1-mesa-glx libglib2.0-0
# или
sudo dnf install mesa-libGL glib2
```

### Проблема: Ошибки с rembg/onnxruntime

```bash
# Переустановка с правильной версией
pip uninstall rembg onnxruntime
pip install rembg==2.0.50 onnxruntime==1.16.0
```

## Автозапуск при входе в систему

```bash
# Создание автозапуска (GNOME)
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/favicon-generator.desktop << 'EOF'
[Desktop Entry]
Type=Application
Exec=/путь/к/вашему/проекту/run_favicon_generator.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Генератор Фавиконов
Comment=Автозапуск генератора фавиконов
EOF
```

## Системные Требования для Оптимальной Работы

- **CPU**: 2+ ядра
- **RAM**: 4GB+ (для AI обработки изображений)
- **GPU**: Опционально, для ускорения OpenCV операций
- **Интернет**: Требуется для скачивания моделей AI и работы с внешними API

## Поддерживаемые Дистрибутивы

✅ **Полностью поддерживаются:**
- Ubuntu 20.04+
- Debian 11+
- Fedora 35+
- CentOS 8+
- Arch Linux
- openSUSE Leap 15.4+

⚠️ **Частично поддерживаются:**
- Старые версии Ubuntu (18.04)
- CentOS 7 (требует обновления Python)

❌ **Не поддерживаются:**
- Дистрибутивы без Python 3.8+
- Системы без графической оболочки

## Обновление

```bash
# Обновление зависимостей
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Обновление самого проекта (если git)
git pull origin main
```

## Удаление

```bash
# Удаление виртуального окружения
rm -rf venv

# Удаление проекта
rm -rf /путь/к/проекту

# Удаление автозапуска
rm ~/.config/autostart/favicon-generator.desktop
rm ~/Desktop/favicon-generator.desktop
```

---

**Примечание**: Эта инструкция протестирована на Ubuntu 22.04, Fedora 38, и Arch Linux. Для других дистрибутивов команды могут немного отличаться. 