# -*- coding: utf-8 -*-

"""
Модуль для работы с Icons8 API
Получение иконок по тематике для использования в качестве фавиконок
"""

import requests
import random
import time
from urllib.parse import quote
import os
from PIL import Image
from io import BytesIO

class Icons8Manager:
    """Менеджер для работы с Icons8 API"""
    
    def __init__(self, api_key=None, silent_mode=False):
        """
        Инициализация Icons8 Manager
        
        Args:
            api_key (str): API ключ Icons8 (опционально)
            silent_mode (bool): Режим без вывода сообщений
        """
        self.api_key = api_key
        self.silent_mode = silent_mode
        self.base_url = "https://search.icons8.com/api/iconsets/v5/search"
        self.icon_url_base = "https://img.icons8.com"
        
        # Кэш для результатов поиска
        self.search_cache = {}
        
        if not self.silent_mode:
            print("🎯 Icons8 Manager инициализирован")
    
    def search_icons_by_theme(self, theme, limit=20):
        """
        Поиск иконок по тематике
        
        Args:
            theme (str): Тематика для поиска
            limit (int): Количество результатов
            
        Returns:
            list: Список иконок
        """
        try:
            # Проверяем кэш
            cache_key = f"{theme}_{limit}"
            if cache_key in self.search_cache:
                if not self.silent_mode:
                    print(f"📋 Использую кэшированные результаты для '{theme}'")
                return self.search_cache[cache_key]
            
            if not self.silent_mode:
                print(f"🔍 Поиск иконок для тематики: {theme}")
            
            # Переводим тематику на английский для поиска
            english_theme = self._translate_theme_to_english(theme)
            
            # Параметры запроса
            params = {
                'term': english_theme,
                'limit': limit,
                'offset': 0,
                'category': '',
                'subcategory': '',
                'style': '',
                'color': '',
                'shape': '',
                'format': 'png',
                'size': '512'
            }
            
            # Выполняем запрос без API ключа (публичный поиск)
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                icons = self._parse_search_results(data)
                
                # Сохраняем в кэш
                self.search_cache[cache_key] = icons
                
                if not self.silent_mode:
                    print(f"✅ Найдено {len(icons)} иконок для '{theme}'")
                
                return icons
            else:
                if not self.silent_mode:
                    print(f"⚠️ Ошибка поиска Icons8: {response.status_code}")
                return []
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка поиска Icons8: {e}")
            return []
    
    def _translate_theme_to_english(self, theme):
        """Переводит тематику на английский для поиска"""
        translations = {
            # Кулинария
            'кулинар': 'cooking chef food kitchen',
            'повар': 'chef cook cooking',
            'готовк': 'cooking food kitchen',
            'еда': 'food restaurant',
            'ресторан': 'restaurant food dining',
            'кафе': 'cafe coffee restaurant',
            
            # Автомобили  
            'авто': 'car automotive vehicle',
            'машин': 'car vehicle auto',
            'автомобил': 'automobile car vehicle',
            'автосервис': 'car service garage repair',
            'ремонт авто': 'car repair service garage',
            'автосалон': 'car dealership showroom',
            
            # Медицина
            'медицин': 'medical health doctor',
            'здоровье': 'health medical care',
            'лечение': 'treatment medical health',
            'стоматолог': 'dentist dental teeth',
            'зубы': 'teeth dental dentist',
            'клиника': 'clinic medical hospital',
            
            # Образование
            'курсы': 'education course learning',
            'обучение': 'education learning study',
            'школа': 'school education learning',
            'учеба': 'study education learning',
            
            # Красота
            'красота': 'beauty salon spa',
            'салон': 'salon beauty spa',
            'косметолог': 'beauty cosmetics spa',
            'парикмахер': 'hairdresser salon beauty',
            
            # Фитнес
            'фитнес': 'fitness gym sport',
            'спорт': 'sport fitness gym',
            'тренировк': 'training fitness workout',
            
            # Фотография
            'фото': 'photography camera photo',
            'съемк': 'photography shooting camera',
            'камер': 'camera photography photo',
            
            # Музыка
            'музык': 'music instrument sound',
            'инструмент': 'instrument music sound',
            
            # Технологии
            'технолог': 'technology tech computer',
            'компьютер': 'computer technology it',
            'програм': 'programming code computer',
            'сайт': 'website web internet',
            
            # Строительство
            'строител': 'construction building tools',
            'ремонт': 'repair tools construction',
            'стройк': 'construction building',
        }
        
        theme_lower = theme.lower()
        
        # Ищем подходящий перевод
        for ru_word, en_translation in translations.items():
            if ru_word in theme_lower:
                return en_translation
        
        # Если не найден конкретный перевод, возвращаем общие термины
        if any(word in theme_lower for word in ['курс', 'обучен', 'школ']):
            return 'education learning course'
        elif any(word in theme_lower for word in ['бизнес', 'компан', 'услуг']):
            return 'business service company'
        else:
            # Возвращаем исходную тематику + общие термины
            return f"{theme} business service"
    
    def _parse_search_results(self, data):
        """Парсит результаты поиска Icons8"""
        icons = []
        
        try:
            # Структура ответа может отличаться, пробуем разные варианты
            items = []
            
            if 'icons' in data:
                items = data['icons']
            elif 'results' in data:
                items = data['results'] 
            elif isinstance(data, list):
                items = data
            
            for item in items:
                try:
                    icon_info = self._extract_icon_info(item)
                    if icon_info:
                        icons.append(icon_info)
                except Exception as e:
                    continue
                    
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка парсинга результатов: {e}")
        
        return icons
    
    def _extract_icon_info(self, item):
        """Извлекает информацию об иконке из результата"""
        try:
            # Пробуем разные форматы данных
            icon_id = None
            name = "icon"
            category = "general"
            
            # Возможные поля для ID
            if 'id' in item:
                icon_id = item['id']
            elif 'icon_id' in item:
                icon_id = item['icon_id']
            elif 'uuid' in item:
                icon_id = item['uuid']
            
            # Возможные поля для имени
            if 'name' in item:
                name = item['name']
            elif 'title' in item:
                name = item['title']
            
            # Возможные поля для категории
            if 'category' in item:
                category = item.get('category', {}).get('name', 'general')
            elif 'categories' in item and item['categories']:
                category = item['categories'][0].get('name', 'general')
            
            if icon_id:
                return {
                    'id': icon_id,
                    'name': name,
                    'category': category,
                    'url_512': f"{self.icon_url_base}/512/{icon_id}.png",
                    'url_256': f"{self.icon_url_base}/256/{icon_id}.png",
                    'url_128': f"{self.icon_url_base}/128/{icon_id}.png"
                }
                
        except Exception as e:
            pass
            
        return None
    
    def get_random_favicon_for_theme(self, theme):
        """
        Получает случайную фавиконку для тематики
        
        Args:
            theme (str): Тематика
            
        Returns:
            dict: Информация о выбранной иконке или None
        """
        icons = self.search_icons_by_theme(theme, limit=10)
        
        if icons:
            selected_icon = random.choice(icons)
            if not self.silent_mode:
                print(f"🎯 Выбрана иконка: {selected_icon['name']} (ID: {selected_icon['id']})")
            return selected_icon
        else:
            if not self.silent_mode:
                print(f"❌ Не найдено иконок для тематики '{theme}'")
            return None
    
    def download_icon(self, icon_info, size=512, output_path=None):
        """
        Загружает иконку
        
        Args:
            icon_info (dict): Информация об иконке
            size (int): Размер иконки (128, 256, 512)
            output_path (str): Путь для сохранения
            
        Returns:
            PIL.Image: Изображение иконки или None
        """
        try:
            # Выбираем URL по размеру
            if size >= 512:
                url = icon_info['url_512']
            elif size >= 256:
                url = icon_info['url_256']
            else:
                url = icon_info['url_128']
            
            if not self.silent_mode:
                print(f"📥 Загрузка иконки: {url}")
            
            # Загружаем иконку
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                # Создаем изображение
                image = Image.open(BytesIO(response.content))
                
                # Сохраняем если указан путь
                if output_path:
                    image.save(output_path)
                    if not self.silent_mode:
                        print(f"💾 Иконка сохранена: {output_path}")
                
                return image
            else:
                if not self.silent_mode:
                    print(f"❌ Ошибка загрузки: {response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка загрузки иконки: {e}")
            return None
    
    def create_favicon_from_theme(self, theme, output_path, size=512):
        """
        Создает фавиконку для тематики
        
        Args:
            theme (str): Тематика
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            if not self.silent_mode:
                print(f"🎨 Создание фавиконки для тематики: {theme}")
            
            # Получаем случайную иконку
            icon_info = self.get_random_favicon_for_theme(theme)
            
            if not icon_info:
                return False
            
            # Загружаем иконку
            image = self.download_icon(icon_info, size)
            
            if image:
                # Убеждаемся что размер правильный
                if image.size != (size, size):
                    image = image.resize((size, size), Image.Resampling.LANCZOS)
                
                # Конвертируем в RGBA для прозрачности
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Сохраняем
                image.save(output_path)
                
                if not self.silent_mode:
                    print(f"✅ Фавиконка создана: {output_path}")
                    file_size = os.path.getsize(output_path)
                    print(f"📁 Размер файла: {file_size} байт")
                
                return True
            else:
                return False
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания фавиконки: {e}")
            return False

# Fallback функция для использования без API ключа
def try_free_icon_search(theme):
    """
    Пробует найти иконки через открытые источники
    
    Args:
        theme (str): Тематика
        
    Returns:
        list: Список URL иконок
    """
    try:
        # Простой поиск через открытые API
        theme_en = theme.replace('кулинар', 'cooking').replace('авто', 'car').replace('медицин', 'medical')
        
        # Можно добавить другие открытые источники иконок
        # Например, Tabler Icons, Heroicons и т.д.
        
        return []
    except:
        return []

def main():
    """Тестирование Icons8 Manager"""
    print("🧪 Тест Icons8 Manager")
    print("=" * 50)
    
    manager = Icons8Manager()
    
    # Тестируем поиск
    theme = "кулинарные курсы"
    icons = manager.search_icons_by_theme(theme, limit=5)
    
    print(f"\n📋 Найдено {len(icons)} иконок для '{theme}':")
    for i, icon in enumerate(icons[:3], 1):
        print(f"  {i}. {icon['name']} (ID: {icon['id']})")
    
    # Тестируем создание фавиконки
    if icons:
        print(f"\n🎨 Создание тестовой фавиконки...")
        test_path = "test_icons8_favicon.png"
        success = manager.create_favicon_from_theme(theme, test_path)
        
        if success:
            print(f"✅ Тестовая фавиконка создана: {test_path}")
        else:
            print("❌ Не удалось создать тестовую фавиконку")

if __name__ == "__main__":
    main() 