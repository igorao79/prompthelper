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
from shared.settings_manager import SettingsManager
from core.update_checker import UpdateChecker
from gui.qt_main import run_qt


def main():
    """Точка входа: только Qt-версия (PySide6)."""
    print("🚀 Запуск Генератора Лендингов v2.0 (Qt)...")
    try:
        # Проверка обновлений (лог)
        try:
            sm = SettingsManager()
            info = UpdateChecker(sm).check()
            if info.available:
                print("🔔 Доступно обновление ветки linux (igorao79/prompthelper)")
            elif info.message:
                print(f"ℹ️ Проверка обновлений: {info.message}")
        except Exception:
            pass

        run_qt()
        return 0
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")
        return 1


if __name__ == "__main__":
    sys.exit(main())