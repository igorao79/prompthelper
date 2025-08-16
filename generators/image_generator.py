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
    
    def __init__(self, silent_mode=False, fast_mode=True, max_workers=3):
        self.silent_mode = silent_mode
        self.fast_mode = fast_mode  # Быстрый режим Pollinations (меньше попыток/размер)
        self.max_workers = max(1, int(max_workers))
        self._retry_total = 3 if fast_mode else 5
        self._backoff_factor = 0.5 if fast_mode else 1
        
        if not self.silent_mode:
            speed_text = "БЫСТРЫЙ" if fast_mode else "СТАНДАРТ"
            print(f"🎨 ImageGenerator - AI-ГЕНЕРАЦИЯ, {speed_text}, ТОЛЬКО Pollinations API!")
    
    def generate_thematic_set(self, theme_input, media_dir, progress_callback=None):
        """
        Генерирует полный набор тематических изображений через Pollinations API
        
        Args:
            theme_input (str): Тематика 
            media_dir (str): Путь к папке media
            progress_callback (callable): Функция обратного вызова
            
        Returns:
            int: Количество успешно созданных изображений
        """
        
        if not self.silent_mode:
            print(f"🎨 AI-ГЕНЕРАЦИЯ: Кардинально разные промпты для {theme_input}")
        
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
        # Позволяем ограничить набор изображений через переменную окружения для бенчмарка
        try:
            img_limit = int(os.getenv('IMG_LIMIT', '0') or '0')
            if img_limit > 0:
                image_names = image_names[:img_limit]
        except Exception:
            pass
        generated_count = 0
        
        # Получаем тематические промпты
        tematic_prompts, theme_data = self._generate_prompts(theme_input)
        
        # Параллельная генерация для ускорения (ограниченное число потоков)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def build_prompt_for_image(image_name):
            if image_name in ["review1", "review2", "review3"]:
                if not self.silent_mode:
                    print(f"🔥 {image_name}: Активируем систему разнообразия лиц")
                try:
                    from generators.prompt_generator import create_human_focused_review_prompts
                    human_reviews = create_human_focused_review_prompts()
                    review_index = int(image_name[-1]) - 1
                    base_prompt = human_reviews[review_index]
                except Exception:
                    base_prompt = "happy customer portrait"
            elif image_name == "favicon":
                base_prompt = f"{theme_input} simple icon logo, minimalist business symbol"
            else:
                base_prompt = tematic_prompts.get(image_name, f'professional {theme_input} service')
            # Рандомизация (короткая в быстром режиме)
            # В обычном (качественном) режиме используем расширенную рандомизацию,
            # в быстром — облегченную.
            if self.fast_mode:
                return self._add_simple_randomization(base_prompt, image_name)
            return self._add_randomization(base_prompt, image_name)

        def generate_one(image_name, index):
            from time import perf_counter
            start_ts = perf_counter()
            if progress_callback:
                progress_callback(f"🎨 Генерация {image_name} ({index}/8)...")
            if not self.silent_mode:
                print(f"🔄 Генерация {image_name} ({index}/8)...")
            prompt = build_prompt_for_image(image_name)
            # Ограничиваем длину промпта, чтобы не упираться в лимиты URL
            prompt = self._truncate_prompt(prompt)
            result = self._generate_image_pollinations_aggressive(prompt, image_name, media_dir)
            elapsed = perf_counter() - start_ts
            if not self.silent_mode:
                print(f"⏱️ {image_name}: {elapsed:.2f}s")
            return (image_name, result, elapsed)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(generate_one, name, i+1): name for i, name in enumerate(image_names)}
            completed = 0
            total_elapsed = 0.0
            for future in as_completed(futures):
                image_name = futures[future]
                try:
                    name, result, elapsed = future.result()
                    total_elapsed += (elapsed or 0)
                    if result:
                        generated_count += 1
                        if not self.silent_mode:
                            print(f"✅ {name}: готово за {elapsed:.2f}s")
                    else:
                        if not self.silent_mode:
                            print(f"❌ {name}: не удалось создать")
                except Exception as e:
                    if not self.silent_mode:
                        print(f"⚠️ Ошибка при создании {image_name}: {e}")
                completed += 1
                if progress_callback:
                    progress_callback(f"📈 Готово {completed}/8 изображений")
            if not self.silent_mode:
                print(f"⏱️ Суммарное время потоков (без учёта параллелизма): {total_elapsed:.2f}s")
        
        if not self.silent_mode:
            print(f"🎯 Создано {generated_count}/8 AI-изображений")
        
        return generated_count
    
    def _generate_image_pollinations_aggressive(self, prompt, image_name, media_dir):
        """Генерирует изображение ТОЛЬКО через Pollinations API с агрессивными настройками"""
        # Добавляем рандомизацию к промпту
        enhanced_prompt = self._add_randomization(prompt, image_name)
        enhanced_prompt = self._truncate_prompt(enhanced_prompt)
        
        # Настройки для разных типов изображений
        if image_name == 'favicon':
            target_size_kb = 50
            output_path = Path(media_dir) / f"{image_name}.png"
            api_params = "?width=512&height=512&model=flux&enhance=false&nologo=true"
        else:
            target_size_kb = 150 if not self.fast_mode else 120
            output_path = Path(media_dir) / f"{image_name}.jpg"
            if self.fast_mode:
                api_params = "?width=832&height=512&model=flux&enhance=false&nologo=true"
            else:
                # Вернули прежние параметры качества как до смены интерфейса
                api_params = "?width=1024&height=768&model=flux&enhance=true&nologo=true"
        
        # Pollinations API URL
        api_url = f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}{api_params}"
        
        if not self.silent_mode:
            print(f"🌐 Подключение к Pollinations API: {enhanced_prompt[:50]}...")
        
        # Создаем агрессивную сессию
        session = self._create_aggressive_session()
        
        # Пробуем несколько раз с разными настройками
        attempts = 3 if self.fast_mode else 4
        for attempt in range(attempts):
            if not self.silent_mode:
                print(f"🔄 Попытка {attempt + 1}/3...")
            
            try:
                # Агрессивные таймауты
                timeout_cfg = (10, 30) if self.fast_mode else (15, 60)
                response = session.get(api_url, timeout=timeout_cfg, stream=True)
                
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
                        # Повторим без stream для надёжности
                        try:
                            raw_resp = session.get(api_url, timeout=timeout_cfg, stream=False)
                            if raw_resp.status_code == 200 and len(raw_resp.content) > 1000:
                                image = Image.open(BytesIO(raw_resp.content))
                                if image_name == 'favicon':
                                    image = self._make_favicon_transparent(image)
                                if self._save_compressed_image(image, str(output_path), target_size_kb=target_size_kb):
                                    return str(output_path)
                        except Exception:
                            pass
                
                elif response.status_code == 429:
                    if not self.silent_mode:
                        print(f"⏰ Pollinations API: Лимит запросов, короткая пауза...")
                    time.sleep(4 if self.fast_mode else 10)
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
        
        # Если все попытки не удались – пробуем альтернативные параметры (другая модель/размер)
        try:
            alt_params = "?width=960&height=640&model=flux&enhance=true&nologo=true" if not self.fast_mode else "?width=768&height=512&model=turbo&enhance=false&nologo=true"
            if image_name == 'favicon':
                alt_params = "?width=512&height=512&model=turbo&enhance=false&nologo=true"
            api_url_alt = f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}{alt_params}"
            resp = session.get(api_url_alt, timeout=(10, 30), stream=False)
            if resp.status_code == 200 and len(resp.content) > 1000:
                image = Image.open(BytesIO(resp.content))
                if image_name == 'favicon':
                    image = self._make_favicon_transparent(image)
                if self._save_compressed_image(image, str(output_path), target_size_kb=target_size_kb):
                    return str(output_path)
        except Exception:
            pass

        # Если после всех вариантов не удалось
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
            total=self._retry_total,
            backoff_factor=self._backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
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

    def _add_simple_randomization(self, prompt: str, image_name: str) -> str:
        """Облегчённая рандомизация для fast_mode: короче строка, меньше терминов.
        Сохраняем тематику, добавляем немного качества и уникальности, чтобы ускорить API и не бить лимиты URL."""
        try:
            import random, time, hashlib
            base = prompt.strip()
            # Короткий набор улучшений
            quality_terms = ["high quality", "professional", "photorealistic"]
            style_terms = ["modern", "clean", "premium"]
            selected = ", ".join(random.sample(quality_terms, 1) + random.sample(style_terms, 1))
            # Уникальность для обхода кэша
            uniq = hashlib.md5(f"{image_name}_{time.time()}_{random.randint(1,99999)}".encode()).hexdigest()[:6]
            enhanced = f"{base}, {selected}, u_{uniq}"
            return enhanced
        except Exception:
            return prompt

    def _truncate_prompt(self, prompt: str, max_len: int = 750) -> str:
        """Ограничивает длину промпта, чтобы не превышать лимиты URL у Pollinations.
        Обрезает по границе слов, добавляя многоточие при необходимости."""
        try:
            if len(prompt) <= max_len:
                return prompt
            cut = prompt[:max_len]
            # стараемся не обрывать слово
            last_space = cut.rfind(' ')
            if last_space > 0:
                cut = cut[:last_space]
            return cut + " ..."
        except Exception:
            return prompt[:max_len]
    
    
    
    def _make_favicon_transparent(self, image):
        """Делает фавиконку с прозрачным фоном и оптимизирует для иконки"""
        try:
            # Преобразуем в RGBA для поддержки прозрачности
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Изменяем размер до 512x512 для фавиконки
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            # НОВОЕ: Попытка улучшить контрастность для иконок
            try:
                from PIL import ImageEnhance
                # Усиливаем контрастность для четкости иконки
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)  # Небольшое увеличение контраста
                
                # Усиливаем резкость для четкости деталей
                sharpness_enhancer = ImageEnhance.Sharpness(image)
                image = sharpness_enhancer.enhance(1.1)  # Небольшое увеличение резкости
            except:
                pass  # Если не получается улучшить, используем оригинал
            
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
                if getattr(self, 'fast_mode', False):
                    # Быстрый однопроходный сейв
                    q = 70
                    image.save(filepath, format=format_type, quality=q, optimize=True)
                else:
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
        """Генерирует промпты для всех изображений (без простых режимов и фоллбеков)"""
        from generators.prompt_generator import create_complete_prompts_dict
        prompts = create_complete_prompts_dict(theme_input)
        return prompts, {'theme': theme_input}

    def _generate_simple_prompts(self, theme_input):
        """Генерирует ПРОСТЫЕ базовые промпты БЕЗ сложной обработки"""
        
        # Простые понятные промпты для каждого типа изображения
        simple_prompts = {
            'main': f'{theme_input} business, modern office building',
            'about1': f'{theme_input} professional team at work',
            'about2': f'{theme_input} service process, modern workplace',
            'about3': f'{theme_input} quality tools and equipment',
            'favicon': f'{theme_input} simple icon logo'
        }
        
        # ДЛЯ REVIEW ИСПОЛЬЗУЕМ СЛОЖНУЮ СИСТЕМУ ДАЖЕ В ПРОСТОМ РЕЖИМЕ!
        if not self.silent_mode:
            print(f"🔥 ПРОСТОЙ РЕЖИМ: Активируем сложную систему лиц для review!")
        
        try:
            from generators.prompt_generator import create_human_focused_review_prompts
            human_reviews = create_human_focused_review_prompts()
            
            simple_prompts.update({
                'review1': human_reviews[0],  # Западный/Европейский тип
                'review2': human_reviews[1],  # Азиатский/Восточный тип  
                'review3': human_reviews[2]   # Африканский/Латиноамериканский тип
            })
            
            if not self.silent_mode:
                print(f"✅ ПРОСТОЙ РЕЖИМ: Получены сложные промпты для review!")
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ ПРОСТОЙ РЕЖИМ: Ошибка сложной системы ({e}), используем fallback")
            
            # Fallback к простым человеческим промптам
            simple_prompts.update({
                'review1': 'happy customer portrait, smiling person',
                'review2': 'satisfied client photo, pleased woman smiling',
                'review3': 'grateful customer headshot, joyful man'
            })
        
        if not self.silent_mode:
            print(f"🎯 ПРОСТЫЕ базовые промпты готовы для: {theme_input}")
        
        return simple_prompts, {'theme': theme_input}


# Класс для совместимости
# Конец файла