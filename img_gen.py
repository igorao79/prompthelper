import requests
import datetime
import os
from PIL import Image, ImageDraw
from io import BytesIO
import json
import time
import random
import uuid
import re
from urllib.parse import quote
from pathlib import Path

class IntelligentContextAnalyzer:
    """Умный анализатор контекста бизнеса с использованием интернета"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.cache = {}  # Кэш для результатов поиска
        
    def search_business_context(self, query):
        """Поиск информации о бизнесе в интернете"""
        try:
            if not self.silent_mode:
                print(f"🔍 Ищу информацию о: {query}")
            
            # Проверяем кэш
            if query in self.cache:
                if not self.silent_mode:
                    print("📋 Использую кэшированные данные")
                return self.cache[query]
            
            # Улучшенные поисковые запросы
            search_queries = [
                f"{query} услуги бизнес",
                f"{query} деятельность",
                f"{query} что это",
                query  # Оригинальный запрос
            ]
            
            # Пробуем разные запросы
            best_context = None
            for search_query in search_queries:
                context_data = self._multi_source_search(search_query)
                
                # Берем первый успешный результат
                if context_data and context_data.get('confidence', 0) > 0.5:
                    best_context = context_data
                    break
            
            # Если не нашли хорошего результата, используем первый доступный
            if not best_context:
                best_context = self._multi_source_search(search_queries[0])
            
            # Если все еще нет результата, используем fallback
            if not best_context:
                best_context = self._dynamic_fallback_analysis(query)
            
            # Сохраняем в кэш
            self.cache[query] = best_context
            
            return best_context
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка поиска: {e}")
            return self._dynamic_fallback_analysis(query)
    
    def _multi_source_search(self, query):
        """Поиск по нескольким источникам"""
        sources_data = []
        
        # 1. Поиск через DuckDuckGo
        duckduck_data = self._search_duckduckgo(query)
        if duckduck_data:
            sources_data.extend(duckduck_data)
        
        # 2. Поиск в Wikipedia
        wiki_data = self._search_wikipedia(query)
        if wiki_data:
            sources_data.append(wiki_data)
        
        # Анализируем собранные данные
        return self._analyze_search_results(sources_data, query)
    
    def _search_duckduckgo(self, query):
        """Поиск через DuckDuckGo API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # Обрабатываем 200 и 202 статусы
            if response.status_code in [200, 202]:
                data = response.json()
                
                results = []
                
                # Основной ответ
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', ''),
                        'description': data.get('Abstract', ''),
                        'source': 'DuckDuckGo Abstract'
                    })
                
                # Связанные темы
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('FirstURL', '').split('/')[-1],
                            'description': topic.get('Text', ''),
                            'source': 'DuckDuckGo Related'
                        })
                
                # Определения из Answer
                if data.get('Answer'):
                    results.append({
                        'title': 'Definition',
                        'description': data.get('Answer', ''),
                        'source': 'DuckDuckGo Answer'
                    })
                
                if not self.silent_mode and results:
                    print(f"✅ DuckDuckGo найдено {len(results)} результатов")
                elif not self.silent_mode:
                    print(f"⚠️ DuckDuckGo не вернул данных (статус {response.status_code})")
                
                return results if results else None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка DuckDuckGo: {e}")
            return None
    
    def _search_wikipedia(self, query):
        """Поиск в Wikipedia"""
        try:
            # Сначала ищем статьи по запросу
            search_url = "https://ru.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 3,
                'srprop': 'snippet'
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                search_results = search_data.get('query', {}).get('search', [])
                
                if search_results:
                    # Берем первый результат и получаем его содержимое
                    first_result = search_results[0]
                    page_title = first_result.get('title', '')
                    
                    # Получаем краткое содержание страницы
                    content_url = "https://ru.wikipedia.org/api/rest_v1/page/summary/" + quote(page_title)
                    content_response = requests.get(content_url, timeout=10)
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        
                        if not self.silent_mode:
                            print(f"✅ Wikipedia найдена статья: {page_title}")
                        
                        return {
                            'title': content_data.get('title', page_title),
                            'description': content_data.get('extract', first_result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')),
                            'source': 'Wikipedia'
                        }
                    else:
                        # Если не удалось получить содержимое, используем snippet
                        if not self.silent_mode:
                            print(f"⚠️ Wikipedia: использую snippet для {page_title}")
                        
                        return {
                            'title': page_title,
                            'description': first_result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
                            'source': 'Wikipedia'
                        }
                else:
                    if not self.silent_mode:
                        print(f"⚠️ Wikipedia: статьи не найдены для '{query}'")
                    return None
            else:
                if not self.silent_mode:
                    print(f"⚠️ Wikipedia поиск ошибка: {search_response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка Wikipedia: {e}")
            return None
    
    def _analyze_search_results(self, sources_data, original_query):
        """Анализ результатов поиска для определения контекста"""
        if not sources_data:
            return self._dynamic_fallback_analysis(original_query)
        
        # Собираем весь текст для анализа
        combined_text = ""
        for source in sources_data:
            combined_text += f" {source.get('title', '')} {source.get('description', '')}"
        
        # ПРОВЕРЯЕМ РЕЛЕВАНТНОСТЬ найденной информации
        relevance_score = self._check_content_relevance(combined_text, original_query)
        
        if relevance_score < 0.3:  # Если релевантность низкая
            if not self.silent_mode:
                print(f"⚠️ Найденная информация не релевантна (score: {relevance_score:.2f})")
                print(f"🔄 Переключаюсь на локальный анализ")
            return self._dynamic_fallback_analysis(original_query)
        
        # Динамический анализ на основе найденной информации
        context = self._dynamic_context_extraction(combined_text, original_query)
        
        # Повышаем confidence если информация релевантна
        context['confidence'] = min(context['confidence'] + (relevance_score * 0.3), 0.9)
        
        if not self.silent_mode:
            print(f"📊 Найдено источников: {len(sources_data)}")
            print(f"✅ Релевантность: {relevance_score:.2f}")
            print(f"🎯 Определен тип бизнеса: {context['business_type']}")
            print(f"🏢 Среда: {context['environment']}")
        
        return context
    
    def _check_content_relevance(self, found_text, original_query):
        """Проверяет релевантность найденного контента к исходному запросу"""
        found_text_lower = found_text.lower()
        query_words = original_query.lower().split()
        
        # Подсчитываем сколько слов из запроса встречается в найденном тексте
        found_words = 0
        total_query_words = len([w for w in query_words if len(w) > 2])  # Слова длиннее 2 символов
        
        for word in query_words:
            if len(word) > 2 and word in found_text_lower:
                found_words += 1
        
        # Базовая релевантность по словам
        word_relevance = found_words / max(total_query_words, 1) if total_query_words > 0 else 0
        
        # Дополнительная проверка на тематические маркеры
        theme_markers = {
            'кулинар': ['кулинар', 'повар', 'готовк', 'еда', 'блюд', 'рецепт', 'кухн'],
            'авто': ['авто', 'машин', 'транспорт', 'двигател', 'ремонт', 'диагностика'],
            'стоматолог': ['стоматолог', 'зуб', 'стоматология', 'медицин', 'врач'],
            'детск': ['детск', 'дети', 'ребен', 'воспитан', 'игр'],
            'фото': ['фото', 'съемк', 'камер', 'изображен'],
            'курс': ['курс', 'обучен', 'учеб', 'образован', 'школ']
        }
        
        theme_bonus = 0
        for key_word in query_words:
            if key_word in theme_markers:
                theme_words = theme_markers[key_word]
                theme_matches = sum(1 for theme_word in theme_words if theme_word in found_text_lower)
                if theme_matches > 0:
                    theme_bonus += 0.2
        
        final_relevance = min(word_relevance + theme_bonus, 1.0)
        return final_relevance
    
    def _dynamic_context_extraction(self, text, query):
        """Динамическое извлечение контекста из текста без фиксированных категорий"""
        text_lower = text.lower()
        query_lower = query.lower()
        combined_text = f"{text_lower} {query_lower}".strip()
        
        # Анализируем ключевые слова для определения типа деятельности
        activity_indicators = {
            'education': ['курсы', 'обучение', 'школа', 'учеба', 'преподавание', 'изучение', 'образование', 'учитель', 'ученик'],
            'service': ['услуги', 'сервис', 'обслуживание', 'консультация', 'помощь', 'ремонт', 'мастер', 'починка'],
            'medical': ['медицин', 'здоровье', 'лечение', 'диагностика', 'клиника', 'врач', 'стоматолог', 'зубы', 'больн'],
            'automotive': ['авто', 'машин', 'автомобил', 'транспорт', 'автосервис', 'двигател'],
            'food': ['кулинар', 'еда', 'готовк', 'повар', 'ресторан', 'кафе', 'питание', 'блюд', 'кухн'],
            'beauty': ['красота', 'салон', 'косметол', 'парикмахер', 'маникюр', 'стрижк', 'прическ'],
            'fitness': ['фитнес', 'спорт', 'тренировк', 'тренер', 'спортзал', 'физкультур'],
            'tech': ['технолог', 'компьютер', 'программир', 'сайт', 'веб', 'it', 'софт'],
            'art': ['искусств', 'творчеств', 'художеств', 'дизайн', 'рисован', 'картин'],
            'music': ['музык', 'инструмент', 'песн', 'концерт', 'пиани', 'гитар'],
            'photography': ['фото', 'съемк', 'камер', 'фотограф'],
            'construction': ['строител', 'стройк', 'отделк', 'монтаж'],
            'childcare': ['детск', 'сад', 'дети', 'ребенок', 'воспитан', 'игровая'],
            'appliance_repair': ['холодильник', 'стиральн', 'техник', 'бытовая', 'электроприбор']
        }
        
        # Определяем основной тип деятельности
        activity_scores = {}
        for activity, keywords in activity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                activity_scores[activity] = score
        
        main_activity = max(activity_scores.keys(), key=lambda k: activity_scores[k]) if activity_scores else 'general'
        
        # Извлекаем конкретные детали из текста
        details = self._extract_dynamic_details(combined_text, query_lower)
        
        # Определяем среду на основе контекста
        environment = self._determine_dynamic_environment(main_activity, details, query_lower)
        
        # Определяем специфичность темы
        specificity = self._calculate_specificity(query_lower, details)
        
        return {
            'category': 'dynamic_business',  # Единая категория
            'business_type': main_activity,
            'confidence': min(0.3 + specificity * 0.4, 0.9),
            'details': details[:5],
            'keywords': self._extract_smart_keywords(combined_text, query_lower),
            'environment': environment,
            'theme_description': self._generate_theme_description(main_activity, details, query_lower)
        }
    
    def _extract_dynamic_details(self, text, query):
        """Извлекает конкретные детали из текста и запроса"""
        import re
        
        # Простое извлечение значимых слов
        words = re.findall(r'\b[а-яё]{3,}\b', text + " " + query)
        
        # Фильтруем служебные слова
        stop_words = {
            'услуги', 'сервис', 'компания', 'организация', 'предприятие', 
            'деятельность', 'работа', 'бизнес', 'центр', 'группа'
        }
        
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Возвращаем наиболее частые и длинные слова
        word_scores = {}
        for word in meaningful_words:
            score = len(word) + meaningful_words.count(word) * 2
            word_scores[word] = score
        
        return sorted(word_scores.keys(), key=lambda w: word_scores[w], reverse=True)[:5]
    
    def _determine_dynamic_environment(self, activity, details, query):
        """Динамически определяет среду на основе анализа"""
        # Базовые среды для типов деятельности
        base_environments = {
            'education': 'educational facility',
            'service': 'service center',
            'medical': 'medical facility', 
            'automotive': 'automotive facility',
            'food': 'culinary environment',
            'beauty': 'beauty salon',
            'fitness': 'fitness facility',
            'tech': 'modern office',
            'art': 'creative studio',
            'music': 'music studio',
            'photography': 'photography studio',
            'construction': 'construction site',
            'childcare': 'kindergarten classroom',
            'appliance_repair': 'technical service workshop'
        }
        
        base_env = base_environments.get(activity, 'professional office')
        
        # Уточняем среду на основе деталей
        if 'кулинар' in query and 'курс' in query:
            return 'professional culinary school kitchen'
        elif 'фото' in query and ('курс' in query or 'обучен' in query):
            return 'photography studio with professional equipment'
        elif 'музык' in query and 'курс' in query:
            return 'music studio with instruments'
        elif 'автосервис' in query or 'ремонт авто' in query:
            return 'automotive service garage'
        elif 'автосалон' in query:
            return 'car dealership showroom'
        
        return base_env
    
    def _calculate_specificity(self, query, details):
        """Вычисляет специфичность темы"""
        # Чем больше деталей и длиннее запрос, тем выше специфичность
        query_words = len(query.split())
        detail_count = len([d for d in details if len(d) > 3])
        
        specificity = (query_words * 0.1) + (detail_count * 0.15)
        return min(specificity, 1.0)
    
    def _extract_smart_keywords(self, text, query):
        """Умное извлечение ключевых слов"""
        import re
        
        # Объединяем текст и запрос
        all_text = f"{text} {query}"
        
        # Извлекаем слова длиной от 3 символов
        words = re.findall(r'\b[а-яё]{3,}\b', all_text.lower())
        
        # Подсчитываем частоту
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Возвращаем наиболее частые слова
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:8]]
    
    def _generate_theme_description(self, activity, details, query):
        """Генерирует описание темы для промптов"""
        if not details:
            return query
        
        # Создаем описание на основе деталей
        main_detail = details[0] if details else activity
        secondary_details = details[1:3] if len(details) > 1 else []
        
        if secondary_details:
            return f"{main_detail} {' '.join(secondary_details)}"
        else:
            return main_detail
    
    def _dynamic_fallback_analysis(self, query):
        """Динамический fallback анализ без интернета"""
        query_lower = query.lower()
        
        if not self.silent_mode:
            print(f"💪 Локальный анализ (точное определение)")
        
        # Улучшенный анализ на основе запроса пользователя
        details = self._extract_fallback_details(query_lower)
        
        # ТОЧНОЕ определение тематики и среды
        activity, environment = self._precise_theme_detection(query_lower)
        
        # Генерируем качественное описание темы
        theme_description = self._generate_precise_description(query_lower, activity)
        
        return {
            'category': 'dynamic_business',
            'business_type': activity,
            'confidence': 0.8,  # Высокая уверенность для точного локального анализа
            'details': details,
            'keywords': query.split()[:5],
            'environment': environment,
            'theme_description': theme_description
        }
    
    def _precise_theme_detection(self, query_lower):
        """Точное определение тематики и среды"""
        
        # Специфические комбинации с высоким приоритетом
        if 'кулинар' in query_lower and 'курс' in query_lower:
            return 'food', 'professional culinary school kitchen'
        elif 'фото' in query_lower and 'курс' in query_lower:
            return 'photography', 'photography studio classroom'
        elif 'музык' in query_lower and 'курс' in query_lower:
            return 'music', 'music education studio'
        elif 'диагностика' in query_lower and 'авто' in query_lower:
            return 'automotive', 'automotive diagnostic center'
        elif 'ремонт' in query_lower and 'авто' in query_lower:
            return 'automotive', 'automotive repair workshop'
        elif 'детск' in query_lower and 'сад' in query_lower:
            return 'childcare', 'bright kindergarten classroom'
        elif 'стоматолог' in query_lower or 'стоматология' in query_lower:
            return 'medical', 'modern dental clinic'
        elif 'ремонт' in query_lower and 'холодильник' in query_lower:
            return 'appliance_repair', 'appliance repair workshop'
        
        # Основные категории
        elif any(word in query_lower for word in ['кулинар', 'повар', 'готовк', 'кухн']):
            return 'food', 'professional kitchen'
        elif any(word in query_lower for word in ['фото', 'съемк', 'камер']):
            return 'photography', 'photography studio'
        elif any(word in query_lower for word in ['музык', 'инструмент']):
            return 'music', 'music studio'
        elif any(word in query_lower for word in ['авто', 'автосервис', 'машин']):
            return 'automotive', 'automotive service center'
        elif any(word in query_lower for word in ['стоматолог', 'зубы']):
            return 'medical', 'dental office'
        elif any(word in query_lower for word in ['детск', 'дети', 'ребен']):
            return 'childcare', 'children activity center'
        elif any(word in query_lower for word in ['курс', 'обучен', 'школа', 'учеб']):
            return 'education', 'modern classroom'
        elif any(word in query_lower for word in ['ремонт', 'мастер', 'починка']):
            return 'service', 'professional service workshop'
        elif any(word in query_lower for word in ['красота', 'салон', 'парикмахер']):
            return 'beauty', 'modern beauty salon'
        elif any(word in query_lower for word in ['фитнес', 'спорт', 'тренер']):
            return 'fitness', 'modern fitness center'
        else:
            return 'service', 'professional business office'
    
    def _generate_precise_description(self, query_lower, activity):
        """Генерирует точное описание темы"""
        
        # Извлекаем ключевые слова
        words = query_lower.split()
        main_words = [w for w in words if len(w) > 3][:2]
        
        if main_words:
            return ' '.join(main_words)
        else:
            # Базовые описания по типу деятельности
            descriptions = {
                'food': 'кулинарные услуги',
                'photography': 'фотографические услуги', 
                'music': 'музыкальные занятия',
                'automotive': 'автомобильные услуги',
                'medical': 'медицинские услуги',
                'childcare': 'детские услуги',
                'education': 'образовательные услуги',
                'service': 'профессиональные услуги',
                'beauty': 'косметические услуги',
                'fitness': 'фитнес услуги'
            }
            return descriptions.get(activity, 'бизнес услуги')
    
    def _extract_fallback_details(self, query):
        """Извлекает детали из запроса для fallback анализа"""
        import re
        
        # Простое извлечение значимых слов
        words = re.findall(r'\b[а-яё]{3,}\b', query)
        
        # Фильтруем служебные слова
        stop_words = {
            'услуги', 'сервис', 'компания', 'организация', 'предприятие', 
            'деятельность', 'работа', 'бизнес', 'центр', 'группа', 'описание'
        }
        
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Возвращаем наиболее длинные слова
        return sorted(meaningful_words, key=len, reverse=True)[:3]

