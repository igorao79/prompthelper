#!/usr/bin/env python3
"""
Генератор фавиконок на основе DiceBear API
Бесплатный сервис с множеством стилей и разнообразием
"""

import requests
import random
import hashlib
import os
from pathlib import Path

class DiceBearFavicon:
    """Генератор фавиконок через DiceBear API"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.base_url = "https://api.dicebear.com/9.x"
        
        # Стили для разных тематик
        self.theme_styles = {
            'кафе': ['bottts', 'personas', 'fun-emoji', 'avataaars', 'pixel-art'],
            'ресторан': ['avataaars', 'personas', 'lorelei', 'miniavs', 'fun-emoji'],
            'автомойка': ['bottts', 'pixel-art', 'shapes', 'identicon', 'rings'],
            'парикмахерская': ['avataaars', 'lorelei', 'personas', 'miniavs', 'fun-emoji'],
            'стоматология': ['avataaars', 'personas', 'miniavs', 'fun-emoji', 'pixel-art'],
            'фитнес': ['avataaars', 'personas', 'pixel-art', 'fun-emoji', 'bottts'],
            'строительство': ['bottts', 'pixel-art', 'shapes', 'identicon', 'rings'],
            'салон': ['lorelei', 'personas', 'avataaars', 'miniavs', 'fun-emoji'],
            'юрист': ['avataaars', 'personas', 'miniavs', 'pixel-art', 'identicon'],
            'медицин': ['avataaars', 'personas', 'miniavs', 'fun-emoji', 'pixel-art'],
            'технолог': ['bottts', 'pixel-art', 'identicon', 'shapes', 'rings'],
            'образован': ['avataaars', 'personas', 'miniavs', 'fun-emoji', 'pixel-art'],
            'финанс': ['avataaars', 'personas', 'miniavs', 'identicon', 'pixel-art'],
            'недвижим': ['avataaars', 'personas', 'miniavs', 'identicon', 'shapes'],
            'туризм': ['avataaars', 'personas', 'lorelei', 'miniavs', 'fun-emoji'],
            'спорт': ['avataaars', 'personas', 'pixel-art', 'fun-emoji', 'bottts'],
        }
        
        # Цветовые схемы для разных тематик
        self.theme_colors = {
            'кафе': ['8B4513', 'D2691E', 'CD853F', 'F5DEB3', 'DEB887'],
            'ресторан': ['DC143C', 'FF6347', 'FFD700', 'FFA500', 'FF4500'],
            'автомойка': ['0000FF', '00BFFF', '1E90FF', '4169E1', '6495ED'],
            'парикмахерская': ['FF69B4', 'FF1493', 'DA70D6', 'BA55D3', 'DDA0DD'],
            'стоматология': ['00CED1', '48D1CC', '20B2AA', '87CEEB', '00BFFF'],
            'фитнес': ['FF6347', 'FF4500', 'FF8C00', 'FFA500', 'FFD700'],
            'строительство': ['FF8C00', 'FFD700', 'DAA520', 'B8860B', 'CD853F'],
            'салон': ['FF69B4', 'FF1493', 'C71585', 'DA70D6', 'BA55D3'],
            'юрист': ['2F4F4F', '696969', '778899', '708090', '8B8B8B'],
            'медицин': ['00CED1', '48D1CC', '20B2AA', '87CEEB', '4682B4'],
            'технолог': ['4169E1', '0000FF', '1E90FF', '6495ED', '87CEEB'],
            'образован': ['4169E1', '0000FF', '1E90FF', '6495ED', '87CEEB'],
            'финанс': ['228B22', '32CD32', '00FF00', '90EE90', '98FB98'],
            'недвижим': ['8B4513', 'CD853F', 'D2691E', 'DEB887', 'F5DEB3'],
            'туризм': ['4169E1', '0000FF', '1E90FF', '6495ED', '87CEEB'],
            'спорт': ['FF6347', 'FF4500', 'FF8C00', 'FFA500', 'FFD700'],
        }
        
    def generate_favicon(self, theme, output_path="", size=512):
        """
        Генерирует фавиконку для тематики
        
        Args:
            theme (str): Тематика бизнеса
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки
            
        Returns:
            bool: Успешность генерации
        """
        try:
            if not self.silent_mode:
                print(f"🎨 Генерирую DiceBear фавиконку для: {theme}")
            
            # Выбираем стиль и параметры
            style_name, params = self._get_style_and_params(theme)
            
            if not self.silent_mode:
                print(f"🎯 Стиль: {style_name}")
                print(f"🌟 Seed: {params.get('seed', 'random')}")
            
            # Генерируем URL
            url = self._build_url(style_name, params, size)
            
            # Скачиваем изображение
            success = self._download_image(url, output_path)
            
            if success and not self.silent_mode:
                print(f"✅ Фавиконка создана: {output_path}")
            
            return success
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации фавиконки: {e}")
            return False
    
    def _get_style_and_params(self, theme):
        """Выбирает стиль и параметры для тематики"""
        # Находим подходящие стили
        styles = self._get_theme_styles(theme)
        
        # Выбираем случайный стиль
        style_name = random.choice(styles)
        
        # Создаем уникальный seed на основе тематики и времени
        seed = self._generate_seed(theme)
        
        # Базовые параметры
        params = {
            'seed': seed,
            'radius': random.randint(0, 20),
            'scale': random.randint(80, 120),
        }
        
        # Добавляем тематические цвета
        colors = self._get_theme_colors(theme)
        if colors:
            params['backgroundColor'] = random.choice(colors)
        
        # Специфичные параметры для разных стилей
        if style_name == 'avataaars':
            params.update({
                'accessoriesProbability': random.randint(10, 50),
                'facialHairProbability': random.randint(10, 40),
                'topProbability': random.randint(70, 100),
            })
        
        elif style_name == 'bottts':
            params.update({
                'colorful': random.choice([True, False]),
            })
        
        elif style_name == 'pixel-art':
            params.update({
                'glassesProbability': random.randint(0, 30),
                'flip': random.choice([True, False]),
            })
        
        elif style_name == 'fun-emoji':
            params.update({
                'translateX': random.randint(-10, 10),
                'translateY': random.randint(-10, 10),
                'rotate': random.randint(0, 360),
            })
        
        elif style_name == 'shapes':
            if colors and len(colors) >= 3:
                params.update({
                    'colors': random.sample(colors, 3),
                })
        
        elif style_name == 'identicon':
            if colors and len(colors) >= 2:
                params.update({
                    'colors': random.sample(colors, 2),
                })
        
        return style_name, params
    
    def _get_theme_styles(self, theme):
        """Получает стили для тематики"""
        theme_lower = theme.lower()
        
        # Ищем подходящие стили
        for key, styles in self.theme_styles.items():
            if key in theme_lower:
                return styles
        
        # Стили по умолчанию
        return ['avataaars', 'bottts', 'pixel-art', 'personas', 'fun-emoji']
    
    def _get_theme_colors(self, theme):
        """Получает цвета для тематики"""
        theme_lower = theme.lower()
        
        # Ищем подходящие цвета
        for key, colors in self.theme_colors.items():
            if key in theme_lower:
                return colors
        
        # Цвета по умолчанию
        return ['4169E1', 'FF6347', '32CD32', 'FFD700', 'FF69B4']
    
    def _generate_seed(self, theme):
        """Создает уникальный seed для тематики"""
        # Используем комбинацию тематики + случайное число для разнообразия
        base_seed = f"{theme}_{random.randint(1000, 9999)}"
        
        # Хешируем для создания стабильного seed
        return hashlib.md5(base_seed.encode()).hexdigest()[:10]
    
    def _build_url(self, style_name, params, size):
        """Строит URL для API запроса"""
        # Базовый URL
        url = f"{self.base_url}/{style_name}/png"
        
        # Добавляем параметры
        query_params = []
        for key, value in params.items():
            if isinstance(value, bool):
                query_params.append(f"{key}={str(value).lower()}")
            elif isinstance(value, list):
                query_params.append(f"{key}={','.join(map(str, value))}")
            else:
                query_params.append(f"{key}={value}")
        
        # Размер для PNG
        query_params.append(f"size={min(size, 256)}")  # DiceBear ограничивает PNG до 256x256
        
        if query_params:
            url += "?" + "&".join(query_params)
        
        return url
    
    def _download_image(self, url, output_path):
        """Скачивает изображение по URL"""
        try:
            # Делаем запрос
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Сохраняем файл
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except requests.exceptions.RequestException as e:
            if not self.silent_mode:
                print(f"❌ Ошибка скачивания: {e}")
            return False
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def get_available_styles(self):
        """Возвращает список доступных стилей"""
        return [
            'adventurer', 'avataaars', 'big-ears', 'big-smile', 'bottts',
            'croodles', 'fun-emoji', 'identicon', 'initials', 'lorelei',
            'micah', 'miniavs', 'notionists', 'open-peeps', 'personas',
            'pixel-art', 'rings', 'shapes', 'thumbs'
        ]
    
    def test_connection(self):
        """Тестирует соединение с API"""
        try:
            test_url = f"{self.base_url}/avataaars/png?seed=test&size=32"
            response = requests.get(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False 