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
        
        # ВАРИАТИВНЫЕ тематические символы и цвета (несколько вариантов для каждой тематики)
        self.theme_symbols = {
            'кафе': {
                'symbols': ['☕', '🍰', '🧁', '🥐', '🍪'], 
                'colors': [
                    ['#8B4513', '#F4A460', '#D2B48C'],
                    ['#6B4423', '#E67E22', '#F39C12'],
                    ['#795548', '#BCAAA4', '#D7CCC8']
                ]
            },
            'кофейня': {
                'symbols': ['☕', '🍰', '🧁', '🥐', '🍪'], 
                'colors': [
                    ['#8B4513', '#F4A460', '#D2B48C'],
                    ['#6B4423', '#E67E22', '#F39C12'],
                    ['#795548', '#BCAAA4', '#D7CCC8']
                ]
            },
            'ресторан': {
                'symbols': ['🍽️', '🍴', '🥘', '🍷', '🍾'], 
                'colors': [
                    ['#FF6347', '#FFD700', '#32CD32'],
                    ['#DC143C', '#FF8C00', '#9ACD32'],
                    ['#B22222', '#DAA520', '#228B22']
                ]
            },
            'доставка еды': {
                'symbols': ['🍕', '🍔', '🥗', '🍜', '🚚', '🛵', '📦'], 
                'colors': [
                    ['#FF4500', '#FFD700', '#228B22'],
                    ['#FF6347', '#FFA500', '#32CD32'],
                    ['#DC143C', '#FF8C00', '#9ACD32']
                ]
            },
            'доставки еды': {
                'symbols': ['🍔', '🍕', '🥗', '🍜', '🚚', '🛵', '📦'], 
                'colors': [
                    ['#FF4500', '#FFD700', '#228B22'],
                    ['#FF6347', '#FFA500', '#32CD32'],
                    ['#DC143C', '#FF8C00', '#9ACD32']
                ]
            },
            'еды': {
                'symbols': ['🥗', '🍜', '🍕', '🍔', '🥘'], 
                'colors': [
                    ['#32CD32', '#FFD700', '#FF6347'],
                    ['#228B22', '#FFA500', '#FF4500'],
                    ['#9ACD32', '#FF8C00', '#DC143C']
                ]
            },
            'еда': {
                'symbols': ['🍜', '🥗', '🍕', '🍔', '🥘'], 
                'colors': [
                    ['#32CD32', '#FFD700', '#FF6347'],
                    ['#228B22', '#FFA500', '#FF4500'],
                    ['#9ACD32', '#FF8C00', '#DC143C']
                ]
            },
            'автомойка': {
                'symbols': ['🚗', '🚙', '🚘', '🧽', '💧'], 
                'colors': [
                    ['#1E90FF', '#87CEEB', '#4169E1'],
                    ['#4682B4', '#B0E0E6', '#6495ED'],
                    ['#00BFFF', '#ADD8E6', '#5F9EA0']
                ]
            },
            'автосалон': {
                'symbols': ['🚙', '🚗', '🚘', '🔑', '🏪'], 
                'colors': [
                    ['#2F4F4F', '#696969', '#C0C0C0'],
                    ['#404040', '#808080', '#D3D3D3'],
                    ['#36454F', '#778899', '#B0C4DE']
                ]
            },
            'продажа авто': {
                'symbols': ['🚘', '🚗', '🚙', '🔑', '💰'], 
                'colors': [
                    ['#2F4F4F', '#696969', '#C0C0C0'],
                    ['#404040', '#808080', '#D3D3D3'],
                    ['#36454F', '#778899', '#B0C4DE']
                ]
            },
            'продажи авто': {
                'symbols': ['🚗', '🚘', '🚙', '🔑', '💰'], 
                'colors': [
                    ['#2F4F4F', '#696969', '#C0C0C0'],
                    ['#404040', '#808080', '#D3D3D3'],
                    ['#36454F', '#778899', '#B0C4DE']
                ]
            },
            'парикмахерская': {
                'symbols': ['✂️', '💅', '💇', '🪒', '🎀'], 
                'colors': [
                    ['#FF69B4', '#DA70D6', '#FFB6C1'],
                    ['#FF1493', '#DDA0DD', '#F0E68C'],
                    ['#C71585', '#BA55D3', '#F5DEB3']
                ]
            },
            'салон': {
                'symbols': ['💅', '✂️', '💇', '🪒', '🎀'], 
                'colors': [
                    ['#FF69B4', '#DA70D6', '#FFB6C1'],
                    ['#FF1493', '#DDA0DD', '#F0E68C'],
                    ['#C71585', '#BA55D3', '#F5DEB3']
                ]
            },
            'стоматология': {
                'symbols': ['🦷', '🏥', '💊', '🩺', '⚕️'], 
                'colors': [
                    ['#FFFFFF', '#E0E0E0', '#87CEEB'],
                    ['#F5F5F5', '#D3D3D3', '#4682B4'],
                    ['#FFFAFA', '#C0C0C0', '#6495ED']
                ]
            },
            'фитнес': {
                'symbols': ['💪', '🏋️', '🤸', '🏃', '⚽'], 
                'colors': [
                    ['#FF4500', '#FF6347', '#FFD700'],
                    ['#FF8C00', '#FF7F50', '#FFA500'],
                    ['#DC143C', '#FF69B4', '#FF1493']
                ]
            },
            'спортзал': {
                'symbols': ['🏋️', '💪', '🤸', '🏃', '⚽'], 
                'colors': [
                    ['#FF4500', '#FF6347', '#FFD700'],
                    ['#FF8C00', '#FF7F50', '#FFA500'],
                    ['#DC143C', '#FF69B4', '#FF1493']
                ]
            },
            'строительство': {
                'symbols': ['🔨', '🔧', '🏗️', '⚒️', '🧱'], 
                'colors': [
                    ['#B8860B', '#DAA520', '#8B4513'],
                    ['#CD853F', '#D2B48C', '#A0522D'],
                    ['#DEB887', '#F4A460', '#D2691E']
                ]
            },
            'ремонт': {
                'symbols': ['🔧', '🔨', '🏗️', '⚒️', '🧱'], 
                'colors': [
                    ['#B8860B', '#DAA520', '#8B4513'],
                    ['#CD853F', '#D2B48C', '#A0522D'],
                    ['#DEB887', '#F4A460', '#D2691E']
                ]
            },
            'юрист': {
                'symbols': ['⚖️', '📜', '🏛️', '📋', '🔍'], 
                'colors': [
                    ['#2F4F4F', '#4682B4', '#B0C4DE'],
                    ['#36454F', '#5F9EA0', '#87CEEB'],
                    ['#191970', '#6495ED', '#ADD8E6']
                ]
            },
            'юридические': {
                'symbols': ['⚖️', '📜', '🏛️', '📋', '🔍'], 
                'colors': [
                    ['#2F4F4F', '#4682B4', '#B0C4DE'],
                    ['#36454F', '#5F9EA0', '#87CEEB'],
                    ['#191970', '#6495ED', '#ADD8E6']
                ]
            },
            'медицин': {
                'symbols': ['🏥', '💊', '🩺', '⚕️', '🔬'], 
                'colors': [
                    ['#FF0000', '#FFFFFF', '#87CEEB'],
                    ['#DC143C', '#F5F5F5', '#4682B4'],
                    ['#B22222', '#FFFAFA', '#6495ED']
                ]
            },
            'больница': {
                'symbols': ['🏥', '💊', '🩺', '⚕️', '🔬'], 
                'colors': [
                    ['#FF0000', '#FFFFFF', '#87CEEB'],
                    ['#DC143C', '#F5F5F5', '#4682B4'],
                    ['#B22222', '#FFFAFA', '#6495ED']
                ]
            },
            'недвижим': {
                'symbols': ['🏠', '🏘️', '🏢', '🔑', '📋'], 
                'colors': [
                    ['#8B4513', '#DAA520', '#32CD32'],
                    ['#A0522D', '#D2691E', '#228B22'],
                    ['#654321', '#CD853F', '#9ACD32']
                ]
            },
            'дом': {
                'symbols': ['🏘️', '🏠', '🏢', '🔑', '📋'], 
                'colors': [
                    ['#8B4513', '#DAA520', '#32CD32'],
                    ['#A0522D', '#D2691E', '#228B22'],
                    ['#654321', '#CD853F', '#9ACD32']
                ]
            },
            'образован': {
                'symbols': ['📚', '🎓', '🎒', '📝', '🔬'], 
                'colors': [
                    ['#4169E1', '#FFD700', '#32CD32'],
                    ['#6495ED', '#FFA500', '#228B22'],
                    ['#1E90FF', '#FF8C00', '#9ACD32']
                ]
            },
            'школ': {
                'symbols': ['🎓', '📚', '🎒', '📝', '🔬'], 
                'colors': [
                    ['#4169E1', '#FFD700', '#32CD32'],
                    ['#6495ED', '#FFA500', '#228B22'],
                    ['#1E90FF', '#FF8C00', '#9ACD32']
                ]
            },
            'финанс': {
                'symbols': ['💰', '💳', '🏦', '📊', '💎'], 
                'colors': [
                    ['#DAA520', '#FFD700', '#228B22'],
                    ['#B8860B', '#FFA500', '#32CD32'],
                    ['#CD853F', '#FF8C00', '#9ACD32']
                ]
            },
            'банк': {
                'symbols': ['🏦', '💰', '💳', '📊', '💎'], 
                'colors': [
                    ['#DAA520', '#FFD700', '#228B22'],
                    ['#B8860B', '#FFA500', '#32CD32'],
                    ['#CD853F', '#FF8C00', '#9ACD32']
                ]
            },
            'технолог': {
                'symbols': ['💻', '📱', '⌚', '🖥️', '🔧'], 
                'colors': [
                    ['#4169E1', '#87CEEB', '#B0C4DE'],
                    ['#1E90FF', '#ADD8E6', '#87CEFA'],
                    ['#6495ED', '#B0E0E6', '#F0F8FF']
                ]
            },
            'IT': {
                'symbols': ['🖥️', '💻', '📱', '⌚', '🔧'], 
                'colors': [
                    ['#4169E1', '#87CEEB', '#B0C4DE'],
                    ['#1E90FF', '#ADD8E6', '#87CEFA'],
                    ['#6495ED', '#B0E0E6', '#F0F8FF']
                ]
            },
            'эвакуатор': {
                'symbols': ['🚛', '🔧', '⚙️', '🔗', '🚨'], 
                'colors': [
                    ['#FF4500', '#FFD700', '#FFA500'],
                    ['#DC143C', '#FF6347', '#FF8C00'],
                    ['#B22222', '#DAA520', '#CD853F']
                ]
            },
            'эвакуац': {
                'symbols': ['🚛', '🔧', '⚙️', '🔗', '🚨'], 
                'colors': [
                    ['#FF4500', '#FFD700', '#FFA500'],
                    ['#DC143C', '#FF6347', '#FF8C00'],
                    ['#B22222', '#DAA520', '#CD853F']
                ]
            },
        }
        
        # Fallback символы для неизвестных тематик (НЕ КРУГИ!)
        self.fallback_symbols = ['🔧', '⚡', '🎪', '📦', '🎨', '⚙️', '🏪', '✨', '🚀']
        self.fallback_colors = [
            ['#4169E1', '#87CEEB', '#B0C4DE'],
            ['#32CD32', '#90EE90', '#98FB98'],
            ['#FFD700', '#FFA500', '#FF8C00'],
            ['#FF6347', '#FF4500', '#DC143C'],
            ['#9370DB', '#BA55D3', '#DA70D6']
        ]
        
        if not self.silent_mode:
            print("🎨 SimpleThematicFavicon инициализирован (ВАРИАТИВНЫЙ)")
    
    def create_thematic_favicon(self, theme, output_path):
        """Создает вариативную тематическую фавиконку (метод для совместимости с GUI)"""
        return self.generate_favicon(theme, output_path)
    
    def generate_favicon(self, theme, output_path):
        """Генерирует ВАРИАТИВНУЮ тематическую фавиконку"""
        try:
            # Получаем СЛУЧАЙНЫЙ символ и цвета для тематики
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
                print(f"✅ Вариативная фавиконка создана: {theme} -> {symbol}")
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка создания фавиконки: {e}")
            return False
    
    def _get_theme_symbol_and_colors(self, theme):
        """Получает СЛУЧАЙНЫЙ символ и цвета для тематики"""
        theme_lower = theme.lower().strip()
        
        # Ищем совпадение
        for key, data in self.theme_symbols.items():
            if key in theme_lower:
                # СЛУЧАЙНЫЙ выбор символа и цветов
                symbol = random.choice(data['symbols'])
                colors = random.choice(data['colors'])
                return symbol, colors
        
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
            
            # Кроссплатформенные шрифты для фавиконок
            font_paths = [
                # Windows
                "C:/Windows/Fonts/seguiemj.ttf",  # Windows Emoji
                "C:/Windows/Fonts/arial.ttf",     # Arial
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                
                # macOS
                "/System/Library/Fonts/Apple Color Emoji.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                
                # Linux - эмодзи шрифты
                "/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf",
                "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
                "/usr/share/fonts/emoji/NotoColorEmoji.ttf",
                "/usr/share/fonts/TTF/NotoColorEmoji.ttf",
                
                # Linux - обычные шрифты
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
                "/usr/share/fonts/TTF/arial.ttf",
                "/usr/share/fonts/truetype/arial.ttf",
                
                # Linux пользовательские папки
                str(Path.home() / ".fonts/NotoColorEmoji.ttf"),
                str(Path.home() / ".local/share/fonts/NotoColorEmoji.ttf"),
                str(Path.home() / ".fonts/arial.ttf"),
                str(Path.home() / ".local/share/fonts/arial.ttf"),
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
        """Рисует красивую геометрическую фигуру как fallback (НЕ КРУГ!)"""
        center = size // 2
        
        # Рисуем красивый ромб с градиентом
        diamond_size = size // 3
        
        color1 = self._hex_to_rgb(colors[0])
        color2 = self._hex_to_rgb(colors[1]) if len(colors) > 1 else color1
        
        # Создаем точки ромба
        points = [
            (center, center - diamond_size),  # верх
            (center + diamond_size, center),  # право
            (center, center + diamond_size),  # низ
            (center - diamond_size, center)   # лево
        ]
        
        # Рисуем заполненный ромб
        draw.polygon(points, fill=color1, outline='white', width=4)
        
        # Добавляем внутренний ромб меньшего размера
        inner_size = diamond_size // 2
        inner_points = [
            (center, center - inner_size),
            (center + inner_size, center),
            (center, center + inner_size),
            (center - inner_size, center)
        ]
        draw.polygon(inner_points, fill=color2, outline='white', width=2)
    
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