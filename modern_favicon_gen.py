# -*- coding: utf-8 -*-

"""
Современный генератор фавиконов 2024
Использует лучшие бесплатные AI методы для качественного удаления фона
"""

import os
import sys
import io
import time
import tempfile
import requests
import uuid
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO

# Опциональные продвинутые зависимости
try:
    import rembg
    REMBG_AVAILABLE = True
    print("✅ rembg доступен - будет использован AI для удаления фона")
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️ rembg недоступен - используются базовые алгоритмы")

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

class ModernFaviconGenerator:
    """
    Современный генератор фавиконов с качественным удалением фона
    
    Особенности:
    - AI удаление фона с rembg (несколько моделей)
    - Продвинутые алгоритмы без внешних зависимостей
    - Адаптивное качество для разных типов изображений
    - Поддержка векторного стиля
    - Автоматическая оптимизация размера файла
    """
    
    def __init__(self, silent_mode=False):
        """
        Инициализация генератора
        
        Args:
            silent_mode (bool): Тихий режим без вывода сообщений
        """
        self.silent_mode = silent_mode
        
        # Инициализируем rembg сессии если доступно
        self.rembg_sessions = {}
        if REMBG_AVAILABLE:
            self._init_rembg_sessions()
        
        if not self.silent_mode:
            print("🚀 Современный генератор фавиконов 2024")
            print("=" * 50)
            if REMBG_AVAILABLE:
                print("🤖 AI удаление фона: ДОСТУПНО")
            else:
                print("🔧 Базовые алгоритмы: АКТИВНЫ")
    
    def _init_rembg_sessions(self):
        """Инициализирует различные модели rembg для разных типов изображений"""
        try:
            # u2net - универсальная модель, хорошо для общих объектов
            self.rembg_sessions['u2net'] = rembg.new_session('u2net')
            
            # silueta - хорошо для силуэтов и простых форм (идеально для логотипов)
            self.rembg_sessions['silueta'] = rembg.new_session('silueta')
            
            if not self.silent_mode:
                print("🎯 Загружены AI модели: u2net, silueta")
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка инициализации rembg: {e}")
            self.rembg_sessions = {}
    
    def generate_favicon_from_prompt(self, prompt, output_path, size=512, style="modern_flat"):
        """
        Генерирует фавиконку из текстового промпта
        
        Args:
            prompt (str): Описание фавиконки
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки (по умолчанию 512)
            style (str): Стиль фавиконки
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            if not self.silent_mode:
                print(f"\n🎨 Генерация фавиконки: {prompt}")
                print(f"📐 Размер: {size}x{size}")
                print(f"🎭 Стиль: {style}")
            
            # Создаем оптимизированный промпт для фавиконки
            optimized_prompt = self._create_favicon_prompt(prompt, style)
            
            # Генерируем базовое изображение
            base_image = self._generate_base_image(optimized_prompt, size)
            
            if not base_image:
                if not self.silent_mode:
                    print("❌ Не удалось сгенерировать базовое изображение")
                return False
            
            # Применяем продвинутое удаление фона
            transparent_image = self._advanced_background_removal(base_image, style)
            
            # Оптимизируем качество
            optimized_image = self._optimize_favicon_quality(transparent_image, size)
            
            # Сохраняем с оптимальным сжатием
            success = self._save_optimized_favicon(optimized_image, output_path)
            
            if success and not self.silent_mode:
                file_size = os.path.getsize(output_path)
                print(f"✅ Фавиконка создана: {output_path}")
                print(f"📁 Размер файла: {file_size:,} байт ({file_size/1024:.1f} КБ)")
            
            return success
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации фавиконки: {e}")
            return False
    
    def _create_favicon_prompt(self, prompt, style):
        """Создает оптимизированный промпт для генерации фавиконки"""
        style_prompts = {
            "modern_flat": "flat design, minimalist icon, simple geometric shapes, clean lines, modern style",
            "gradient": "gradient colors, modern icon, smooth transitions, professional design",
            "outline": "outline style, line art, minimal design, vector illustration",
            "filled": "solid colors, filled shapes, bold design, strong contrast",
            "abstract": "abstract geometric, creative design, artistic icon, unique pattern",
            "corporate": "professional logo, business style, corporate identity, clean design"
        }
        
        base_style = style_prompts.get(style, style_prompts["modern_flat"])
        
        # Создаем промпт специально для фавиконки БЕЗ ТЕКСТА
        favicon_prompt = (
            f"{prompt}, {base_style}, "
            "simple composition, centered design, clear background, "
            "high contrast, scalable design, vector style, professional quality, "
            "clean edges, optimized for small sizes, transparent background, "
            "PNG format, isolated object, NO TEXT, NO LETTERS, NO WORDS, "
            "symmetrical layout, bold colors, crisp details, symbol only, "
            "graphic element, visual icon without text, pure visual design"
        )
        
        return favicon_prompt
    
    def _generate_base_image(self, prompt, size):
        """Генерирует базовое изображение для фавиконки"""
        try:
            # Используем Pollinations AI с оптимизированными параметрами
            enhanced_prompt = f"{prompt}, high quality, sharp details, professional design"
            
            import urllib.parse
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Специальные параметры для фавиконок
            params = (
                f"?width={size}&height={size}&model=flux&enhance=true&nologo=true"
                "&style=digital-art&quality=high"
            )
            
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}{params}"
            
            if not self.silent_mode:
                print("⏳ Генерация базового изображения...")
            
            response = requests.get(image_url, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Убеждаемся в правильном размере
                if image.size != (size, size):
                    image = image.resize((size, size), Image.Resampling.LANCZOS)
                
                # Конвертируем в RGBA для работы с прозрачностью
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                return image
            else:
                if not self.silent_mode:
                    print(f"❌ Ошибка API: {response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации: {e}")
            return None
    
    def _advanced_background_removal(self, image, style):
        """Продвинутое удаление фона с использованием нескольких методов"""
        try:
            if not self.silent_mode:
                print("🤖 Применение AI удаления фона...")
            
            # Метод 1: rembg AI (приоритетный)
            if REMBG_AVAILABLE and self.rembg_sessions:
                ai_result = self._rembg_removal(image, style)
                if ai_result:
                    if not self.silent_mode:
                        print("✅ AI удаление фона успешно")
                    return ai_result
            
            # Метод 2: Продвинутый анализ краев и цветов
            advanced_result = self._advanced_edge_color_removal(image)
            if advanced_result:
                if not self.silent_mode:
                    print("✅ Продвинутый алгоритм применен")
                return advanced_result
            
            # Метод 3: Базовый алгоритм (fallback)
            if not self.silent_mode:
                print("⚠️ Использование базового алгоритма")
            return self._basic_smart_removal(image)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка удаления фона: {e}")
            return image
    
    def _rembg_removal(self, image, style):
        """Удаление фона с помощью rembg AI"""
        try:
            # Выбираем подходящую модель в зависимости от стиля
            if style in ["outline", "abstract", "modern_flat"]:
                model_name = 'silueta'  # Лучше для простых форм
            else:
                model_name = 'u2net'    # Универсальная модель
            
            session = self.rembg_sessions.get(model_name)
            if not session:
                session = self.rembg_sessions.get('u2net')  # Fallback
            
            if not session:
                return None
            
            # Конвертируем PIL в байты
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Применяем rembg
            output = rembg.remove(img_byte_arr.getvalue(), session=session)
            
            # Конвертируем обратно в PIL
            result_image = Image.open(io.BytesIO(output))
            
            # Убеждаемся что формат RGBA
            if result_image.mode != 'RGBA':
                result_image = result_image.convert('RGBA')
            
            return result_image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка rembg: {e}")
            return None
    
    def _advanced_edge_color_removal(self, image):
        """Продвинутый алгоритм удаления фона на основе краев и цветов"""
        try:
            width, height = image.size
            
            # Анализируем все края изображения
            edge_pixels = []
            
            # Собираем пиксели с краев (больше точек выборки)
            edge_thickness = max(2, min(width, height) // 50)
            
            for thickness in range(edge_thickness):
                # Верхний и нижний края
                for x in range(width):
                    if thickness < height:
                        edge_pixels.append(image.getpixel((x, thickness)))
                        edge_pixels.append(image.getpixel((x, height - 1 - thickness)))
                
                # Левый и правый края
                for y in range(height):
                    if thickness < width:
                        edge_pixels.append(image.getpixel((thickness, y)))
                        edge_pixels.append(image.getpixel((width - 1 - thickness, y)))
            
            # Анализируем углы отдельно (они часто содержат фон)
            corner_pixels = [
                image.getpixel((0, 0)),
                image.getpixel((width-1, 0)),
                image.getpixel((0, height-1)),
                image.getpixel((width-1, height-1))
            ]
            
            # Определяем цвет фона с улучшенным алгоритмом
            bg_color = self._smart_background_detection(edge_pixels + corner_pixels)
            
            if not bg_color:
                return None
            
            # Создаем умную маску
            mask = self._create_smart_mask(image, bg_color)
            
            # Применяем маску
            result = image.copy()
            result.putalpha(mask)
            
            return result
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка продвинутого алгоритма: {e}")
            return None
    
    def _smart_background_detection(self, pixels):
        """Умное определение цвета фона"""
        try:
            # Фильтруем светлые пиксели (возможный фон)
            light_pixels = []
            for pixel in pixels:
                if len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    brightness = (r + g + b) / 3
                    
                    # Расширили критерии для лучшего определения
                    if brightness > 200:  # Светлые пиксели
                        light_pixels.append((r, g, b))
            
            if not light_pixels:
                # Если светлых нет, ищем среди всех
                all_colors = []
                for pixel in pixels:
                    if len(pixel) >= 3:
                        all_colors.append((pixel[0], pixel[1], pixel[2]))
                
                if not all_colors:
                    return None
                
                # Используем самый частый цвет
                return self._find_most_frequent_color(all_colors)
            
            # Группируем похожие светлые цвета
            color_groups = {}
            tolerance = 20
            
            for color in light_pixels:
                found_group = False
                for group_color in color_groups:
                    if self._color_distance(color, group_color) <= tolerance:
                        color_groups[group_color].append(color)
                        found_group = True
                        break
                
                if not found_group:
                    color_groups[color] = [color]
            
            if not color_groups:
                return None
            
            # Находим самую большую группу
            largest_group = max(color_groups.values(), key=len)
            
            # Вычисляем средний цвет в группе
            avg_r = sum(c[0] for c in largest_group) // len(largest_group)
            avg_g = sum(c[1] for c in largest_group) // len(largest_group)
            avg_b = sum(c[2] for c in largest_group) // len(largest_group)
            
            return (avg_r, avg_g, avg_b)
            
        except Exception as e:
            return None
    
    def _color_distance(self, color1, color2):
        """Вычисляет расстояние между цветами"""
        return ((color1[0] - color2[0]) ** 2 + 
                (color1[1] - color2[1]) ** 2 + 
                (color1[2] - color2[2]) ** 2) ** 0.5
    
    def _find_most_frequent_color(self, colors):
        """Находит самый частый цвет"""
        color_counts = {}
        tolerance = 15
        
        for color in colors:
            found = False
            for existing_color in color_counts:
                if self._color_distance(color, existing_color) <= tolerance:
                    color_counts[existing_color] += 1
                    found = True
                    break
            
            if not found:
                color_counts[color] = 1
        
        if not color_counts:
            return None
        
        return max(color_counts.keys(), key=lambda k: color_counts[k])
    
    def _create_smart_mask(self, image, bg_color):
        """Создает умную маску для удаления фона"""
        try:
            width, height = image.size
            mask = Image.new('L', (width, height), 255)
            
            # Улучшенный алгоритм создания маски
            tolerance = 35  # Увеличенная толерантность
            
            for y in range(height):
                for x in range(width):
                    pixel = image.getpixel((x, y))
                    
                    if len(pixel) >= 3:
                        # Проверяем расстояние до цвета фона
                        distance = self._color_distance(pixel[:3], bg_color)
                        
                        if distance <= tolerance:
                            # Дополнительная проверка на контекст
                            if self._is_likely_background(image, x, y, bg_color):
                                mask.putpixel((x, y), 0)  # Прозрачный
            
            # Применяем морфологические операции для сглаживания
            mask = self._smooth_mask(mask)
            
            return mask
            
        except Exception as e:
            # Возвращаем непрозрачную маску в случае ошибки
            return Image.new('L', image.size, 255)
    
    def _is_likely_background(self, image, x, y, bg_color, radius=2):
        """Проверяет, является ли пиксель частью фона на основе контекста"""
        try:
            width, height = image.size
            bg_count = 0
            total_count = 0
            
            # Анализируем окрестности пикселя
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = image.getpixel((nx, ny))
                        if len(neighbor) >= 3:
                            distance = self._color_distance(neighbor[:3], bg_color)
                            if distance <= 25:
                                bg_count += 1
                            total_count += 1
            
            if total_count == 0:
                return False
            
            # Если больше 60% соседей похожи на фон, считаем пиксель фоновым
            return (bg_count / total_count) > 0.6
            
        except Exception as e:
            return False
    
    def _smooth_mask(self, mask):
        """Сглаживает маску для лучшего качества"""
        try:
            # Применяем размытие для сглаживания краев
            smoothed = mask.filter(ImageFilter.GaussianBlur(radius=1))
            
            # Применяем морфологические операции если OpenCV доступен
            if OPENCV_AVAILABLE:
                # Конвертируем в numpy
                mask_array = np.array(smoothed)
                
                # Морфологическое закрытие для заполнения дыр
                kernel = np.ones((3, 3), np.uint8)
                closed = cv2.morphologyEx(mask_array, cv2.MORPH_CLOSE, kernel)
                
                # Морфологическое открытие для удаления шума
                opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
                
                return Image.fromarray(opened, mode='L')
            
            return smoothed
            
        except Exception as e:
            return mask
    
    def _basic_smart_removal(self, image):
        """Базовый, но умный алгоритм удаления фона"""
        try:
            # Применяем адаптивную фильтрацию
            enhanced = ImageEnhance.Contrast(image).enhance(1.2)
            
            # Анализируем края для определения фона
            width, height = image.size
            edge_samples = []
            
            # Увеличиваем количество образцов с краев
            sample_step = max(1, min(width, height) // 20)
            
            for i in range(0, width, sample_step):
                edge_samples.append(enhanced.getpixel((i, 0)))
                edge_samples.append(enhanced.getpixel((i, height-1)))
            
            for i in range(0, height, sample_step):
                edge_samples.append(enhanced.getpixel((0, i)))
                edge_samples.append(enhanced.getpixel((width-1, i)))
            
            # Определяем фон
            bg_color = self._smart_background_detection(edge_samples)
            
            if not bg_color:
                return image
            
            # Создаем маску
            mask = self._create_smart_mask(enhanced, bg_color)
            
            # Применяем к оригинальному изображению
            result = image.copy()
            result.putalpha(mask)
            
            return result
            
        except Exception as e:
            return image
    
    def _optimize_favicon_quality(self, image, target_size):
        """Оптимизирует качество фавиконки"""
        try:
            # Убеждаемся в правильном размере
            if image.size != (target_size, target_size):
                image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Повышаем резкость для мелких деталей
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
            
            # Слегка повышаем контрастность
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.15)
            
            # Улучшаем насыщенность для более ярких цветов
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            # Применяем легкое сглаживание для финальной обработки
            image = image.filter(ImageFilter.SMOOTH_MORE)
            
            return image
            
        except Exception as e:
            return image
    
    def _save_optimized_favicon(self, image, output_path, target_size_kb=50):
        """Сохраняет фавиконку с оптимальным сжатием"""
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Оптимизируем прозрачность
            optimized = self._optimize_transparency(image)
            
            # Сохраняем с различными уровнями оптимизации
            for optimize_level in [True, False]:
                try:
                    optimized.save(
                        output_path,
                        format='PNG',
                        optimize=optimize_level,
                        compress_level=9
                    )
                    
                    # Проверяем размер файла
                    file_size = os.path.getsize(output_path)
                    if file_size <= target_size_kb * 1024:
                        return True
                    
                except Exception as e:
                    continue
            
            # Если не удалось достичь целевого размера, сохраняем как есть
            optimized.save(output_path, format='PNG')
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def _optimize_transparency(self, image):
        """Оптимизирует прозрачность для лучшего качества"""
        try:
            if image.mode != 'RGBA':
                return image
            
            # Получаем альфа-канал
            alpha = image.split()[-1]
            
            # Применяем порог для четкой прозрачности
            alpha = alpha.point(lambda x: 0 if x < 128 else 255)
            
            # Собираем изображение обратно
            rgb = image.convert('RGB')
            result = Image.merge('RGBA', rgb.split() + (alpha,))
            
            return result
            
        except Exception as e:
            return image
    
    def create_favicon_variants(self, base_prompt, output_dir, count=5):
        """
        Создает несколько вариантов фавиконки для выбора лучшего
        
        Args:
            base_prompt (str): Базовое описание
            output_dir (str): Папка для сохранения
            count (int): Количество вариантов
            
        Returns:
            list: Список путей к созданным файлам
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            created_files = []
            
            styles = ["modern_flat", "gradient", "outline", "filled", "abstract"]
            
            if not self.silent_mode:
                print(f"\n🎨 Создание {count} вариантов фавиконки...")
            
            for i in range(count):
                style = styles[i % len(styles)]
                filename = f"favicon_variant_{i+1}_{style}.png"
                filepath = os.path.join(output_dir, filename)
                
                if not self.silent_mode:
                    print(f"\n🔄 Вариант {i+1}/{count} - Стиль: {style}")
                
                success = self.generate_favicon_from_prompt(
                    base_prompt, 
                    filepath, 
                    size=512, 
                    style=style
                )
                
                if success:
                    created_files.append(filepath)
            
            if not self.silent_mode:
                print(f"\n✅ Создано {len(created_files)} вариантов в {output_dir}")
            
            return created_files
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания вариантов: {e}")
            return []

