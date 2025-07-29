#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ПАРАЛЛЕЛЬНЫЙ ГЕНЕРАТОР ИЗОБРАЖЕНИЙ 🚀
Генерирует промпты и картинки ОДНОВРЕМЕННО для максимальной скорости!
"""

import os
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image
from io import BytesIO
import requests
from urllib.parse import quote
import hashlib

class ParallelImageGenerator:
    """🚀 Параллельный генератор - промпты и картинки одновременно!"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.generated_prompts = {}
        self.generation_results = {}
        
        if not self.silent_mode:
            print("🚀 ParallelImageGenerator - ПАРАЛЛЕЛЬНАЯ ГЕНЕРАЦИЯ!")
    
    def generate_thematic_set_parallel(self, theme_input, media_dir, method="1", progress_callback=None):
        """
        🚀 ПАРАЛЛЕЛЬНАЯ генерация - промпты и картинки одновременно!
        """
        if not self.silent_mode:
            print(f"🚀 ПАРАЛЛЕЛЬНАЯ генерация для: {theme_input}")
        
        if progress_callback:
            progress_callback("🚀 Запуск параллельной генерации...")
        
        # Создаем папку
        os.makedirs(media_dir, exist_ok=True)
        
        image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
        
        # 🚀 ЭТАП 1: Быстро генерируем fallback промпты и начинаем генерацию картинок
        if progress_callback:
            progress_callback("⚡ Создание базовых промптов...")
        
        fallback_prompts = self._generate_fallback_prompts_fast(theme_input)
        self.generated_prompts = fallback_prompts.copy()
        
        # 🚀 ЭТАП 2: Запускаем ВСЕ процессы параллельно
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            
            # 🧠 ЗАДАЧА 1: Генерация качественных промптов (в фоне)
            if progress_callback:
                progress_callback("🧠 Запуск качественных промптов в фоне...")
            
            future_prompts = executor.submit(self._generate_quality_prompts_async, theme_input)
            futures.append(('prompts', future_prompts))
            
            # 🎨 ЗАДАЧА 2-9: Генерация всех картинок параллельно (сразу с fallback промптами)
            if progress_callback:
                progress_callback("🎨 Запуск генерации всех картинок...")
            
            for i, image_name in enumerate(image_names):
                prompt = fallback_prompts.get(image_name, f'professional {theme_input} service')
                future_image = executor.submit(
                    self._generate_image_with_retry, 
                    prompt, image_name, media_dir, i+1, len(image_names)
                )
                futures.append((image_name, future_image))
            
            # 🔄 ЭТАП 3: Собираем результаты по мере готовности
            generated_count = 0
            quality_prompts_ready = False
            
            for future in as_completed([f[1] for f in futures]):
                # Находим какая задача завершилась
                for task_name, task_future in futures:
                    if task_future == future:
                        try:
                            result = future.result()
                            
                            if task_name == 'prompts':
                                # 🧠 Качественные промпты готовы!
                                if result:
                                    self.generated_prompts.update(result)
                                    quality_prompts_ready = True
                                    if not self.silent_mode:
                                        print("✅ Качественные промпты готовы!")
                                    if progress_callback:
                                        progress_callback("✅ Качественные промпты готовы!")
                            
                            elif result:  # Картинка готова
                                generated_count += 1
                                if not self.silent_mode:
                                    print(f"✅ {task_name}: Создано ({generated_count}/{len(image_names)})")
                                if progress_callback:
                                    progress_callback(f"✅ Готово {generated_count}/{len(image_names)} картинок")
                        
                        except Exception as e:
                            if not self.silent_mode:
                                print(f"❌ Ошибка {task_name}: {e}")
                        break
        
        # 🎯 ЭТАП 4: Опционально регенерируем картинки с качественными промптами
        if quality_prompts_ready and generated_count < len(image_names):
            if progress_callback:
                progress_callback("🔄 Улучшение картинок качественными промптами...")
            
            # Регенерируем только неудачные картинки с новыми промптами
            self._regenerate_failed_images(theme_input, media_dir, image_names, generated_count)
        
        if not self.silent_mode:
            print(f"🎯 ПАРАЛЛЕЛЬНАЯ генерация завершена: {generated_count}/{len(image_names)}")
        
        if progress_callback:
            progress_callback(f"🎉 Завершено: {generated_count}/{len(image_names)} изображений")
        
        return generated_count
    
    def _generate_fallback_prompts_fast(self, theme_input):
        """⚡ Мгновенная генерация базовых промптов"""
        
        # Специальная обработка для разных тематик
        if 'участк' in theme_input.lower() or 'дача' in theme_input.lower():
            return {
                'main': "beautiful rural property with scenic countryside views and development potential",
                'about1': "professional real estate consultation with property documents and plans",
                'about2': "land survey equipment and property measurement tools",
                'about3': "rural property development and planning documentation",
                'review1': "satisfied property buyer smiling happily with rural landscape background",
                'review2': "pleased customer at rural property with natural surroundings",
                'review3': "grateful client reviewing property documents outdoors",
                'favicon': "simple house icon with tree symbol minimalist property logo"
            }
        
        # Обычные fallback промпты
        return {
            'main': f'professional {theme_input} service office modern high quality',
            'about1': f'modern {theme_input} professional equipment workspace',
            'about2': f'expert {theme_input} team working with professional tools',
            'about3': f'quality {theme_input} facility with modern standards',
            'review1': 'satisfied customer smiling happy positive professional photo',
            'review2': 'pleased client confident satisfied expression headshot',
            'review3': 'grateful person positive smile content photograph',
            'favicon': f'{theme_input} simple minimalist icon logo business symbol'
        }
    
    def _generate_quality_prompts_async(self, theme_input):
        """🧠 Генерация качественных промптов в фоновом режиме"""
        try:
            if not self.silent_mode:
                print("🧠 Запуск DeepSeek для качественных промптов...")
            
            # Генерируем через DeepSeek/Ollama
            from generators.ollama_ai_enhancer import create_ollama_enhanced_prompts
            quality_prompts = create_ollama_enhanced_prompts(theme_input)
            
            if not self.silent_mode:
                print("✅ DeepSeek промпты готовы!")
            
            return quality_prompts
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка качественных промптов: {e}")
            return None
    
    def _generate_image_with_retry(self, prompt, image_name, media_dir, current, total):
        """🎨 Генерация одной картинки с повторными попытками"""
        try:
            if not self.silent_mode:
                print(f"🎨 Генерация {image_name} ({current}/{total}): {prompt[:50]}...")
            
            # Генерируем через Pollinations API
            result = self._generate_image_pollinations_fast(prompt, image_name, media_dir)
            
            if result:
                if not self.silent_mode:
                    print(f"✅ {image_name}: Успешно создано")
                return result
            else:
                if not self.silent_mode:
                    print(f"❌ {image_name}: Не удалось создать")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка {image_name}: {e}")
            return None
    
    def _generate_image_pollinations_fast(self, prompt, image_name, media_dir):
        """🌐 БЫСТРАЯ генерация через Pollinations API"""
        try:
            # Улучшаем промпт
            enhanced_prompt = f"{prompt}, high quality, professional, detailed"
            
            # Создаем URL
            api_params = "?width=1024&height=1024&nologo=true&enhance=true"
            if image_name == 'favicon':
                api_params = "?width=512&height=512&nologo=true&enhance=true"
            
            api_url = f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}{api_params}"
            
            # Быстрый запрос
            response = requests.get(api_url, timeout=(10, 30))
            
            if response.status_code == 200 and len(response.content) > 1000:
                # Сохраняем изображение
                output_path = Path(media_dir) / f"{image_name}.jpg"
                
                # Обрабатываем изображение
                image = Image.open(BytesIO(response.content))
                
                # Для фавиконки - PNG с прозрачностью
                if image_name == 'favicon':
                    output_path = Path(media_dir) / f"{image_name}.png"
                    image = self._make_favicon_transparent(image)
                    image.save(output_path, "PNG", optimize=True)
                else:
                    # Сжимаем обычные изображения
                    image = image.convert('RGB')
                    image.save(output_path, "JPEG", quality=85, optimize=True)
                
                return str(output_path)
            
            return None
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Pollinations ошибка для {image_name}: {e}")
            return None
    
    def _make_favicon_transparent(self, image):
        """🎨 Создание прозрачного фона для фавиконки"""
        try:
            # Конвертируем в RGBA
            image = image.convert("RGBA")
            
            # Делаем белый фон прозрачным
            data = image.getdata()
            new_data = []
            
            for item in data:
                # Если пиксель белый или почти белый, делаем прозрачным
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # Прозрачный
                else:
                    new_data.append(item)
            
            image.putdata(new_data)
            return image
            
        except:
            return image
    
    def _regenerate_failed_images(self, theme_input, media_dir, image_names, successful_count):
        """🔄 Регенерация неудачных картинок с качественными промптами"""
        try:
            # Проверяем какие файлы отсутствуют
            missing_images = []
            for image_name in image_names:
                jpg_path = Path(media_dir) / f"{image_name}.jpg"
                png_path = Path(media_dir) / f"{image_name}.png"
                
                if not jpg_path.exists() and not png_path.exists():
                    missing_images.append(image_name)
            
            if missing_images and self.generated_prompts:
                if not self.silent_mode:
                    print(f"🔄 Регенерация {len(missing_images)} картинок...")
                
                for image_name in missing_images:
                    if image_name in self.generated_prompts:
                        quality_prompt = self.generated_prompts[image_name]
                        self._generate_image_pollinations_fast(quality_prompt, image_name, media_dir)
                        
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка регенерации: {e}")

# Функция для интеграции с существующим кодом
def create_parallel_generator(silent_mode=False):
    """Создает параллельный генератор"""
    return ParallelImageGenerator(silent_mode=silent_mode) 