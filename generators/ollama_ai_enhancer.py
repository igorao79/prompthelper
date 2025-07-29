#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OLLAMA ИИ-УСИЛИТЕЛЬ ПРОМПТОВ 2025 - DEEPSEEK КАЧЕСТВО! 🧠⚡
Полностью бесплатный, локальный ИИ-усилитель с неограниченными кредитами
DEEPSEEK = КАЧЕСТВО + СКОРОСТЬ!
"""

import requests
import json
import time
import random
import os
import subprocess
from typing import Dict, List, Optional

class OllamaAIEnhancer:
    """Ollama ИИ-усилитель - DEEPSEEK КАЧЕСТВО! 🧠⚡"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.api_endpoint = f"{self.ollama_url}/api/generate"
        
        # ⚡ ПРИМЕНЯЕМ СУПЕР ОПТИМИЗАЦИИ
        self._apply_speed_optimizations()
        
        # 🧠 DEEPSEEK модели для КАЧЕСТВЕННОЙ генерации!
        self.preferred_models = [
            "deepseek-r1:1.5b",             # 🧠 САМАЯ УМНАЯ для размера!
            "deepseek-r1:8b",               # 🧠 СУПЕР КАЧЕСТВО
            "llama3.2:3b-instruct-q4_0",   # Fallback быстрый
            "gemma2:2b-instruct-q4_0",     # Fallback ультра-быстрый
            "qwen2.5:3b-instruct-q4_0",    # Fallback Alibaba
        ]
        
        # 🎯 КАЧЕСТВЕННЫЕ промпты для правильного понимания
        self.enhancement_prompts = {
            'main': """Generate BUSINESS IMAGE prompt for: {theme}

Context: Professional business service
Requirements:
- English only
- Professional business environment  
- High quality, modern
- 15 words maximum
- NO technical equipment unless relevant

Output only the image prompt:""",
            
            'about': """Generate BUSINESS TOOLS prompt for: {theme}

Context: Professional equipment/workspace for this business
Requirements:
- English only
- Tools relevant to THIS specific business
- Professional setup
- 12 words maximum

Output only the image prompt:""",
            
            'review': """Generate CUSTOMER PHOTO prompt for: {theme}

Context: Happy customer of this business
Requirements:
- English only
- Smiling person only
- Satisfied customer expression
- 10 words maximum

Output only the image prompt:""",
            
            'favicon': """Generate SIMPLE ICON prompt for: {theme}

Context: Business logo/symbol
Requirements:
- English only
- Minimalist business icon
- Simple, clean design
- 8 words maximum

Output only the image prompt:"""
        }
        
        # ⚡ СУПЕР-БЫСТРЫЕ настройки генерации
        self.fast_generation_options = {
            "temperature": 0.1,     # Меньше креативности = точнее
            "top_k": 10,           # Сосредоточенность
            "top_p": 0.7,          # Точность
            "repeat_penalty": 1.0, # Без повторов
            "num_predict": 30,     # Еще короче = быстрее
            "num_ctx": 512,        # Совсем короткий контекст
            "stop": ["\n", ".", "!", "Output:", "Prompt:"] # Быстрый стоп
        }

    def _apply_speed_optimizations(self):
        """⚡ Применяем ВСЕ оптимизации скорости Ollama"""
        speed_env = {
            "OLLAMA_FLASH_ATTENTION": "1",        # КРИТИЧНО!
            "OLLAMA_KV_CACHE_TYPE": "q4_0",       # Еще быстрее кеш
            "OLLAMA_NUM_PARALLEL": "8",           # Больше потоков
            "OLLAMA_MAX_LOADED_MODELS": "1",      # Только одна модель
            "OLLAMA_KEEP_ALIVE": "10m",           # Дольше в памяти
            "OLLAMA_GPU_LAYERS": "999",           # Все на GPU
            "OLLAMA_HOST": "127.0.0.1:11434",     # Локальный хост
            "OLLAMA_MAX_QUEUE": "20",             # Больше очередь
            "OLLAMA_CONCURRENT_REQUESTS": "4",    # Параллельные запросы
        }
        
        # Устанавливаем переменные окружения
        for key, value in speed_env.items():
            os.environ[key] = value
            
        print(f"⚡ Применены СУПЕР-оптимизации скорости Ollama!")

    def test_ollama_availability(self) -> bool:
        """⚡ Мгновенная проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False

    def get_best_available_model(self) -> Optional[str]:
        """🧠 Находим САМУЮ КАЧЕСТВЕННУЮ доступную модель"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                available_models = [model["name"] for model in response.json().get("models", [])]
                
                # Приоритет на DeepSeek!
                for model in self.preferred_models:
                    if model in available_models:
                        print(f"🧠 Найдена КАЧЕСТВЕННАЯ модель: {model}")
                        return model
                
                # Fallback на любую доступную
                if available_models:
                    best = available_models[0]
                    print(f"📦 Используем доступную модель: {best}")
                    return best
        except:
            pass
        
        return None

    def create_enhanced_prompt(self, theme: str, prompt_type: str = "main") -> str:
        """🧠 КАЧЕСТВЕННАЯ генерация промптов с DeepSeek"""
        if not self.test_ollama_availability():
            print("❌ Ollama недоступен, используем fallback")
            return self._fallback_prompt(theme, prompt_type)
        
        model = self.get_best_available_model()
        if not model:
            print("❌ Нет доступных моделей, используем fallback") 
            return self._fallback_prompt(theme, prompt_type)
        
        # ⚡ БЫСТРАЯ генерация
        start_time = time.time()
        
        try:
            # Подготавливаем КАЧЕСТВЕННЫЙ промпт
            template = self.enhancement_prompts.get(prompt_type, self.enhancement_prompts['main'])
            user_prompt = template.format(theme=theme)
            
            # ⚡ СУПЕР-БЫСТРЫЙ запрос к Ollama
            payload = {
                "model": model,
                "prompt": user_prompt,
                "stream": False,
                "options": self.fast_generation_options
            }
            
            print(f"🧠 Генерируем {prompt_type} промпт через {model}...")
            
            response = requests.post(
                self.api_endpoint, 
                json=payload, 
                timeout=10  # Еще короче таймаут
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # 🎯 КАЧЕСТВЕННАЯ очистка результата
                cleaned = self._smart_clean_response(generated_text, theme, prompt_type)
                
                duration = time.time() - start_time
                print(f"✅ Сгенерирован промпт за {duration:.1f}с: {cleaned[:50]}...")
                
                return cleaned
            else:
                print(f"❌ Ошибка Ollama: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Ошибка генерации: {e}")
        
        # Fallback
        return self._fallback_prompt(theme, prompt_type)

    def _smart_clean_response(self, text: str, theme: str, prompt_type: str) -> str:
        """🎯 УМНАЯ очистка ответа с контекстом"""
        if not text:
            return self._fallback_prompt(theme, prompt_type)
        
        # ⚡ БЫСТРАЯ очистка от reasoning тегов DeepSeek
        text = text.replace("<think>", "").replace("</think>", "")
        text = text.replace("<thinking>", "").replace("</thinking>", "")
        text = text.replace("Output only the image prompt:", "")
        text = text.replace("English only", "")
        text = text.replace("Requirements:", "")
        text = text.replace("Context:", "")
        text = text.replace("Image prompt:", "")
        text = text.replace("Prompt:", "")
        text = text.strip()
        
        # Берем только первую строку без reasoning
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Пропускаем пустые строки и reasoning
            if line and not line.startswith('<') and not line.startswith('I need') and not line.startswith('Let me'):
                text = line
                break
        
        # Ограничиваем длину
        text = text[:120]
        
        # Убираем кавычки
        text = text.strip('\'"')
        
        # Убираем точки в конце
        text = text.rstrip('.')
        
        # Проверяем на русские слова
        russian_words = ['автомобил', 'машин', 'услуг', 'бизнес', 'компани', 'сервис', 'участок', 'дача']
        for word in russian_words:
            if word in text.lower():
                return self._fallback_prompt(theme, prompt_type)
        
        # Проверяем релевантность для специфичных тематик
        if self._is_relevant_response(text, theme, prompt_type):
            return text if text else self._fallback_prompt(theme, prompt_type)
        else:
            print(f"⚠️ Нерелевантный ответ, используем fallback")
            return self._fallback_prompt(theme, prompt_type)

    def _is_relevant_response(self, text: str, theme: str, prompt_type: str) -> bool:
        """🎯 Проверяем релевантность ответа тематике"""
        text_lower = text.lower()
        theme_lower = theme.lower()
        
        # Для загородных участков НЕ должно быть техники
        if 'участк' in theme_lower or 'дача' in theme_lower:
            tech_words = ['drone', 'scanner', '3d', 'camera', 'software', 'equipment', 'technology']
            if any(word in text_lower for word in tech_words):
                return False
        
        # Для автосервиса ДОЛЖНЫ быть автомобильные термины
        if 'авто' in theme_lower and prompt_type == 'about':
            auto_words = ['car', 'vehicle', 'automotive', 'garage', 'tool', 'engine']
            if not any(word in text_lower for word in auto_words):
                return False
        
        return True

    def _fallback_prompt(self, theme: str, prompt_type: str) -> str:
        """🎯 КАЧЕСТВЕННЫЙ fallback для промптов"""
        
        # Специальная обработка загородных участков
        if 'участк' in theme.lower() or 'дача' in theme.lower():
            fallbacks = {
                'main': "beautiful rural property with scenic countryside views and development potential",
                'about': "professional real estate consultation with property documents and site plans",
                'review': "satisfied property buyer smiling happily with rural landscape background",
                'favicon': "simple house icon with tree symbol minimalist rural property logo"
            }
            return fallbacks.get(prompt_type, fallbacks['main'])
        
        # Обычные fallback промпты
        fallbacks = {
            'main': f"professional {theme} business office modern high quality service",
            'about': f"modern {theme} professional equipment workspace tools",
            'review': f"satisfied customer smiling happy positive expression professional photo",
            'favicon': f"{theme} simple minimalist icon logo business symbol"
        }
        
        return fallbacks.get(prompt_type, fallbacks['main'])

def create_ollama_enhanced_prompts(theme_input: str) -> Dict[str, str]:
    """
    🧠 DEEPSEEK КАЧЕСТВЕННАЯ функция создания всех промптов
    """
    print(f"🧠 DEEPSEEK Ollama ИИ-усилитель запущен для: {theme_input}")
    
    enhancer = OllamaAIEnhancer()
    
    # 🎯 КАЧЕСТВЕННАЯ генерация всех промптов
    prompts = {}
    
    try:
        # Генерируем основные промпты
        prompts['main'] = enhancer.create_enhanced_prompt(theme_input, 'main')
        prompts['about1'] = enhancer.create_enhanced_prompt(theme_input, 'about')
        prompts['about2'] = enhancer.create_enhanced_prompt(theme_input, 'about')
        prompts['about3'] = enhancer.create_enhanced_prompt(theme_input, 'about')
        
        # Review промпты с людьми
        prompts['review1'] = enhancer.create_enhanced_prompt(theme_input, 'review')
        prompts['review2'] = enhancer.create_enhanced_prompt(theme_input, 'review')
        prompts['review3'] = enhancer.create_enhanced_prompt(theme_input, 'review')
        
        # Фавикон
        prompts['favicon'] = enhancer.create_enhanced_prompt(theme_input, 'favicon')
        
        print(f"✅ DEEPSEEK Ollama ИИ-усилитель завершил обработку!")
        
    except Exception as e:
        print(f"⚠️ Ошибка DEEPSEEK усилителя: {e}")
        # КАЧЕСТВЕННЫЙ fallback
        enhancer_fallback = OllamaAIEnhancer()
        prompts = {
            'main': enhancer_fallback._fallback_prompt(theme_input, 'main'),
            'about1': enhancer_fallback._fallback_prompt(theme_input, 'about'),
            'about2': enhancer_fallback._fallback_prompt(theme_input, 'about'),
            'about3': enhancer_fallback._fallback_prompt(theme_input, 'about'),
            'review1': enhancer_fallback._fallback_prompt(theme_input, 'review'),
            'review2': enhancer_fallback._fallback_prompt(theme_input, 'review'),
            'review3': enhancer_fallback._fallback_prompt(theme_input, 'review'),
            'favicon': enhancer_fallback._fallback_prompt(theme_input, 'favicon')
        }
    
    return prompts 