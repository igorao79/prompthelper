#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СУПЕР ИИ-УСИЛИТЕЛЬ ПРОМПТОВ 
Интеграция с множественными ИИ источниками для создания промптов ВЫСОЧАЙШЕГО качества
"""

import requests
import json
import time
import random
from typing import Dict, List, Optional

class SuperAIEnhancer:
    """Супер ИИ-усилитель с множественными источниками"""
    
    def __init__(self):
        # Несколько источников ИИ для максимальной надёжности
        self.ai_sources = {
            'huggingface': {
                'url': 'https://api-inference.huggingface.co/models',
                'models': [
                    'microsoft/DialoGPT-medium',
                    'facebook/blenderbot-400M-distill',
                    'EleutherAI/gpt-neo-1.3B'
                ]
            },
            'together': {
                'url': 'https://api.together.xyz/inference',
                'models': ['togethercomputer/RedPajama-INCITE-Chat-3B-v1']
            },
            'replicate': {
                'url': 'https://api.replicate.com/v1/predictions',
                'models': ['meta/llama-2-7b-chat']
            }
        }
        
        # Умные промпты для максимального качества
        self.enhancement_templates = {
            'main': """Transform this business theme: '{theme}' into a professional, visually stunning image description.

Focus on: modern professional setting, expert team, cutting-edge equipment, premium service quality, sophisticated atmosphere.

Create a detailed, vivid description that would produce an amazing business image. Be specific about professional elements, lighting, and quality indicators.

Enhanced prompt:""",
            
            'about': """Create a compelling business image description for '{theme}' equipment/process/facility.

Include: state-of-the-art technology, professional workflow, quality standards, expert craftsmanship, modern facility design.

Make it visual, specific, and impressive for professional business imagery.

Description:""",
            
            'review': """Generate a perfect customer testimonial portrait description.

Focus ONLY on: genuinely happy person, authentic smile, professional headshot quality, clean simple background, satisfied expression, positive energy.

NO business equipment or workspace - just a person radiating satisfaction and trust.

Portrait description:""",
            
            'favicon': """Design description for a modern business icon representing '{theme}'.

Create: minimalist professional symbol, clean geometric design, business emblem concept, scalable logo idea, contemporary branding element.

Avoid circles and clichés. Focus on sophisticated, memorable business symbolism.

