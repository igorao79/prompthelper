"""
Генератор фавиконок через favicon.io
Самый популярный и полностью бесплатный сервис генерации фавиконок
"""

import requests
import os
import time
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont
import zipfile
import tempfile

class FaviconIOGenerator:
    """Генератор фавиконок через favicon.io API"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.base_url = "https://favicon.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def generate_text_favicon(self, text, theme="", output_path="", size=512):
        """
        Генерирует фавиконку из текста используя favicon.io
        
        Args:
            text (str): Текст для фавиконки (1-2 буквы)
            theme (str): Тематика для цветовой схемы
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки
            
        Returns:
            bool: Успешность генерации
        """
        try:
            if not self.silent_mode:
                print(f"🎨 Генерирую фавиконку из текста: {text}")
            
            # Получаем первые буквы для фавиконки
            favicon_text = self._extract_favicon_text(text, theme)
            
            # Цветовые схемы по тематикам
            color_scheme = self._get_color_scheme(theme)
            
            # Создаем простую но красивую фавиконку локально
            # (favicon.io не имеет прямого API, поэтому делаем локально в их стиле)
            favicon_created = self._create_favicon_locally(
                favicon_text, color_scheme, output_path, size
            )
            
            if favicon_created and not self.silent_mode:
                print(f"✅ Фавиконка создана: {output_path}")
            
            return favicon_created
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации фавиконки: {e}")
            return False
    
    def _extract_favicon_text(self, text, theme):
        """Извлекает подходящий текст для фавиконки"""
        if not text or not theme:
            return "★"
        
        # Ищем первые буквы тематики
        words = theme.split()
        if len(words) >= 2:
            # Берем первые буквы двух слов
            return f"{words[0][0]}{words[1][0]}".upper()
        elif len(words) == 1 and len(words[0]) >= 2:
            # Берем первые две буквы одного слова
            return words[0][:2].upper()
        elif len(words) == 1:
            # Берем первую букву
            return words[0][0].upper()
        else:
            # Используем звездочку как fallback
            return "★"
    
    def _get_color_scheme(self, theme):
        """Возвращает цветовую схему для тематики"""
        # Цветовые схемы для разных типов бизнеса
        theme_colors = {
            # Технические/IT
            'tech': {'bg': '#2563eb', 'text': '#ffffff'},  # Синий
            'it': {'bg': '#7c3aed', 'text': '#ffffff'},     # Фиолетовый
            'digital': {'bg': '#0891b2', 'text': '#ffffff'}, # Cyan
            
            # Медицина/Здоровье
            'медицин': {'bg': '#dc2626', 'text': '#ffffff'}, # Красный
            'здоровь': {'bg': '#059669', 'text': '#ffffff'}, # Зеленый
            'клиник': {'bg': '#dc2626', 'text': '#ffffff'},  # Красный
            
            # Автомобильная тематика
            'авто': {'bg': '#3b82f6', 'text': '#ffffff'},    # Синий вместо черного
            'машин': {'bg': '#6366f1', 'text': '#ffffff'},   # Индиго вместо серого
            'сервис': {'bg': '#0891b2', 'text': '#ffffff'},  # Cyan
            'мойк': {'bg': '#06b6d4', 'text': '#ffffff'},    # Голубой для автомойки
            
            # Образование
            'образован': {'bg': '#7c3aed', 'text': '#ffffff'}, # Фиолетовый
            'курс': {'bg': '#2563eb', 'text': '#ffffff'},       # Синий
            'школ': {'bg': '#059669', 'text': '#ffffff'},       # Зеленый
            
            # Недвижимость
            'недвижим': {'bg': '#059669', 'text': '#ffffff'},   # Зеленый
            'дом': {'bg': '#dc2626', 'text': '#ffffff'},        # Красный
            'квартир': {'bg': '#2563eb', 'text': '#ffffff'},    # Синий
            
            # Красота
            'салон': {'bg': '#ec4899', 'text': '#ffffff'},      # Розовый
            'красот': {'bg': '#a855f7', 'text': '#ffffff'},     # Фиолетовый
            'стриж': {'bg': '#f59e0b', 'text': '#ffffff'},      # Оранжевый
            
            # Еда
            'ресторан': {'bg': '#dc2626', 'text': '#ffffff'},   # Красный
            'кафе': {'bg': '#f59e0b', 'text': '#ffffff'},       # Оранжевый
            'доставк': {'bg': '#059669', 'text': '#ffffff'},    # Зеленый
            
            # Строительство
            'строител': {'bg': '#f59e0b', 'text': '#ffffff'},   # Оранжевый
            'ремонт': {'bg': '#374151', 'text': '#ffffff'},     # Серый
            'дизайн': {'bg': '#a855f7', 'text': '#ffffff'},     # Фиолетовый
        }
        
        # Ищем подходящую тематику
        theme_lower = theme.lower()
        for key, colors in theme_colors.items():
            if key in theme_lower:
                return colors
        
        # Красивые цвета по умолчанию
        default_schemes = [
            {'bg': '#2563eb', 'text': '#ffffff'},  # Синий
            {'bg': '#059669', 'text': '#ffffff'},  # Зеленый
            {'bg': '#dc2626', 'text': '#ffffff'},  # Красный
            {'bg': '#7c3aed', 'text': '#ffffff'},  # Фиолетовый
            {'bg': '#f59e0b', 'text': '#ffffff'},  # Оранжевый
            {'bg': '#0891b2', 'text': '#ffffff'},  # Cyan
        ]
        
        return random.choice(default_schemes)
    
    def _create_favicon_locally(self, text, color_scheme, output_path, size):
        """Создает фавиконку локально в стиле favicon.io"""
        try:
            # Создаем изображение
            img = Image.new('RGB', (size, size), color=color_scheme['bg'])
            draw = ImageDraw.Draw(img)
            
            # Пытаемся загрузить красивый шрифт
            try:
                # Пытаемся найти системные шрифты
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf", 
                    "C:/Windows/Fonts/segoeui.ttf",
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/arial.ttf"  # Linux
                ]
                
                font = None
                font_size = int(size * 0.6)  # 60% от размера изображения
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                
                if not font:
                    # Используем стандартный шрифт PIL
                    font = ImageFont.load_default()
                    
            except Exception:
                font = ImageFont.load_default()
            
            # Вычисляем позицию для центрирования текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Рисуем текст
            draw.text((x, y), text, fill=color_scheme['text'], font=font)
            
            # Сохраняем
            if output_path.endswith('.png'):
                img.save(output_path, 'PNG')
            else:
                # Конвертируем в JPG
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img)
                rgb_img.save(output_path, 'JPEG', quality=95)
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания фавиконки: {e}")
            return False
    
    def generate_emoji_favicon(self, theme, output_path="", size=512):
        """
        Генерирует фавиконку из эмодзи в зависимости от тематики
        
        Args:
            theme (str): Тематика для выбора подходящего эмодзи
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки
            
        Returns:
            bool: Успешность генерации
        """
        try:
            if not self.silent_mode:
                print(f"🎨 Генерирую фавиконку-эмодзи для тематики: {theme}")
            
            # Эмодзи для разных тематик - МАКСИМУМ ИКОНОК!
            theme_emojis = {
                # Авто
                'автомойка': '🚗', 'авто': '🚗', 'машин': '🚗', 'сто': '🔧',
                'шиномонт': '🛞', 'автосервис': '🚗', 'автозапчаст': '🔧',
                
                # Еда и напитки
                'ресторан': '🍽️', 'кафе': '☕', 'еда': '🍕', 'доставк': '🛵',
                'пицц': '🍕', 'суши': '🍣', 'бургер': '🍔', 'бар': '🍺',
                'пекарн': '🍞', 'кондитер': '🍰', 'мороженое': '🍦',
                
                # Медицина
                'медицин': '⚕️', 'здоровь': '💊', 'клиник': '🏥', 'врач': '👨‍⚕️',
                'стоматолог': '🦷', 'аптек': '💊', 'ветеринар': '🐕‍🦺',
                'массаж': '💆', 'лечебн': '🏥', 'оптик': '👓',
                
                # Образование
                'образован': '📚', 'школ': '🎓', 'курс': '📖', 'универ': '🎓',
                'детсад': '👶', 'учебн': '📝', 'репетит': '📚',
                
                # Недвижимость
                'недвижим': '🏠', 'дом': '🏡', 'квартир': '🏢', 'риелтор': '🏠',
                'строй': '🏗️', 'ипотек': '🏦', 'аренд': '🏠',
                
                # Красота
                'красот': '💄', 'салон': '✂️', 'стриж': '💇', 'парикмахер': '💇‍♀️',
                'маникюр': '💅', 'косметолог': '💄', 'массаж': '💆',
                'брови': '👁️', 'татуаж': '💄', 'эпиляци': '✨',
                
                # Строительство
                'строител': '🔨', 'ремонт': '🔧', 'дизайн': '🎨', 'плитк': '🔨',
                'сантехник': '🔧', 'электрик': '⚡', 'отделк': '🎨',
                'кровл': '🏠', 'фундамент': '🏗️', 'окна': '🪟',
                
                # Спорт и фитнес
                'спорт': '⚽', 'фитнес': '💪', 'йог': '🧘', 'тренажер': '🏋️',
                'бассейн': '🏊', 'теннис': '🎾', 'футбол': '⚽', 'танц': '💃',
                'единоборств': '🥊', 'гимнастик': '🤸',
                
                # Технологии
                'технолог': '💻', 'it': '⌨️', 'програм': '💾', 'компьютер': '💻',
                'интернет': '🌐', 'сайт': '💻', 'мобильн': '📱',
                'разработк': '👨‍💻', 'дизайн': '🎨', 'реклам': '📢',
                
                # Юриспруденция
                'юрист': '⚖️', 'адвокат': '📋', 'нотариус': '📜', 'право': '⚖️',
                'консультаци': '📋', 'документ': '📄', 'суд': '🏛️',
                
                # Финансы
                'финанс': '💰', 'банк': '🏦', 'страхован': '🛡️', 'кредит': '💳',
                'бухгалтер': '📊', 'налог': '💰', 'инвестиц': '📈',
                
                # Туризм
                'туризм': '✈️', 'отель': '🏨', 'путешеств': '🗺️', 'экскурси': '📍',
                'виза': '📋', 'билет': '🎫', 'гид': '🗺️',
                
                # Домашние услуги
                'уборк': '🧹', 'клининг': '🧽', 'химчистк': '👔', 'прачечн': '👕',
                'домработниц': '🏠', 'глажк': '👔', 'мойк': '🧽',
                
                # Транспорт
                'такси': '🚕', 'перевозк': '🚛', 'грузовик': '🚛', 'автобус': '🚌',
                'мотоцикл': '🏍️', 'велосипед': '🚴', 'самокат': '🛴',
                
                # Природа и растения
                'цвет': '🌸', 'сад': '🌳', 'растен': '🌿', 'ландшафт': '🌲',
                'семен': '🌱', 'удобрени': '🌿', 'газон': '🌱',
                
                # Животные
                'ветеринар': '🐕‍🦺', 'зоомагазин': '🐕', 'дрессировк': '🐕',
                'груминг': '🐩', 'птиц': '🐦', 'рыб': '🐟',
                
                # Мебель и интерьер
                'мебель': '🪑', 'диван': '🛋️', 'кровать': '🛏️', 'кухн': '🍽️',
                'шкаф': '🚪', 'стол': '🪑', 'интерьер': '🏠',
                
                # Развлечения
                'кино': '🎬', 'театр': '🎭', 'музы': '🎵', 'концерт': '🎤',
                'фотограф': '📸', 'видео': '📹', 'игр': '🎮',
                
                # Безопасность
                'охран': '🛡️', 'безопасност': '🔒', 'сигнализаци': '🚨',
                'камер': '📹', 'замк': '🔐', 'ключ': '🔑'
            }
            
            # Ищем подходящий эмодзи
            emoji = '⭐'  # По умолчанию
            theme_lower = theme.lower()
            
            for key, value in theme_emojis.items():
                if key in theme_lower:
                    emoji = value
                    break
            
            # Создаем фавиконку с эмодзи
            return self._create_emoji_favicon(emoji, output_path, size)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации эмодзи-фавиконки: {e}")
            return False
    
    def _create_emoji_favicon(self, emoji, output_path, size):
        """Создает фавиконку с эмодзи"""
        try:
            # Создаем изображение с прозрачным фоном
            img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Пытаемся загрузить шрифт с поддержкой эмодзи
            font_size = int(size * 0.8)  # 80% от размера
            
            try:
                # Для Windows - используем Segoe UI Emoji
                emoji_fonts = [
                    "C:/Windows/Fonts/seguiemj.ttf",  # Windows 10+
                    "C:/Windows/Fonts/segoe-ui-emoji.ttf",
                    "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
                ]
                
                font = None
                for font_path in emoji_fonts:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            break
                        except:
                            continue
                
                if not font:
                    font = ImageFont.load_default()
                    
            except Exception:
                font = ImageFont.load_default()
            
            # Вычисляем позицию для центрирования
            bbox = draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Рисуем эмодзи
            draw.text((x, y), emoji, fill='black', font=font)
            
            # Сохраняем
            if output_path.endswith('.png'):
                img.save(output_path, 'PNG')
            else:
                # Конвертируем в JPG с белым фоном
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, img)
                rgb_img.save(output_path, 'JPEG', quality=95)
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания эмодзи-фавиконки: {e}")
            return False
    
    def generate_favicon_from_theme(self, theme, output_path="", size=512):
        """
        Основной метод генерации фавиконки по тематике
        
        Args:
            theme (str): Тематика бизнеса
            output_path (str): Путь для сохранения
            size (int): Размер фавиконки
            
        Returns:
            bool: Успешность генерации
        """
        try:
            if not self.silent_mode:
                print(f"🚀 Генерирую фавиконку для тематики: {theme}")
            
            # НОВЫЙ ПОДХОД: Используем DiceBear API
            try:
                from .dicebear_favicon import DiceBearFavicon
                dicebear_gen = DiceBearFavicon(silent_mode=self.silent_mode)
                result = dicebear_gen.generate_favicon(theme, output_path, size)
                
                if result:
                    if not self.silent_mode:
                        print(f"✅ Фавиконка создана методом: dicebear")
                    return True
            except Exception as e:
                if not self.silent_mode:
                    print(f"⚠️ DiceBear метод не сработал: {e}")
            
            # Fallback на старые методы
            methods = [
                ('emoji', self.generate_emoji_favicon),
                ('text', self.generate_text_favicon)
            ]
            
            for method_name, method_func in methods:
                try:
                    if method_name == 'text':
                        result = method_func(theme, theme, output_path, size)
                    else:
                        result = method_func(theme, output_path, size)
                    
                    if result:
                        if not self.silent_mode:
                            print(f"✅ Фавиконка создана методом: {method_name}")
                        return True
                        
                except Exception as e:
                    if not self.silent_mode:
                        print(f"⚠️ Метод {method_name} не сработал: {e}")
                    continue
            
            # Если ничего не сработало
            if not self.silent_mode:
                print("❌ Не удалось создать фавиконку ни одним методом")
            return False
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Критическая ошибка генерации фавиконки: {e}")
            return False 