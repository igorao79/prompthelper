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

class IntelligentContextAnalyzer_DEPRECATED_DO_NOT_USE:
    """УМНЫЙ анализатор любых тематик без интернета"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        
        # Словарь переводов ключевых слов
        self.translations = {
            # Типы деятельности
            'продажа': 'sales', 'продаж': 'sales', 'продаем': 'sales',
            'покупка': 'purchase', 'покупаем': 'purchase',
            'аренда': 'rental', 'арендуем': 'rental', 'сдаем': 'rental',
            'производство': 'manufacturing', 'производим': 'manufacturing',
            'изготовление': 'manufacturing', 'изготавливаем': 'manufacturing',
            'ремонт': 'repair', 'ремонтируем': 'repair', 'починка': 'repair',
            'установка': 'installation', 'устанавливаем': 'installation',
            'монтаж': 'installation', 'монтируем': 'installation',
            'строительство': 'construction', 'строим': 'construction',
            'консультация': 'consulting', 'консультируем': 'consulting',
            'обучение': 'training', 'обучаем': 'training', 'курсы': 'training',
            'доставка': 'delivery', 'доставляем': 'delivery',
            'перевозка': 'transportation', 'перевозим': 'transportation',
            'дизайн': 'design', 'проектирование': 'design',
            
            # Предметы и товары
            'лестниц': 'stairs', 'лестницы': 'stairs', 'лестница': 'stairs',
            'окн': 'windows', 'окна': 'windows', 'окно': 'windows',
            'двер': 'doors', 'дверь': 'doors', 'двери': 'doors',
            'мебел': 'furniture', 'мебель': 'furniture',
            'автомобил': 'cars', 'машин': 'cars', 'авто': 'cars',
            'телефон': 'phones', 'смартфон': 'smartphones',
            'компьютер': 'computers', 'ноутбук': 'laptops',
            'одежд': 'clothing', 'одежда': 'clothing',
            'обув': 'shoes', 'обувь': 'shoes',
            'стройматериал': 'building materials', 'материал': 'materials',
            'инструмент': 'tools', 'оборудование': 'equipment',
            'сантехник': 'plumbing', 'сантехника': 'plumbing',
            'электрик': 'electrical', 'электрика': 'electrical',
            'кровл': 'roofing', 'крыш': 'roofing', 'кровля': 'roofing',
            'фундамент': 'foundation', 'подвал': 'basement',
            'кухн': 'kitchen', 'кухня': 'kitchen', 'кухни': 'kitchen',
            'ванн': 'bathroom', 'ванная': 'bathroom',
            'плитк': 'tiles', 'плитка': 'tiles',
            'обои': 'wallpaper', 'краск': 'paint', 'покраск': 'painting',
            
            # Транспорт
            'грузовик': 'trucks', 'фур': 'trucks', 'фура': 'trucks',
            'прицеп': 'trailers', 'полуприцеп': 'semi-trailers',
            'мотоцикл': 'motorcycles', 'скутер': 'scooters',
            'велосипед': 'bicycles', 'самокат': 'scooters',
            'лодк': 'boats', 'яхт': 'yachts', 'катер': 'boats',
            
            # Еда и напитки  
            'хлеб': 'bread', 'выпечка': 'bakery', 'торт': 'cakes',
            'мяс': 'meat', 'колбас': 'sausages',
            'молок': 'milk', 'сыр': 'cheese', 'творог': 'cottage cheese',
            'овощ': 'vegetables', 'фрукт': 'fruits',
            'кофе': 'coffee', 'чай': 'tea', 'напитк': 'beverages',
            'пиц': 'pizza', 'бургер': 'burgers', 'суш': 'sushi',
            'ресторан': 'restaurant', 'кафе': 'cafe', 'бар': 'bar',
            
            # Услуги
            'стрижк': 'haircut', 'парикмахер': 'barbershop',
            'маникюр': 'manicure', 'педикюр': 'pedicure',
            'массаж': 'massage', 'косметолог': 'cosmetology',
            'фотограф': 'photography', 'видеосъемк': 'videography',
            'уборк': 'cleaning', 'клининг': 'cleaning',
            'стирк': 'laundry', 'химчистк': 'dry cleaning',
            'охран': 'security', 'сигнализац': 'alarm systems',
            
            # Медицина
            'стоматолог': 'dentistry', 'зубн': 'dental',
            'терапевт': 'therapy', 'хирург': 'surgery',
            'педиатр': 'pediatrics', 'гинеколог': 'gynecology',
            'кардиолог': 'cardiology', 'невролог': 'neurology',
            'офтальмолог': 'ophthalmology', 'лор': 'ENT',
            'массажист': 'massage therapist',
            
            # Животные
            'ветеринар': 'veterinary', 'груминг': 'pet grooming',
            'зоомагазин': 'pet store', 'корм': 'pet food',
            'собак': 'dogs', 'кошк': 'cats', 'птиц': 'birds',
            
            # Образование
            'школ': 'school', 'университет': 'university',
            'детский сад': 'kindergarten', 'репетитор': 'tutoring',
            'языков': 'language courses', 'компьютерн': 'computer courses',
            
            # Развлечения
            'игр': 'games', 'развлечен': 'entertainment',
            'квест': 'escape room', 'боулинг': 'bowling',
            'кинотеатр': 'cinema', 'театр': 'theater',
            'концерт': 'concerts', 'праздник': 'events',
            
            # Спорт и фитнес
            'спортзал': 'gym', 'фитнес': 'fitness',
            'йог': 'yoga', 'пилатес': 'pilates',
            'тренер': 'trainer', 'тренировк': 'training',
            'плаван': 'swimming', 'бокс': 'boxing',
            'карате': 'karate', 'дзюдо': 'judo',
            
            # Красота
            'салон красоты': 'beauty salon', 'барбершоп': 'barbershop',
            'косметика': 'cosmetics', 'парфюм': 'perfume',
            'татуировк': 'tattoo', 'пирсинг': 'piercing',
            
            # Недвижимость
            'квартир': 'apartments', 'дом': 'houses', 'коттедж': 'cottages',
            'офис': 'offices', 'склад': 'warehouses', 'гараж': 'garages',
            'участок': 'land plots', 'дач': 'country houses',
            
            # Финансы
            'банк': 'banking', 'кредит': 'loans', 'ипотек': 'mortgage',
            'страхован': 'insurance', 'инвестиц': 'investments',
            
            # Юридические
            'юрист': 'legal services', 'адвокат': 'lawyer',
            'нотариус': 'notary', 'регистрац': 'registration',
            
            # IT
            'сайт': 'website', 'приложен': 'mobile app',
            'програм': 'software', 'дизайн': 'design',
            'реклам': 'advertising', 'маркетинг': 'marketing',
        }
        
        # Типы бизнес-деятельности
        self.business_types = {
            'retail': ['продажа', 'магазин', 'торговля', 'покупка'],
            'manufacturing': ['производство', 'изготовление', 'завод', 'фабрика'],
            'service': ['услуги', 'сервис', 'обслуживание', 'помощь'],
            'repair': ['ремонт', 'починка', 'восстановление', 'замена'],
            'installation': ['установка', 'монтаж', 'подключение'],
            'construction': ['строительство', 'стройка', 'возведение'],
            'consulting': ['консультация', 'совет', 'помощь', 'поддержка'],
            'training': ['обучение', 'курсы', 'тренинг', 'образование'],
            'healthcare': ['медицин', 'лечение', 'здоровье', 'терапия'],
            'beauty': ['красота', 'салон', 'стрижка', 'маникюр'],
            'food': ['еда', 'питание', 'ресторан', 'кафе', 'готовка'],
            'transportation': ['перевозка', 'доставка', 'транспорт', 'логистика'],
        }
    
    def search_business_context(self, query):
        """Умный анализ любой тематики БЕЗ интернета"""
        if not self.silent_mode:
            print(f"🧠 Умный анализ тематики: {query}")
        
        # Анализируем ключевые слова
        analysis = self._analyze_keywords(query)
        
        # Определяем тип деятельности
        business_category = self._determine_business_category(query, analysis)
        
        # Создаем контекст
        context = {
            'category': 'smart_analysis',
            'business_type': analysis['main_topic'],
            'activity_type': analysis['activity_type'],
            'english_terms': analysis['english_terms'],
            'business_category': business_category,
            'confidence': 0.8,
            'keywords': analysis['english_terms'][:3],
            'environment': f"professional {analysis['main_topic']} {business_category}"
        }
        
        if not self.silent_mode:
            print(f"🎯 Тип деятельности: {analysis['activity_type']}")
            print(f"🏢 Категория: {business_category}")
            print(f"🔤 Английские термины: {', '.join(analysis['english_terms'][:3])}")
        
        return context
    
    def _analyze_keywords(self, query):
        """Анализирует ключевые слова и переводит их"""
        query_lower = query.lower()
        
        # Ищем ключевые слова и переводим
        found_translations = []
        activity_type = 'service'  # по умолчанию
        
        for ru_word, en_translation in self.translations.items():
            if ru_word in query_lower:
                found_translations.append(en_translation)
                
                # Определяем тип деятельности по первому найденному слову
                if ru_word in ['продажа', 'продаж', 'продаем', 'магазин', 'торговля']:
                    activity_type = 'sales'
                elif ru_word in ['производство', 'производим', 'изготовление', 'изготавливаем']:
                    activity_type = 'manufacturing'
                elif ru_word in ['ремонт', 'ремонтируем', 'починка']:
                    activity_type = 'repair'
                elif ru_word in ['установка', 'устанавливаем', 'монтаж', 'монтируем']:
                    activity_type = 'installation'
                elif ru_word in ['строительство', 'строим']:
                    activity_type = 'construction'
                elif ru_word in ['консультация', 'консультируем']:
                    activity_type = 'consulting'
                elif ru_word in ['обучение', 'обучаем', 'курсы']:
                    activity_type = 'training'
                elif ru_word in ['доставка', 'доставляем', 'перевозка', 'перевозим']:
                    activity_type = 'delivery'
        
        # Если не нашли переводов, создаем из исходной темы
        if not found_translations:
            # Берем последнее слово как основной предмет
            words = query_lower.split()
            if words:
                main_topic = words[-1]  # последнее слово обычно предмет
                found_translations = [main_topic]
            else:
                found_translations = [query_lower]
        
        # Определяем главную тему (обычно последний элемент или предмет)
        main_topic = found_translations[-1] if found_translations else query_lower
        
        return {
            'activity_type': activity_type,
            'main_topic': main_topic,
            'english_terms': found_translations,
            'original_query': query
        }
    
    def _determine_business_category(self, query, analysis):
        """Определяет категорию бизнеса"""
        query_lower = query.lower()
        
        # Проверяем по ключевым словам
        for category, keywords in self.business_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return category
        
        # По умолчанию возвращаем на основе анализа
        activity_map = {
            'sales': 'retail',
            'manufacturing': 'manufacturing', 
            'repair': 'service',
            'installation': 'service',
            'construction': 'construction',
            'consulting': 'consulting',
            'training': 'training',
            'delivery': 'transportation'
        }
        
        return activity_map.get(analysis['activity_type'], 'service')
    
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
        """ИСПРАВЛЕННЫЙ поиск через DuckDuckGo API"""
        try:
            # Простой запрос без лишних слов
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1',
                'no_redirect': '1'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            # 202 это нормальный статус для DuckDuckGo
            if response.status_code in [200, 202]:
                data = response.json()
                results = []
                
                # Основной ответ (Abstract)
                if data.get('Abstract') and len(data.get('Abstract', '')) > 20:
                    results.append({
                        'title': data.get('Heading', query),
                        'description': data.get('Abstract', ''),
                        'source': 'DuckDuckGo Abstract',
                        'relevance': 'high'
                    })
                
                # Быстрые ответы (Answer) - часто самые точные
                if data.get('Answer') and len(data.get('Answer', '')) > 10:
                    results.append({
                        'title': 'Определение',
                        'description': data.get('Answer', ''),
                        'source': 'DuckDuckGo Answer',
                        'relevance': 'high'
                    })
                
                # Связанные темы - ИСПРАВЛЕННАЯ обработка
                for topic in data.get('RelatedTopics', [])[:5]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        text = topic.get('Text', '')
                        if len(text) > 30:
                            # Проверяем релевантность - либо содержит слова из запроса, либо берем первые результаты
                            query_words = query.lower().split()
                            is_relevant = any(word in text.lower() for word in query_words if len(word) > 2)
                            
                            if is_relevant or len(results) == 0:  # Берем релевантные или первые результаты если нет других
                                results.append({
                                    'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' ') if topic.get('FirstURL') else query,
                                    'description': text,
                                    'source': 'DuckDuckGo Related',
                                    'relevance': 'medium'
                                })
                
                # Результаты поиска (Results) - если нет других данных
                if not results and data.get('Results'):
                    for result in data.get('Results', [])[:3]:
                        if result.get('Text'):
                            results.append({
                                'title': result.get('Text', ''),
                                'description': result.get('Text', ''),
                                'source': 'DuckDuckGo Results',
                                'relevance': 'low'
                            })
                
                if not self.silent_mode:
                    if results:
                        print(f"✅ DuckDuckGo найдено {len(results)} результатов")
                    else:
                        print(f"⚠️ DuckDuckGo: пустой ответ для '{query}'")
                
                return results if results else None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка DuckDuckGo: {e}")
            return None
    
    def _search_wikipedia(self, query):
        """УЛУЧШЕННЫЙ поиск в Wikipedia с множественными запросами"""
        try:
            # Пробуем разные варианты поисковых запросов
            search_variants = [
                query,  # Оригинальный запрос
                f"{query} услуги",  # + услуги 
                f"{query} деятельность",  # + деятельность
                f"{query} бизнес",  # + бизнес
                query.replace('недвижимость', 'недвижимости агентство'),  # Специфичные замены
                query.replace('авто', 'автомобильный сервис')
            ]
            
            best_result = None
            best_relevance = 0
            
            for search_query in search_variants:
                result = self._single_wikipedia_search(search_query, query)
                if result:
                    # Проверяем релевантность
                    relevance = self._calculate_wikipedia_relevance(result['description'], query)
                    if relevance > best_relevance:
                        best_relevance = relevance
                        best_result = result
                        best_result['relevance_score'] = relevance
                        
                    # Если нашли очень релевантный результат, останавливаемся
                    if relevance > 0.7:
                        break
            
            if best_result:
                if not self.silent_mode:
                    print(f"✅ Wikipedia лучший результат: {best_result['title']} (релевантность: {best_relevance:.2f})")
                return best_result
            else:
                if not self.silent_mode:
                    print(f"⚠️ Wikipedia: релевантные статьи не найдены для '{query}'")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка Wikipedia: {e}")
            return None
            
    def _single_wikipedia_search(self, search_query, original_query):
        """Выполняет одиночный поиск в Wikipedia"""
        try:
            search_url = "https://ru.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': 5,  # Увеличили лимит
                'srprop': 'snippet|titlesnippet'
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=12)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                search_results = search_data.get('query', {}).get('search', [])
                
                # Ищем наиболее релевантный результат среди первых 5
                for result in search_results:
                    page_title = result.get('title', '')
                    snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                    
                    # Быстрая проверка релевантности по заголовку и snippet
                    title_relevance = self._calculate_wikipedia_relevance(page_title, original_query)
                    snippet_relevance = self._calculate_wikipedia_relevance(snippet, original_query)
                    
                    if title_relevance > 0.3 or snippet_relevance > 0.2:
                        # Получаем полное содержание
                        content_url = "https://ru.wikipedia.org/api/rest_v1/page/summary/" + quote(page_title)
                        try:
                            content_response = requests.get(content_url, timeout=8)
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                return {
                                    'title': content_data.get('title', page_title),
                                    'description': content_data.get('extract', snippet),
                                    'source': 'Wikipedia'
                                }
                        except:
                            pass
                        
                        # Fallback на snippet
                        return {
                            'title': page_title,
                            'description': snippet,
                            'source': 'Wikipedia'
                        }
                
                    return None
            else:
                return None
                
        except Exception:
            return None
    
    def _calculate_wikipedia_relevance(self, text, query):
        """Вычисляет релевантность текста к запросу"""
        if not text or not query:
            return 0
        
        text_lower = text.lower()
        query_words = query.lower().split()
        
        # Подсчитываем совпадения слов
        matches = sum(1 for word in query_words if word in text_lower)
        
        # Бонусы за специфичные совпадения
        bonus = 0
        if query.lower() in text_lower:
            bonus += 0.3
        
        # Штрафы за нерелевантные слова
        penalty = 0
        irrelevant_words = ['статья', 'категория', 'шаблон', 'файл', 'обсуждение']
        if any(word in text_lower for word in irrelevant_words):
            penalty = 0.2
        
        base_score = matches / max(len(query_words), 1)
        final_score = min(1.0, base_score + bonus - penalty)
        
        return final_score
    
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
        """Проверяет релевантность найденного контента к исходному запросу БЕЗ хардкода"""
        found_text_lower = found_text.lower()
        query_words = original_query.lower().split()
        
        # Подсчитываем сколько слов из запроса встречается в найденном тексте
        found_words = 0
        total_query_words = len([w for w in query_words if len(w) > 2])  # Слова длиннее 2 символов
        
        for word in query_words:
            if len(word) > 2 and word in found_text_lower:
                found_words += 1
        
        # Базовая релевантность по словам - ТОЛЬКО ЭТО, никаких хардкодированных тематик
        word_relevance = found_words / max(total_query_words, 1) if total_query_words > 0 else 0
        
        # Дополнительный бонус за точное совпадение запроса
        exact_match_bonus = 0
        if original_query.lower() in found_text_lower:
            exact_match_bonus = 0.3
        
        final_relevance = min(word_relevance + exact_match_bonus, 1.0)
        return final_relevance
    
    def _dynamic_context_extraction(self, text, query):
        """Динамическое извлечение контекста из текста БЕЗ предварительных категорий"""
        text_lower = text.lower()
        query_lower = query.lower()
        combined_text = f"{text_lower} {query_lower}".strip()
        
        # Извлекаем ключевые слова ТОЛЬКО из найденного текста
        meaningful_words = self._extract_dynamic_details(combined_text, query_lower)
        
        # Определяем основной тип деятельности ТОЛЬКО из текста
        main_activity = meaningful_words[0] if meaningful_words else query_lower.split()[0]
        
        # Определяем среду на основе контекста
        environment = self._determine_dynamic_environment(main_activity, meaningful_words, query_lower)
        
        # Определяем специфичность темы
        specificity = self._calculate_specificity(query_lower, meaningful_words)
        
        return {
            'category': 'internet_search_based',  # Единая категория
            'business_type': main_activity,
            'confidence': min(0.4 + specificity * 0.3, 0.8),
            'details': meaningful_words[:5],
            'keywords': self._extract_smart_keywords(combined_text, query_lower),
            'environment': environment,
            'theme_description': self._generate_theme_description(main_activity, meaningful_words, query_lower)
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
        """Динамически определяет среду ТОЛЬКО на основе найденных данных"""
        # Создаем среду на основе ключевых слов из интернет поиска
        environment_words = []
        
        # Добавляем найденные ключевые слова
        environment_words.extend([activity] + details[:2])
        
        # Создаем описание среды из реальных найденных данных
        if len(environment_words) >= 2:
            return f"professional {environment_words[0]} {environment_words[1]} workplace"
        else:
            return f"professional {activity} workplace"
    
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
        """Динамический fallback анализ - ТОЛЬКО на основе ключевых слов из запроса"""
        query_lower = query.lower()
        
        if not self.silent_mode:
            print(f"💪 Локальный анализ (чистый поиск по ключевым словам)")
        
        # Извлекаем ключевые слова без предварительной категоризации
        words = query_lower.split()
        meaningful_words = [w for w in words if len(w) > 2][:5]
        
        # Базовый анализ ТОЛЬКО на основе пользовательского ввода
        main_keyword = meaningful_words[0] if meaningful_words else query_lower.split()[0]
        
        return {
            'category': 'internet_search_based',
            'business_type': main_keyword,
            'confidence': 0.6,  # Средняя уверенность - лучше искать в интернете
            'details': meaningful_words,
            'keywords': meaningful_words,
            'environment': f"professional {main_keyword} workplace",
            'theme_description': f"услуги {main_keyword}"
        }

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

# ===== НЕДОСТАЮЩИЕ КЛАССЫ ДЛЯ СОВМЕСТИМОСТИ =====

class ImageGenerator:
    """Класс для генерации полного набора тематических изображений"""
    
    def __init__(self, silent_mode=False, use_icons8_for_favicons=True):
        self.silent_mode = silent_mode
        self.use_icons8_for_favicons = use_icons8_for_favicons
        # Старый анализатор больше не используется - используем SmartPromptGenerator
        
        # Импорты для генерации
        try:
            from icons8_api import Icons8API
            self.icons8_api = Icons8API()
            self.icons8_manager = self.icons8_api  # Алиас для совместимости с GUI
        except ImportError:
            self.icons8_api = None
            self.icons8_manager = None
            if not silent_mode:
                print("⚠️ Icons8 API недоступен")
        
        # Импорты для генерации
        try:
            from modern_favicon_gen import ModernFaviconGenerator
            self.favicon_generator = ModernFaviconGenerator()
        except ImportError:
            self.favicon_generator = None
            if not silent_mode:
                print("⚠️ ModernFaviconGenerator недоступен")
    
    def generate_thematic_set(self, theme_input, media_dir, method="1", progress_callback=None):
        """
        Генерирует полный набор тематических изображений
        
        Args:
            theme_input (str): Тематика 
            media_dir (str): Путь к папке media
            method (str): Метод генерации
            progress_callback (callable): Функция обратного вызова
            
        Returns:
            dict: Словарь с результатами генерации
        """
        if not self.silent_mode:
            print(f"🎨 Генерация тематических изображений для: {theme_input}")
        
        # Получаем умные промпты напрямую (БЕЗ старого анализатора)
        prompts, theme_data = self._generate_prompts(theme_input)
        
        results = {}
        image_names = ['main', 'about1', 'about2', 'about3', 'review1', 'review2', 'review3', 'favicon']
        
        for i, image_name in enumerate(image_names):
            if progress_callback:
                progress_callback(f"🎨 Генерация {image_name} ({i+1}/8)...")
            
            try:
                if image_name == 'favicon' and self.use_icons8_for_favicons and self.icons8_api:
                    # Генерируем фавикон через Icons8
                    result = self._generate_favicon_via_icons8(theme_input, media_dir, theme_data)
                else:
                    # Генерируем обычное изображение
                    result = self._generate_image_via_pollinations(
                        prompts.get(image_name, theme_input), 
                        image_name, 
                        media_dir
                    )
                
                results[image_name] = result
                
                if not self.silent_mode:
                    status = "✅" if result else "❌"
                    print(f"{status} {image_name}: {'Успешно' if result else 'Ошибка'}")
                    
            except Exception as e:
                if not self.silent_mode:
                    print(f"❌ Ошибка генерации {image_name}: {e}")
                results[image_name] = None
        
        return results
    
    def _generate_favicon_via_icons8(self, theme, media_dir, theme_data):
        """Генерирует фавикон через Icons8"""
        try:
            # Используем данные темы для улучшения поиска иконки
            business_type = theme_data.get('business_type', theme)
            icon_path = self.icons8_api.download_icon(
                business_type,
                str(media_dir),
                'favicon'
            )
            return icon_path
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Icons8 ошибка, используем Pollinations: {e}")
            # Fallback на Pollinations
            return self._generate_image_via_pollinations(theme, 'favicon', media_dir)
    
    def _generate_image_via_pollinations(self, prompt, image_name, media_dir):
        """Генерирует изображение через современный API с разнообразием"""
        try:
            # Используем новый современный API генератор
            from modern_image_api import ModernImageAPI
            modern_api = ModernImageAPI(silent_mode=self.silent_mode)
            
            # Определяем размер
            size = '512x512' if image_name == 'favicon' else '1024x768'
            
            # Генерируем с разнообразием
            result = modern_api.generate_image(
                prompt=prompt,
                image_name=image_name,
                output_dir=media_dir,
                size=size
            )
            
            return result
            
        except ImportError:
            # Fallback на старый метод если новый API недоступен
            if not self.silent_mode:
                print("⚠️ Современный API недоступен, используется базовый")
            return self._generate_image_fallback(prompt, image_name, media_dir)
        
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка современного API: {e}")
            return self._generate_image_fallback(prompt, image_name, media_dir)

    def _generate_image_fallback(self, prompt, image_name, media_dir):
        """Fallback метод генерации изображений"""
        try:
            import requests
            from pathlib import Path
            from PIL import Image
            
            # API Pollinations
            api_url = "https://image.pollinations.ai/prompt/"
            full_prompt = f"{prompt}, high quality, professional"
            
            # Параметры для разных типов изображений
            if image_name == 'favicon':
                params = "?width=512&height=512&model=flux"
                target_size_kb = 50  # Фавиконы до 50кб
                output_path = Path(media_dir) / f"{image_name}.png"  # PNG для прозрачности
            else:
                params = "?width=1024&height=768&model=flux"
                target_size_kb = 150  # Остальные изображения до 150кб
                output_path = Path(media_dir) / f"{image_name}.jpg"  # JPEG для лучшего сжатия
            
            url = f"{api_url}{full_prompt}{params}"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Загружаем в PIL Image для обработки
                import io
                image = Image.open(io.BytesIO(response.content))
                
                # Обрезаем водяной знак
                cropped_image = self._remove_pollinations_watermark_from_image(image)
                
                # Сжимаем и сохраняем с автоматическим контролем размера
                if self.save_compressed_image(cropped_image, str(output_path), target_size_kb=target_size_kb):
                    if not self.silent_mode:
                        final_size_kb = output_path.stat().st_size / 1024
                        print(f"🎨 {image_name}: Создано и сжато до {final_size_kb:.1f}кб")
                    return str(output_path)
                else:
                    if not self.silent_mode:
                        print(f"❌ Не удалось сохранить {image_name}")
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Fallback ошибка: {e}")
        
        return None

    def generate_via_pollinations_clean(self, prompt):
        """Генерирует изображение через Pollinations и возвращает PIL Image объект"""
        try:
            import requests
            from PIL import Image
            import io
            
            # API Pollinations
            api_url = "https://image.pollinations.ai/prompt/"
            full_prompt = f"{prompt}, high quality, professional"
            params = "?width=1024&height=768&model=flux"
            
            url = f"{api_url}{full_prompt}{params}"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Загружаем в PIL Image
                image = Image.open(io.BytesIO(response.content))
                
                # Применяем обрезку водяного знака
                cropped_image = self._remove_pollinations_watermark_from_image(image)
                
                if not self.silent_mode:
                    print(f"🎨 Изображение сгенерировано и обрезано")
                
                return cropped_image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка генерации: {e}")
        
        return None

    def make_favicon_transparent(self, image):
        """Делает фон фавикона прозрачным"""
        try:
            from PIL import Image
            
            # Конвертируем в RGBA если нужно
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Простой алгоритм удаления белого фона
            data = image.getdata()
            new_data = []
            
            for item in data:
                # Если пиксель белый или близкий к белому - делаем прозрачным
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # прозрачный
                else:
                    new_data.append(item)
            
            image.putdata(new_data)
            
            if not self.silent_mode:
                print("🔍 Фон фавикона сделан прозрачным")
            
            return image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка создания прозрачности: {e}")
            return image

    def save_compressed_image(self, image, filepath, target_size_kb=150):
        """УЛУЧШЕННОЕ сжатие изображений с сохранением качества"""
        try:
            from PIL import Image
            import io
            
            # Определяем формат по расширению файла
            if filepath.lower().endswith('.png'):
                format_type = 'PNG'
            else:
                format_type = 'JPEG'
            
            # Для PNG - более деликатное сжатие с сохранением качества
            if format_type == 'PNG':
                # Проверяем исходный размер
                buffer = io.BytesIO()
                image.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    # Если размер уже подходит - сохраняем без изменений
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 PNG сохранен {size_kb:.1f}кб (без сжатия)")
                    return True
                
                # Стратегия 1: Легкое ресайз с сохранением качества (только если сильно превышает)
                if size_kb > target_size_kb * 1.5:  # Только если превышает в 1.5 раза
                    for scale in [0.95, 0.9, 0.85, 0.8]:  # Более мягкий ресайз
                        new_width = int(image.width * scale)
                        new_height = int(image.height * scale)
                        
                        # Высококачественный ресайз
                        resized = image.resize((new_width, new_height), Image.LANCZOS)
                        
                        buffer = io.BytesIO()
                        resized.save(buffer, format='PNG', optimize=True)
                        size_kb = len(buffer.getvalue()) / 1024
                        
                        if size_kb <= target_size_kb:
                            with open(filepath, 'wb') as f:
                                f.write(buffer.getvalue())
                            
                            if not self.silent_mode:
                                print(f"📦 PNG сжат до {size_kb:.1f}кб (легкий ресайз {scale:.2f}x)")
                            return True
                
                # Стратегия 2: Деликатная квантизация с большим количеством цветов
                if image.mode == 'RGBA':
                    # Для прозрачных изображений - больше цветов
                    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    quantized = quantized.convert('RGBA')
                else:
                    # Для обычных изображений - тоже больше цветов
                    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                
                buffer = io.BytesIO()
                quantized.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                if size_kb <= target_size_kb:
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    if not self.silent_mode:
                        print(f"📦 PNG сжат до {size_kb:.1f}кб (деликатная квантизация 256 цветов)")
                    return True
                
                # Стратегия 3: Комбинированная - легкий ресайз + квантизация
                for scale in [0.9, 0.85, 0.8]:
                    new_width = int(image.width * scale)
                    new_height = int(image.height * scale)
                    resized = image.resize((new_width, new_height), Image.LANCZOS)
                    
                    if resized.mode == 'RGBA':
                        final_image = resized.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                        final_image = final_image.convert('RGBA')
                    else:
                        final_image = resized.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    
                    buffer = io.BytesIO()
                    final_image.save(buffer, format='PNG', optimize=True)
                    size_kb = len(buffer.getvalue()) / 1024
                    
                    if size_kb <= target_size_kb:
                        with open(filepath, 'wb') as f:
                            f.write(buffer.getvalue())
                        
                        if not self.silent_mode:
                            print(f"📦 PNG сжат до {size_kb:.1f}кб (ресайз {scale:.2f}x + 256 цветов)")
                        return True
                
                # Крайний случай - сохраняем как есть, но предупреждаем
                buffer = io.BytesIO()
                image.save(buffer, format='PNG', optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                
                if not self.silent_mode:
                    print(f"⚠️ PNG сохранен {size_kb:.1f}кб (превышает лимит, но качество сохранено)")
                return True
            
            else:
                # Для JPEG - более качественное сжатие
                # Конвертируем в RGB если нужно (JPEG не поддерживает прозрачность)
                if image.mode in ('RGBA', 'LA'):
                    # Создаем белый фон
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        rgb_image.paste(image, mask=image.split()[-1])
                    else:
                        rgb_image.paste(image)
                    image = rgb_image
                elif image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                # Пробуем более высокие уровни качества для JPEG
                for quality in [95, 90, 85, 80, 75, 70, 65, 60]:  # Начинаем с высокого качества
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=quality, optimize=True)
                    size_kb = len(buffer.getvalue()) / 1024
                    
                    if size_kb <= target_size_kb:
                        with open(filepath, 'wb') as f:
                            f.write(buffer.getvalue())
                        
                        if not self.silent_mode:
                            print(f"📦 JPEG сжат до {size_kb:.1f}кб (качество {quality}%)")
                        return True
                
                # Если все еще не помещается - легкий ресайз с хорошим качеством
                for scale in [0.95, 0.9, 0.85]:
                    new_width = int(image.width * scale)
                    new_height = int(image.height * scale)
                    resized = image.resize((new_width, new_height), Image.LANCZOS)
                    
                    for quality in [85, 80, 75, 70]:  # Сохраняем хорошее качество
                        buffer = io.BytesIO()
                        resized.save(buffer, format='JPEG', quality=quality, optimize=True)
                        size_kb = len(buffer.getvalue()) / 1024
                        
                        if size_kb <= target_size_kb:
                            with open(filepath, 'wb') as f:
                                f.write(buffer.getvalue())
                            
                            if not self.silent_mode:
                                print(f"📦 JPEG сжат до {size_kb:.1f}кб (ресайз {scale:.2f}x, качество {quality}%)")
                            return True
                
                # Последняя попытка с минимально приемлемым качеством
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=65, optimize=True)
                size_kb = len(buffer.getvalue()) / 1024
                
                with open(filepath, 'wb') as f:
                    f.write(buffer.getvalue())
                
                if not self.silent_mode:
                    if size_kb <= target_size_kb:
                        print(f"📦 JPEG сжат до {size_kb:.1f}кб (качество 65%)")
                    else:
                        print(f"⚠️ JPEG сохранен {size_kb:.1f}кб (превышает лимит, но качество сохранено)")
                return True
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сжатия: {e}")
            return False

    def _remove_pollinations_watermark_from_image(self, image):
        """Удаляет водяной знак с PIL Image объекта"""
        try:
            width, height = image.size
            
            # Определяем область обрезки
            if width >= 1024 and height >= 768:
                crop_box = (0, 0, width - 80, height - 60)
            elif width >= 512 and height >= 512:
                crop_box = (0, 0, width - 50, height - 40)
            else:
                crop_box = (0, 0, width - 30, height - 25)
            
            # Обрезаем изображение
            cropped_img = image.crop(crop_box)
            
            if not self.silent_mode:
                new_width, new_height = cropped_img.size
                print(f"✂️ Обрезано с {width}x{height} до {new_width}x{new_height}")
            
            return cropped_img
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка обрезки: {e}")
            return image

    def _generate_prompts(self, theme_input):
        """УМНАЯ генерация промптов для ЛЮБЫХ тематик"""
        # Импортируем умный генератор
        try:
            from smart_prompt_generator import SmartPromptGenerator
            smart_gen = SmartPromptGenerator()
            prompts, analysis = smart_gen.generate_prompts(theme_input, silent_mode=self.silent_mode)
            
            theme_data = {
                'business_type': analysis['main_product'],
                'activity_type': analysis['activity_type'],
                'analysis': analysis
            }
            
            return prompts, theme_data
            
        except ImportError:
            # Фоллбэк на старую систему, если умный генератор недоступен
            if not self.silent_mode:
                print("⚠️ Умный генератор недоступен, используется базовая система")
            return self._generate_fallback_prompts(theme_input)
    
    def _generate_fallback_prompts(self, theme_input):
        """Простая фоллбэк система для генерации промптов"""
        business_type = theme_input.lower()
        
        prompts = {
            'main': f"professional {business_type} business exterior, modern commercial building",
            'about1': f"{business_type} interior, professional workspace, modern facilities",
            'about2': f"professional working with {business_type}, quality service delivery",
            'about3': f"excellent {business_type} results, professional quality work",
            'review1': f"satisfied {business_type} customer, happy client experience",
            'review2': f"{business_type} consultation, professional service meeting",
            'review3': f"professional {business_type} team, experienced staff",
            'favicon': f"{business_type} icon, business symbol, professional logo"
        }
        
        theme_data = {
            'business_type': business_type,
            'activity_type': 'service'
        }
        
        return prompts, theme_data

    def _generate_auto_prompts(self, business_type):
        """Специализированные промпты для автобизнеса"""
        prompts = {}
        
        main_variants = [
            f"modern car dealership exterior, glass showroom windows, luxury cars displayed",
            f"professional auto service garage, clean workshop, modern equipment",
            f"car showroom interior, shiny new vehicles, professional lighting",
            f"auto repair shop front view, service bay doors, professional signage"
        ]
        prompts['main'] = self._select_random_variant(main_variants)
        
        about1_variants = [
            f"car showroom interior, luxury vehicles on display, modern dealership design",
            f"auto service workshop, mechanic tools, clean organized garage",
            f"car repair bay, hydraulic lifts, professional automotive equipment",
            f"vehicle inspection area, diagnostic equipment, modern auto service"
        ]
        prompts['about1'] = self._select_random_variant(about1_variants)
        
        about2_variants = [
            f"professional mechanic working on car engine, automotive repair process",
            f"car salesman showing vehicle features to customers, professional consultation",
            f"automotive technician using diagnostic equipment, precision work",
            f"expert mechanic servicing car, professional automotive maintenance"
        ]
        prompts['about2'] = self._select_random_variant(about2_variants)
        
        about3_variants = [
            f"perfectly serviced car, high quality automotive repair results",
            f"luxury car in showroom, premium vehicle sales offering",
            f"satisfied customer receiving car keys, successful automotive service",
            f"restored vehicle, professional auto body work, excellent results"
        ]
        prompts['about3'] = self._select_random_variant(about3_variants)
        
        review1_variants = [
            f"happy customer receiving car keys, satisfied smile, successful car purchase",
            f"pleased client with serviced vehicle, automotive satisfaction, thumbs up",
            f"delighted car owner, professional automotive service experience"
        ]
        prompts['review1'] = self._select_random_variant(review1_variants)
        
        review2_variants = [
            f"car consultation meeting, salesman explaining vehicle features",
            f"automotive service advisor discussing repair options with customer",
            f"professional car buying consultation, expert automotive guidance"
        ]
        prompts['review2'] = self._select_random_variant(review2_variants)
        
        review3_variants = [
            f"professional automotive team, skilled mechanics, excellent car service",
            f"car dealership staff, experienced automotive professionals, quality service",
            f"auto service team, qualified technicians, professional uniforms"
        ]
        prompts['review3'] = self._select_random_variant(review3_variants)
        
        prompts['favicon'] = "car icon, automotive symbol, simple vehicle logo design"
        
        return prompts
    
    def _generate_medical_prompts(self, business_type):
        """Специализированные промпты для медицины"""
        prompts = {}
        
        main_variants = [
            f"modern dental clinic exterior, medical center building, professional healthcare",
            f"medical office entrance, clean professional healthcare facility",
            f"dental practice front view, modern medical building design"
        ]
        prompts['main'] = self._select_random_variant(main_variants)
        
        about1_variants = [
            f"dental office interior, modern dental chair, professional medical equipment",
            f"medical consultation room, clean healthcare environment, modern facilities",
            f"dental clinic waiting area, comfortable medical office design"
        ]
        prompts['about1'] = self._select_random_variant(about1_variants)
        
        about2_variants = [
            f"dentist working with patient, professional dental care, medical precision",
            f"medical consultation process, healthcare professional examining patient",
            f"dental treatment procedure, skilled dentist, professional healthcare"
        ]
        prompts['about2'] = self._select_random_variant(about2_variants)
        
        about3_variants = [
            f"perfect dental results, healthy smile, professional dental care outcome",
            f"successful medical treatment, patient health improvement, quality healthcare",
            f"excellent dental work, satisfied patient, professional medical results"
        ]
        prompts['about3'] = self._select_random_variant(about3_variants)
        
        review1_variants = [
            f"happy patient after dental treatment, satisfied smile, quality healthcare",
            f"pleased medical patient, successful treatment results, healthcare satisfaction",
            f"grateful patient, excellent medical care experience, positive outcome"
        ]
        prompts['review1'] = self._select_random_variant(review1_variants)
        
        review2_variants = [
            f"medical consultation, doctor explaining treatment options to patient",
            f"dental consultation meeting, professional healthcare advice, patient care",
            f"healthcare professional consultation, medical expertise, patient guidance"
        ]
        prompts['review2'] = self._select_random_variant(review2_variants)
        
        review3_variants = [
            f"medical team, professional healthcare staff, quality patient care",
            f"dental clinic team, experienced medical professionals, healthcare excellence",
            f"healthcare specialists, qualified medical staff, professional medical service"
        ]
        prompts['review3'] = self._select_random_variant(review3_variants)
        
        prompts['favicon'] = "medical cross icon, healthcare symbol, dental logo design"
        
        return prompts
    
    def _generate_food_prompts(self, business_type):
        """Специализированные промпты для общепита"""
        prompts = {}
        
        main_variants = [
            f"cozy coffee shop exterior, cafe storefront, welcoming entrance",
            f"modern restaurant facade, elegant dining establishment, attractive exterior",
            f"charming cafe building, coffee shop front view, inviting atmosphere"
        ]
        prompts['main'] = self._select_random_variant(main_variants)
        
        about1_variants = [
            f"coffee shop interior, cozy seating area, warm cafe atmosphere",
            f"restaurant dining room, elegant table setting, comfortable dining space",
            f"cafe interior design, modern coffee bar, relaxing environment"
        ]
        prompts['about1'] = self._select_random_variant(about1_variants)
        
        about2_variants = [
            f"barista making coffee, professional coffee preparation, skilled brewing",
            f"chef cooking in restaurant kitchen, culinary expertise, food preparation",
            f"cafe staff serving customers, professional food service, hospitality"
        ]
        prompts['about2'] = self._select_random_variant(about2_variants)
        
        about3_variants = [
            f"delicious coffee and pastries, high quality cafe offerings, food presentation",
            f"gourmet restaurant dishes, culinary excellence, fine dining presentation",
            f"artisan coffee drinks, premium cafe products, beautiful food styling"
        ]
        prompts['about3'] = self._select_random_variant(about3_variants)
        
        review1_variants = [
            f"happy cafe customer enjoying coffee, satisfied dining experience",
            f"pleased restaurant guest, excellent meal experience, culinary satisfaction",
            f"delighted coffee shop visitor, positive cafe experience, customer joy"
        ]
        prompts['review1'] = self._select_random_variant(review1_variants)
        
        review2_variants = [
            f"friendly cafe service, barista recommending drinks, personalized attention",
            f"restaurant consultation, waiter explaining menu, professional food service",
            f"coffee shop consultation, expert coffee recommendations, customer guidance"
        ]
        prompts['review2'] = self._select_random_variant(review2_variants)
        
        review3_variants = [
            f"professional cafe team, skilled baristas, excellent coffee service",
            f"restaurant staff, experienced culinary team, quality food service",
            f"coffee shop employees, friendly service team, hospitality professionals"
        ]
        prompts['review3'] = self._select_random_variant(review3_variants)
        
        prompts['favicon'] = "coffee cup icon, cafe symbol, restaurant logo design"
        
        return prompts
    
    def _generate_beauty_prompts(self, business_type):
        """Специализированные промпты для салонов красоты"""
        prompts = {}
        
        main_variants = [
            f"modern beauty salon exterior, stylish salon front, professional beauty services",
            f"barbershop storefront, classic barber pole, traditional grooming establishment",
            f"elegant beauty spa entrance, luxury salon design, premium beauty services"
        ]
        prompts['main'] = self._select_random_variant(main_variants)
        
        about1_variants = [
            f"beauty salon interior, modern styling stations, elegant salon design",
            f"barbershop interior, classic barber chairs, traditional grooming atmosphere",
            f"spa treatment room, relaxing beauty environment, luxurious salon space"
        ]
        prompts['about1'] = self._select_random_variant(about1_variants)
        
        about2_variants = [
            f"hairstylist cutting hair, professional beauty service, skilled styling",
            f"barber grooming client, traditional barbering techniques, expert grooming",
            f"beauty treatment process, professional cosmetologist, quality beauty care"
        ]
        prompts['about2'] = self._select_random_variant(about2_variants)
        
        about3_variants = [
            f"perfect hairstyle result, beautiful styling outcome, professional beauty work",
            f"satisfied grooming results, excellent barbering, quality men's grooming",
            f"stunning beauty transformation, professional salon results, beauty excellence"
        ]
        prompts['about3'] = self._select_random_variant(about3_variants)
        
        review1_variants = [
            f"happy salon client, satisfied with new hairstyle, beauty service satisfaction",
            f"pleased barbershop customer, excellent grooming experience, men's satisfaction",
            f"delighted beauty client, transformation satisfaction, positive beauty experience"
        ]
        prompts['review1'] = self._select_random_variant(review1_variants)
        
        review2_variants = [
            f"beauty consultation, stylist discussing hair options with client",
            f"barbershop consultation, barber explaining grooming services, professional advice",
            f"salon consultation meeting, beauty expert guidance, personalized beauty care"
        ]
        prompts['review2'] = self._select_random_variant(review2_variants)
        
        review3_variants = [
            f"professional salon team, skilled stylists, excellent beauty service",
            f"barbershop staff, experienced barbers, quality grooming professionals",
            f"beauty salon specialists, qualified cosmetologists, professional beauty care"
        ]
        prompts['review3'] = self._select_random_variant(review3_variants)
        
        prompts['favicon'] = "scissors icon, beauty symbol, salon logo design"
        
        return prompts
    
    def _generate_universal_prompts(self, business_type):
        """Универсальные промпты для любого бизнеса"""
        prompts = {}
        
        main_variants = [
            f"modern {business_type} exterior view, professional building design",
            f"elegant {business_type} entrance, welcoming business atmosphere",
            f"contemporary {business_type} facility, modern commercial architecture"
        ]
        prompts['main'] = self._select_random_variant(main_variants)
        
        about1_variants = [
            f"{business_type} interior design, professional workspace, modern facilities",
            f"inside {business_type}, comfortable customer area, organized layout",
            f"{business_type} working environment, professional equipment, clean design"
        ]
        prompts['about1'] = self._select_random_variant(about1_variants)
        
        about2_variants = [
            f"professional working at {business_type}, high quality service delivery",
            f"{business_type} service process, skilled professional, attention to detail",
            f"expert at work, {business_type} expertise, professional precision"
        ]
        prompts['about2'] = self._select_random_variant(about2_variants)
        
        about3_variants = [
            f"high quality {business_type} results, professional outcome, customer satisfaction",
            f"excellent {business_type} service results, premium quality work",
            f"successful {business_type} project, professional excellence, quality delivery"
        ]
        prompts['about3'] = self._select_random_variant(about3_variants)
        
        review1_variants = [
            f"happy {business_type} customer, satisfied client, positive experience",
            f"pleased customer with {business_type} service, satisfaction and joy",
            f"delighted {business_type} client, excellent service experience"
        ]
        prompts['review1'] = self._select_random_variant(review1_variants)
        
        review2_variants = [
            f"professional {business_type} consultation, expert advice, customer guidance",
            f"{business_type} service consultation, professional recommendations",
            f"customer meeting at {business_type}, personalized professional attention"
        ]
        prompts['review2'] = self._select_random_variant(review2_variants)
        
        review3_variants = [
            f"professional {business_type} team, skilled staff, excellent service",
            f"{business_type} specialists, experienced professionals, quality team",
            f"qualified {business_type} staff, professional service team, customer care"
        ]
        prompts['review3'] = self._select_random_variant(review3_variants)
        
        prompts['favicon'] = f"simple {business_type} icon, professional symbol, business logo"
        
        return prompts
    
    def _select_random_variant(self, variants):
        """Выбирает случайный вариант из списка"""
        import random
        return random.choice(variants)


class ThematicImageGenerator:
    """Упрощенный генератор для совместимости"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.image_generator = ImageGenerator(silent_mode=silent_mode)
    
    def generate_single_image(self, prompt, image_name, output_dir):
        """Генерирует одно изображение"""
        return self.image_generator._generate_image_via_pollinations(
            prompt, image_name, output_dir
        )
    
    def get_theme_prompts(self, theme_input):
        """Получает промпты для темы - для совместимости с GUI"""
        # Генерируем умные промпты напрямую
        prompts, theme_data = self.image_generator._generate_prompts(theme_input)
        
        return prompts, theme_data
    
    def add_randomization(self, prompt):
        """Добавляет рандомизацию к промпту для обычных изображений"""
        import random
        
        # Стили для рандомизации
        styles = [
            "professional", "modern", "clean", "elegant", "minimalist",
            "sophisticated", "premium", "high-quality", "detailed"
        ]
        
        # Цветовые схемы
        colors = [
            "vibrant colors", "soft colors", "natural tones", "warm palette",
            "cool tones", "balanced colors", "harmonious colors"
        ]
        
        # Композиция
        composition = [
            "well-composed", "balanced composition", "dynamic composition",
            "centered composition", "artistic composition"
        ]
        
        selected_style = random.choice(styles)
        selected_color = random.choice(colors) 
        selected_comp = random.choice(composition)
        
        enhanced_prompt = f"{prompt}, {selected_style}, {selected_color}, {selected_comp}, photorealistic"
        
        return enhanced_prompt
    
    def add_favicon_randomization(self, prompt):
        """Добавляет рандомизацию специально для фавиконов"""
        import random
        
        # Стили для фавиконов
        favicon_styles = [
            "flat design", "minimal design", "geometric design", "simple icon",
            "clean symbol", "modern icon", "vector style", "logo style"
        ]
        
        # Цвета для фавиконов
        favicon_colors = [
            "bold colors", "single color", "duo-tone", "monochrome",
            "bright accent", "professional colors"
        ]
        
        selected_style = random.choice(favicon_styles)
        selected_color = random.choice(favicon_colors)
        
        enhanced_prompt = f"{prompt}, {selected_style}, {selected_color}, icon, symbol"
        
        return enhanced_prompt