Icon concept:"""
        }
        
        # Качественные дескрипторы для улучшения
        self.quality_enhancers = {
            'professional': ['expert', 'premium', 'sophisticated', 'elite', 'world-class'],
            'modern': ['cutting-edge', 'state-of-the-art', 'contemporary', 'advanced', 'innovative'],
            'quality': ['exceptional', 'superior', 'outstanding', 'excellent', 'top-tier'],
            'visual': ['stunning', 'impressive', 'remarkable', 'striking', 'captivating']
        }
    
    def create_super_enhanced_prompts(self, theme: str) -> Dict[str, str]:
        """
        Создаёт супер-улучшенные промпты через множественные ИИ источники
        
        Args:
            theme (str): Тематика бизнеса
            
        Returns:
            Dict[str, str]: Словарь супер-промптов высочайшего качества
        """
        print(f"🚀 СУПЕР ИИ-УСИЛИТЕЛЬ запущен для: {theme}")
        
        enhanced_prompts = {}
        
        # Генерируем через лучшие доступные ИИ
        for prompt_type in ['main', 'about', 'review', 'favicon']:
            try:
                if prompt_type == 'main':
                    enhanced_prompts['main'] = self._generate_super_prompt(theme, prompt_type)
                elif prompt_type == 'about':
                    enhanced_prompts['about1'] = self._generate_super_prompt(theme, prompt_type)
                    enhanced_prompts['about2'] = self._generate_super_prompt(theme, prompt_type)  
                    enhanced_prompts['about3'] = self._generate_super_prompt(theme, prompt_type)
                elif prompt_type == 'review':
                    enhanced_prompts['review1'] = self._generate_super_prompt(theme, prompt_type)
                    enhanced_prompts['review2'] = self._generate_super_prompt(theme, prompt_type)
                    enhanced_prompts['review3'] = self._generate_super_prompt(theme, prompt_type)
                elif prompt_type == 'favicon':
                    enhanced_prompts['favicon'] = self._generate_super_prompt(theme, prompt_type)
                    
            except Exception as e:
                print(f"⚠️ Ошибка генерации {prompt_type}: {e}")
                # Используем продвинутый fallback
                enhanced_prompts.update(self._create_advanced_fallback(theme, prompt_type))
        
        # Пост-обработка для максимального качества
        enhanced_prompts = self._post_process_prompts(enhanced_prompts, theme)
        
        print(f"✅ СУПЕР ИИ-УСИЛИТЕЛЬ завершил обработку!")
        return enhanced_prompts
    
    def _generate_super_prompt(self, theme: str, prompt_type: str) -> str:
        """
        Генерирует супер-промпт через лучшие доступные ИИ
        
        Args:
            theme (str): Тематика
            prompt_type (str): Тип промпта
            
        Returns:
            str: Супер-улучшенный промпт
        """
        # Пробуем разные ИИ источники по приоритету
        for source_name, source_config in self.ai_sources.items():
            try:
                result = self._try_ai_source(theme, prompt_type, source_name, source_config)
                if result and len(result) > 20:  # Проверяем качество
                    return self._enhance_with_quality_terms(result, theme)
            except Exception as e:
                print(f"🔄 {source_name} недоступен, пробуем следующий...")
                continue
        
        # Если все ИИ недоступны, используем продвинутый локальный генератор
        return self._create_premium_fallback(theme, prompt_type)
    
    def _try_ai_source(self, theme: str, prompt_type: str, source_name: str, source_config: Dict) -> str:
        """
        Пробует конкретный ИИ источник
        
        Args:
            theme (str): Тематика
            prompt_type (str): Тип промпта  
            source_name (str): Название источника
            source_config (Dict): Конфигурация источника
            
        Returns:
            str: Результат от ИИ
        """
        if source_name == 'huggingface':
            return self._query_huggingface(theme, prompt_type, source_config)
        # Здесь можно добавить другие источники
        else:
            return self._create_premium_fallback(theme, prompt_type)
    
    def _query_huggingface(self, theme: str, prompt_type: str, config: Dict) -> str:
        """
        Запрос к Hugging Face API
        """
        model = random.choice(config['models'])
        ai_prompt = self.enhancement_templates[prompt_type].format(theme=theme)
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": ai_prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
        }
        
        response = requests.post(
            f"{config['url']}/{model}",
            headers=headers,
            json=payload,
            timeout=8
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                
                # Умная экстракция результата
                for separator in ['Enhanced prompt:', 'Description:', 'Portrait description:', 'Icon concept:']:
                    if separator in generated_text:
                        extracted = generated_text.split(separator)[-1].strip()
                        if len(extracted) > 15:
                            return self._clean_ai_output(extracted)
                
                # Если нет сепараторов, берём конец текста
                if len(generated_text) > len(ai_prompt) + 10:
                    extracted = generated_text[len(ai_prompt):].strip()
                    return self._clean_ai_output(extracted)
        
        raise Exception(f"Неудачный ответ: {response.status_code}")
    
    def _clean_ai_output(self, text: str) -> str:
        """
        Очищает и улучшает вывод ИИ
        
        Args:
            text (str): Сырой текст от ИИ
            
        Returns:
            str: Очищенный текст
        """
        # Базовая очистка
        cleaned = text.replace('\n', ' ').replace('\r', ' ')
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.strip('\'".,!?;:')
        
        # Убираем повторы и мусор
        words = cleaned.split()
        unique_words = []
        for word in words:
            if word.lower() not in [w.lower() for w in unique_words[-3:]]:  # Избегаем повторов
                unique_words.append(word)
        
        # Ограничиваем длину разумными пределами
        if len(unique_words) > 30:
            unique_words = unique_words[:30]
        
        return ' '.join(unique_words)
    
    def _enhance_with_quality_terms(self, prompt: str, theme: str) -> str:
        """
        Улучшает промпт качественными дескрипторами
        
        Args:
            prompt (str): Базовый промпт
            theme (str): Тематика
            
        Returns:
            str: Улучшенный промпт
        """
        # Добавляем качественные термины если их нет
        for category, terms in self.quality_enhancers.items():
            if not any(term in prompt.lower() for term in terms):
                selected_term = random.choice(terms)
                prompt = f"{selected_term} {prompt}"
                break  # Добавляем только один термин чтобы не перегружать
        
        return prompt
    
    def _create_premium_fallback(self, theme: str, prompt_type: str) -> str:
        """
        Создаёт премиум fallback промпт
        
        Args:
            theme (str): Тематика
            prompt_type (str): Тип промпта
            
        Returns:
            str: Премиум промпт
        """
        premium_templates = {
            'main': f"cutting-edge {theme} business center with world-class professional team and state-of-the-art equipment",
            'about': f"exceptional {theme} service workflow with premium quality standards and sophisticated technology", 
            'review': "portrait photo of genuinely satisfied customer, authentic smile, professional headshot style, clean background",
            'favicon': f"sophisticated {theme} business emblem, modern minimalist icon design, premium brand symbol"
        }
        
        base = premium_templates.get(prompt_type, f"premium {theme} professional service")
        
        # Добавляем случайные улучшения
        enhancements = [
            "expertly crafted", "meticulously designed", "precision engineered", 
            "thoughtfully curated", "strategically positioned", "carefully optimized"
        ]
        
        enhancement = random.choice(enhancements)
        return f"{enhancement} {base}"
    
    def _create_advanced_fallback(self, theme: str, prompt_type: str) -> Dict[str, str]:
        """
        Создаёт продвинутый fallback для отсутствующих промптов
        """
        fallbacks = {}
        
        if prompt_type == 'main':
            fallbacks['main'] = self._create_premium_fallback(theme, 'main')
        elif prompt_type == 'about':
            for i in range(1, 4):
                fallbacks[f'about{i}'] = self._create_premium_fallback(theme, 'about')
        elif prompt_type == 'review':
            for i in range(1, 4):
                fallbacks[f'review{i}'] = self._create_premium_fallback(theme, 'review')
        elif prompt_type == 'favicon':
            fallbacks['favicon'] = self._create_premium_fallback(theme, 'favicon')
        
        return fallbacks
    
    def _post_process_prompts(self, prompts: Dict[str, str], theme: str) -> Dict[str, str]:
        """
        Пост-обработка для финального улучшения качества
        
        Args:
            prompts (Dict[str, str]): Сырые промпты
            theme (str): Тематика
            
        Returns:
            Dict[str, str]: Финально обработанные промпты
        """
        processed = {}
        
        for key, prompt in prompts.items():
            # Финальная оптимизация
            processed_prompt = prompt
            
            # Убеждаемся что промпт качественный
            if len(processed_prompt) < 20:
                processed_prompt = self._create_premium_fallback(theme, key.replace('1','').replace('2','').replace('3',''))
            
            # Ограничиваем длину для оптимальной работы с API
            words = processed_prompt.split()
            if len(words) > 25:
                processed_prompt = ' '.join(words[:25])
            
            processed[key] = processed_prompt
        
        return processed

# Основная функция интеграции
def create_super_ai_prompts(theme: str) -> Dict[str, str]:
    """
    Создаёт промпты через СУПЕР ИИ-УСИЛИТЕЛЬ
    
    Args:
        theme (str): Тематика бизнеса
        
    Returns:
        Dict[str, str]: Супер-промпты высочайшего качества  
    """
    enhancer = SuperAIEnhancer()
    return enhancer.create_super_enhanced_prompts(theme) 