def test_modern_favicon_generator():
    """Тестирование современного генератора фавиконов"""
    print("🧪 Тест современного генератора фавиконов")
    print("=" * 60)
    
    generator = ModernFaviconGenerator(silent_mode=False)
    
    # Создаем тестовую папку
    test_dir = "test_favicons"
    os.makedirs(test_dir, exist_ok=True)
    
    # Тестовые промпты
    test_prompts = [
        "современная IT компания, синий логотип",
        "ресторан итальянской кухни, красный и зеленый", 
        "фитнес клуб, динамичный спортивный символ",
        "детский сад, яркий и дружелюбный дизайн",
        "юридическая фирма, строгий профессиональный стиль"
    ]
    
    successful_tests = 0
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Тест {i}/{len(test_prompts)}: {prompt}")
        
        output_path = os.path.join(test_dir, f"test_favicon_{i}.png")
        
        success = generator.generate_favicon_from_prompt(
            prompt=prompt,
            output_path=output_path,
            size=512,
            style="modern_flat"
        )
        
        if success:
            successful_tests += 1
            print(f"✅ Тест {i} пройден")
        else:
            print(f"❌ Тест {i} провален")
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Успешно: {successful_tests}/{len(test_prompts)}")
    print(f"📁 Файлы сохранены в: {test_dir}")
    
    # Тест создания вариантов
    print(f"\n🎨 Тест создания вариантов...")
    variants_dir = os.path.join(test_dir, "variants")
    variants = generator.create_favicon_variants(
        "современная технологическая компания",
        variants_dir,
        count=3
    )
    
    print(f"🎯 Создано вариантов: {len(variants)}")
    
    return successful_tests == len(test_prompts)

if __name__ == "__main__":
    # Запускаем тесты
    test_success = test_modern_favicon_generator()
    
    if test_success:
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n⚠️ Некоторые тесты провалены") 