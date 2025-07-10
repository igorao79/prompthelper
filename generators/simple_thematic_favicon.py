#!/usr/bin/env python3
"""
Простой генератор тематических фавиконок
Создает настоящие иконки для тематик, а не человечков
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

class SimpleThematicFavicon:
    """Генератор простых тематических фавиконок"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        # Тематические символы и цвета
        self.theme_symbols = {
            'кафе': {'symbol': '☕', 'colors': ['#8B4513', '#F4A460', '#D2B48C']},
            'кофейня': {'symbol': '☕', 'colors': ['#8B4513', '#F4A460', '#D2B48C']},
            'ресторан': {'symbol': '🍽️', 'colors': ['#FF6347', '#FFD700', '#32CD32']},
            'доставка еды': {'symbol': '🍕', 'colors': ['#FF4500', '#FFD700', '#228B22']},
            'доставки еды': {'symbol': '🍔', 'colors': ['#FF4500', '#FFD700', '#228B22']},
            'еды': {'symbol': '🥗', 'colors': ['#32CD32', '#FFD700', '#FF6347']},
            'еда': {'symbol': '🍜', 'colors': ['#32CD32', '#FFD700', '#FF6347']},
            'автомойка': {'symbol': '🚗', 'colors': ['#1E90FF', '#87CEEB', '#4169E1']},
            'автосалон': {'symbol': '🚙', 'colors': ['#2F4F4F', '#696969', '#C0C0C0']},
            'продажа авто': {'symbol': '🚘', 'colors': ['#2F4F4F', '#696969', '#C0C0C0']},
            'продажи авто': {'symbol': '🚗', 'colors': ['#2F4F4F', '#696969', '#C0C0C0']},
            'парикмахерская': {'symbol': '✂️', 'colors': ['#FF69B4', '#DA70D6', '#FFB6C1']},
            'салон': {'symbol': '💅', 'colors': ['#FF69B4', '#DA70D6', '#FFB6C1']},
            'стоматология': {'symbol': '🦷', 'colors': ['#FFFFFF', '#E0E0E0', '#87CEEB']},
            'фитнес': {'symbol': '💪', 'colors': ['#FF4500', '#FF6347', '#FFD700']},
            'спортзал': {'symbol': '🏋️', 'colors': ['#FF4500', '#FF6347', '#FFD700']},
            'строительство': {'symbol': '🔨', 'colors': ['#B8860B', '#DAA520', '#8B4513']},
            'ремонт': {'symbol': '🔧', 'colors': ['#B8860B', '#DAA520', '#8B4513']},
            'юрист': {'symbol': '⚖️', 'colors': ['#2F4F4F', '#4682B4', '#B0C4DE']},
            'юридические': {'symbol': '⚖️', 'colors': ['#2F4F4F', '#4682B4', '#B0C4DE']},
            'медицин': {'symbol': '🏥', 'colors': ['#FF0000', '#FFFFFF', '#87CEEB']},
            'больница': {'symbol': '🏥', 'colors': ['#FF0000', '#FFFFFF', '#87CEEB']},
            'недвижим': {'symbol': '🏠', 'colors': ['#8B4513', '#DAA520', '#32CD32']},
            'дом': {'symbol': '🏘️', 'colors': ['#8B4513', '#DAA520', '#32CD32']},
            'образован': {'symbol': '📚', 'colors': ['#4169E1', '#FFD700', '#32CD32']},
            'школ': {'symbol': '🎓', 'colors': ['#4169E1', '#FFD700', '#32CD32']},
            'финанс': {'symbol': '💰', 'colors': ['#DAA520', '#FFD700', '#228B22']},
            'банк': {'symbol': '🏦', 'colors': ['#DAA520', '#FFD700', '#228B22']},
            'технолог': {'symbol': '💻', 'colors': ['#4169E1', '#87CEEB', '#B0C4DE']},
            'IT': {'symbol': '🖥️', 'colors': ['#4169E1', '#87CEEB', '#B0C4DE']},
        }
        
        # Fallback символы для неизвестных тематик
        self.fallback_symbols = ['🔷', '🔶', '⭐', '🎯', '🔵', '🟢', '🟡', '🟠', '🟣']
        self.fallback_colors = [
            ['#4169E1', '#87CEEB', '#B0C4DE'],
            ['#32CD32', '#90EE90', '#98FB98'],
            ['#FFD700', '#FFA500', '#FF8C00'],
            ['#FF6347', '#FF4500', '#DC143C'],
            ['#9370DB', '#BA55D3', '#DA70D6']
        ]
        
        if not self.silent_mode:
            print("🎨 SimpleThematicFavicon инициализирован")
    
    def generate_favicon(self, theme, output_path):
        """Генерирует тематическую фавиконку"""
        try:
            # Получаем символ и цвета для тематики
            symbol, colors = self._get_theme_symbol_and_colors(theme)
            
            # Создаем изображение 256x256
            size = 256
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Рисуем фон с градиентом
            self._draw_gradient_background(draw, size, colors)
            
            # Добавляем символ
            self._draw_symbol(draw, size, symbol, colors)
            
            # Конвертируем в RGB для JPG
            if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                rgb_image = Image.new('RGB', (size, size), 'white')
                rgb_image.paste(image, mask=image)
                image = rgb_image
            
            # Сохраняем
            image.save(output_path, format='PNG' if output_path.lower().endswith('.png') else 'JPEG')
            
            if not self.silent_mode:
                print(f"✅ Фавиконка создана: {theme} -> {symbol}")
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания фавиконки: {e}")
            return False
    
    def _get_theme_symbol_and_colors(self, theme):
        """Получает символ и цвета для тематики"""
        theme_lower = theme.lower().strip()
        
        # Ищем точное совпадение
        for key, data in self.theme_symbols.items():
            if key in theme_lower:
                return data['symbol'], data['colors']
        
        # Fallback: случайный символ и цвета
        symbol = random.choice(self.fallback_symbols)
        colors = random.choice(self.fallback_colors)
        
        return symbol, colors
    
    def _draw_gradient_background(self, draw, size, colors):
        """Рисует градиентный фон"""
        # Выбираем два цвета для градиента
        color1 = self._hex_to_rgb(colors[0])
        color2 = self._hex_to_rgb(colors[1])
        
        # Рисуем радиальный градиент
        center = size // 2
        max_radius = size // 2
        
        for y in range(size):
            for x in range(size):
                # Вычисляем расстояние от центра
                distance = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
                ratio = min(distance / max_radius, 1.0)
                
                # Интерполируем цвет
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                
                draw.point((x, y), (r, g, b))
    
    def _draw_symbol(self, draw, size, symbol, colors):
        """Рисует символ на фавиконке"""
        try:
            # Пытаемся использовать системный шрифт с поддержкой эмодзи
            font_size = size // 3
            
            # Список шрифтов для попытки
            font_paths = [
                "C:/Windows/Fonts/seguiemj.ttf",  # Windows Emoji
                "C:/Windows/Fonts/arial.ttf",     # Arial
                "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
                "/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf",  # Linux
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            # Получаем размеры текста
            bbox = draw.textbbox((0, 0), symbol, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Центрируем текст
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Рисуем тень
            shadow_color = self._hex_to_rgb(colors[2]) if len(colors) > 2 else (100, 100, 100)
            draw.text((x + 2, y + 2), symbol, font=font, fill=shadow_color)
            
            # Рисуем основной символ
            draw.text((x, y), symbol, font=font, fill='white')
            
        except Exception as e:
            # Fallback: рисуем простую геометрическую фигуру
            self._draw_fallback_shape(draw, size, colors)
    
    def _draw_fallback_shape(self, draw, size, colors):
        """Рисует простую фигуру как fallback"""
        center = size // 2
        radius = size // 4
        
        # Рисуем круг
        color = self._hex_to_rgb(colors[0])
        draw.ellipse([
            center - radius, center - radius,
            center + radius, center + radius
        ], fill=color, outline='white', width=3)
    
    def _hex_to_rgb(self, hex_color):
        """Конвертирует HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Функция для использования в основном коде
def generate_simple_thematic_favicon(theme, output_path, silent_mode=False):
    """Генерирует простую тематическую фавиконку"""
    generator = SimpleThematicFavicon(silent_mode=silent_mode)
    return generator.generate_favicon(theme, output_path)

if __name__ == "__main__":
    # Тестирование
    generator = SimpleThematicFavicon()
    
    test_themes = [
        "кафе", "доставка еды", "автомойка", "продажа авто",
        "парикмахерская", "стоматология", "строительство", "юрист"
    ]
    
    os.makedirs("test_simple_favicons", exist_ok=True)
    
    for i, theme in enumerate(test_themes):
        output_path = f"test_simple_favicons/favicon_{theme.replace(' ', '_')}.png"
        success = generator.generate_favicon(theme, output_path)
        print(f"{i+1}. {theme}: {'✅' if success else '❌'}") 