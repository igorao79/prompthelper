#!/usr/bin/env python3
"""
Умный генератор вариативных промптов
Создает разные варианты каждый раз, но исключает проблемные слова
"""

import random

class SmartVariativePrompts:
    """Генератор вариативных промптов с умными исключениями"""
    
    def __init__(self):
        # Базовые элементы для конструирования промптов
        self.business_elements = {
            'доставка еды': {
                'objects': ['delicious pizza', 'fresh sushi', 'gourmet burger', 'hot pasta', 'asian noodles', 'healthy salad', 'italian cuisine', 'mexican food', 'chinese takeout', 'french pastry'],
                'actions': ['preparing', 'cooking', 'serving', 'delivering', 'presenting', 'plating', 'garnishing'],
                'qualities': ['fresh', 'hot', 'delicious', 'gourmet', 'artisan', 'homemade', 'organic', 'premium'],
                'environments': ['kitchen', 'restaurant', 'food counter', 'dining area', 'food preparation area'],
                'banned_words': ['box', 'package', 'container', 'коробк', 'упаковк']  # СТРОГО ЗАПРЕЩЕНО
            },
            'продажа авто': {
                'objects': ['luxury car', 'new vehicle', 'sports car', 'sedan', 'suv', 'car interior', 'dashboard', 'steering wheel', 'car seats'],
                'actions': ['displaying', 'showcasing', 'presenting', 'consulting', 'demonstrating'],
                'qualities': ['premium', 'luxury', 'modern', 'elegant', 'sleek', 'sophisticated'],
                'environments': ['showroom', 'dealership', 'car lot', 'sales office', 'exhibition hall'],
                'banned_words': ['mechanic', 'repair', 'tool', 'механик', 'ремонт'],  # СТРОГО ЗАПРЕЩЕНО для about2
                'about2_safe': ['car interior', 'leather seats', 'dashboard design', 'comfort features', 'modern controls']
            },
            'кафе': {
                'objects': ['coffee cup', 'espresso', 'cappuccino', 'latte art', 'coffee beans', 'pastry', 'croissant'],
                'actions': ['brewing', 'serving', 'enjoying', 'relaxing', 'socializing'],
                'qualities': ['aromatic', 'fresh', 'premium', 'artisan', 'cozy', 'warm'],
                'environments': ['coffee shop', 'cafe interior', 'coffee bar', 'seating area', 'barista station']
            },
            'автомойка': {
                'objects': ['clean car', 'washing equipment', 'soap foam', 'shiny vehicle', 'water spray'],
                'actions': ['washing', 'cleaning', 'polishing', 'detailing', 'drying'],
                'qualities': ['spotless', 'gleaming', 'professional', 'thorough', 'careful'],
                'environments': ['car wash bay', 'service area', 'cleaning station', 'wash tunnel']
            }
        }
        
        # Общие элементы для неизвестных тематик
        self.general_elements = {
            'objects': ['service', 'workspace', 'equipment', 'facility', 'interior'],
            'actions': ['working', 'providing', 'delivering', 'maintaining', 'operating'],
            'qualities': ['professional', 'modern', 'quality', 'efficient', 'reliable'],
            'environments': ['office', 'workplace', 'service area', 'facility', 'center']
        }
        
        # Стили и композиции для разнообразия
        self.styles = ['professional photography', 'commercial style', 'high quality', 'studio lighting', 'natural lighting']
        self.compositions = ['centered composition', 'close-up view', 'wide angle', 'detailed shot', 'atmospheric']
        self.moods = ['bright', 'warm', 'inviting', 'modern', 'elegant', 'clean', 'vibrant']
    
    def generate_prompts(self, theme_input):
        """Генерирует вариативные промпты для тематики"""
        theme_lower = theme_input.lower().strip()
        
        # Находим подходящие элементы
        elements = self._get_theme_elements(theme_lower)
        
        # Генерируем промпты для каждого типа изображения
        prompts = {}
        
        # Main - главное изображение бизнеса
        prompts['main'] = self._generate_main_prompt(elements, theme_input)
        
        # About1 - первое изображение о услуге  
        prompts['about1'] = self._generate_about1_prompt(elements, theme_input)
        
        # About2 - КРИТИЧЕСКОЕ - здесь НЕ ДОЛЖНО быть механиков для авто
        prompts['about2'] = self._generate_about2_prompt(elements, theme_input, theme_lower)
        
        # About3 - третье изображение
        prompts['about3'] = self._generate_about3_prompt(elements, theme_input)
        
        # Review изображения - люди
        prompts['review1'] = self._generate_review_prompt()
        prompts['review2'] = self._generate_review_prompt() 
        prompts['review3'] = self._generate_review_prompt()
        
        # Favicon - простой символ
        prompts['favicon'] = 'business icon symbol'
        
        return prompts
    
    def _get_theme_elements(self, theme_lower):
        """Получает элементы для тематики"""
        # Ищем точное или частичное совпадение
        for key, elements in self.business_elements.items():
            if key in theme_lower or any(word in theme_lower for word in key.split()):
                return elements
                
        # Дополнительные проверки для вариаций
        if any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            return self.business_elements['доставка еды']
        elif any(word in theme_lower for word in ['авто', 'машин', 'car', 'vehicle', 'продаж']):
            return self.business_elements['продажа авто']
        elif any(word in theme_lower for word in ['кофе', 'coffee', 'кафе', 'cafe']):
            return self.business_elements['кафе']
        elif any(word in theme_lower for word in ['мойка', 'wash', 'clean']):
            return self.business_elements['автомойка']
        
        return self.general_elements
    
    def _generate_main_prompt(self, elements, theme):
        """Генерирует главный промпт"""
        obj = random.choice(elements['objects'])
        quality = random.choice(elements['qualities'])
        env = random.choice(elements['environments'])
        style = random.choice(self.styles)
        
        return f"{quality} {obj} in {env}, {style}"
    
    def _generate_about1_prompt(self, elements, theme):
        """Генерирует первый about промпт"""
        obj = random.choice(elements['objects'])
        action = random.choice(elements['actions'])
        mood = random.choice(self.moods)
        
        return f"{action} {obj}, {mood} atmosphere, professional quality"
    
    def _generate_about2_prompt(self, elements, theme, theme_lower):
        """КРИТИЧЕСКИЙ метод - генерирует about2 БЕЗ механиков для авто"""
        # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ АВТО ТЕМАТИК
        if any(word in theme_lower for word in ['авто', 'машин', 'car', 'продаж', 'салон']):
            # Для авто используем ТОЛЬКО безопасные объекты
            if 'about2_safe' in elements:
                safe_obj = random.choice(elements['about2_safe'])
                quality = random.choice(elements['qualities'])
                return f"{quality} {safe_obj}, interior design, comfort features"
            else:
                return "elegant car interior with leather seats, premium comfort"
        
        # Для остальных тематик - обычная генерация
        obj = random.choice(elements['objects'])
        quality = random.choice(elements['qualities'])
        comp = random.choice(self.compositions)
        
        # Проверяем на запрещенные слова
        prompt = f"{quality} {obj}, {comp}, detailed view"
        
        if 'banned_words' in elements:
            for banned in elements['banned_words']:
                if banned.lower() in prompt.lower():
                    # Заменяем на безопасный вариант
                    return self._generate_safe_about2(elements, theme)
        
        return prompt
    
    def _generate_safe_about2(self, elements, theme):
        """Генерирует безопасный about2 промпт"""
        quality = random.choice(elements['qualities'])
        comp = random.choice(self.compositions)
        
        # Безопасные варианты
        safe_variants = [
            f"{quality} service environment, {comp}",
            f"professional workspace, {quality} facilities",
            f"{quality} interior design, modern setup"
        ]
        
        return random.choice(safe_variants)
    
    def _generate_about3_prompt(self, elements, theme):
        """Генерирует третий about промпт"""
        obj = random.choice(elements['objects'])
        action = random.choice(elements['actions'])
        style = random.choice(self.styles)
        
        return f"{action} {obj}, results showcase, {style}"
    
    def _generate_review_prompt(self):
        """Генерирует промпты для отзывов - только люди"""
        people_variants = [
            "happy satisfied customer smiling",
            "pleased client with positive expression", 
            "delighted customer showing satisfaction",
            "cheerful person expressing joy",
            "content customer with thumbs up",
            "satisfied client in consultation",
            "happy customer receiving service"
        ]
        
        return random.choice(people_variants)

