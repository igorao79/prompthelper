"""
Основной генератор изображений
Использует проверенный код с исправлениями для промптов и фавиконок
"""

import requests
import datetime
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from io import BytesIO
import json
import time
import random
import uuid
import re
from urllib.parse import quote
from pathlib import Path

class ImageGenerator:
    """Класс для генерации полного набора тематических изображений"""
    
    def __init__(self, silent_mode=False, use_icons8_for_favicons=True):
        self.silent_mode = silent_mode
        self.use_icons8_for_favicons = use_icons8_for_favicons  # Для совместимости
        
        if not self.silent_mode:
            print("🎨 ImageGenerator инициализирован с исправлениями промптов")
    
    def generate_thematic_set(self, theme_input, media_dir, method="1", progress_callback=None):
        """
        Генерирует полный набор тематических изображений
        
        Args:
            theme_input (str): Тематика 
            media_dir (str): Путь к папке media
            method (str): Метод генерации
            progress_callback (callable): Функция обратного вызова
            
        Returns:
            int: Количество успешно созданных изображений
        """
        if not self.silent_mode:
            print(f"🎨 Генерация тематических изображений для: {theme_input}")
        
        # Получаем умные промпты с исправлениями
        prompts, theme_data = self._generate_prompts(theme_input)
        
        # Создаем папку для изображений
        os.makedirs(media_dir, exist_ok=True)
        
        image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
        generated_count = 0
        
        for i, image_name in enumerate(image_names):
            if progress_callback:
                progress_callback(f"🎨 Генерация {image_name} ({i+1}/8)...")
            
            try:
                if image_name == 'favicon':
                    # Генерируем фавикон через простой тематический генератор
                    result = self._generate_favicon_simple(theme_input, media_dir)
                else:
                    # Генерируем обычное изображение
                    prompt = prompts.get(image_name, f'professional {theme_input} service')
                    result = self._generate_image_via_pollinations(
                        prompt, 
                        image_name, 
                        media_dir
                    )
                
                if result:
                    generated_count += 1
                    if not self.silent_mode:
                        print(f"✅ {image_name}: Создано")
                else:
                    if not self.silent_mode:
                        print(f"❌ {image_name}: Ошибка")
                        
            except Exception as e:
                if not self.silent_mode:
                    print(f"❌ Ошибка генерации {image_name}: {e}")
        
        if not self.silent_mode:
            print(f"🎯 Создано {generated_count}/8 изображений")
        
        return generated_count
    
    def _generate_favicon_simple(self, theme, media_dir):
        """Генерирует фавикон через простой тематический генератор"""
        try:
            from generators.simple_thematic_favicon import generate_simple_thematic_favicon
            
            output_path = os.path.join(media_dir, "favicon.png")
            success = generate_simple_thematic_favicon(theme, output_path, silent_mode=self.silent_mode)
            
            return output_path if success else None
            
        except ImportError:
            if not self.silent_mode:
                print("⚠️ Простой генератор фавиконок недоступен, используем Pollinations")
            return self._generate_image_via_pollinations(f"{theme} icon symbol", 'favicon', media_dir)
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка простого генератора фавиконок: {e}")
            return self._generate_image_via_pollinations(f"{theme} icon symbol", 'favicon', media_dir)
    
    def _generate_image_via_pollinations(self, prompt, image_name, media_dir):
        """Генерирует изображение через современный API с разнообразием"""
        try:
            # Добавляем рандомизацию к промпту
            enhanced_prompt = self._add_randomization(prompt, image_name)
            
            # API Pollinations
            api_url = "https://image.pollinations.ai/prompt/"
            full_prompt = f"{enhanced_prompt}, high quality, professional"
            
            # Параметры для разных типов изображений
            if image_name == 'favicon':
                params = "?width=512&height=512&model=flux"
                target_size_kb = 50  # Фавиконы до 50кб
                output_path = Path(media_dir) / f"{image_name}.png"  # PNG для прозрачности
            else:
                params = "?width=1024&height=768&model=flux"
                target_size_kb = 150  # Остальные изображения до 150кб
                output_path = Path(media_dir) / f"{image_name}.jpg"  # JPEG для лучшего сжатия
            
            url = f"{api_url}{quote(full_prompt)}{params}"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Загружаем в PIL Image для обработки
                image = Image.open(BytesIO(response.content))
                
                # Обрезаем водяной знак
                cropped_image = self._remove_pollinations_watermark_from_image(image)
                
                # Для фавиконки делаем прозрачный фон
                if image_name == 'favicon':
                    cropped_image = self._make_favicon_transparent(cropped_image)
                
                # Сжимаем и сохраняем с автоматическим контролем размера
                if self._save_compressed_image(cropped_image, str(output_path), target_size_kb=target_size_kb):
                    if not self.silent_mode:
                        final_size_kb = output_path.stat().st_size / 1024
                        print(f"🎨 {image_name}: Создано и сжато до {final_size_kb:.1f}кб")
                    return str(output_path)
                else:
                    if not self.silent_mode:
                        print(f"❌ Не удалось сохранить {image_name}")
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации {image_name}: {e}")
        
        return None
    
    def _add_randomization(self, prompt, image_name):
        """Добавляет рандомизацию к промпту"""
        import random
        
        if image_name == 'favicon':
            # Стили для фавиконов
            favicon_styles = [
                "flat design", "minimal design", "geometric design", "simple icon",
                "clean symbol", "modern icon", "vector style", "logo style"
            ]
            
            favicon_colors = [
                "bold colors", "single color", "duo-tone", "monochrome",
                "bright accent", "professional colors"
            ]
            
            selected_style = random.choice(favicon_styles)
            selected_color = random.choice(favicon_colors)
            
            return f"{prompt}, {selected_style}, {selected_color}, icon, symbol"
        else:
            # Стили для обычных изображений
            styles = [
                "professional", "modern", "clean", "elegant", "minimalist",
                "sophisticated", "premium", "high-quality", "detailed"
            ]
            
            colors = [
                "vibrant colors", "soft colors", "natural tones", "warm palette",
                "cool tones", "balanced colors", "harmonious colors"
            ]
            
            composition = [
                "well-composed", "balanced composition", "dynamic composition",
                "centered composition", "artistic composition"
            ]
            
            selected_style = random.choice(styles)
            selected_color = random.choice(colors) 
            selected_comp = random.choice(composition)
            
            return f"{prompt}, {selected_style}, {selected_color}, {selected_comp}, photorealistic"
    
    def _make_favicon_transparent(self, image):
        """Делает фон фавикона прозрачным"""
        try:
            # Конвертируем в RGBA если нужно
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Простой алгоритм удаления белого фона
            data = image.getdata()
            new_data = []
            
            for item in data:
                # Если пиксель белый или близкий к белому - делаем прозрачным
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # прозрачный
                else:
                    new_data.append(item)
            
            image.putdata(new_data)
            
            if not self.silent_mode:
                print("🔍 Фон фавикона сделан прозрачным")
            
            return image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка создания прозрачности: {e}")
            return image
    
    def _save_compressed_image(self, image, filepath, target_size_kb=150):
        """УЛУЧШЕННОЕ сжатие изображений с сохранением качества"""
        try:
            from PIL import Image
            import io
            
            # Определяем формат по расширению файла
            if filepath.lower().endswith('.png'):
                format_type = 'PNG'
            else:
                format_type = 'JPEG'
            
            # Для PNG - более деликатное сжатие с сохранением качества
            if format_type == 'PNG':
                # Проверяем исходный размер
                buffer = io.BytesIO()
                image.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    # Если размер уже подходит - сохраняем без изменений
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 PNG сохранен {size_kb:.1f}кб (без сжатия)")
                    return True
                
                # Стратегия 1: Легкое ресайз с сохранением качества (только если сильно превышает)
                if size_kb > target_size_kb * 1.5:  # Только если превышает в 1.5 раза
                    for scale in [0.95, 0.9, 0.85, 0.8]:  # Более мягкий ресайз
                        new_width = int(image.width * scale)
                        new_height = int(image.height * scale)
                        
                        # Высококачественный ресайз
                        resized = image.resize((new_width, new_height), Image.LANCZOS)
                        
                        buffer = io.BytesIO()
                        resized.save(buffer, format='PNG', optimize=True)
                        size_kb = len(buffer.getvalue()) / 1024
                        
                        if size_kb <= target_size_kb:
                            with open(filepath, 'wb') as f:
                                f.write(buffer.getvalue())
                            
                            if not self.silent_mode:
                                print(f"📦 PNG сжат до {size_kb:.1f}кб (легкий ресайз {scale:.2f}x)")
                            return True
                
                # Стратегия 2: Деликатная квантизация с большим количеством цветов
                if image.mode == 'RGBA':
                    # Для прозрачных изображений - больше цветов
                    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    quantized = quantized.convert('RGBA')
                else:
                    # Для обычных изображений - тоже больше цветов
                    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                
                buffer = io.BytesIO()
                quantized.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 PNG сжат до {size_kb:.1f}кб (деликатная квантизация 256 цветов)")
                    return True
                
                # Крайний случай - сохраняем как есть, но предупреждаем
                buffer = io.BytesIO()
                image.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                
                if not self.silent_mode:
                    print(f"⚠️ PNG сохранен {size_kb:.1f}кб (превышает лимит, но качество сохранено)")
                return True
            
            else:
                # Для JPEG - более качественное сжатие
                # Конвертируем в RGB если нужно (JPEG не поддерживает прозрачность)
                if image.mode in ('RGBA', 'LA'):
                    # Создаем белый фон
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        rgb_image.paste(image, mask=image.split()[-1])
                    else:
                        rgb_image.paste(image)
                    image = rgb_image
                elif image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                # Пробуем более высокие уровни качества для JPEG
                for quality in [95, 90, 85, 80, 75, 70, 65, 60]:  # Начинаем с высокого качества
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=quality, optimize=True)
                    size_kb = len(buffer.getvalue()) / 1024
                    
                    if size_kb <= target_size_kb:
                        with open(filepath, 'wb') as f:
                            f.write(buffer.getvalue())
                        
                        if not self.silent_mode:
                            print(f"📦 JPEG сжат до {size_kb:.1f}кб (качество {quality}%)")
                        return True
                
                # Если все еще не помещается - легкий ресайз с хорошим качеством
                for scale in [0.95, 0.9, 0.85]:
                    new_width = int(image.width * scale)
                    new_height = int(image.height * scale)
                    resized = image.resize((new_width, new_height), Image.LANCZOS)
                    
                    for quality in [85, 80, 75, 70]:  # Сохраняем хорошее качество
                        buffer = io.BytesIO()
                        resized.save(buffer, format='JPEG', quality=quality, optimize=True)
                        size_kb = len(buffer.getvalue()) / 1024
                        
                        if size_kb <= target_size_kb:
                            with open(filepath, 'wb') as f:
                                f.write(buffer.getvalue())
                            
                            if not self.silent_mode:
                                print(f"📦 JPEG сжат до {size_kb:.1f}кб (ресайз {scale:.2f}x, качество {quality}%)")
                            return True
                
                # Последняя попытка с минимально приемлемым качеством
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=65, optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                
                if not self.silent_mode:
                    if size_kb <= target_size_kb:
                        print(f"📦 JPEG сжат до {size_kb:.1f}кб (качество 65%)")
                    else:
                        print(f"⚠️ JPEG сохранен {size_kb:.1f}кб (превышает лимит, но качество сохранено)")
                return True
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сжатия: {e}")
            return False

    def _remove_pollinations_watermark_from_image(self, image):
        """Удаляет водяной знак с PIL Image объекта"""
        try:
            width, height = image.size
            
            # Определяем область обрезки
            if width >= 1024 and height >= 768:
                crop_box = (0, 0, width - 80, height - 60)
            elif width >= 512 and height >= 512:
                crop_box = (0, 0, width - 50, height - 40)
            else:
                crop_box = (0, 0, width - 30, height - 25)
            
            # Обрезаем изображение
            cropped_img = image.crop(crop_box)
            
            if not self.silent_mode:
                new_width, new_height = cropped_img.size
                print(f"✂️ Обрезано с {width}x{height} до {new_width}x{new_height}")
            
            return cropped_img
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка обрезки: {e}")
            return image

    def _generate_prompts(self, theme_input):
        """УМНАЯ генерация вариативных промптов с исправлениями"""
        # Импортируем умный вариативный генератор
        try:
            from generators.smart_variative_prompts import create_smart_thematic_prompts
            prompts_list = create_smart_thematic_prompts(theme_input)
            
            # Конвертируем список в словарь
            image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
            prompts = {}
            
            for i, name in enumerate(image_names):
                if i < len(prompts_list):
                    prompts[name] = prompts_list[i]
                else:
                    prompts[name] = f'professional {theme_input} service'
            
            theme_data = {
                'business_type': theme_input,
                'activity_type': 'service'
            }
            
            if not self.silent_mode:
                print(f"✅ Использованы вариативные промпты для {theme_input}")
                # Показываем исправления для проблемных тематик
                if 'доставка еды' in theme_input.lower() or 'еда' in theme_input.lower():
                    print("🍕 Вариативные промпты доставки еды - разные блюда каждый раз!")
                if 'продажа авто' in theme_input.lower() or 'автосалон' in theme_input.lower():
                    print("🚗 Вариативные промпты авто - about2 всегда показывает интерьер!")
            
            return prompts, theme_data
            
        except ImportError:
            # Фоллбэк на старую систему, если умный генератор недоступен
            if not self.silent_mode:
                print("⚠️ Вариативный генератор недоступен, используется базовая система")
            return self._generate_fallback_prompts(theme_input)
    
    def _generate_fallback_prompts(self, theme_input):
        """Простая фоллбэк система для генерации промптов"""
        business_type = theme_input.lower()
        
        prompts = {
            'main': f"professional {business_type} business exterior, modern commercial building",
            'about1': f"{business_type} interior, professional workspace, modern facilities",
            'about2': f"professional working with {business_type}, quality service delivery",
            'about3': f"excellent {business_type} results, professional quality work",
            'review1': f"satisfied {business_type} customer, happy client experience",
            'review2': f"{business_type} consultation, professional service meeting",
            'review3': f"professional {business_type} team, experienced staff",
            'favicon': f"{business_type} icon, business symbol, professional logo"
        }
        
        theme_data = {
            'business_type': business_type,
            'activity_type': 'service'
        }
        
        return prompts, theme_data

# Класс для совместимости
class ThematicImageGenerator:
    """Упрощенный генератор для совместимости"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.image_generator = ImageGenerator(silent_mode=silent_mode)
    
    def generate_single_image(self, prompt, image_name, output_dir):
        """Генерирует одно изображение"""
        return self.image_generator._generate_image_via_pollinations(
            prompt, image_name, output_dir
        )
    
    def get_theme_prompts(self, theme_input):
        """Получает промпты для темы - для совместимости с GUI"""
        prompts, theme_data = self.image_generator._generate_prompts(theme_input)
        return prompts, theme_data 