class ThematicImageGenerator:
    def __init__(self, silent_mode=False):
        """
        Умный генератор тематических изображений для лендингов
        
        Args:
            silent_mode (bool): Если True, не выводит сообщения в консоль
        """
        self.silent_mode = silent_mode
        self.context_analyzer = IntelligentContextAnalyzer(silent_mode)
        
        if not self.silent_mode:
            print("🎨 AI Генератор Тематических Изображений для Лендингов")
            print("=" * 60)
            print("✨ Умная генерация изображений с динамическим анализом через интернет")

    def detect_theme_from_input(self, user_input):
        """Определяет тематику с помощью интернет-поиска"""
        context_data = self.context_analyzer.search_business_context(user_input)
        return context_data['business_type'], context_data

    def generate_intelligent_prompts(self, context_data, original_input):
        """Динамическая генерация промптов на основе интернет-анализа"""
        
        business_type = context_data.get('business_type', 'general')
        environment = context_data['environment']
        details = context_data['details']
        keywords = context_data['keywords']
        theme_description = context_data.get('theme_description', original_input)
        
        # Динамическая генерация промптов на основе типа деятельности и среды
        return self._generate_dynamic_prompts(business_type, environment, details, keywords, theme_description, original_input)
    
    def _generate_dynamic_prompts(self, business_type, environment, details, keywords, theme_description, original_input):
        """Генерирует промпты динамически на основе анализа"""
        
        # Используем правильные термины для промптов
        clean_theme = theme_description if theme_description else original_input
        
        # СПЕЦИАЛЬНЫЕ промпты для конкретных тематик
        if 'кулинар' in original_input.lower() and 'курс' in original_input.lower():
            return self._generate_culinary_course_prompts()
        elif 'фото' in original_input.lower() and 'курс' in original_input.lower():
            return self._generate_photography_course_prompts()
        elif 'диагностика' in original_input.lower() and 'авто' in original_input.lower():
            return self._generate_auto_diagnostic_prompts()
        elif 'стоматолог' in original_input.lower() or 'стоматология' in original_input.lower():
            return self._generate_dental_prompts()
        elif 'детск' in original_input.lower() and 'сад' in original_input.lower():
            return self._generate_kindergarten_prompts()
        
        # ОБЩИЕ промпты для остальных тематик
        return self._generate_general_business_prompts(business_type, environment, clean_theme)
    
    def _generate_culinary_course_prompts(self):
        """Специальные промпты для кулинарных курсов"""
        return {
            "main": "professional culinary school kitchen, chef instructor teaching cooking techniques, students learning culinary arts",
            "about1": "professional chef demonstrating cooking techniques, culinary education in action, hands-on cooking instruction",
            "about2": "modern culinary school kitchen equipment, professional cooking tools and appliances, culinary training facility",
            "about3": "culinary consultation and course planning, chef discussing recipes with students, cooking class planning",
            "review1": "satisfied student after completing cooking course, successful culinary education experience, happy cook",
            "review2": "professional culinary instructor, expert cooking teacher, satisfied cooking course graduate",
            "review3": "group of happy cooking course graduates, successful culinary education stories, cooking skills achievement",
            "favicon": "chef hat icon, culinary education symbol, cooking course logo, professional culinary design"
        }
    
    def _generate_photography_course_prompts(self):
        """Специальные промпты для фотокурсов"""
        return {
            "main": "photography studio classroom, professional photographer teaching camera techniques, students learning photography",
            "about1": "photography instructor demonstrating camera settings, hands-on photography education, professional photo training",
            "about2": "professional photography studio equipment, cameras and lighting setup, photography education facility",
            "about3": "photography consultation and course planning, instructor discussing techniques with students, photo class planning",
            "review1": "satisfied student after photography course completion, successful photo education experience, happy photographer",
            "review2": "professional photography instructor, expert photo teacher, satisfied photography course graduate",
            "review3": "group of happy photography graduates, successful photo education stories, photography skills achievement",
            "favicon": "camera icon, photography education symbol, photo course logo, professional photography design"
        }
    
    def _generate_auto_diagnostic_prompts(self):
        """Специальные промпты для автодиагностики"""
        return {
            "main": "professional automotive diagnostic center, mechanic using diagnostic equipment, car engine analysis",
            "about1": "automotive technician performing car diagnostics, professional vehicle inspection, expert mechanic at work",
            "about2": "modern automotive diagnostic equipment, professional car diagnostic tools, auto service facility",
            "about3": "automotive consultation and diagnosis explanation, mechanic discussing car issues with client, vehicle service planning",
            "review1": "satisfied customer after car diagnostic service, successful vehicle repair experience, happy car owner",
            "review2": "professional automotive diagnostic specialist, expert car mechanic, satisfied auto service client",
            "review3": "group of satisfied auto service customers, successful car repair stories, automotive service satisfaction",
            "favicon": "car diagnostic icon, automotive service symbol, vehicle inspection logo, professional auto design"
        }
    
    def _generate_dental_prompts(self):
        """Специальные промпты для стоматологии"""
        return {
            "main": "modern dental clinic, professional dentist examining patient, clean dental office environment",
            "about1": "dentist performing dental examination, professional dental care, expert dentist at work",
            "about2": "modern dental equipment and tools, professional dental office setup, dental clinic facility",
            "about3": "dental consultation and treatment planning, dentist discussing treatment with patient, dental care planning",
            "review1": "satisfied patient after dental treatment, successful dental care experience, happy smile",
            "review2": "professional dentist, expert dental specialist, satisfied dental patient",
            "review3": "group of satisfied dental patients, successful dental treatment stories, dental care satisfaction",
            "favicon": "tooth icon, dental care symbol, dentist logo, professional dental design"
        }
    
    def _generate_kindergarten_prompts(self):
        """Специальные промпты для детского сада"""
        return {
            "main": "bright kindergarten classroom, children playing and learning, professional childcare environment",
            "about1": "kindergarten teacher with children, educational play activities, professional childcare in action",
            "about2": "colorful kindergarten classroom with toys and learning materials, children's educational environment",
            "about3": "parent consultation at kindergarten, discussing child development with teachers, childcare planning",
            "review1": "happy child enjoying kindergarten activities, successful early education experience, joyful learning",
            "review2": "satisfied parent and happy child, professional kindergarten teacher, quality childcare service",
            "review3": "group of happy children and parents, successful kindergarten stories, quality early education",
            "favicon": "children icon, kindergarten symbol, childcare logo, professional early education design"
        }
    
    def _generate_general_business_prompts(self, business_type, environment, theme):
        """Общие промпты для любого бизнеса"""
        return {
            "main": f"{environment}, professional {business_type} service, expert specialist at work",
            "about1": f"professional {business_type} specialist providing service, expert working with client, quality service delivery",
            "about2": f"{environment} with professional equipment, {business_type} workspace setup, service facility",
            "about3": f"{theme} consultation area, client meeting with specialist, professional service planning",
            "review1": f"satisfied customer after {business_type} service, successful {theme} experience, happy client",
            "review2": f"professional {business_type} specialist, expert service provider, satisfied customer testimonial",
            "review3": f"group of happy customers, successful {theme} stories, positive service reviews",
            "favicon": f"{business_type} icon, professional service symbol, business logo design"
        }

    def get_theme_prompts(self, theme_input):
        """Получает промпты с использованием интернет-анализа"""
        detected_theme, context_data = self.detect_theme_from_input(theme_input)
        
        if not self.silent_mode:
            print(f"🎯 Определена категория: {detected_theme}")
            print(f"📊 Уверенность: {context_data['confidence']:.2f}")
            print(f"🔍 Детали: {', '.join(context_data['details'])}")
            print(f"🏢 Среда: {context_data['environment']}")
        
        prompts = self.generate_intelligent_prompts(context_data, theme_input)
        return prompts, detected_theme

    def add_randomization(self, prompt):
        """Добавляет случайные элементы к промпту для уникальности"""
        
        # Случайные стили и характеристики
        styles = [
            "natural lighting", "soft lighting", "bright ambient", "professional lighting"
        ]
        
        # Случайные ракурсы
        angles = [
            "wide angle shot", "medium shot", "close-up view", "establishing shot", 
            "straight on", "professional angle"
        ]
        
        # Случайные детали интерьера/экстерьера
        details = [
            "modern furniture", "elegant decor", "contemporary design", "minimalist style",
            "professional setup", "clean lines", "stylish arrangement"
        ]
        
        # Добавляем случайные элементы (убрали цветовые схемы)
        selected_style = random.choice(styles)
        selected_angle = random.choice(angles)
        selected_detail = random.choice(details)
        
        # Генерируем уникальный seed для дополнительной рандомизации
        unique_seed = str(uuid.uuid4())[:8]
        
        enhanced_prompt = f"{prompt}, {selected_style}, {selected_angle}, {selected_detail}, seed:{unique_seed}"
        
        return enhanced_prompt

    def add_favicon_randomization(self, prompt):
        """Добавляет специальную рандомизацию для фавиконок"""
        
        # Стили иконок
        icon_styles = [
            "minimalist icon", "modern flat icon", "geometric icon", "abstract icon",
            "stylized icon", "contemporary icon", "sleek icon", "professional icon"
        ]
        
        # Варианты дизайна
        design_variants = [
            "circular design", "square design", "rounded square", "hexagonal shape",
            "shield shape", "badge style", "emblem style", "logo mark"
        ]
        
        # Визуальные эффекты для иконок
        visual_effects = [
            "subtle gradient", "solid colors", "duo-tone", "monochrome",
            "outlined style", "filled style", "negative space", "geometric patterns"
        ]
        
        # Композиционные варианты
        compositions = [
            "centered composition", "balanced layout", "symmetrical design", "dynamic arrangement",
            "focused element", "simplified form", "clean structure", "bold design"
        ]
        
        # Выбираем случайные элементы
        selected_style = random.choice(icon_styles)
        selected_design = random.choice(design_variants)
        selected_effect = random.choice(visual_effects)
        selected_composition = random.choice(compositions)
        
        # Генерируем уникальный seed
        unique_seed = str(uuid.uuid4())[:8]
        
        enhanced_prompt = f"{prompt}, {selected_style}, {selected_design}, {selected_effect}, {selected_composition}, seed:{unique_seed}"
        
        return enhanced_prompt

