#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ИИ-генератор промптов для изображений
Использует умный анализ тематик и динамическую генерацию без жестких шаблонов
"""

import random
import re
from typing import Dict, List, Tuple

class AIPromptGenerator:
    """Умный ИИ-генератор промптов с анализом тематик"""
    
    def __init__(self):
        # Базовые концепции для анализа
        self.business_concepts = {
            'service_indicators': ['услуг', 'сервис', 'service', 'помощь', 'поддержка', 'консультация'],
            'product_indicators': ['продажа', 'товар', 'магазин', 'shop', 'store', 'продукт'],
            'digital_indicators': ['онлайн', 'digital', 'интернет', 'веб', 'сайт', 'приложение'],
            'physical_indicators': ['офис', 'магазин', 'центр', 'студия', 'мастерская', 'склад']
        }
        
        # Семантические группы для качественной генерации
        self.semantic_groups = {
            'automotive': ['автомобиль', 'машина', 'авто', 'транспорт', 'шины', 'сервис', 'ремонт'],
            'real_estate': ['недвижимость', 'квартира', 'дом', 'участок', 'аренда', 'продажа'],
            'healthcare': ['медицина', 'здоровье', 'лечение', 'врач', 'клиника', 'больница'],
            'education': ['обучение', 'курсы', 'школа', 'образование', 'учеба', 'преподавание'],
            'food': ['еда', 'ресторан', 'кафе', 'доставка', 'питание', 'кулинария'],
            'beauty': ['красота', 'салон', 'косметика', 'уход', 'стиль', 'мода'],
            'finance': ['финансы', 'банк', 'кредит', 'инвестиции', 'страхование', 'деньги'],
            'technology': ['технологии', 'софт', 'программы', 'компьютер', 'разработка'],
            'construction': ['строительство', 'ремонт', 'отделка', 'дизайн', 'архитектура'],
            'logistics': ['доставка', 'перевозка', 'логистика', 'транспортировка', 'склад'],
            'tourism': ['туризм', 'путешествия', 'отель', 'экскурсии', 'отдых'],
            'legal': ['юридические', 'право', 'адвокат', 'консультация', 'документы'],
            'marketing': ['реклама', 'маркетинг', 'продвижение', 'брендинг', 'SMM'],
            'landscape': ['ландшафт', 'сад', 'озеленение', 'благоустройство', 'дизайн']
        }

    def analyze_theme_intelligence(self, theme: str) -> Dict:
        """Умный анализ тематики с ИИ-подходом"""
        theme_lower = theme.lower()
        words = re.findall(r'\b\w+\b', theme_lower)
        
        # Определяем основную категорию через семантический анализ
        category_scores = {}
        
        for category, keywords in self.semantic_groups.items():
            score = 0
            matched_words = []
            
            for word in words:
                for keyword in keywords:
                    # Умная оценка релевантности
                    if word == keyword:
                        score += 10  # Точное совпадение
                        matched_words.append(word)
                    elif word.startswith(keyword) or keyword.startswith(word):
                        if len(keyword) >= 4:  # Минимальная длина для частичного совпадения
                            score += 7
                            matched_words.append(word)
                    elif keyword in word or word in keyword:
                        if len(min(word, keyword)) >= 4:
                            score += 5
                            matched_words.append(word)
            
            if score > 0:
                category_scores[category] = {
                    'score': score,
                    'matched_words': matched_words,
                    'relevance': score / max(len(words), 1)
                }
        
        # Определяем лучшую категорию
        best_category = 'general'
        best_score = 0
        matched_terms = []
        
        if category_scores:
            best_category = max(category_scores.keys(), key=lambda k: category_scores[k]['score'])
            best_score = category_scores[best_category]['score']
            matched_terms = category_scores[best_category]['matched_words']
        
        # Анализируем специфические подтипы
        subtype = self._detect_subtype(theme_lower, words, best_category)
        
        # Определяем тип бизнеса (продукт/услуга)
        business_type = self._analyze_business_type(theme_lower, words)
        
        return {
            'main_category': best_category,
            'subtype': subtype,
            'business_type': business_type,
            'confidence': min(best_score / 10, 1.0),
            'matched_terms': matched_terms,
            'complexity': len(words),
            'specificity': self._calculate_specificity(theme_lower, words)
        }

    def _detect_subtype(self, theme_lower: str, words: List[str], category: str) -> str:
        """Определяет специфический подтип в категории"""
        
        # Специфические индикаторы подтипов
        subtype_patterns = {
            'automotive': {
                'tire_service': ['шин', 'колес', 'сезонная', 'замена'],
                'car_service': ['ремонт', 'диагностика', 'сервис'],
                'car_sales': ['продажа', 'автосалон', 'дилер'],
                'car_import': ['импорт', 'подбор', 'сша', 'европа']
            },
            'real_estate': {
                'student_housing': ['студент', 'общежитие', 'для студентов'],
                'land_plots': ['участок', 'дача', 'ферма', 'загородный'],
                'short_rental': ['краткосрочная', 'посуточно', 'аренда на'],
                'commercial': ['коммерческая', 'офис', 'торговая']
            },
            'education': {
                'language_courses': ['язык', 'английский', 'французский', 'курсы'],
                'professional_training': ['профессиональное', 'специальность', 'квалификация'],
                'online_courses': ['онлайн', 'дистанционно', 'интернет']
            }
        }
        
        if category in subtype_patterns:
            for subtype, indicators in subtype_patterns[category].items():
                matches = sum(1 for indicator in indicators 
                            for word in words 
                            if indicator in word or word in indicator)
                if matches >= 1:
                    return subtype
        
        return 'general'

    def _analyze_business_type(self, theme_lower: str, words: List[str]) -> str:
        """Анализирует тип бизнеса"""
        
        service_indicators = ['услуг', 'сервис', 'помощь', 'консультация', 'поддержка']
        product_indicators = ['продажа', 'магазин', 'товар', 'покупка']
        
        service_score = sum(1 for indicator in service_indicators 
                          for word in words 
                          if indicator in word)
        
        product_score = sum(1 for indicator in product_indicators 
                          for word in words 
                          if indicator in word)
        
        if product_score > service_score:
            return 'product'
        elif service_score > 0:
            return 'service'
        else:
            return 'mixed'

    def _calculate_specificity(self, theme_lower: str, words: List[str]) -> float:
        """Вычисляет специфичность тематики"""
        
        # Факторы специфичности
        length_factor = min(len(words) / 5, 1.0)  # Длинные темы обычно более специфичны
        compound_factor = len([w for w in words if len(w) > 6]) / max(len(words), 1)
        
        # Специфические термины
        specific_terms = ['профессиональный', 'специализированный', 'эксклюзивный', 'premium']
        specificity_bonus = sum(1 for term in specific_terms if term in theme_lower) * 0.2
        
        return min(length_factor + compound_factor + specificity_bonus, 1.0)

    def generate_intelligent_prompts(self, theme: str) -> Dict[str, str]:
        """Генерирует промпты используя ИИ-анализ"""
        
        analysis = self.analyze_theme_intelligence(theme)
        
        # Генерируем контекстные промпты
        context = self._build_context(analysis, theme)
        
        prompts = {
            'main': self._generate_main_prompt(context, analysis),
            'about1': self._generate_about_prompt(context, analysis, focus='equipment'),
            'about2': self._generate_about_prompt(context, analysis, focus='process'),
            'about3': self._generate_about_prompt(context, analysis, focus='facility'),
            'review1': self._generate_review_prompt(),
            'review2': self._generate_review_prompt(),
            'review3': self._generate_review_prompt(),
            'favicon': self._generate_favicon_prompt(theme)
        }
        
        return prompts

    def _build_context(self, analysis: Dict, theme: str) -> Dict:
        """Строит контекст для генерации"""
        
        category = analysis['main_category']
        subtype = analysis['subtype']
        business_type = analysis['business_type']
        
        # Создаем семантические дескрипторы
        quality_descriptors = self._get_quality_descriptors(analysis['confidence'])
        style_descriptors = self._get_style_descriptors(category, subtype)
        environment_descriptors = self._get_environment_descriptors(business_type)
        
        return {
            'category': category,
            'subtype': subtype,
            'business_type': business_type,
            'quality_level': quality_descriptors,
            'style_elements': style_descriptors,
            'environment': environment_descriptors,
            'specificity': analysis['specificity'],
            'matched_terms': analysis['matched_terms']
        }

    def _get_quality_descriptors(self, confidence: float) -> List[str]:
        """Получает дескрипторы качества основанные на уверенности"""
        
        if confidence >= 0.8:
            return ['professional', 'expert', 'premium', 'high-quality', 'specialized']
        elif confidence >= 0.6:
            return ['professional', 'quality', 'reliable', 'experienced', 'modern']
        else:
            return ['professional', 'quality', 'standard', 'efficient', 'practical']

    def _get_style_descriptors(self, category: str, subtype: str) -> List[str]:
        """Получает стилевые дескрипторы для категории"""
        
        style_map = {
            'automotive': ['modern', 'technical', 'efficient', 'reliable', 'industrial'],
            'real_estate': ['elegant', 'comfortable', 'spacious', 'attractive', 'welcoming'],
            'healthcare': ['clean', 'sterile', 'comfortable', 'caring', 'professional'],
            'education': ['modern', 'interactive', 'engaging', 'supportive', 'innovative'],
            'food': ['appetizing', 'fresh', 'delicious', 'hygienic', 'inviting'],
            'beauty': ['elegant', 'luxurious', 'relaxing', 'stylish', 'sophisticated'],
            'finance': ['trustworthy', 'secure', 'professional', 'confident', 'prestigious'],
            'technology': ['innovative', 'cutting-edge', 'efficient', 'smart', 'advanced'],
            'construction': ['solid', 'precise', 'durable', 'skilled', 'organized'],
            'landscape': ['beautiful', 'natural', 'creative', 'harmonious', 'artistic']
        }
        
        return style_map.get(category, ['professional', 'quality', 'modern', 'efficient'])

    def _get_environment_descriptors(self, business_type: str) -> List[str]:
        """Получает дескрипторы среды для типа бизнеса"""
        
        environment_map = {
            'service': ['office', 'consultation room', 'service center', 'workspace', 'facility'],
            'product': ['showroom', 'store', 'warehouse', 'display area', 'retail space'],
            'mixed': ['business center', 'facility', 'office space', 'commercial area', 'workplace']
        }
        
        return environment_map.get(business_type, ['professional environment'])

    def _generate_main_prompt(self, context: Dict, analysis: Dict) -> str:
        """Генерирует основной промпт"""
        
        # Выбираем базовые элементы
        quality = random.choice(context['quality_level'])
        style = random.choice(context['style_elements'])
        environment = random.choice(context['environment'])
        
        # Строим промпт на основе анализа
        if analysis['specificity'] > 0.7:
            # Высоко специфичные темы
            if context['subtype'] != 'general':
                prompt = f"{quality} {context['subtype']} {style} {environment} with expert team and modern equipment"
            else:
                prompt = f"{quality} {context['category']} {style} {environment} showcasing expertise and quality service"
        else:
            # Общие темы
            prompt = f"{quality} {context['category']} {style} {environment} with professional team and modern facilities"
        
        return prompt

    def _generate_about_prompt(self, context: Dict, analysis: Dict, focus: str) -> str:
        """Генерирует промпт для секции about"""
        
        quality = random.choice(context['quality_level'])
        style = random.choice(context['style_elements'])
        
        focus_elements = {
            'equipment': ['equipment', 'tools', 'technology', 'instruments', 'systems'],
            'process': ['process', 'workflow', 'methodology', 'approach', 'procedure'],
            'facility': ['facility', 'environment', 'workspace', 'center', 'location']
        }
        
        focus_element = random.choice(focus_elements[focus])
        
        if context['subtype'] != 'general':
            prompt = f"{quality} {context['subtype']} {focus_element} with {style} design and professional standards"
        else:
            prompt = f"{quality} {context['category']} {focus_element} with {style} approach and expert operation"
        
        return prompt

    def _generate_review_prompt(self) -> str:
        """Генерирует промпт для отзыва (фокус на людях)"""
        
        person_types = [
            "happy customer", "satisfied client", "pleased woman", "smiling man",
            "grateful person", "content customer", "cheerful client", "positive person"
        ]
        
        ages = [
            "young adult", "middle-aged person", "mature adult", "30-40 years old",
            "25-35 years old", "40-50 years old", "adult person"
        ]
        
        expressions = [
            "genuine smile", "happy expression", "satisfied look", "positive facial expression",
            "natural smile", "pleased appearance", "grateful expression", "bright smile"
        ]
        
        backgrounds = [
            "clean background", "neutral background", "simple background", "professional background"
        ]
        
        person = random.choice(person_types)
        age = random.choice(ages)
        expression = random.choice(expressions)
        background = random.choice(backgrounds)
        
        return f"portrait photo of {person}, {age}, {expression}, HUMAN FACE ONLY, NO OBJECTS, civilian clothes, {background}"

    def _generate_favicon_prompt(self, theme: str) -> str:
        """Генерирует промпт для фавиконки"""
        return f"{theme} icon symbol, simple minimalist logo, business emblem"


def create_ai_prompts(theme: str) -> Dict[str, str]:
    """Основная функция для создания ИИ-промптов"""
    generator = AIPromptGenerator()
    return generator.generate_intelligent_prompts(theme) 