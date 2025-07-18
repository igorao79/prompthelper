#!/usr/bin/env python3
"""
Генератор фавиконок на основе Avatar Placeholder API
Использует бесплатный API для генерации случайных аватаров
"""

import requests
import random
import hashlib
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
import time

class RandomAvatarFavicon:
    """Генератор фавиконок через Avatar Placeholder API"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.base_url = "https://avatar.iran.liara.run"
        
        # Тематические имена для разных бизнесов
        self.business_names = {
            'кафе': ['Coffee', 'Espresso', 'Latte', 'Cappuccino', 'Mocha', 'Barista', 'Bean', 'Brew'],
            'кофейня': ['Coffee', 'Espresso', 'Latte', 'Cappuccino', 'Mocha', 'Barista', 'Bean', 'Brew'],
            'ресторан': ['Chef', 'Cook', 'Diner', 'Taste', 'Flavor', 'Dish', 'Menu', 'Grill'],
            'автомойка': ['Clean', 'Wash', 'Shine', 'Auto', 'Car', 'Polish', 'Soap', 'Rinse'],
            'парикмахерская': ['Style', 'Cut', 'Hair', 'Trim', 'Salon', 'Stylist', 'Shear', 'Clip'],
            'стоматология': ['Dental', 'Tooth', 'Smile', 'Care', 'Clean', 'White', 'Bright', 'Health'],
            'фитнес': ['Fit', 'Strong', 'Power', 'Gym', 'Active', 'Sport', 'Train', 'Muscle'],
            'строительство': ['Build', 'Construct', 'Hammer', 'Tool', 'Brick', 'Steel', 'Fix', 'Make'],
            'салон': ['Beauty', 'Style', 'Glam', 'Shine', 'Look', 'Elegant', 'Chic', 'Pretty'],
            'юрист': ['Legal', 'Law', 'Justice', 'Right', 'Fair', 'Judge', 'Case', 'Court'],
            'медицин': ['Health', 'Care', 'Doctor', 'Heal', 'Med', 'Clinic', 'Safe', 'Well'],
            'технолог': ['Tech', 'Digital', 'Code', 'Smart', 'Data', 'Logic', 'Cyber', 'Net'],
            'образован': ['Learn', 'Study', 'Know', 'Teach', 'Brain', 'Mind', 'Smart', 'Wise'],
            'финанс': ['Money', 'Bank', 'Gold', 'Rich', 'Save', 'Invest', 'Profit', 'Cash'],
            'недвижим': ['House', 'Home', 'Build', 'Estate', 'Key', 'Door', 'Roof', 'Room'],
            'доставка': ['Fast', 'Quick', 'Speed', 'Rush', 'Move', 'Go', 'Send', 'Bring'],
            'еды': ['Food', 'Meal', 'Eat', 'Taste', 'Fresh', 'Yummy', 'Dish', 'Cook'],
            'еда': ['Food', 'Meal', 'Eat', 'Taste', 'Fresh', 'Yummy', 'Dish', 'Cook'],
            'доставка еды': ['Food', 'Meal', 'Eat', 'Taste', 'Fresh', 'Yummy', 'Dish', 'Cook'],
            'доставки еды': ['Food', 'Meal', 'Eat', 'Taste', 'Fresh', 'Yummy', 'Dish', 'Cook'],
        }
        
        # Общие варианты для неизвестных тематик
        self.default_names = [
            'Business', 'Pro', 'Expert', 'Master', 'Best', 'Top', 'Prime', 'Elite',
            'Smart', 'Quick', 'Fast', 'Easy', 'Simple', 'Good', 'Great', 'Super'
        ]
        
        if not self.silent_mode:
            print("🎭 RandomAvatarFavicon инициализирован")
    
    def generate_favicon(self, theme, output_path):
        """Генерирует фавиконку для тематики"""
        try:
            # Получаем имя для генерации
            name = self._get_theme_name(theme)
            
            # Определяем тип аватара
            avatar_type = self._get_avatar_type(theme)
            
            # Генерируем URL
            if avatar_type == 'initials':
                url = f"{self.base_url}/username?username={name}"
            elif avatar_type == 'boy':
                url = f"{self.base_url}/public/boy"
            elif avatar_type == 'girl':
                url = f"{self.base_url}/public/girl"
            else:
                url = f"{self.base_url}/public"
            
            if not self.silent_mode:
                print(f"🌐 Запрос к Avatar API: {name} ({avatar_type})")
            
            # Загружаем изображение
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Конвертируем в фавиконку
            image = Image.open(BytesIO(response.content))
            
            # Убеждаемся что изображение квадратное
            if image.size[0] != image.size[1]:
                min_size = min(image.size)
                image = image.crop((0, 0, min_size, min_size))
            
            # Изменяем размер для фавиконки
            image = image.resize((256, 256), Image.Resampling.LANCZOS)
            
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Сохраняем
            image.save(output_path, format='PNG')
            
            if not self.silent_mode:
                print(f"✅ Фавиконка сохранена: {output_path}")
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации фавиконки: {e}")
            return False
    
    def _get_theme_name(self, theme):
        """Получает имя для генерации на основе тематики"""
        theme_lower = theme.lower()
        
        # Ищем подходящие имена для тематики
        for key, names in self.business_names.items():
            if key in theme_lower:
                return random.choice(names)
        
        # Если не нашли специфичное имя, используем общее
        return random.choice(self.default_names)
    
    def _get_avatar_type(self, theme):
        """Определяет тип аватара на основе тематики"""
        theme_lower = theme.lower()
        
        # Для некоторых тематик лучше использовать инициалы
        if any(word in theme_lower for word in ['технолог', 'финанс', 'юрист', 'медицин']):
            return 'initials'
        
        # Для салонов красоты лучше женские аватары
        if any(word in theme_lower for word in ['салон', 'парикмахерская', 'косметолог']):
            return 'girl'
        
        # Для строительства и автосервиса - мужские
        if any(word in theme_lower for word in ['строительство', 'автомойка', 'механик']):
            return 'boy'
        
        # Для остальных - случайный выбор
        return random.choice(['public', 'boy', 'girl', 'initials'])
    
    def generate_diverse_set(self, themes, output_dir):
        """Генерирует разнообразный набор фавиконок для разных тематик"""
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        for i, theme in enumerate(themes):
            output_path = os.path.join(output_dir, f"favicon_{i+1}.png")
            success = self.generate_favicon(theme, output_path)
            results.append(success)
            
            # Небольшая задержка между запросами
            if i < len(themes) - 1:
                time.sleep(0.5)
        
        return results

# Функция для использования в основном коде
def generate_random_avatar_favicon(theme, output_path, silent_mode=False):
    """Генерирует случайную фавиконку-аватар для тематики"""
    generator = RandomAvatarFavicon(silent_mode=silent_mode)
    return generator.generate_favicon(theme, output_path)

if __name__ == "__main__":
    # Тестирование
    generator = RandomAvatarFavicon()
    
    test_themes = [
        "кафе", "автомойка", "парикмахерская", "стоматология", 
        "фитнес", "строительство", "доставка еды", "юрист"
    ]
    
    results = generator.generate_diverse_set(test_themes, "test_avatars")
    print(f"Результаты: {sum(results)}/{len(results)} успешно") 