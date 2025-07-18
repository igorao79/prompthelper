"""
Генератор изображений ТОЛЬКО через API
Без локальной генерации, только внешние API
"""

import requests
import datetime
import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from io import BytesIO
import json
import time
import random
import uuid
import re
from urllib.parse import quote
from pathlib import Path
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIOnlyImageGenerator:
    """Генератор изображений ТОЛЬКО через внешние API"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        if not self.silent_mode:
            print("🌐 APIOnlyImageGenerator: Только внешние API, без локальной генерации")
    
    def generate_thematic_set(self, theme_input, media_dir, method="1", progress_callback=None):
        """Генерирует полный набор изображений через API"""
        if not self.silent_mode:
            print(f"🎨 Генерация изображений через API для: {theme_input}")
        
        # Получаем умные промпты
        prompts = self._generate_prompts(theme_input)
        
        # Создаем папку для изображений
        try:
            os.makedirs(media_dir, exist_ok=True)
            if not self.silent_mode:
                print(f"📁 Папка media создана: {media_dir}")
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания папки media: {e}")
            return 0
        
        image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
        generated_count = 0
        
        for i, image_name in enumerate(image_names):
            if progress_callback:
                progress_callback(f"🎨 Генерация {image_name} ({i+1}/8)...")
            
            try:
                if image_name == 'favicon':
                    prompt = f"{theme_input} icon symbol logo"
                else:
                    prompt = prompts.get(image_name, f'professional {theme_input} service')
                
                result = self._generate_image_via_api(prompt, image_name, media_dir)
                
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
    
    def _generate_image_via_api(self, prompt, image_name, media_dir):
        """Генерирует изображение ТОЛЬКО через внешние API"""
        try:
            # Улучшаем промпт
            enhanced_prompt = self._add_randomization(prompt, image_name)
            
            # Параметры для разных типов изображений
            if image_name == 'favicon':
                target_size_kb = 50
                output_path = Path(media_dir) / f"{image_name}.png"
            else:
                target_size_kb = 150
                output_path = Path(media_dir) / f"{image_name}.jpg"
            
            # Создаем правильную сессию для Linux
            session = self._create_optimized_session()
            
            # Список API для попыток
            api_urls = [
                # Основной API
                f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}?width=1024&height=768&model=flux",
                # Альтернативные API
                f"https://picsum.photos/1024/768?random={hash(enhanced_prompt) % 10000}",
                f"https://source.unsplash.com/1024x768/?{enhanced_prompt.replace(' ', '+')}",
                f"https://via.placeholder.com/1024x768/4A90E2/FFFFFF?text={enhanced_prompt[:20].replace(' ', '+')}"
            ]
            
            for i, api_url in enumerate(api_urls):
                try:
                    if not self.silent_mode:
                        print(f"🌐 API {i+1}/{len(api_urls)} для {image_name}: {api_url[:50]}...")
                    
                    response = session.get(api_url, 
                                         timeout=(30, 120),
                                         stream=True,
                                         allow_redirects=True)
                    
                    if response.status_code == 200:
                        image_data = response.content
                        
                        # Проверяем что это изображение, а не HTML
                        if len(image_data) > 1000 and not image_data.startswith(b'<!DOCTYPE'):
                            # Загружаем в PIL Image
                            image = Image.open(BytesIO(image_data))
                            
                            # Обрезаем водяной знак если нужно
                            if "pollinations" in api_url:
                                image = self._remove_pollinations_watermark_from_image(image)
                            
                            # Для фавиконки делаем прозрачный фон
                            if image_name == 'favicon':
                                image = self._make_favicon_transparent(image)
                            
                            # Сжимаем и сохраняем
                            if self._save_compressed_image(image, str(output_path), target_size_kb=target_size_kb):
                                if not self.silent_mode:
                                    final_size_kb = output_path.stat().st_size / 1024
                                    print(f"✅ {image_name}: Создано через API {i+1} ({final_size_kb:.1f}кб)")
                                return str(output_path)
                        else:
                            if not self.silent_mode:
                                print(f"⚠️ API {i+1}: получен HTML вместо изображения")
                    else:
                        if not self.silent_mode:
                            print(f"⚠️ API {i+1}: код {response.status_code}")
                        
                except Exception as e:
                    if not self.silent_mode:
                        print(f"⚠️ API {i+1} не работает: {e}")
                    continue
            
            if not self.silent_mode:
                print(f"❌ Все API недоступны для {image_name}")
            return None
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации {image_name}: {e}")
            return None
    
    def _create_optimized_session(self):
        """Создает оптимизированную сессию для Linux"""
        session = requests.Session()
        
        # Retry стратегия
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # Правильные заголовки для Linux
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def _add_randomization(self, prompt, image_name):
        """Добавляет рандомизацию к промпту"""
        if image_name == 'favicon':
            return f"{prompt}, icon, symbol, logo, simple"
        elif image_name.startswith('review'):
            return f"{prompt}, person, portrait, professional"
        elif image_name == 'main':
            return f"{prompt}, professional, modern, high quality"
        else:
            return f"{prompt}, business, professional, clean"
    
    def _remove_pollinations_watermark_from_image(self, image):
        """Удаляет водяной знак pollinations"""
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
            
            return cropped_img
            
        except Exception as e:
            return image
    
    def _make_favicon_transparent(self, image):
        """Делает фавиконку прозрачной"""
        try:
            # Конвертируем в RGBA для прозрачности
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Делаем белый фон прозрачным
            data = image.getdata()
            
            newData = []
            for item in data:
                # Если пиксель близок к белому, делаем его прозрачным
                if item[0] > 200 and item[1] > 200 and item[2] > 200:
                    newData.append((255, 255, 255, 0))  # Прозрачный
                else:
                    newData.append(item)
            
            image.putdata(newData)
            return image
            
        except Exception as e:
            return image
    
    def _save_compressed_image(self, image, filepath, target_size_kb=150):
        """Сжимает и сохраняет изображение"""
        try:
            # Определяем формат по расширению
            file_ext = Path(filepath).suffix.lower()
            
            if file_ext == '.png':
                # PNG сжатие
                for quality in [95, 85, 75, 65]:
                    buffer = BytesIO()
                    image.save(buffer, format='PNG', optimize=True, compress_level=6)
                    size_kb = len(buffer.getvalue()) / 1024
                    
                    if size_kb <= target_size_kb:
                        with open(filepath, 'wb') as f:
                            f.write(buffer.getvalue())
                        return True
                
                # Сохраняем как есть если не удалось сжать
                image.save(filepath, format='PNG', optimize=True)
                return True
            
            else:
                # JPEG сжатие
                # Конвертируем в RGB если нужно
                if image.mode in ('RGBA', 'LA'):
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        rgb_image.paste(image, mask=image.split()[-1])
                    else:
                        rgb_image.paste(image)
                    image = rgb_image
                elif image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                # Пробуем разные уровни качества
                for quality in [95, 85, 75, 65, 55]:
                    buffer = BytesIO()
                    image.save(buffer, format='JPEG', quality=quality, optimize=True)
                    size_kb = len(buffer.getvalue()) / 1024
                    
                    if size_kb <= target_size_kb:
                        with open(filepath, 'wb') as f:
                            f.write(buffer.getvalue())
                        return True
                
                # Сохраняем с минимальным качеством
                image.save(filepath, format='JPEG', quality=50, optimize=True)
                return True
                
        except Exception as e:
            return False
    
    def _generate_prompts(self, theme_input):
        """Генерирует промпты для разных изображений"""
        prompts = {
            'main': f"professional {theme_input} business main image",
            'about1': f"modern {theme_input} company about us",
            'about2': f"quality {theme_input} service team",
            'about3': f"expert {theme_input} professional work",
            'review1': f"satisfied {theme_input} customer portrait",
            'review2': f"happy {theme_input} client testimonial",
            'review3': f"positive {theme_input} feedback success",
            'favicon': f"{theme_input} icon symbol logo"
        }
        
        return prompts 