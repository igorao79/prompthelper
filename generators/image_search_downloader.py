"""
Модуль поиска и загрузки изображений из бесплатных источников
Использует Pixabay, Unsplash и агрегатор API для поиска тематических изображений
ПРЕИМУЩЕСТВО: Реальные фото вместо AI-генерации!
"""

import os
import requests
import time
import random
from urllib.parse import quote
from PIL import Image
from io import BytesIO
from pathlib import Path
import json

class ImageSearchDownloader:
    """Класс для поиска и загрузки изображений по тематике из бесплатных источников"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        # API endpoints
        self.pixabay_api = "https://pixabay.com/api/"
        self.unsplash_api = "https://api.unsplash.com/search/photos"
        self.aggregate_api = "https://mulberry-tiny-washer.glitch.me/data"
        
        # API ключи (можно настроить)
        self.pixabay_key = "46654479-d809d8c0df4c3b9a6768ee3a9"  # Публичный ключ для тестов
        self.unsplash_key = None  # Нужно получить на unsplash.com/developers
        
        if not self.silent_mode:
            print("🔍 ImageSearchDownloader - поиск РЕАЛЬНЫХ фотографий!")
    
    def search_and_download_thematic_set(self, theme_input, media_dir, progress_callback=None):
        """
        Ищет и загружает полный набор изображений по тематике
        
        Args:
            theme_input (str): Тематика для поиска (например "шиномонтаж")
            media_dir (str): Папка для сохранения
            progress_callback (callable): Функция прогресса
            
        Returns:
            int: Количество загруженных изображений
        """
        if not self.silent_mode:
            print(f"🔍 ПОИСК РЕАЛЬНЫХ ИЗОБРАЖЕНИЙ по теме: {theme_input}")
        
        # Создаем папку
        try:
            os.makedirs(media_dir, exist_ok=True)
            if not self.silent_mode:
                print(f"📁 Папка создана: {media_dir}")
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания папки: {e}")
            return 0
        
        # Определяем поисковые запросы для разных типов изображений
        search_queries = self._generate_search_queries(theme_input)
        
        image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
        downloaded_count = 0
        
        for i, image_name in enumerate(image_names):
            if progress_callback:
                progress_callback(f"🔍 Поиск {image_name} ({i+1}/8)...")
            
            if not self.silent_mode:
                print(f"🔍 Поиск изображения {image_name} ({i+1}/8)...")
            
            query = search_queries.get(image_name, theme_input)
            
            # Пробуем разные источники
            result = self._download_single_image(query, image_name, media_dir)
            
            if result:
                downloaded_count += 1
                if not self.silent_mode:
                    print(f"✅ {image_name}: Загружено из источника!")
            else:
                if not self.silent_mode:
                    print(f"❌ {image_name}: Не удалось найти подходящее изображение")
        
        if not self.silent_mode:
            print(f"🎯 Загружено {downloaded_count}/8 РЕАЛЬНЫХ изображений!")
        
        return downloaded_count
    
    def _generate_search_queries(self, theme_input):
        """Генерирует специфичные поисковые запросы для каждого типа изображения"""
        
        # Переводим тематику на английский для лучшего поиска
        theme_en = self._translate_theme_to_english(theme_input)
        
        return {
            'main': f"{theme_en} business professional service",
            'about1': f"{theme_en} team work professional",
            'about2': f"{theme_en} process workflow modern",  
            'about3': f"{theme_en} equipment tools technology",
            'review1': "happy customer smiling portrait business",
            'review2': "satisfied client woman professional",
            'review3': "pleased customer man testimonial",
            'favicon': f"{theme_en} icon logo symbol simple"
        }
    
    def _translate_theme_to_english(self, theme_ru):
        """Простой перевод популярных тематик на английский"""
        translations = {
            'шиномонтаж': 'tire service auto repair',
            'автосервис': 'auto service car repair', 
            'сантехник': 'plumber plumbing service',
            'электрик': 'electrician electrical service',
            'клининг': 'cleaning service housekeeping',
            'ремонт': 'repair service maintenance',
            'строительство': 'construction building',
            'медицина': 'medical healthcare clinic',
            'образование': 'education learning school',
            'юридические услуги': 'legal services lawyer',
            'бухгалтерия': 'accounting bookkeeping finance',
            'красота': 'beauty salon cosmetics',
            'фитнес': 'fitness gym sport',
            'ресторан': 'restaurant food dining',
            'доставка': 'delivery shipping logistics',
            'недвижимость': 'real estate property',
            'страхование': 'insurance financial',
            'туризм': 'travel tourism vacation'
        }
        
        # Ищем точное совпадение
        for ru_key, en_value in translations.items():
            if ru_key.lower() in theme_ru.lower():
                return en_value
        
        # Если не нашли, возвращаем как есть + business
        return f"{theme_ru} business service"
    
    def _download_single_image(self, query, image_name, media_dir):
        """Загружает одно изображение, пробуя разные источники"""
        
        # Источники в порядке приоритета
        sources = [
            ('pixabay', self._search_pixabay),
            ('aggregate', self._search_aggregate_api),
            ('unsplash', self._search_unsplash) if self.unsplash_key else None
        ]
        
        # Убираем None
        sources = [s for s in sources if s is not None]
        
        for source_name, search_func in sources:
            if not self.silent_mode:
                print(f"🔍 Пробуем {source_name} для запроса: {query}")
            
            try:
                image_url = search_func(query, image_name)
                if image_url:
                    downloaded_path = self._download_image_from_url(
                        image_url, image_name, media_dir
                    )
                    if downloaded_path:
                        if not self.silent_mode:
                            print(f"✅ Загружено из {source_name}: {image_url[:50]}...")
                        return downloaded_path
                    
            except Exception as e:
                if not self.silent_mode:
                    print(f"⚠️ Ошибка {source_name}: {str(e)[:50]}...")
                continue
        
        return None
    
    def _search_pixabay(self, query, image_name):
        """Поиск в Pixabay API"""
        params = {
            'key': self.pixabay_key,
            'q': query,
            'image_type': 'photo',
            'orientation': 'horizontal',
            'category': 'business',
            'min_width': 640,
            'min_height': 480,
            'safesearch': 'true',
            'per_page': 20
        }
        
        # Специальные настройки для разных типов
        if image_name == 'favicon':
            params.update({
                'orientation': 'all',
                'category': 'symbols',
                'image_type': 'vector'
            })
        elif 'review' in image_name:
            params.update({
                'category': 'people',
                'orientation': 'vertical'
            })
        
        response = requests.get(self.pixabay_api, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('hits'):
                # Берем первое изображение из топа
                hit = data['hits'][0]
                return hit.get('webformatURL') or hit.get('largeImageURL')
        
        return None
    
    def _search_aggregate_api(self, query, image_name):
        """Поиск через агрегатор API"""
        params = {
            'query': query,
            'service': 'unsplash,pixabay'  # Исключаем платные источники
        }
        
        response = requests.get(self.aggregate_api, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('imageData'):
                # Берем первое изображение
                image_data = data['imageData'][0]
                return image_data.get('src')
        
        return None
    
    def _search_unsplash(self, query, image_name):
        """Поиск в Unsplash API (если есть ключ)"""
        if not self.unsplash_key:
            return None
            
        headers = {'Authorization': f'Client-ID {self.unsplash_key}'}
        params = {
            'query': query,
            'orientation': 'landscape',
            'per_page': 20
        }
        
        if 'review' in image_name:
            params['orientation'] = 'portrait'
        
        response = requests.get(self.unsplash_api, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                return result.get('urls', {}).get('regular')
        
        return None
    
    def _download_image_from_url(self, image_url, image_name, media_dir):
        """Загружает изображение по URL и обрабатывает его"""
        try:
            # Загружаем изображение
            response = requests.get(image_url, timeout=30, stream=True)
            
            if response.status_code == 200:
                # Открываем изображение
                image = Image.open(BytesIO(response.content))
                
                # Определяем путь сохранения
                if image_name == 'favicon':
                    output_path = Path(media_dir) / f"{image_name}.png"
                    target_size_kb = 50
                    # Для фавиконки делаем квадратной
                    image = self._make_favicon(image)
                else:
                    output_path = Path(media_dir) / f"{image_name}.jpg"
                    target_size_kb = 150
                
                # Сохраняем с сжатием
                if self._save_compressed_image(image, str(output_path), target_size_kb):
                    return str(output_path)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка загрузки {image_url[:30]}...: {e}")
        
        return None
    
    def _make_favicon(self, image):
        """Создает фавиконку из изображения"""
        try:
            # Преобразуем в RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Делаем квадратной 512x512
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception:
            return image
    
    def _save_compressed_image(self, image, filepath, target_size_kb=150):
        """Сохраняет изображение с нужным размером"""
        try:
            # Определяем формат
            if filepath.endswith('.png'):
                format_type = 'PNG'
                image.save(filepath, format=format_type, optimize=True)
            else:
                format_type = 'JPEG'
                # Для JPEG подбираем качество
                for quality in [95, 85, 75, 65, 55, 45]:
                    image.save(filepath, format=format_type, quality=quality, optimize=True)
                    
                    # Проверяем размер
                    file_size_kb = os.path.getsize(filepath) / 1024
                    if file_size_kb <= target_size_kb:
                        break
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения: {e}")
            return False


# Функция для интеграции с основной системой
def create_image_search_generator(silent_mode=False):
    """Создает генератор поиска изображений для совместимости"""
    return ImageSearchDownloader(silent_mode=silent_mode)


# Класс для совместимости с существующим кодом  
class ThematicImageSearcher:
    """Класс для совместимости - поиск вместо генерации"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.searcher = ImageSearchDownloader(silent_mode=silent_mode)
    
    def generate_thematic_set(self, theme_input, media_dir, method="search", progress_callback=None):
        """Генерирует набор через поиск вместо AI"""
        return self.searcher.search_and_download_thematic_set(
            theme_input, media_dir, progress_callback
        ) 