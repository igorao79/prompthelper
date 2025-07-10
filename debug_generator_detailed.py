#!/usr/bin/env python3
"""
Детальная отладка генератора изображений с выводом ошибок
"""

import os
import tempfile
from pathlib import Path
import traceback

def debug_single_image():
    """Отладка генерации одного изображения"""
    print("🔍 ДЕТАЛЬНАЯ ОТЛАДКА ОДНОГО ИЗОБРАЖЕНИЯ")
    print("=" * 50)
    
    try:
        from generators.image_generator import ImageGenerator
        
        # Создаем временную папку для тестирования
        test_dir = tempfile.mkdtemp()
        print(f"📁 Тестовая папка: {test_dir}")
        
        # Создаем генератор
        generator = ImageGenerator(silent_mode=False, use_icons8_for_favicons=True)
        print("✅ Генератор создан")
        
        # Получаем промпты
        prompts, theme_data = generator._generate_prompts("кафе")
        print(f"📝 Промпты получены: {len(prompts)}")
        
        # Тестируем один промпт
        test_prompt = prompts.get('main', 'cozy coffee shop')
        print(f"🎯 Тестируем промпт: {test_prompt}")
        
        # Пробуем генерировать изображение
        try:
            result = generator._generate_image_via_pollinations(test_prompt, 'main', test_dir)
            print(f"🎯 Результат: {result}")
            
            if result:
                print("✅ Изображение создано успешно")
                print(f"📁 Путь: {result}")
            else:
                print("❌ Изображение не создано")
            
        except Exception as e:
            print(f"❌ ОШИБКА в _generate_image_via_pollinations: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

def debug_requests():
    """Отладка requests"""
    print("\n🔍 ОТЛАДКА REQUESTS")
    print("=" * 30)
    
    try:
        import requests
        from urllib.parse import quote
        
        # Простой тест запроса
        test_prompt = "cozy coffee shop interior"
        encoded = quote(test_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&model=flux"
        
        print(f"🌐 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Статус: {response.status_code}")
        print(f"📦 Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            print("✅ Запрос успешен")
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка requests: {e}")
        traceback.print_exc()

def debug_pil():
    """Отладка PIL"""
    print("\n🔍 ОТЛАДКА PIL")
    print("=" * 20)
    
    try:
        from PIL import Image
        from io import BytesIO
        
        # Создаем простое изображение
        img = Image.new('RGB', (100, 100), color='red')
        print("✅ PIL Image создан")
        
        # Тестируем BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        print(f"✅ Сохранение в BytesIO: {len(buffer.getvalue())} байт")
        
    except Exception as e:
        print(f"❌ Ошибка PIL: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_requests()
    debug_pil()
    debug_single_image() 