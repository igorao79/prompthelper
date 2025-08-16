#!/usr/bin/env python3
"""
Отладочный скрипт для проверки проблем с созданием лендинга
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_create_landing():
    """Отлаживаем проблему с созданием лендинга"""
    
    print("🐛 ОТЛАДКА СОЗДАНИЯ ЛЕНДИНГА")
    print("=" * 50)
    
    try:
        # Импортируем GUI
        from gui.main_window import LandingPageGeneratorGUI
        
        print("✅ GUI класс импортирован")
        
        # Создаем приложение
        app = LandingPageGeneratorGUI()
        
        print("✅ GUI приложение создано")
        
        # Проверяем все поля формы
        print("\n📋 ПРОВЕРКА ПОЛЕЙ ФОРМЫ:")
        
        print(f"🎯 Тематика: '{app.theme_var.get()}'")
        print(f"🌍 Страна: '{app.selected_country.get()}'")
        print(f"🌐 Домен: '{app.domain_var.get()}'")
        print(f"🏙️ Город: '{getattr(app, 'current_city', 'НЕ УСТАНОВЛЕН')}'")
        print(f"📁 Папка сохранения: '{app.save_path_var.get()}'")
        
        # Устанавливаем тестовые данные
        print("\n🔧 УСТАНОВКА ТЕСТОВЫХ ДАННЫХ:")
        
        app.theme_var.set("шиномонтаж")
        print(f"✅ Тематика установлена: '{app.theme_var.get()}'")
        
        app.selected_country.set("Россия")
        print(f"✅ Страна установлена: '{app.selected_country.get()}'")
        
        app.domain_var.set("shinoservice.ru")
        print(f"✅ Домен установлен: '{app.domain_var.get()}'")
        
        # Генерируем город
        try:
            app.current_city = app.city_generator.get_random_city("Россия")
            print(f"✅ Город сгенерирован: '{app.current_city}'")
        except Exception as e:
            print(f"❌ Ошибка генерации города: {e}")
            app.current_city = "Москва"  # Fallback
            print(f"🔧 Установлен fallback город: '{app.current_city}'")
        
        # Проверяем папку сохранения
        save_path = app.save_path_var.get()
        if Path(save_path).exists():
            print(f"✅ Папка сохранения существует: '{save_path}'")
        else:
            # Устанавливаем рабочий стол как альтернативу
            desktop_path = str(Path.home() / "Desktop")
            if Path(desktop_path).exists():
                app.save_path_var.set(desktop_path)
                print(f"🔧 Папка изменена на: '{desktop_path}'")
            else:
                # Используем домашнюю папку
                home_path = str(Path.home())
                app.save_path_var.set(home_path)
                print(f"🔧 Папка изменена на: '{home_path}'")
        
        # Тестируем валидацию
        print("\n🔍 ТЕСТИРОВАНИЕ ВАЛИДАЦИИ:")
        
        is_valid, error_msg = app.validate_form()
        if is_valid:
            print("✅ Валидация прошла успешно!")
        else:
            print(f"❌ Ошибка валидации: {error_msg}")
            return False
        
        # Тестируем импорты, которые могут вызвать проблемы
        print("\n📦 ПРОВЕРКА ИМПОРТОВ:")
        
        try:
            from generators.prompt_generator import create_landing_prompt
            print("✅ create_landing_prompt импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта create_landing_prompt: {e}")
            return False
        
        try:
            from shared.helpers import validate_domain, get_language_by_country
            print("✅ shared.helpers импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта shared.helpers: {e}")
            return False
        
        try:
            from core.cursor_manager import CursorManager
            print("✅ CursorManager импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта CursorManager: {e}")
            return False
        
        # Попробуем вызвать метод создания лендинга
        print("\n🎬 ИМИТАЦИЯ СОЗДАНИЯ ЛЕНДИНГА:")
        
        print("📋 Готовые данные для создания:")
        theme = app.theme_var.get().strip()
        country = app.selected_country.get()
        domain = app.domain_var.get().strip()
        city = app.current_city
        save_path = app.save_path_var.get()
        
        print(f"  • Тематика: {theme}")
        print(f"  • Страна: {country}")
        print(f"  • Домен: {domain}")
        print(f"  • Город: {city}")
        print(f"  • Папка: {save_path}")
        
        # Проверяем что все импорты и данные готовы
        try:
            language = get_language_by_country(country)
            print(f"  • Язык: {language}")
        except Exception as e:
            print(f"❌ Ошибка получения языка: {e}")
            return False
        
        print("\n🎯 РЕЗУЛЬТАТ ОТЛАДКИ:")
        print("✅ Все проверки пройдены успешно!")
        print("✅ Форма готова к созданию лендинга")
        print("✅ Все импорты работают")
        
        print("\n💡 ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМЫ:")
        print("1. Ошибка в threaded процессе (_create_landing_process)")
        print("2. Проблема с cursor_manager.create_project_structure")
        print("3. Блокировка GUI thread")
        print("4. Ошибка без вывода сообщения")
        
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        print("• Проверьте консоль на ошибки при нажатии кнопки")
        print("• Убедитесь что все поля формы заполнены")
        print("• Попробуйте запустить приложение из терминала для вывода ошибок")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка отладки: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🐛 ЗАПУСК ОТЛАДКИ СОЗДАНИЯ ЛЕНДИНГА")
        
        success = debug_create_landing()
        
        if success:
            print("\n✅ Отладка завершена успешно")
            print("💡 Если проблема сохраняется, запустите главное приложение через терминал:")
            print("   python3 main.py")
        else:
            print("\n❌ Отладка выявила проблемы")
            
    except KeyboardInterrupt:
        print("\n👋 Отладка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка отладки: {e}")
        import traceback
        traceback.print_exc() 