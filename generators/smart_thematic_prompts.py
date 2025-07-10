#!/usr/bin/env python3
"""
Умный генератор тематических промптов
Исправляет проблемы с коробками в доставке еды и механиками в продажах авто
"""

import random

class SmartThematicPrompts:
    """Генератор правильных тематических промптов"""
    
    def __init__(self):
        # Специальные промпты для проблемных тематик
        self.special_prompts = {
            'доставка еды': {
                'main': 'delicious hot fresh pizza with melted cheese',
                'about1': 'fresh green salad bowl with vegetables',
                'about2': 'gourmet burger with fries and sauce',
                'about3': 'asian noodle soup with chopsticks',
                'review1': 'happy customer eating delicious meal',
                'review2': 'satisfied customer with tasty food',
                'review3': 'pleased customer enjoying dinner'
            },
            'доставки еды': {
                'main': 'fresh sushi rolls on wooden board',
                'about1': 'hot pasta dish with herbs',
                'about2': 'healthy sandwich with fresh ingredients',
                'about3': 'warm soup bowl with bread',
                'review1': 'happy customer eating delicious meal',
                'review2': 'satisfied customer with tasty food',
                'review3': 'pleased customer enjoying dinner'
            },
            'продажа авто': {
                'main': 'shiny new car in showroom lighting',
                'about1': 'luxury car exterior close-up view',
                'about2': 'elegant car interior with leather seats',  # НЕ МЕХАНИК!
                'about3': 'car dashboard with modern features',
                'review1': 'happy customer with new car keys',
                'review2': 'satisfied car buyer smiling',
                'review3': 'pleased customer next to new car'
            },
            'продажи авто': {
                'main': 'beautiful car in dealership showroom',
                'about1': 'premium car headlights and grille',
                'about2': 'comfortable car seats and interior',  # НЕ МЕХАНИК!
                'about3': 'car steering wheel and controls',
                'review1': 'happy customer with new car keys',
                'review2': 'satisfied car buyer smiling',
                'review3': 'pleased customer next to new car'
            },
            'автосалон': {
                'main': 'modern car showroom with new vehicles',
                'about1': 'luxury sports car on display',
                'about2': 'car dealership office interior',  # НЕ МЕХАНИК!
                'about3': 'car consultation desk area',
                'review1': 'happy customer with new car keys',
                'review2': 'satisfied car buyer smiling',
                'review3': 'pleased customer next to new car'
            },
            'автосалона': {
                'main': 'bright car showroom with premium cars',
                'about1': 'elegant car exterior details',
                'about2': 'car showroom sales area',  # НЕ МЕХАНИК!
                'about3': 'modern car display setup',
                'review1': 'happy customer with new car keys',
                'review2': 'satisfied car buyer smiling',
                'review3': 'pleased customer next to new car'
            }
        }
        
        # Общие промпты для других тематик
        self.general_prompts = {
            'кафе': {
                'main': 'cozy coffee shop interior with warm lighting',
                'about1': 'barista making fresh espresso coffee',
                'about2': 'beautiful coffee beans and brewing equipment',
                'about3': 'comfortable cafe seating area',
                'review1': 'happy customer enjoying coffee',
                'review2': 'satisfied customer in cafe',
                'review3': 'pleased customer with coffee cup'
            },
            'автомойка': {
                'main': 'professional car wash facility exterior',
                'about1': 'clean modern car wash equipment',
                'about2': 'sparkling clean car after washing',
                'about3': 'car wash service bay interior',
                'review1': 'happy customer with clean car',
                'review2': 'satisfied customer after car wash',
                'review3': 'pleased customer with shiny vehicle'
            },
            'стоматология': {
                'main': 'modern dental office reception area',
                'about1': 'clean dental treatment room',
                'about2': 'dental equipment and technology',
                'about3': 'comfortable patient waiting area',
                'review1': 'happy patient with healthy smile',
                'review2': 'satisfied patient after treatment',
                'review3': 'pleased patient showing white teeth'
            },
            'парикмахерская': {
                'main': 'stylish hair salon interior design',
                'about1': 'professional hair styling station',
                'about2': 'modern hair washing area',
                'about3': 'comfortable salon waiting area',
                'review1': 'happy customer with new hairstyle',
                'review2': 'satisfied customer after haircut',
                'review3': 'pleased customer with styled hair'
            }
        }
    
    def get_prompts_for_theme(self, theme):
        """Получает правильные промпты для тематики"""
        theme_lower = theme.lower().strip()
        
        # Проверяем специальные случаи
        for key, prompts in self.special_prompts.items():
            if key in theme_lower:
                return prompts
        
        # Проверяем общие тематики
        for key, prompts in self.general_prompts.items():
            if key in theme_lower:
                return prompts
        
        # Fallback промпты для неизвестных тематик
        return {
            'main': f'professional {theme} service environment',
            'about1': f'modern {theme} equipment and workspace',
            'about2': f'quality {theme} facility interior',  # НЕ МЕХАНИК!
            'about3': f'clean {theme} service area',
            'review1': f'happy {theme} customer',
            'review2': f'satisfied {theme} client',
            'review3': f'pleased {theme} customer'
        }
    
    def get_specific_prompt(self, theme, image_name):
        """Получает конкретный промпт для изображения"""
        prompts = self.get_prompts_for_theme(theme)
        return prompts.get(image_name, f'professional {theme} service')

# Функция для использования в основном коде
def create_smart_thematic_prompts(theme_input):
    """Создает умные тематические промпты"""
    generator = SmartThematicPrompts()
    prompts_dict = generator.get_prompts_for_theme(theme_input)
    
    # Возвращаем в виде списка для совместимости
    return [
        prompts_dict['main'],
        prompts_dict['about1'], 
        prompts_dict['about2'],
        prompts_dict['about3'],
        prompts_dict.get('review1', 'happy customer'),
        prompts_dict.get('review2', 'satisfied customer'),
        prompts_dict.get('review3', 'pleased customer'),
        'business icon'  # для фавиконки
    ]

if __name__ == "__main__":
    # Тестирование
    generator = SmartThematicPrompts()
    
    test_themes = [
        "доставка еды",
        "продажа авто", 
        "кафе",
        "автомойка"
    ]
    
    for theme in test_themes:
        print(f"\n=== {theme.upper()} ===")
        prompts = generator.get_prompts_for_theme(theme)
        for key, prompt in prompts.items():
            print(f"{key}: {prompt}") 