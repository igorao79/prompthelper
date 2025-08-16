# -*- coding: utf-8 -*-

"""
Главный файл запуска генератора лендингов
Версия 2.0 с улучшениями:
- Поиск в списке стран
- Избранные страны
- Выбор папки для создания проектов
- История тематик (последние 10)
- Редактирование промпта через встроенный редактор
- Автоматическое определение текущего года
- Правильный путь к рабочему столу
- Проверка существования папок
"""

import sys
import os
from pathlib import Path

try:
    from gui import LandingPageGeneratorGUI
    # Qt-версия (опционально)
    try:
        from gui.qt_main import run_qt
        HAS_QT = True
    except Exception:
        HAS_QT = False
    
    def main():
        """Основная функция запуска"""
        print("🚀 Запуск Генератора Лендингов v2.0...")
        
        try:
            # Если доступна PySide6 — запускаем современный Qt UI, иначе Tkinter
            if HAS_QT:
                run_qt()
            else:
                app = LandingPageGeneratorGUI()
                app.run()
        except Exception as e:
            print(f"Ошибка запуска приложения: {e}")
            input("Нажмите Enter для выхода...")
            return 1
        
        return 0

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все необходимые файлы находятся в папке с программой:")
    print("- gui.py")
    print("- shared/helpers.py") 
    print("- shared/data.py")
    print("- generators/prompt_generator.py")
    print("- core/cursor_manager.py")
    input("Нажмите Enter для выхода...")
    sys.exit(1)
    
except Exception as e:
    print(f"Критическая ошибка: {e}")
    input("Нажмите Enter для выхода...")
    sys.exit(1) 