#!/usr/bin/env python3
"""
Отладка генератора изображений
"""

import os
import tempfile
from pathlib import Path

def debug_image_generator():
    """Отладка генератора изображений"""
    print("🔍 ОТЛАДКА ГЕНЕРАТОРА ИЗОБРАЖЕНИЙ")
    print("=" * 50)
    
    try:
        from generators.image_generator import ImageGenerator
        
        # Создаем временную папку для тестирования
        test_dir = tempfile.mkdtemp()
        print(f"📁 Тестовая папка: {test_dir}")
        
        # Создаем генератор
        generator = ImageGenerator(silent_mode=False, use_icons8_for_favicons=True)
        print("✅ Генератор создан")
        
        # Тестируем генерацию
        theme = "кафе"
        print(f"🎯 Тестируем тему: {theme}")
        
        def progress_callback(msg):
            print(f"📊 Прогресс: {msg}")
        
        # Запускаем генерацию
        result = generator.generate_thematic_set(
            theme_input=theme,
            media_dir=test_dir,
            method="1",
            progress_callback=progress_callback
        )
        
        print(f"🎯 Результат: {result} (тип: {type(result)})")
        
        # Проверяем созданные файлы
        created_files = []
        for file in Path(test_dir).glob("*"):
            if file.is_file():
                created_files.append(file.name)
        
        print(f"📁 Созданные файлы: {created_files}")
        print(f"📊 Количество файлов: {len(created_files)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка отладки: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_image_generator() 