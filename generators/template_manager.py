# -*- coding: utf-8 -*-

"""
Менеджер шаблонов для генерации изображений
Обеспечивает вариативность наборов из 8 изображений и предотвращает повторение одинаковых наборов подряд
"""

import random
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class TemplateManager:
    """Менеджер наборов шаблонов изображений с контролем повторений"""
    
    # 9 различных наборов по 8 изображений в каждом
    TEMPLATE_SETS = {
        "classic": ["main", "about1", "about2", "about3", "gallery1", "gallery2", "gallery3", "favicon"],
        "business": ["hero", "team", "services", "portfolio", "reviews", "contact", "office", "favicon"],
        "modern": ["banner", "features", "testimonials", "process", "showcase", "clients", "blog", "favicon"],
        "creative": ["header", "vision", "projects", "skills", "awards", "partners", "news", "favicon"],
        "corporate": ["intro", "company", "solutions", "experience", "success", "support", "careers", "favicon"],
        "startup": ["pitch", "founders", "product", "roadmap", "investors", "community", "updates", "favicon"],
        "agency": ["brand", "expertise", "cases", "methods", "results", "culture", "insights", "favicon"],
        "ecommerce": ["store", "products", "categories", "deals", "reviews", "shipping", "support", "favicon"],
        "personal": ["profile", "story", "work", "achievements", "interests", "contact", "social", "favicon"]
    }
    
    # Получаем список всех наборов
    ALL_SET_NAMES = list(TEMPLATE_SETS.keys())
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Инициализация менеджера шаблонов
        
        Args:
            history_file: Путь к файлу истории использования наборов шаблонов
        """
        self.history_file = history_file or "template_usage_history.json"
        self.last_used_set = None
        self.usage_history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Загружает историю использования наборов шаблонов"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_used_set = data.get("last_used_set")
                    return data
        except Exception as e:
            print(f"⚠️ Ошибка загрузки истории шаблонов: {e}")
        
        return {"last_used_set": None, "set_usage_count": {}, "generation_history": []}
    
    def _save_history(self):
        """Сохраняет историю использования наборов шаблонов"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения истории шаблонов: {e}")
    
    def get_random_template_set(self) -> Tuple[str, List[str]]:
        """
        Выбирает случайный набор шаблонов, исключая последний использованный
        
        Returns:
            Tuple[str, List[str]]: (set_name, template_names)
        """
        available_sets = self.ALL_SET_NAMES.copy()
        
        # Исключаем последний использованный набор, если есть альтернативы
        if self.last_used_set and self.last_used_set in available_sets and len(available_sets) > 1:
            available_sets.remove(self.last_used_set)
        
        # Выбираем случайный набор
        selected_set_name = random.choice(available_sets)
        selected_templates = self.TEMPLATE_SETS[selected_set_name].copy()
        
        return selected_set_name, selected_templates
    
    def get_template_set_by_name(self, set_name: str) -> Optional[List[str]]:
        """
        Получает набор шаблонов по названию
        
        Args:
            set_name: Название набора
            
        Returns:
            Optional[List[str]]: Список шаблонов или None, если набор не найден
        """
        return self.TEMPLATE_SETS.get(set_name)
    
    def mark_set_used(self, set_name: str):
        """
        Отмечает набор как использованный
        
        Args:
            set_name: Название использованного набора
        """
        self.last_used_set = set_name
        self.usage_history["last_used_set"] = set_name
        
        # Обновляем счетчик использования наборов
        set_usage_count = self.usage_history.get("set_usage_count", {})
        set_usage_count[set_name] = set_usage_count.get(set_name, 0) + 1
        self.usage_history["set_usage_count"] = set_usage_count
        
        # Добавляем в историю генераций
        generation_history = self.usage_history.get("generation_history", [])
        generation_history.append({
            "set_name": set_name,
            "templates": self.TEMPLATE_SETS[set_name],
            "timestamp": datetime.now().isoformat(),
        })
        
        # Оставляем только последние 100 записей
        if len(generation_history) > 100:
            generation_history = generation_history[-100:]
        
        self.usage_history["generation_history"] = generation_history
        
        self._save_history()
    
    def get_template_prompts(self, theme: str, template_names: List[str]) -> Dict[str, str]:
        """
        Генерирует промпты для конкретного набора шаблонов
        
        Args:
            theme: Основная тематика
            template_names: Список названий шаблонов
            
        Returns:
            Dict[str, str]: Словарь {template_name: prompt}
        """
        def _p(fallback: str) -> str:
            return f"{fallback}, no text, no words, no letters, no watermark, no caption"
        
        # Базовые промпты для разных типов изображений
        prompt_mapping = {
            # Главные/основные изображения
            "main": _p(f"{theme}, professional real photo, realistic lighting"),
            "hero": _p(f"{theme}, hero banner style, professional photography"),
            "banner": _p(f"{theme}, modern banner design, clean layout"),
            "header": _p(f"{theme}, header image, professional look"),
            "intro": _p(f"{theme}, introduction visual, welcoming atmosphere"),
            "pitch": _p(f"{theme}, pitch presentation style, engaging visual"),
            "brand": _p(f"{theme}, brand identity visual, professional representation"),
            "store": _p(f"{theme}, storefront view, commercial photography"),
            "profile": _p(f"{theme}, profile image, personal branding"),
            
            # О нас/команда
            "about1": _p(f"{theme}, team at work, realistic"),
            "about2": _p(f"{theme}, service process, realistic"),
            "about3": _p(f"{theme}, satisfied client, realistic"),
            "team": _p(f"{theme}, professional team photo, group shot"),
            "company": _p(f"{theme}, company culture, office environment"),
            "founders": _p(f"{theme}, founders portrait, professional headshots"),
            "story": _p(f"{theme}, company story visual, documentary style"),
            
            # Услуги/продукты
            "services": _p(f"{theme}, service showcase, professional demonstration"),
            "features": _p(f"{theme}, feature highlights, product focus"),
            "solutions": _p(f"{theme}, solution presentation, problem solving"),
            "product": _p(f"{theme}, product showcase, detailed view"),
            "products": _p(f"{theme}, product catalog, variety display"),
            "categories": _p(f"{theme}, category overview, organized display"),
            
            # Портфолио/работы
            "gallery1": _p(f"{theme}, wide angle workspace view, realistic, documentary style"),
            "gallery2": _p(f"{theme}, action shot of work in progress, realistic"),
            "gallery3": _p(f"{theme}, equipment and tools close-up, product focus, realistic"),
            "portfolio": _p(f"{theme}, portfolio showcase, best work examples"),
            "projects": _p(f"{theme}, project gallery, creative showcase"),
            "cases": _p(f"{theme}, case study visual, successful projects"),
            "work": _p(f"{theme}, work samples, professional output"),
            
            # Отзывы/результаты
            "reviews": _p(f"{theme}, customer testimonial scene, happy client"),
            "testimonials": _p(f"{theme}, client success story, positive feedback"),
            "results": _p(f"{theme}, successful outcomes, achievement display"),
            "success": _p(f"{theme}, success metrics, progress visualization"),
            
            # Контакты/поддержка
            "contact": _p(f"{theme}, contact information visual, office front"),
            "office": _p(f"{theme}, office space, professional workspace"),
            "support": _p(f"{theme}, customer support, helpful service"),
            "shipping": _p(f"{theme}, shipping process, logistics"),
            
            # Процессы/методы
            "process": _p(f"{theme}, work process, step by step"),
            "methods": _p(f"{theme}, methodology demonstration, systematic approach"),
            "experience": _p(f"{theme}, expertise showcase, skilled professionals"),
            "skills": _p(f"{theme}, skill demonstration, professional competence"),
            
            # Дополнительные
            "blog": _p(f"{theme}, content creation, writing process"),
            "news": _p(f"{theme}, news update, latest information"),
            "updates": _p(f"{theme}, product updates, new developments"),
            "insights": _p(f"{theme}, industry insights, expert knowledge"),
            "culture": _p(f"{theme}, company culture, team spirit"),
            "careers": _p(f"{theme}, career opportunities, professional growth"),
            "community": _p(f"{theme}, community engagement, user interaction"),
            "investors": _p(f"{theme}, investor relations, business growth"),
            "roadmap": _p(f"{theme}, future plans, strategic direction"),
            "deals": _p(f"{theme}, special offers, promotional content"),
            "awards": _p(f"{theme}, achievements recognition, awards ceremony"),
            "partners": _p(f"{theme}, partnership collaboration, business relationships"),
            "clients": _p(f"{theme}, client showcase, customer logos"),
            "showcase": _p(f"{theme}, product showcase, feature highlights"),
            "vision": _p(f"{theme}, company vision, future outlook"),
            "expertise": _p(f"{theme}, professional expertise, specialized knowledge"),
            "achievements": _p(f"{theme}, personal achievements, milestone celebration"),
            "interests": _p(f"{theme}, personal interests, hobby display"),
            "social": _p(f"{theme}, social media presence, online engagement"),
            
            # Favicon (всегда одинаковый)
            "favicon": _p(f"{theme} minimalist icon logo, simple, flat, high contrast"),
        }
        
        # Возвращаем промпты только для запрошенных шаблонов
        return {name: prompt_mapping.get(name, _p(f"{theme}, {name} related image, professional")) 
                for name in template_names}
    
    def get_usage_statistics(self) -> Dict:
        """
        Возвращает статистику использования наборов шаблонов
        
        Returns:
            Dict: Статистика использования
        """
        set_usage_count = self.usage_history.get("set_usage_count", {})
        total_usage = sum(set_usage_count.values())
        
        stats = {
            "total_generations": total_usage,
            "unique_sets_used": len(set_usage_count),
            "most_used_set": max(set_usage_count.items(), key=lambda x: x[1]) if set_usage_count else None,
            "least_used_set": min(set_usage_count.items(), key=lambda x: x[1]) if set_usage_count else None,
            "last_used_set": self.usage_history.get("last_used_set"),
            "set_usage_distribution": set_usage_count,
            "available_sets": self.ALL_SET_NAMES
        }
        
        return stats
    
    def reset_history(self):
        """Сбрасывает историю использования наборов шаблонов"""
        self.usage_history = {"last_used_set": None, "set_usage_count": {}, "generation_history": []}
        self.last_used_set = None
        self._save_history()
    
    @classmethod
    def get_available_template_sets(cls) -> Dict[str, List[str]]:
        """Возвращает словарь всех доступных наборов шаблонов"""
        return cls.TEMPLATE_SETS.copy()
    
    @classmethod
    def get_set_names(cls) -> List[str]:
        """Возвращает список названий всех наборов"""
        return cls.ALL_SET_NAMES.copy()
