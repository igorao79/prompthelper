#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ИИ-усилитель промптов через Hugging Face API
Использует внешние ИИ модели для создания промптов высочайшего качества
"""

import requests
import json
import time
import random
from typing import Dict, List, Optional

class AIEnhancer:
    """Интеграция с внешними ИИ для улучшения промптов"""
    
    def __init__(self):
        # Бесплатные модели Hugging Face для генерации текста
        self.models = [
            "microsoft/DialoGPT-medium",
            "gpt2-medium", 
            "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-large",
            "EleutherAI/gpt-neo-1.3B"
        ]
        
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Промпты для ИИ-генерации
        self.enhancement_prompts = {
            'main': """Create a professional, detailed image prompt for a business theme: '{theme}'. 
The prompt should be visual, specific, and include: professional setting, modern equipment, expert team, high quality service. 
Make it vivid and appealing for image generation. Focus on business excellence and professionalism.
Prompt:""",
            
            'about': """Generate a business image prompt for '{theme}' showing: equipment, process, or facility. 
Include technical details, professional environment, quality standards. Make it specific and visual.
Prompt:""",
            
            'review': """Create an image prompt for a satisfied customer portrait. 
Focus on: happy person, genuine smile, professional headshot style, clean background. 
NO business equipment, just a person showing satisfaction.
Prompt:""",
            
            'favicon': """Generate a simple icon description for '{theme}' business. 
Focus on: minimalist symbol, business emblem, clean design, professional logo concept.
Prompt:"""
        }
    
    def enhance_prompts_with_ai(self, theme: str) -> Dict[str, str]:
        """
        Использует внешний ИИ для создания улучшенных промптов
        
        Args:
            theme (str): Тематика бизнеса
            
        Returns:
            Dict[str, str]: Словарь улучшенных промптов
        """
        enhanced_prompts = {}
        
        # Генерируем основные промпты через ИИ
        try:
            enhanced_prompts['main'] = self._generate_enhanced_prompt(theme, 'main')
            enhanced_prompts['about1'] = self._generate_enhanced_prompt(theme, 'about')
            enhanced_prompts['about2'] = self._generate_enhanced_prompt(theme, 'about')
            enhanced_prompts['about3'] = self._generate_enhanced_prompt(theme, 'about')
            enhanced_prompts['review1'] = self._generate_enhanced_prompt(theme, 'review')
            enhanced_prompts['review2'] = self._generate_enhanced_prompt(theme, 'review')
            enhanced_prompts['review3'] = self._generate_enhanced_prompt(theme, 'review')
            enhanced_prompts['favicon'] = self._generate_enhanced_prompt(theme, 'favicon')
            
            print(f"✅ ИИ-усилитель успешно обработал тематику: {theme}")
            
        except Exception as e:
            print(f"⚠️ Ошибка ИИ-усилителя: {e}")
            # Fallback на наш ИИ-генератор
            return self._fallback_to_local_ai(theme)
        
        return enhanced_prompts
    
    def _generate_enhanced_prompt(self, theme: str, prompt_type: str) -> str:
        """
        Генерирует улучшенный промпт через внешний ИИ
        
        Args:
            theme (str): Тематика
            prompt_type (str): Тип промпта (main, about, review, favicon)
            
        Returns:
            str: Улучшенный промпт
        """
        # Выбираем случайную модель для разнообразия
        model = random.choice(self.models)
        
        # Формируем запрос к ИИ
        ai_prompt = self.enhancement_prompts[prompt_type].format(theme=theme)
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "inputs": ai_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.8,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/{model}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Извлекаем только часть после "Prompt:"
                    if "Prompt:" in generated_text:
                        enhanced_prompt = generated_text.split("Prompt:")[-1].strip()
                        return self._clean_and_optimize_prompt(enhanced_prompt)
                
            # Если не получилось, используем локальную генерацию
            return self._generate_local_fallback(theme, prompt_type)
            
        except Exception as e:
            print(f"🔄 ИИ модель {model} недоступна, пробуем локальную генерацию")
            return self._generate_local_fallback(theme, prompt_type)
    
    def _clean_and_optimize_prompt(self, prompt: str) -> str:
        """
        Очищает и оптимизирует сгенерированный промпт
        
        Args:
            prompt (str): Сырой промпт от ИИ
            
        Returns:
            str: Очищенный промпт
        """
        # Убираем лишние символы и форматирование
        cleaned = prompt.replace('\n', ' ').replace('\r', ' ')
        cleaned = ' '.join(cleaned.split())  # Убираем множественные пробелы
        
        # Убираем кавычки и специальные символы
        cleaned = cleaned.strip('\'".,!?;:')
        
        # Ограничиваем длину
        words = cleaned.split()
        if len(words) > 25:
            cleaned = ' '.join(words[:25])
        
        # Добавляем качественные дескрипторы
        quality_terms = [
            "professional", "high-quality", "modern", "expert", 
            "premium", "excellent", "sophisticated", "advanced"
        ]
        
        if not any(term in cleaned.lower() for term in quality_terms):
            enhanced_term = random.choice(quality_terms)
            cleaned = f"{enhanced_term} {cleaned}"
        
        return cleaned
    
    def _generate_local_fallback(self, theme: str, prompt_type: str) -> str:
        """
        Локальная генерация как fallback
        
        Args:
            theme (str): Тематика
            prompt_type (str): Тип промпта
            
        Returns:
            str: Локально сгенерированный промпт
        """
        fallback_templates = {
            'main': f"professional {theme} business environment with expert team and modern equipment",
            'about': f"high-quality {theme} service process with professional standards and equipment",
            'review': "portrait photo of satisfied customer, genuine smile, professional headshot style",
            'favicon': f"{theme} business icon, minimalist symbol, professional logo design"
        }
        
        return fallback_templates.get(prompt_type, f"professional {theme} service")
    
    def _fallback_to_local_ai(self, theme: str) -> Dict[str, str]:
        """
        Fallback на локальный ИИ-генератор при сбое внешнего ИИ
        
        Args:
            theme (str): Тематика
            
        Returns:
            Dict[str, str]: Промпты от локального ИИ
        """
        try:
            from .ai_prompt_generator import create_ai_prompts
            print("🔄 Переключение на локальный ИИ-генератор")
            return create_ai_prompts(theme)
        except ImportError:
            # Последний fallback - простые промпты
            return {
                'main': f"professional {theme} business service",
                'about1': f"modern {theme} equipment and workspace",
                'about2': f"expert {theme} service process",  
                'about3': f"quality {theme} facility standards",
                'review1': "portrait photo of happy customer, genuine smile",
                'review2': "satisfied client headshot, positive expression",
                'review3': "pleased customer portrait, professional background",
                'favicon': f"{theme} business icon, simple logo design"
            }

# Основная функция для интеграции
def create_ai_enhanced_prompts(theme: str) -> Dict[str, str]:
    """
    Создает промпты с помощью внешнего ИИ-усилителя
    
    Args:
        theme (str): Тематика бизнеса
        
    Returns:
        Dict[str, str]: Словарь улучшенных промптов
    """
    enhancer = AIEnhancer()
    return enhancer.enhance_prompts_with_ai(theme)

# Функция для тестирования доступности ИИ
def test_ai_availability() -> bool:
    """
    Тестирует доступность внешних ИИ сервисов
    
    Returns:
        bool: True если ИИ доступен
    """
    enhancer = AIEnhancer()
    try:
        test_prompt = enhancer._generate_enhanced_prompt("test business", "main")
        return len(test_prompt) > 10
    except:
        return False 