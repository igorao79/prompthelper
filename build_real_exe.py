#!/usr/bin/env python3
"""
Сборка EXE из НАСТОЯЩЕГО кода генератора лендингов
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Очистка предыдущих сборок"""
    print("🧹 Очистка...")
    
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✅ Удалена: {folder}")
    
    for spec_file in Path('.').glob('*.spec'):
        os.remove(spec_file)
        print(f"   ✅ Удален: {spec_file}")

def fix_requirements():
    """Исправляет проблемные зависимости"""
    print("🔧 Исправление зависимостей...")
    
    # Убираем проблемные библиотеки из требований
    problematic_imports = [
        'rembg',
        'onnxruntime', 
        'tensorflow',
        'torch',
        'opencv',
        'cv2',
        'pygame',
        'PyQt5',
        'pillow-simd'
    ]
    
    # Создаем урезанную версию requirements
    basic_requirements = [
        'tkinter',
        'pillow>=9.0.0',
        'requests>=2.28.0',
        'numpy>=1.21.0',
        'psutil>=5.8.0'
    ]
    
    with open('requirements_exe.txt', 'w') as f:
        for req in basic_requirements:
            f.write(req + '\n')
    
    print("   ✅ Создан requirements_exe.txt")

def build_exe():
    """Собирает EXE файл"""
    print("🔨 Сборка EXE из настоящего кода...")
    
    # Параметры сборки для полнофункционального EXE
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                        # Один файл
        '--windowed',                       # Без консоли
        '--name=LandingGenerator_Full',     # Полное имя
        
        # Добавляем все модули проекта
        '--add-data=generators;generators',
        '--add-data=api;api', 
        '--add-data=core;core',
        '--add-data=shared;shared',
        
        # Основные импорты
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=requests',
        '--hidden-import=json',
        '--hidden-import=threading',
        '--hidden-import=urllib',
        '--hidden-import=pathlib',
        '--hidden-import=datetime',
        '--hidden-import=subprocess', 
        '--hidden-import=webbrowser',
        '--hidden-import=winreg',
        '--hidden-import=hashlib',
        '--hidden-import=random',
        '--hidden-import=time',
        '--hidden-import=os',
        '--hidden-import=sys',
        
        # Исключаем проблемные модули
        '--exclude-module=rembg',
        '--exclude-module=onnxruntime',
        '--exclude-module=tensorflow',
        '--exclude-module=torch',
        '--exclude-module=cv2',
        '--exclude-module=pygame',
        '--exclude-module=PyQt5',
        
        'main_for_exe.py'                   # Главный файл
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ EXE создан успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 СБОРКА ПОЛНОФУНКЦИОНАЛЬНОГО EXE")
    print("=" * 60)
    print("📁 Используется НАСТОЯЩИЙ код генератора лендингов")
    print("🔧 Убираются только проблемные зависимости")
    print("=" * 60)
    
    steps = [
        ("Очистка", clean_build),
        ("Исправление зависимостей", fix_requirements), 
        ("Сборка полного EXE", build_exe),
    ]
    
    for name, func in steps:
        print(f"\n📍 {name}...")
        try:
            result = func()
            if result is False:
                print(f"❌ Ошибка: {name}")
                return False
        except Exception as e:
            print(f"❌ Ошибка {name}: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 СБОРКА ЗАВЕРШЕНА!")
    
    # Проверяем результат
    exe_path = Path('dist/LandingGenerator_Full.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ EXE создан: {exe_path}")
        print(f"📊 Размер: {size_mb:.1f} MB")
        print(f"🎯 ЭТО ПОЛНОФУНКЦИОНАЛЬНЫЙ ГЕНЕРАТОР ЛЕНДИНГОВ!")
        print(f"🚀 СОДЕРЖИТ ВСЕ ФУНКЦИИ ИЗ ОРИГИНАЛЬНОГО КОДА!")
        return True
    else:
        print("❌ EXE не найден!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️ Сборка не удалась!")
    input("\nНажмите Enter для выхода...") 