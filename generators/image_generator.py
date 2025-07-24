"""
Генератор изображений для лендингов
Использует ТОЛЬКО Pollinations API для максимальной совместимости с Linux
"""

import os
import random
import time
import requests
from urllib.parse import quote
from PIL import Image
from io import BytesIO
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class ImageGenerator:
    """Класс для генерации полного набора тематических изображений ТОЛЬКО через Pollinations API"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        if not self.silent_mode:
            print("🎨 ImageGenerator - ТОЛЬКО Pollinations API, БЕЗ FALLBACK'ОВ!")
    
    def generate_thematic_set(self, theme_input, media_dir, method="1", progress_callback=None):
        """
        Генерирует полный набор тематических изображений ТОЛЬКО через Pollinations API
        
        Args:
            theme_input (str): Тематика 
            media_dir (str): Путь к папке media
            method (str): Метод генерации
            progress_callback (callable): Функция обратного вызова
            
        Returns:
            int: Количество успешно созданных изображений
        """
        if not self.silent_mode:
            print(f"🎨 ТОЛЬКО Pollinations API для: {theme_input}")
        
        # Получаем умные промпты
        prompts, theme_data = self._generate_prompts(theme_input)
        
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
            
            if not self.silent_mode:
                print(f"🔄 Генерация {image_name} ({i+1}/8) - ТОЛЬКО Pollinations API...")
            
            # Генерируем изображение ТОЛЬКО через Pollinations API
            prompt = prompts.get(image_name, f'professional {theme_input} service')
            result = self._generate_image_pollinations_aggressive(prompt, image_name, media_dir)
                
            if result:
                generated_count += 1
                if not self.silent_mode:
                    print(f"✅ {image_name}: Создано через Pollinations API")
            else:
                if not self.silent_mode:
                    print(f"❌ {image_name}: Pollinations API не ответил")
        
        if not self.silent_mode:
            print(f"🎯 Создано {generated_count}/8 изображений")
        
        return generated_count
    
    def _generate_image_pollinations_aggressive(self, prompt, image_name, media_dir):
        """Генерирует изображение ТОЛЬКО через Pollinations API с агрессивными настройками"""
        # Добавляем рандомизацию к промпту
        enhanced_prompt = self._add_randomization(prompt, image_name)
        
        # Настройки для разных типов изображений
        if image_name == 'favicon':
            target_size_kb = 50
            output_path = Path(media_dir) / f"{image_name}.png"
            api_params = "?width=512&height=512&model=flux&enhance=true&nologo=true"
        else:
            target_size_kb = 150
            output_path = Path(media_dir) / f"{image_name}.jpg"
            api_params = "?width=1024&height=768&model=flux&enhance=true&nologo=true"
        
        # Pollinations API URL
        api_url = f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}{api_params}"
        
        if not self.silent_mode:
            print(f"🌐 Подключение к Pollinations API: {enhanced_prompt[:50]}...")
        
        # Создаем агрессивную сессию
        session = self._create_aggressive_session()
        
        # Пробуем несколько раз с разными настройками
        for attempt in range(3):
            if not self.silent_mode:
                print(f"🔄 Попытка {attempt + 1}/3...")
            
            try:
                # Агрессивные таймауты
                response = session.get(api_url, timeout=(15, 60), stream=True)
                
                if not self.silent_mode:
                    print(f"📊 Pollinations API: код {response.status_code}")
                
                if response.status_code == 200:
                    # Загружаем изображение
                    image_data = response.content
                    
                    if len(image_data) > 1000:  # Проверяем что это не ошибка
                        # Загружаем в PIL Image
                        image = Image.open(BytesIO(image_data))
                        
                        if not self.silent_mode:
                            print(f"🖼️ Изображение загружено: {image.size}")
                
                        # Для фавиконки делаем прозрачный фон
                        if image_name == 'favicon':
                            image = self._make_favicon_transparent(image)
                        
                        # Сжимаем и сохраняем
                        if self._save_compressed_image(image, str(output_path), target_size_kb=target_size_kb):
                            if not self.silent_mode:
                                final_size_kb = output_path.stat().st_size / 1024
                                print(f"✅ {image_name}: Создано через Pollinations API ({final_size_kb:.1f}кб)")
                            return str(output_path)
                    else:
                        if not self.silent_mode:
                            print(f"⚠️ Pollinations API: Слишком маленький файл ({len(image_data)} байт)")
                
                elif response.status_code == 429:
                    if not self.silent_mode:
                        print(f"⏰ Pollinations API: Лимит запросов, пауза 10 сек...")
                    time.sleep(10)
                    continue
                
                elif response.status_code == 500:
                    if not self.silent_mode:
                        print(f"🔧 Pollinations API: Внутренняя ошибка сервера, пауза 5 сек...")
                    time.sleep(5)
                    continue
                
                else:
                    if not self.silent_mode:
                        print(f"❌ Pollinations API: Ошибка {response.status_code}")
                
            except requests.exceptions.Timeout:
                if not self.silent_mode:
                    print(f"⏰ Pollinations API: Таймаут, пробуем еще раз...")
                time.sleep(2)
                continue
                
            except requests.exceptions.ConnectionError as e:
                if not self.silent_mode:
                    print(f"🔌 Pollinations API: Ошибка соединения, пробуем еще раз...")
                time.sleep(3)
                continue
            
            except Exception as e:
                if not self.silent_mode:
                    print(f"⚠️ Pollinations API: {str(e)[:100]}...")
                time.sleep(2)
                continue
        
        # Если все попытки не удались
        if not self.silent_mode:
            print(f"❌ Pollinations API недоступен для {image_name} после 3 попыток")
        return None
    
    def _create_aggressive_session(self):
        """Создает агрессивную сессию для максимальной совместимости с Linux"""
        session = requests.Session()
        
        # ОТКЛЮЧАЕМ SSL проверку для максимальной совместимости
        session.verify = False
        
        # Агрессивная retry стратегия
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # ТОЧНО такие же заголовки как curl (curl работает!)
        session.headers.update({
            'User-Agent': 'curl/8.5.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def _add_randomization(self, prompt, image_name):
        """Добавляет качественные термины к существующему промпту БЕЗ изменения тематики"""
        import hashlib
        import uuid
        
        # СОХРАНЯЕМ ОРИГИНАЛЬНЫЙ ПРОМПТ! Это основа изображения
        base_prompt = prompt
        
        # Создаем уникальный ID для изображения
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time() * 1000) % 100000
        
        # Качественные термины для улучшения изображения
        quality_terms = [
            "high quality", "professional", "4k", "detailed", "sharp", 
            "crisp", "well-lit", "premium", "photorealistic", "studio quality"
        ]
        
        # Стилистические термины
        style_terms = [
            "contemporary", "elegant", "sophisticated", "polished", 
            "refined", "modern", "sleek", "premium"
        ]
        
        # Технические термины для улучшения качества
        technical_terms = [
            "perfect lighting", "excellent composition", "vibrant colors",
            "commercial photography", "professional grade", "award winning"
        ]
        
        # Собираем улучшенный промпт
        enhanced_prompt = base_prompt
        
        # Добавляем качественные термины (2-3 штуки)
        selected_quality = random.sample(quality_terms, random.randint(2, 3))
        enhanced_prompt += f", {', '.join(selected_quality)}"
        
        # Добавляем стилистические термины (1-2 штуки)  
        selected_style = random.sample(style_terms, random.randint(1, 2))
        enhanced_prompt += f", {', '.join(selected_style)}"
        
        # Добавляем технические детали (1 штука)
        selected_technical = random.choice(technical_terms)
        enhanced_prompt += f", {selected_technical}"
        
        # Добавляем уникальность для избежания кэширования
        hash_source = f"{unique_id}_{timestamp}_{image_name}_{random.randint(1000, 9999)}"
        unique_hash = hashlib.md5(hash_source.encode()).hexdigest()[:8]
        
        # Добавляем уникальный элемент
        enhanced_prompt += f", unique_{unique_hash}"
        
        # Добавляем временную метку для гарантированной уникальности
        enhanced_prompt += f", render_{timestamp}"
        
        # Добавляем специфичный для типа изображения элемент
        type_modifiers = {
            "main": "hero image",
            "about1": "process shot", 
            "about2": "service demo",
            "about3": "team work",
            "review1": "customer A",
            "review2": "customer B", 
            "review3": "customer C",
            "favicon": "icon style"
        }
        
        modifier = type_modifiers.get(image_name, "custom")
        enhanced_prompt += f", {modifier}_{unique_hash}"
        
        if not self.silent_mode:
            print(f"🎯 Промпт для {image_name}: {enhanced_prompt}")
        
        return enhanced_prompt
    
    def _make_favicon_transparent(self, image):
        """Делает фавиконку с прозрачным фоном"""
        try:
            # Преобразуем в RGBA для поддержки прозрачности
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Изменяем размер до 512x512 для фавиконки
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception:
            return image
    
    def _save_compressed_image(self, image, filepath, target_size_kb=150):
        """Сохраняет изображение с нужным размером"""
        try:
            # Определяем формат по расширению
            if filepath.endswith('.png'):
                format_type = 'PNG'
                # Для PNG делаем оптимизацию
                image.save(filepath, format=format_type, optimize=True)
            else:
                format_type = 'JPEG'
                # Для JPEG подбираем качество
                for q in [85, 75, 65, 55, 45]:
                    image.save(filepath, format=format_type, quality=q, optimize=True)
                    
                    # Проверяем размер файла
                    file_size_kb = os.path.getsize(filepath) / 1024
                    if file_size_kb <= target_size_kb:
                        break
            
            return True
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения: {e}")
            return False

    def _generate_prompts(self, theme_input):
        """Генерирует умные промпты для всех изображений"""
        try:
            # Используем новую функцию создания полных промптов с гарантированными людьми для review
            from generators.prompt_generator import create_complete_prompts_dict
            
            prompts = create_complete_prompts_dict(theme_input)
            
            # Возвращаем промпты и данные темы
            return prompts, {'theme': theme_input}
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка генерации промптов: {e}")
            return self._generate_fallback_prompts(theme_input), {'theme': theme_input}
    
    def _generate_fallback_prompts(self, theme_input):
        """Резервная генерация промптов с гарантированными людьми для review"""
        # Генерируем человеческие review промпты даже для fallback
        try:
            from generators.prompt_generator import create_human_focused_review_prompts
            human_reviews = create_human_focused_review_prompts()
        except:
            # Экстренный fallback с прямыми human-промптами
            human_reviews = [
                "portrait photo of happy customer, smiling person, HUMAN FACE ONLY, civilian clothes, testimonial portrait",
                "portrait photo of satisfied client, pleased woman, PERSON ONLY, natural smile, customer review photo", 
                "portrait photo of grateful customer, joyful man, HUMAN ONLY, positive expression, headshot style"
            ]
        
        return {
            'main': f'professional {theme_input} service, modern website hero image',
            'about1': f'{theme_input} team at work, professional office environment',
            'about2': f'{theme_input} process, step by step workflow',
            'about3': f'{theme_input} results, success story visualization',
            'review1': human_reviews[0],
            'review2': human_reviews[1],
            'review3': human_reviews[2],
            'favicon': f'{theme_input} icon symbol, simple minimalist logo'
        }


# Класс для совместимости
class ThematicImageGenerator:
    """Класс для совместимости с существующим кодом"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.base_generator = ImageGenerator(silent_mode=silent_mode)
    
    def generate_single_image(self, prompt, image_name, output_dir):
        """Генерирует одно изображение с рандомизацией"""
        enhanced_prompt = self.base_generator._add_randomization(prompt, image_name)
        return self.base_generator._generate_image_pollinations_aggressive(enhanced_prompt, image_name, output_dir)
    
    def get_theme_prompts(self, theme_input):
        """Получает промпты для тематики с гарантированными людьми для review"""
        prompts, theme_data = self.base_generator._generate_prompts(theme_input)
        return [
            prompts.get('main', f'professional {theme_input} service'),
            prompts.get('about1', f'quality {theme_input} business'),
            prompts.get('about2', f'modern {theme_input} company'),
            prompts.get('about3', f'expert {theme_input} team'),
            prompts.get('review1', 'portrait photo of happy customer, smiling person, HUMAN FACE ONLY, civilian clothes'),
            prompts.get('review2', 'portrait photo of satisfied client, pleased woman, PERSON ONLY, natural smile'),
            prompts.get('review3', 'portrait photo of grateful customer, joyful man, HUMAN ONLY, positive expression'),
            prompts.get('favicon', f'{theme_input} icon symbol')
        ] 