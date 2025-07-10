#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
from pathlib import Path
from PIL import Image
from io import BytesIO
import json
import time

class ModernImageAPI:
    """Современный API генератор изображений 2025 года"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        # API endpoints и ключи (можно настроить через переменные среды)
        self.apis = {
            'flux_pro': {
                'url': 'https://api.aimlapi.com/images/generations',
                'model': 'flux-pro/v1.1',
                'quality': 'highest',
                'speed': 'fast',
                'cost': 0.055  # $ за изображение
            },
            'flux_dev': {
                'url': 'https://api.aimlapi.com/images/generations', 
                'model': 'flux-dev/v1',
                'quality': 'high',
                'speed': 'medium',
                'cost': 0.025
            },
            'fal_flux': {
                'url': 'https://fal.run/fal-ai/flux-pro',
                'model': 'flux-pro',
                'quality': 'highest',
                'speed': 'fastest',
                'cost': 0.055
            },
            'pollinations': {
                'url': 'https://image.pollinations.ai/prompt/',
                'model': 'flux',
                'quality': 'good',
                'speed': 'fast',
                'cost': 0  # бесплатно
            }
        }
        
        # Настройки по умолчанию
        self.default_api = 'pollinations'  # Можно изменить на flux_pro при наличии ключа
        
    def generate_image(self, prompt, image_name='image', output_dir='.', size='1024x768', api_name=None):
        """
        Генерирует изображение с автоматическим выбором лучшего API
        
        Args:
            prompt (str): Текстовый промпт
            image_name (str): Имя файла
            output_dir (str): Папка для сохранения
            size (str): Размер изображения
            api_name (str): Принудительный выбор API
            
        Returns:
            str: Путь к сгенерированному файлу или None
        """
        
        # Выбираем API
        api_name = api_name or self.default_api
        
        if not self.silent_mode:
            print(f"🎨 Генерация {image_name} через {api_name}...")
        
        # Генерируем разные промпты для разнообразия
        enhanced_prompt = self._enhance_prompt(prompt, image_name)
        
        # Пробуем основной API
        result = None
        try:
            if api_name == 'flux_pro':
                result = self._generate_flux_pro(enhanced_prompt, size)
            elif api_name == 'flux_dev':
                result = self._generate_flux_dev(enhanced_prompt, size)
            elif api_name == 'fal_flux':
                result = self._generate_fal_flux(enhanced_prompt, size)
            else:  # pollinations fallback
                result = self._generate_pollinations(enhanced_prompt, size)
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка {api_name}: {e}")
            
            # Fallback на Pollinations
            if api_name != 'pollinations':
                try:
                    result = self._generate_pollinations(enhanced_prompt, size)
                except Exception as e2:
                    if not self.silent_mode:
                        print(f"❌ Fallback тоже не сработал: {e2}")
                    return None
        
        if result:
            return self._save_and_compress_image(result, image_name, output_dir)
        
        return None
    
    def _enhance_prompt(self, prompt, image_name):
        """Улучшает промпт для разнообразия"""
        
        # Базовые улучшения качества
        quality_words = ["high quality", "professional", "detailed", "sharp", "clear"]
        
        # Разные стили для разных типов изображений
        style_variants = {
            'main': [
                "modern commercial building exterior",
                "contemporary business facade", 
                "professional office building",
                "sleek company headquarters"
            ],
            'about1': [
                "spacious interior workspace",
                "modern office environment",
                "professional consultation area",
                "comfortable business space"
            ],
            'about2': [
                "professional at work",
                "expert providing service",
                "skilled specialist working",
                "professional consultation"
            ],
            'about3': [
                "excellent results showcase",
                "quality work demonstration",
                "successful project outcome",
                "professional achievement"
            ],
            'favicon': [
                "simple business icon",
                "clean company logo",
                "minimalist symbol",
                "professional emblem"
            ]
        }
        
        # Добавляем разнообразие
        if image_name in style_variants:
            style = random.choice(style_variants[image_name])
            enhanced = f"{prompt}, {style}, {random.choice(quality_words)}"
        else:
            enhanced = f"{prompt}, {random.choice(quality_words)}"
        
        return enhanced
    
    def _generate_flux_pro(self, prompt, size):
        """Генерация через FLUX 1.1 Pro API"""
        # Здесь будет код для FLUX Pro API при наличии ключа
        raise Exception("FLUX Pro API key required")
    
    def _generate_flux_dev(self, prompt, size):
        """Генерация через FLUX Dev API"""
        # Здесь будет код для FLUX Dev API при наличии ключа
        raise Exception("FLUX Dev API key required")
    
    def _generate_fal_flux(self, prompt, size):
        """Генерация через fal.ai FLUX API"""
        # Здесь будет код для fal.ai API при наличии ключа
        raise Exception("fal.ai API key required")
    
    def _generate_pollinations(self, prompt, size):
        """Генерация через Pollinations (бесплатно)"""
        try:
            api_url = "https://image.pollinations.ai/prompt/"
            
            # Определяем размеры
            if size == '512x512':
                params = "?width=512&height=512&model=flux"
            else:
                params = "?width=1024&height=768&model=flux"
            
            url = f"{api_url}{prompt}{params}"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
                
        except Exception as e:
            raise Exception(f"Pollinations error: {e}")
        
        return None
    
    def _save_and_compress_image(self, image, image_name, output_dir):
        """Сохраняет и сжимает изображение"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Обрезаем водяной знак если есть
            cropped_image = self._remove_watermark(image)
            
            # Определяем формат и целевой размер
            if image_name == 'favicon':
                file_path = output_path / f"{image_name}.png"
                target_size_kb = 50
                format_type = 'PNG'
            else:
                file_path = output_path / f"{image_name}.jpg"
                target_size_kb = 150
                format_type = 'JPEG'
            
            # Сжимаем до нужного размера
            self._compress_and_save(cropped_image, str(file_path), target_size_kb, format_type)
            
            if not self.silent_mode:
                actual_size = file_path.stat().st_size / 1024
                print(f"✅ {image_name}: Сохранено {actual_size:.1f}кб")
            
            return str(file_path)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения {image_name}: {e}")
            return None
    
    def _remove_watermark(self, image):
        """Удаляет водяной знак Pollinations"""
        try:
            width, height = image.size
            
            # Обрезаем нижние 60 пикселей где обычно водяной знак
            crop_height = max(1, height - 60)
            cropped = image.crop((0, 0, width, crop_height))
            
            if not self.silent_mode:
                print(f"✂️ Обрезано с {width}x{height} до {width}x{crop_height}")
            
            return cropped
            
        except Exception:
            return image
    
    def _compress_and_save(self, image, file_path, target_size_kb, format_type):
        """Продвинутое сжатие изображений"""
        import io
        
        if format_type == 'PNG':
            # PNG сжатие с квантизацией
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Пробуем разные уровни сжатия
            for colors in [256, 128, 64]:
                buffer = io.BytesIO()
                try:
                    # Для RGBA используем FASTOCTREE метод
                    quantized = image.quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
                    quantized = quantized.convert('RGBA')
                except:
                    # Fallback - конвертируем в RGB для квантизации
                    rgb_image = image.convert('RGB')
                    quantized = rgb_image.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
                    quantized = quantized.convert('RGBA')
                    
                quantized.save(buffer, format='PNG', optimize=True)
                
                size_kb = len(buffer.getvalue()) / 1024
                if size_kb <= target_size_kb:
                    with open(file_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 PNG сжат до {size_kb:.1f}кб ({colors} цветов)")
                    return
            
            # Если не удалось - сохраняем как есть
            image.save(file_path, format='PNG', optimize=True)
            
        else:
            # JPEG сжатие с динамическим качеством
            for quality in [95, 90, 85, 80, 75, 70]:
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=quality, optimize=True)
                
                size_kb = len(buffer.getvalue()) / 1024
                if size_kb <= target_size_kb:
                    with open(file_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 JPEG сжат до {size_kb:.1f}кб (качество {quality}%)")
                    return
            
            # Если не удалось - сохраняем с минимальным качеством
            image.save(file_path, format='JPEG', quality=70, optimize=True)

    def set_api_key(self, api_name, api_key):
        """Устанавливает API ключ для премиум сервисов"""
        if api_name in self.apis:
            self.apis[api_name]['api_key'] = api_key
            if not self.silent_mode:
                print(f"✅ API ключ установлен для {api_name}")
    
    def get_api_info(self):
        """Возвращает информацию о доступных API"""
        info = []
        for name, config in self.apis.items():
            info.append({
                'name': name,
                'quality': config['quality'],
                'speed': config['speed'],
                'cost': config['cost'],
                'available': 'api_key' in config or config['cost'] == 0
            })
        return info 