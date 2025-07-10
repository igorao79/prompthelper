#!/usr/bin/env python3
"""
Простой скрипт сборки EXE файла
Без кириллицы и сложных зависимостей
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Очищает предыдущие сборки"""
    print("🧹 Очистка предыдущих сборок...")
    
    # Удаляем папки
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✅ Удалена папка: {folder}")
    
    # Удаляем spec файлы
    for spec_file in Path('.').glob('*.spec'):
        os.remove(spec_file)
        print(f"   ✅ Удален файл: {spec_file}")

def install_requirements():
    """Устанавливает зависимости"""
    print("📦 Установка зависимостей...")
    
    # Основные зависимости
    required_packages = [
        'tkinter',
        'pillow',
        'requests',
        'pyinstaller',
    ]
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ {package} (уже установлен)")

def create_launcher():
    """Создает простой лаунчер"""
    launcher_code = '''#!/usr/bin/env python3
"""
Простой лаунчер для генератора лендингов
"""

import sys
import os
from pathlib import Path

# Добавляем пути к модулям
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # Импортируем и запускаем главный модуль
    from main import main
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Ошибка запуска: {e}")
    input("Нажмите Enter для выхода...")
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("✅ Создан launcher.py")

def build_exe():
    """Собирает EXE файл"""
    print("🔨 Сборка EXE файла...")
    
    # Параметры сборки
    build_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Один файл
        '--noconsole',                  # Без консоли
        '--name=LandingGenerator',      # Имя без кириллицы
        '--add-data=generators;generators',
        '--add-data=api;api',
        '--add-data=core;core', 
        '--add-data=shared;shared',
        '--hidden-import=tkinter',
        '--hidden-import=PIL',
        '--hidden-import=requests',
        '--hidden-import=json',
        '--hidden-import=threading',
        '--hidden-import=urllib',
        '--hidden-import=pathlib',
        '--hidden-import=datetime',
        '--hidden-import=subprocess',
        '--hidden-import=webbrowser',
        '--hidden-import=winreg',
        'launcher.py'
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        print("✅ EXE файл создан успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 ПРОСТАЯ СБОРКА EXE ФАЙЛА")
    print("=" * 50)
    
    # Проверяем Python
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Рабочая папка: {os.getcwd()}")
    
    # Шаги сборки
    steps = [
        ("Очистка", clean_build),
        ("Установка зависимостей", install_requirements),
        ("Создание лаунчера", create_launcher),
        ("Сборка EXE", build_exe),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📍 {step_name}...")
        try:
            result = step_func()
            if result is False:
                print(f"❌ Ошибка на этапе: {step_name}")
                return False
        except Exception as e:
            print(f"❌ Ошибка на этапе {step_name}: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 СБОРКА ЗАВЕРШЕНА!")
    
    # Проверяем результат
    exe_path = Path('dist/LandingGenerator.exe')
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Файл создан: {exe_path}")
        print(f"📊 Размер: {file_size:.1f} MB")
        print(f"🎯 Готов к использованию!")
    else:
        print("❌ EXE файл не найден!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n⚠️ Сборка не удалась!")
        print("💡 Проверьте ошибки выше")
    
    input("\nНажмите Enter для выхода...") 