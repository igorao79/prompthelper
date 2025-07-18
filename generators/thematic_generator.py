"""
Тематический генератор изображений
Разбит из img_gen.py для лучшей организации
"""

import random
import time
from .image_generator import ImageGenerator

class ThematicImageGenerator:
    """Генератор тематических изображений с продвинутой рандомизацией"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.base_generator = ImageGenerator(silent_mode=silent_mode)
    
    def generate_single_image(self, prompt, image_name, output_dir):
        """Генерирует одно изображение с рандомизацией"""
        enhanced_prompt = self.add_randomization(prompt)
        return self.base_generator._generate_image_via_pollinations(
            enhanced_prompt, image_name, output_dir
        )
    
    def get_theme_prompts(self, theme_input):
        """Получает промпты для тематики"""
        # Импортируем здесь чтобы избежать циклических импортов
        try:
            from generators.prompt_generator import create_thematic_prompts
            return create_thematic_prompts(theme_input)
        except ImportError:
            return self._fallback_prompts(theme_input)
    
    def add_randomization(self, prompt):
        """Добавляет случайные элементы к промпту для уникальности"""
        
        # Стили и модификаторы
        styles = [
            "photorealistic", "professional photography", "high quality commercial photo",
            "modern digital art", "clean minimalist style", "corporate photography",
            "studio lighting", "natural lighting", "dramatic lighting", "soft lighting"
        ]
        
        perspectives = [
            "front view", "side angle", "three-quarter view", "close-up detail",
            "wide establishing shot", "medium shot", "overhead view", "low angle",
            "centered composition", "rule of thirds", "dynamic angle"
        ]
        
        color_moods = [
            "vibrant professional colors", "natural warm tones", "cool professional palette",
            "bright and inviting", "modern color scheme", "clean white background",
            "gradient background", "neutral tones", "rich saturated colors"
        ]
        
        technical_quality = [
            "8K resolution", "ultra sharp focus", "professional quality",
            "commercial grade", "high detail", "crisp and clear",
            "well lit", "perfectly exposed", "noise-free"
        ]
        
        environments = [
            "modern office environment", "clean professional setting",
            "contemporary workspace", "bright indoor lighting",
            "minimalist background", "professional studio setup"
        ]
        
        # Случайно выбираем элементы
        style = random.choice(styles)
        perspective = random.choice(perspectives) 
        color = random.choice(color_moods)
        quality = random.choice(technical_quality)
        environment = random.choice(environments)
        
        # Добавляем временную метку для уникальности
        timestamp = int(time.time() * 1000)
        seed = random.randint(1000, 9999)
        
        # Собираем финальный промпт
        enhanced = f"{prompt}, {style}, {perspective}, {color}, {quality}, {environment}"
        
        # Добавляем случайные детали
        details = [
            "professional equipment visible", "clean organized space",
            "modern technology", "quality materials", "expert presentation",
            "business environment", "customer-focused", "service excellence"
        ]
        
        selected_details = random.sample(details, k=random.randint(1, 3))
        enhanced += f", {', '.join(selected_details)}"
        
        return enhanced
    
    def add_review_randomization(self, prompt):
        """Специальная рандомизация для отзывов - ТОЛЬКО ОБЫЧНЫЕ ЛЮДИ"""
        
        # КРИТИЧНО: Review = отзыв обычного клиента, НЕ РАБОЧИЕ!
        person_types = [
            "happy customer", "satisfied client", "pleased woman", "smiling man",
            "grateful person", "content customer", "cheerful client", "positive person",
            "thankful customer", "delighted client", "appreciative woman", "joyful man"
        ]
        
        ages = [
            "young adult", "middle-aged person", "mature adult", "30-40 years old",
            "25-35 years old", "40-50 years old", "adult person"
        ]
        
        expressions = [
            "genuine smile", "happy expression", "satisfied look", "positive facial expression",
            "authentic joy", "natural smile", "pleased appearance", "grateful expression"
        ]
        
        # Случайный выбор
        person = random.choice(person_types)
        age = random.choice(ages)
        expression = random.choice(expressions)
        
        # Уникальность
        timestamp = int(time.time() * 1000)
        seed = random.randint(1000, 9999)
        
        # РАДИКАЛЬНЫЙ промпт - ТОЛЬКО ЛЮДИ, НИ ОБЪЕКТОВ, НИ ОБОРУДОВАНИЯ БЕЗ ЦИФР!
        enhanced = (
            f"portrait photo of {person}, {age}, {expression}, "
            f"HUMAN FACE ONLY, PERSON ONLY, NO OBJECTS VISIBLE, NO EQUIPMENT, "
            f"NO CARS, NO TOOLS, NO WORK ITEMS, NO UNIFORMS, "
            f"civilian clothes, casual clothing, regular person, "
            f"customer testimonial portrait, clean background, "
            f"professional headshot style, natural lighting, "
            f"IGNORE ORIGINAL PROMPT THEME, PERSON ONLY"
        )
        
        return enhanced
    
    def add_favicon_randomization(self, prompt):
        """Рандомизация для фавиконов - НЕ КРУГИ, НЕ КРУЖКИ!"""
        
        # ТЕМАТИЧЕСКИЕ иконочные символы - НЕ КРУГИ!
        pure_icons = [
            "business emblem", "company symbol", "professional logo", "service icon",
            "abstract arrow", "stylized gear", "industrial symbol", "tech emblem",
            "diamond shape", "hexagon symbol", "shield shape", "star emblem",
            "triangular badge", "square icon", "rectangular logo", "angular design"
        ]
        
        # Стили ТОЛЬКО для иконок
        icon_styles = [
            "flat design", "vector art", "minimalist", "geometric", 
            "simple lines", "solid shapes", "clean outline", "bold design"
        ]
        
        # Простые цвета
        colors = [
            "blue", "green", "orange", "red", "purple", "navy", "teal", "gold"
        ]
        
        # Случайный выбор
        icon = random.choice(pure_icons)
        style = random.choice(icon_styles)
        color = random.choice(colors)
        
        # Уникальность
        timestamp = int(time.time() * 1000)
        seed = random.randint(10000, 99999)
        
        # ТЕМАТИЧЕСКИЙ ИКОНОЧНЫЙ промпт - БЕЗ КРУГОВ!
        enhanced = (
            f"{prompt} {icon}, {style}, {color} color, "
            f"BUSINESS ICON ONLY, NO PHOTOS, NO REALISTIC IMAGES, NO PEOPLE, "
            f"NO CIRCLES, NO ROUND SHAPES, NO CIRCULAR DESIGNS, "
            f"thematic business symbol, flat vector design, company emblem, "
            f"professional pictogram, brand mark, angular shape, clean silhouette, "
            f"BUSINESS THEMED ICON, SERVICE SYMBOL, INDUSTRY RELATED, "
            f"transparent background, centered, scalable vector"
        )
        
        return enhanced
    
    def _fallback_prompts(self, theme_input):
        """Базовые промпты если импорт не удался"""
        return [
            f"professional {theme_input} service",
            f"quality {theme_input} business",
            f"modern {theme_input} company",
            f"expert {theme_input} team",
            f"reliable {theme_input} service",
            f"professional {theme_input} office",
            f"experienced {theme_input} specialists",
            f"trusted {theme_input} provider"
        ] 