class ImageGenerator:
    def __init__(self, silent_mode=False, use_icons8_for_favicons=True):
        """
        Простой и надежный генератор изображений без вотермарков
        
        Args:
            silent_mode (bool): Если True, не выводит сообщения в консоль
            use_icons8_for_favicons (bool): Использовать Icons8 для фавиконок
        """
        self.silent_mode = silent_mode
        self.use_icons8_for_favicons = use_icons8_for_favicons
        
        # Инициализируем Icons8 Manager если нужно
        self.icons8_manager = None
        if self.use_icons8_for_favicons:
            try:
                from icons8_api import Icons8Manager
                self.icons8_manager = Icons8Manager(silent_mode=True)
                if not silent_mode:
                    print("🎯 Icons8 Manager подключен для фавиконок")
            except ImportError:
                if not silent_mode:
                    print("⚠️ Icons8 API недоступен, используется AI генерация")
                self.use_icons8_for_favicons = False
        
        if not silent_mode:
            print("🎨 AI Генератор Изображений")
            print("=" * 50)
            print("✨ Высококачественные изображения без вотермарков")
            if self.use_icons8_for_favicons:
                print("🎯 Icons8 интегрирован для фавиконок")
        
    def remove_watermark(self, image):
        """Удаляет вотермарк снизу изображения"""
        try:
            width, height = image.size
            
            # Обрезаем нижние 30 пикселей где обычно вотермарк
            cropped_height = height - 30
            cropped_image = image.crop((0, 0, width, cropped_height))
            
            # Растягиваем обратно до оригинального размера
            final_image = cropped_image.resize((width, height), Image.Resampling.LANCZOS)
            
            return final_image
        except:
            return image
    
    def make_favicon_transparent(self, image):
        """Делает фавиконку прозрачной с использованием продвинутого алгоритма"""
        try:
            # Пытаемся использовать продвинутый процессор
            try:
                from favicon_processor import AdvancedFaviconProcessor
                processor = AdvancedFaviconProcessor(silent_mode=True)
                
                # Сохраняем временно
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name)
                    
                    # Обрабатываем
                    processed = processor._advanced_background_removal(image)
                    if processed:
                        if not self.silent_mode:
                            print("🎨 Применен продвинутый алгоритм удаления фона")
                        return processed
                    
            except ImportError:
                if not self.silent_mode:
                    print("⚠️ Продвинутый процессор недоступен, используется базовый алгоритм")
            
            # Базовый алгоритм (улучшенный)
            return self._basic_background_removal(image)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка при создании прозрачности: {e}")
            return image
    
    def _basic_background_removal(self, image):
        """Базовый улучшенный алгоритм удаления фона"""
        try:
            # Конвертируем в RGBA если нужно
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Получаем данные пикселей
            data = image.getdata()
            width, height = image.size
            
            # Анализируем края изображения более тщательно
            edge_pixels = []
            
            # Собираем больше пикселей с краев
            edge_sample_size = max(5, min(width, height) // 20)
            
            # Верхний и нижний края
            for x in range(0, width, max(1, width//edge_sample_size)):
                edge_pixels.append(image.getpixel((x, 0)))
                edge_pixels.append(image.getpixel((x, height-1)))
            
            # Левый и правый края  
            for y in range(0, height, max(1, height//edge_sample_size)):
                edge_pixels.append(image.getpixel((0, y)))
                edge_pixels.append(image.getpixel((width-1, y)))
            
            # Определяем наиболее вероятный цвет фона
            bg_color = self._find_background_color(edge_pixels)
            
            if not bg_color:
                if not self.silent_mode:
                    print("🎨 Фон не обнаружен, прозрачность не применена")
                return image
            
            # Создаем новые данные с прозрачным фоном
            new_data = []
            pixels_made_transparent = 0
            
            for item in data:
                if self._is_background_pixel_improved(item, bg_color):
                    new_data.append((255, 255, 255, 0))  # Прозрачный
                    pixels_made_transparent += 1
                else:
                    new_data.append(item)  # Оставляем как есть
            
            # Проверяем разумность удаления
            total_pixels = len(data)
            transparency_ratio = pixels_made_transparent / total_pixels
            
            if transparency_ratio > 0.8:  # Повысили лимит
                if not self.silent_mode:
                    print(f"🚫 Слишком много пикселей для удаления ({transparency_ratio:.1%}), прозрачность не применена")
                return image
            
            # Применяем новые данные
            image.putdata(new_data)
            
            if not self.silent_mode:
                print(f"🎨 Удален фон RGB{bg_color}, прозрачных пикселей: {transparency_ratio:.1%}")
            
            return image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка базового удаления фона: {e}")
            return image
    
    def _find_background_color(self, pixels):
        """Находит цвет фона из пикселей краев"""
        # Фильтруем только светлые пиксели
        light_pixels = []
        for pixel in pixels:
            if len(pixel) >= 3:
                r, g, b = pixel[0], pixel[1], pixel[2]
                # Расширили диапазон для лучшего определения
                if r > 220 and g > 220 and b > 220:
                    light_pixels.append((r, g, b))
        
        if not light_pixels:
            return None
        
        # Группируем похожие цвета
        color_groups = {}
        for color in light_pixels:
            # Округляем до групп по 15
            group_key = (
                (color[0] // 15) * 15,
                (color[1] // 15) * 15,
                (color[2] // 15) * 15
            )
            color_groups[group_key] = color_groups.get(group_key, 0) + 1
        
        if not color_groups:
            return None
        
        # Возвращаем самую частую группу
        return max(color_groups.keys(), key=lambda k: color_groups[k])
    
    def _is_background_pixel_improved(self, pixel, bg_color, tolerance=30):
        """Улучшенная проверка фонового пикселя"""
        if len(pixel) < 3 or not bg_color:
            return False
        
        r, g, b = pixel[0], pixel[1], pixel[2]
        bg_r, bg_g, bg_b = bg_color[0], bg_color[1], bg_color[2]
        
        # Проверяем близость цветов
        distance = ((r - bg_r) ** 2 + (g - bg_g) ** 2 + (b - bg_b) ** 2) ** 0.5
        
        # Дополнительная проверка на светлость
        is_light = r > 210 and g > 210 and b > 210
        
        return distance <= tolerance and is_light
        
    def translate_prompt(self, russian_prompt: str):
        """Простой перевод промпта на английский"""
        translations = {
            "кот": "cat", "котенок": "kitten", "котеночек": "cute kitten",
            "собака": "dog", "щенок": "puppy", "песик": "dog",
            "закат": "sunset", "горы": "mountains", "лес": "forest",
            "море": "ocean", "пляж": "beach", "дом": "house", 
            "город": "city", "автомобиль": "car", "машина": "car",
            "цветы": "flowers", "роза": "rose", "тюльпан": "tulip",
            "девушка": "woman", "женщина": "woman", "девочка": "girl",
            "мужчина": "man", "парень": "young man", "мальчик": "boy",
            "ребенок": "child", "дети": "children",
            "красивый": "beautiful", "красивая": "beautiful",
            "реалистичный": "realistic", "фотореалистичный": "photorealistic",
            "портрет": "portrait", "пейзаж": "landscape",
            "природа": "nature", "весна": "spring", "лето": "summer",
            "осень": "autumn", "зима": "winter",
            "дождь": "rain", "снег": "snow", "солнце": "sun",
            "небо": "sky", "облака": "clouds", "звезды": "stars",
            "еда": "food", "торт": "cake", "пицца": "pizza"
        }
        
        english_prompt = russian_prompt.lower()
        for ru, en in translations.items():
            english_prompt = english_prompt.replace(ru, en)
        
        return english_prompt
    
    def generate_via_pollinations_clean(self, prompt):
        """Генерация через Pollinations AI с удалением вотермарка"""
        try:
            enhanced_prompt = f"{prompt}, high quality, detailed, masterpiece, 8k, professional photography"
            
            base_url = "https://image.pollinations.ai/prompt/"
            
            import urllib.parse
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            params = "?width=1024&height=1024&model=flux&enhance=true&nologo=true"
            
            image_url = base_url + encoded_prompt + params
            
            if not self.silent_mode:
                print(f"📝 Промпт: {enhanced_prompt}")
                print("⏳ Генерация изображения без вотермарка...")
            
            response = requests.get(image_url, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Удаляем вотермарк если есть
                clean_image = self.remove_watermark(image)
                
                return clean_image
            else:
                if not self.silent_mode:
                    print(f"❌ Ошибка: {response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка: {e}")
            return None

    def compress_image(self, image, target_size_kb=150, quality=85):
        """
        Сжимает изображение до указанного размера в килобайтах
        
        Args:
            image: PIL Image объект
            target_size_kb: Целевой размер в килобайтах (по умолчанию 150кб)
            quality: Качество JPEG (по умолчанию 85)
        
        Returns:
            PIL Image: Сжатое изображение
        """
        try:
            # Сохраняем исходные размеры
            original_width, original_height = image.size
            
            # Если изображение слишком большое, уменьшаем его
            max_dimension = 1200  # Максимальный размер стороны
            if original_width > max_dimension or original_height > max_dimension:
                # Вычисляем новые размеры с сохранением пропорций
                if original_width > original_height:
                    new_width = max_dimension
                    new_height = int((original_height * max_dimension) / original_width)
                else:
                    new_height = max_dimension
                    new_width = int((original_width * max_dimension) / original_height)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                if not self.silent_mode:
                    print(f"🔄 Размер изменен с {original_width}x{original_height} на {new_width}x{new_height}")
            
            # Определяем формат для сжатия
            has_transparency = False
            if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                has_transparency = True
            
            # Сжатие для изображений с прозрачностью (PNG)
            if has_transparency:
                return self._compress_png(image, target_size_kb)
            else:
                # Сжатие для обычных изображений (JPEG)
                return self._compress_jpeg(image, target_size_kb, quality)
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка сжатия: {e}")
            return image
    
    def _compress_jpeg(self, image, target_size_kb, initial_quality=85):
        """Сжимает изображение в JPEG формате"""
        try:
            # Конвертируем в RGB если нужно
            if image.mode in ('RGBA', 'LA'):
                # Создаем белый фон
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Пробуем разные уровни качества
            for quality in range(initial_quality, 20, -5):
                # Сохраняем в память
                import io
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=quality, optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    if not self.silent_mode:
                        print(f"📦 Сжато до {size_kb:.1f}кб (качество: {quality})")
                    
                    # Возвращаем изображение из буфера
                    buffer.seek(0)
                    return Image.open(buffer)
                    
            # Если не удалось достичь целевого размера, возвращаем с минимальным качеством
            if not self.silent_mode:
                print(f"⚠️ Не удалось достичь {target_size_kb}кб, сжато с качеством 25")
            
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=25, optimize=True)
            buffer.seek(0)
            return Image.open(buffer)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка JPEG сжатия: {e}")
            return image
    
    def _compress_png(self, image, target_size_kb):
        """Сжимает PNG изображение с сохранением прозрачности"""
        try:
            # Пробуем уменьшить количество цветов
            original_mode = image.mode
            
            # Для PNG пробуем разные уровни оптимизации
            import io
            
            # Пробуем с optimize=True
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            size_kb = len(buffer.getvalue()) / 1024
            
            if size_kb <= target_size_kb:
                if not self.silent_mode:
                    print(f"📦 PNG сжат до {size_kb:.1f}кб (optimize)")
                buffer.seek(0)
                return Image.open(buffer)
            
            # Если файл всё ещё большой, пробуем уменьшить цвета
            if original_mode == 'RGBA':
                # Квантизация для уменьшения размера
                quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                # Возвращаем в RGBA режим
                quantized = quantized.convert('RGBA')
                
                buffer = io.BytesIO()
                quantized.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    if not self.silent_mode:
                        print(f"📦 PNG сжат до {size_kb:.1f}кб (квантизация)")
                    buffer.seek(0)
                    return Image.open(buffer)
            
            # Если всё ещё большой, возвращаем оптимизированную версию
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            final_size_kb = len(buffer.getvalue()) / 1024
            
            if not self.silent_mode:
                print(f"📦 PNG сжат до {final_size_kb:.1f}кб (лучший результат)")
            
            buffer.seek(0)
            return Image.open(buffer)
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка PNG сжатия: {e}")
            return image
    
    def save_compressed_image(self, image, filepath, target_size_kb=150):
        """
        Сжимает и сохраняет изображение
        
        Args:
            image: PIL Image объект
            filepath: Путь для сохранения
            target_size_kb: Целевой размер в килобайтах
        """
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image, target_size_kb)
            
            # Определяем формат по расширению файла
            file_path = Path(filepath)
            extension = file_path.suffix.lower()
            
            # Определяем лучший формат для сжатия
            has_transparency = False
            if compressed_image.mode in ('RGBA', 'LA') or 'transparency' in compressed_image.info:
                has_transparency = True
            
            # Сохраняем в соответствующем формате
            if extension == '.png' and has_transparency:
                # PNG с прозрачностью
                compressed_image.save(filepath, format='PNG', optimize=True)
            elif extension == '.png' and not has_transparency:
                # PNG без прозрачности - конвертируем в JPEG для лучшего сжатия
                jpeg_path = str(file_path).replace('.png', '.jpg')
                if compressed_image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', compressed_image.size, (255, 255, 255))
                    if compressed_image.mode == 'RGBA':
                        background.paste(compressed_image, mask=compressed_image.split()[-1])
                    compressed_image = background
                elif compressed_image.mode != 'RGB':
                    compressed_image = compressed_image.convert('RGB')
                
                compressed_image.save(jpeg_path, format='JPEG', quality=85, optimize=True)
                # Переименовываем обратно в PNG для совместимости
                os.rename(jpeg_path, filepath)
            elif extension in ['.jpg', '.jpeg']:
                # JPEG формат
                if compressed_image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', compressed_image.size, (255, 255, 255))
                    if compressed_image.mode == 'RGBA':
                        background.paste(compressed_image, mask=compressed_image.split()[-1])
                    compressed_image = background
                elif compressed_image.mode != 'RGB':
                    compressed_image = compressed_image.convert('RGB')
                
                compressed_image.save(filepath, format='JPEG', quality=85, optimize=True)
            else:
                # По умолчанию используем наиболее подходящий формат
                if has_transparency:
                    compressed_image.save(filepath, format='PNG', optimize=True)
                else:
                    # Сохраняем как JPEG для лучшего сжатия
                    if compressed_image.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', compressed_image.size, (255, 255, 255))
                        if compressed_image.mode == 'RGBA':
                            background.paste(compressed_image, mask=compressed_image.split()[-1])
                        compressed_image = background
                    elif compressed_image.mode != 'RGB':
                        compressed_image = compressed_image.convert('RGB')
                    
                    jpeg_path = str(file_path).replace(extension, '.jpg')
                    compressed_image.save(jpeg_path, format='JPEG', quality=85, optimize=True)
                    os.rename(jpeg_path, filepath)
            
            # Проверяем итоговый размер
            final_size_kb = Path(filepath).stat().st_size / 1024
            if not self.silent_mode:
                print(f"💾 Сохранено: {filepath} ({final_size_kb:.1f}кб)")
            
            return True
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения: {e}")
            return False

    def generate_thematic_set(self, theme_input, media_dir, method="1", progress_callback=None):
        """
        Генерирует полный набор из 8 тематических изображений
        
        Args:
            theme_input (str): Тематика бизнеса
            media_dir (str): Путь к папке media
            method (str): Метод генерации (1, 2, 3)
            progress_callback (callable): Функция обратного вызова для обновления прогресса
            
        Returns:
            dict: Результаты генерации {имя_файла: путь_к_файлу или None}
        """
        thematic_gen = ThematicImageGenerator(silent_mode=self.silent_mode)
        prompts, detected_theme = thematic_gen.get_theme_prompts(theme_input)
        
        # Создаем папку media если её нет
        os.makedirs(media_dir, exist_ok=True)
        
        if not self.silent_mode:
            print(f"\n🎨 Начинаю генерацию 8 изображений для тематики: {detected_theme}")
            print("=" * 60)
        
        if progress_callback:
            progress_callback(f"🎨 Генерация изображений для тематики: {detected_theme}")
        
        image_names = ["main", "about1", "about2", "about3", "review1", "review2", "review3", "favicon"]
        results = {}
        
        for i, image_name in enumerate(image_names, 1):
            if not self.silent_mode:
                print(f"\n🖼️  Генерация {i}/8: {image_name}")
                print("-" * 40)
            
            if progress_callback:
                progress_callback(f"🖼️  Генерация {i}/8: {image_name}")
            
            prompt = prompts[image_name]
            
            # Добавляем рандомизацию для уникальности
            if image_name == "favicon":
                # Специальная рандомизация для фавиконок
                prompt = thematic_gen.add_favicon_randomization(prompt)
                prompt += ", TRANSPARENT BACKGROUND, icon design, vector style, flat design, simple logo, no background, white cutout, isolated on transparent, PNG with alpha channel, clear background, cutout style, logo without background"
            else:
                # Обычная рандомизация для остальных изображений
                prompt = thematic_gen.add_randomization(prompt)
            
            # Специальная обработка для фавиконки
            if image_name == "favicon" and self.use_icons8_for_favicons and self.icons8_manager:
                # Используем Icons8 для фавиконки
                filename = os.path.join(media_dir, f"{image_name}.png")
                favicon_success = self.icons8_manager.create_favicon_from_theme(theme_input, filename, 512)
                
                if favicon_success:
                    results[image_name] = filename
                    if not self.silent_mode:
                        print(f"✅ Фавиконка Icons8 сохранена: {filename}")
                else:
                    if not self.silent_mode:
                        print("⚠️ Icons8 не сработал, переключаюсь на AI генерацию")
                    # Fallback на AI генерацию
                    image = self.generate_via_pollinations_clean(prompt)
                    if image:
                        image = image.resize((512, 512), Image.Resampling.LANCZOS)
                        image = self.make_favicon_transparent(image)
                        
                        # Используем сжатие для AI фавиконки (целевой размер 50кб)
                        filename = os.path.join(media_dir, f"{image_name}.png")
                        if self.save_compressed_image(image, filename, target_size_kb=50):
                            results[image_name] = filename
                            if not self.silent_mode:
                                print(f"✅ AI фавиконка сохранена: {filename}")
                        else:
                            results[image_name] = None
                    else:
                        results[image_name] = None
            else:
                # Обычная генерация для остальных изображений
                image = self.generate_via_pollinations_clean(prompt)
                
                if image:
                    filename = os.path.join(media_dir, f"{image_name}.png")
                    
                    # Для AI фавиконки делаем размер 512x512 и убираем фон
                    if image_name == "favicon":
                        image = image.resize((512, 512), Image.Resampling.LANCZOS)
                        image = self.make_favicon_transparent(image)
                        
                        # Используем сжатие для AI фавиконки (целевой размер 50кб)
                        if self.save_compressed_image(image, filename, target_size_kb=50):
                            results[image_name] = filename
                            if not self.silent_mode:
                                print(f"✅ AI фавиконка сохранена с сжатием: {filename}")
                        else:
                            results[image_name] = None
                    else:
                        # Для обычных изображений используем сжатие до 150кб
                        if self.save_compressed_image(image, filename, target_size_kb=150):
                            results[image_name] = filename
                            if not self.silent_mode:
                                print(f"✅ Сохранено с сжатием: {filename}")
                        else:
                            results[image_name] = None
                    
                    # Небольшая задержка между запросами (не нужна для Icons8)
                    if image_name != "favicon" or not self.use_icons8_for_favicons:
                        time.sleep(2)
                else:
                    if not self.silent_mode:
                        print(f"❌ Не удалось создать {image_name}")
                    results[image_name] = None
        
        # Показываем результаты
        if not self.silent_mode:
            print(f"\n🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
            print("=" * 60)
            print(f"📁 Папка: {media_dir}")
            print(f"🎯 Тематика: {detected_theme}")
            print("\n📋 Созданные файлы:")
            
            for name, filename in results.items():
                if filename:
                    print(f"  ✅ {name}: {filename}")
                else:
                    print(f"  ❌ {name}: НЕ СОЗДАН")
        
        if progress_callback:
            successful_count = len([f for f in results.values() if f is not None])
            progress_callback(f"✅ Создано {successful_count}/8 изображений")
        
        return results

def main():
    """Основная функция для запуска как отдельной программы"""
    generator = ImageGenerator()
    
    print("\n🌟 Динамический AI-генератор изображений для любых тематик!")
    print("=" * 60)
    print("🧠 Интеллектуальный анализ через интернет")
    print("🎨 Автоматическая адаптация под любую тематику")
    print()
    
    while True:
        theme_input = input("Введите тематику бизнеса (или 'выход'): ").strip()
        
        if theme_input.lower() in ['выход', 'exit', 'quit']:
            print("👋 До свидания!")
            break
            
        if not theme_input:
            continue
        
        try:
            # Генерируем набор
            results = generator.generate_thematic_set(theme_input, "media", "1")
            
            print(f"\n💡 Теперь вы можете использовать созданные изображения в своем лендинге!")
            print("   Просто скопируйте папку 'media' в ваш проект.")
            
            continue_choice = input("\nСоздать изображения для другой тематики? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no', 'нет']:
                break
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 