#!/usr/bin/env python3
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