# Функция для совместимости
def create_smart_thematic_prompts(theme_input):
    """Создает вариативные тематические промпты"""
    generator = SmartVariativePrompts()
    prompts_dict = generator.generate_prompts(theme_input)
    
    # Возвращаем в виде списка для совместимости
    return [
        prompts_dict['main'],
        prompts_dict['about1'], 
        prompts_dict['about2'],
        prompts_dict['about3'],
        prompts_dict['review1'],
        prompts_dict['review2'],
        prompts_dict['review3'],
        prompts_dict['favicon']
    ]

if __name__ == "__main__":
    # Тестирование вариативности
    generator = SmartVariativePrompts()
    
    test_themes = ["доставка еды", "продажа авто", "кафе"]
    
    for theme in test_themes:
        print(f"\n=== {theme.upper()} - ТЕСТ ВАРИАТИВНОСТИ ===")
        
        # Генерируем 3 разных набора для проверки вариативности
        for i in range(3):
            print(f"\nВариант {i+1}:")
            prompts = generator.generate_prompts(theme)
            
            for key, prompt in prompts.items():
                print(f"  {key}: {prompt}")
                
                # Проверяем на запрещенные слова
                if theme == "доставка еды" and any(bad in prompt.lower() for bad in ['box', 'коробк']):
                    print(f"    ❌ НАЙДЕНЫ КОРОБКИ!")
                elif theme == "продажа авто" and key == "about2" and any(bad in prompt.lower() for bad in ['mechanic', 'механик']):
                    print(f"    ❌ НАЙДЕН МЕХАНИК!")
                else:
                    print(f"    ✅ Промпт безопасен") 