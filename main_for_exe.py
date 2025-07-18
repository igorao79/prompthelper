#!/usr/bin/env python3
"""
Генератор лендингов - версия для EXE
Полнофункциональная версия без проблемных зависимостей
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Импортируем настоящий gui модуль
try:
    from gui import LandingPageGeneratorGUI
    
    def main():
        """Запуск настоящего приложения"""
        print("🚀 Запуск Генератора Лендингов v2.0...")
        
        app = LandingPageGeneratorGUI()
        app.run()
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Ошибка запуска: {e}")
    input("Нажмите Enter для выхода...") 