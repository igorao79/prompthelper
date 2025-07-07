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

class IntelligentContextAnalyzer:
    """Умный анализатор контекста бизнеса с использованием интернета"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.cache = {}  # Кэш для результатов поиска
        
    def search_business_context(self, query):
        """Поиск информации о бизнесе в интернете"""
        try:
            # Формируем поисковый запрос
            search_query = f"{query} бизнес деятельность описание"
            
            if not self.silent_mode:
                print(f"🔍 Ищу информацию о: {query}")
            
            # Проверяем кэш
            if query in self.cache:
                if not self.silent_mode:
                    print("📋 Использую кэшированные данные")
                return self.cache[query]
            
            # Поиск через различные источники
            context_data = self._multi_source_search(search_query)
            
            # Сохраняем в кэш
            self.cache[query] = context_data
            
            return context_data
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка поиска: {e}")
            return self._dynamic_fallback_analysis(query)
    
    def _multi_source_search(self, query):
        """Поиск по нескольким источникам"""
        sources_data = []
        
        # 1. Поиск через Google (бесплатный API)
        google_data = self._search_google_custom(query)
        if google_data:
            sources_data.extend(google_data)
        
        # 2. Поиск через DuckDuckGo
        duckduck_data = self._search_duckduckgo(query)
        if duckduck_data:
            sources_data.extend(duckduck_data)
        
        # 3. Поиск в Wikipedia
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
            if response.status_code == 200:
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
                
                return results
                
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка DuckDuckGo: {e}")
            return None
    
    def _search_wikipedia(self, query):
        """Поиск в Wikipedia"""
        try:
            # Поиск статей
            search_url = "https://ru.wikipedia.org/api/rest_v1/page/summary/" + quote(query)
            
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': data.get('extract', ''),
                    'source': 'Wikipedia'
                }
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка Wikipedia: {e}")
            return None
    
    def _search_google_custom(self, query):
        """Поиск через Google Custom Search API (если доступен)"""
        # Здесь можно добавить Google Custom Search API
        # Для демонстрации используем простой парсинг
        return None
    
    def _analyze_search_results(self, sources_data, original_query):
        """Анализ результатов поиска для определения контекста"""
        if not sources_data:
            return self._dynamic_fallback_analysis(original_query)
        
        # Собираем весь текст для анализа
        combined_text = ""
        for source in sources_data:
            combined_text += f" {source.get('title', '')} {source.get('description', '')}"
        
        # Динамический анализ на основе найденной информации
        context = self._dynamic_context_extraction(combined_text, original_query)
        
        if not self.silent_mode:
            print(f"📊 Найдено источников: {len(sources_data)}")
            print(f"🎯 Определен тип бизнеса: {context['business_type']}")
            print(f"🏢 Среда: {context['environment']}")
        
        return context
    
    def _dynamic_context_extraction(self, text, query):
        """Динамическое извлечение контекста из текста без фиксированных категорий"""
        text_lower = text.lower()
        query_lower = query.lower()
        combined_text = f"{text_lower} {query_lower}".strip()
        
        # Анализируем ключевые слова для определения типа деятельности
        activity_indicators = {
            'education': ['курсы', 'обучение', 'школа', 'учеба', 'преподавание', 'изучение', 'образование'],
            'service': ['услуги', 'сервис', 'обслуживание', 'консультация', 'помощь'],
            'medical': ['медицин', 'здоровье', 'лечение', 'диагностика', 'клиника', 'врач'],
            'automotive': ['авто', 'машин', 'автомобил', 'транспорт'],
            'food': ['кулинар', 'еда', 'готовк', 'повар', 'ресторан', 'кафе', 'питание'],
            'beauty': ['красота', 'салон', 'косметол', 'парикмахер', 'маникюр'],
            'fitness': ['фитнес', 'спорт', 'тренировк', 'тренер', 'спортзал'],
            'tech': ['технолог', 'компьютер', 'программир', 'сайт', 'веб', 'it'],
            'art': ['искусств', 'творчеств', 'художеств', 'дизайн', 'рисован'],
            'music': ['музык', 'инструмент', 'песн', 'концерт'],
            'photography': ['фото', 'съемк', 'камер'],
            'construction': ['строител', 'ремонт', 'стройк', 'отделк']
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
        # Извлекаем существительные и прилагательные
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
            'medical': 'medical facility', 
            'automotive': 'automotive facility',
            'food': 'culinary environment',
            'beauty': 'beauty salon',
            'fitness': 'fitness facility',
            'tech': 'modern office',
            'art': 'creative studio',
            'music': 'music studio',
            'photography': 'photography studio',
            'construction': 'construction site'
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
        
        # Простой анализ на основе запроса пользователя
        details = self._extract_dynamic_details("", query_lower)
        
        # Определяем тип деятельности по ключевым словам
        if any(word in query_lower for word in ['кулинар', 'повар', 'готовк']):
            activity = 'food'
            environment = 'professional kitchen'
        elif any(word in query_lower for word in ['фото', 'съемк']):
            activity = 'photography'
            environment = 'photography studio'
        elif any(word in query_lower for word in ['музык', 'инструмент']):
            activity = 'music'
            environment = 'music studio'
        elif any(word in query_lower for word in ['автосервис', 'ремонт авто', 'диагностика авто']):
            activity = 'automotive'
            environment = 'automotive workshop'
        elif any(word in query_lower for word in ['стоматолог', 'зубы']):
            activity = 'medical'
            environment = 'dental office'
        else:
            activity = 'general'
            environment = 'professional office'
        
        return {
            'category': 'dynamic_business',
            'business_type': activity,
            'confidence': 0.5,
            'details': details,
            'keywords': query.split()[:5],
            'environment': environment,
            'theme_description': details[0] if details else query
        }

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
            print("✨ Умная генерация изображений с анализом через интернет")

    def detect_theme_from_input(self, user_input):
        """Определяет тематику с помощью интернет-поиска"""
        context_data = self.context_analyzer.search_business_context(user_input)
        return context_data['category'], context_data

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
        
        # Базовые элементы для промптов
        main_theme = theme_description if theme_description else original_input
        primary_detail = details[0] if details else business_type
        secondary_detail = details[1] if len(details) > 1 else 'professional service'
        tertiary_detail = details[2] if len(details) > 2 else 'consultation'
        
        # Адаптируем среду под конкретную тематику
        if business_type == 'food' and 'курс' in original_input.lower():
            adapted_environment = 'professional culinary school kitchen with chef instructors'
        elif business_type == 'photography' and 'курс' in original_input.lower():
            adapted_environment = 'photography studio classroom with professional equipment'
        elif business_type == 'music' and 'курс' in original_input.lower():
            adapted_environment = 'music education studio with various instruments'
        elif business_type == 'automotive' and 'ремонт' in original_input.lower():
            adapted_environment = 'professional automotive repair workshop'
        elif business_type == 'automotive' and 'салон' in original_input.lower():
            adapted_environment = 'luxury car dealership showroom'
        elif business_type == 'medical' and 'стомат' in original_input.lower():
            adapted_environment = 'modern dental clinic office'
        else:
            adapted_environment = environment
        
        return {
            "main": f"{adapted_environment}, {primary_detail} activity, professional {business_type} environment",
            "about1": f"{primary_detail} demonstration, professional {business_type} service, expert at work",
            "about2": f"{adapted_environment} equipment and tools, {secondary_detail} process, professional setup",
            "about3": f"{main_theme} consultation area, {tertiary_detail} service, client interaction",
            "review1": f"satisfied customer after {primary_detail} service, successful {main_theme} experience, happy client",
            "review2": f"professional {business_type} specialist, expert {secondary_detail} service, customer satisfaction",
            "review3": f"group of happy customers, {main_theme} success stories, positive service experience",
            "favicon": f"{primary_detail} icon, {business_type} symbol, professional design, transparent background"
        }
        
        # Для других категорий генерируем контекстные промпты (УДАЛИТЬ - старый код)
        elif category == 'automotive_sales':
            return {
                "main": "luxury car dealership showroom, multiple vehicles displayed, professional automotive sales environment",
                "about1": "elegant sports car in showroom spotlight, premium vehicle presentation, automotive sales",
                "about2": "professional car salesperson with customer, vehicle consultation, automotive sales process",
                "about3": "luxury car interior showcase, premium features demonstration, automotive sales detail",
                "review1": "happy family with new car keys, successful vehicle purchase, automotive sales satisfaction",
                "review2": "businessman signing car purchase documents, automotive sales transaction, professional service",
                "review3": "satisfied customers with their new vehicles, automotive dealership success stories",
                "favicon": "car sales icon, automotive dealership symbol, vehicle key, modern design, transparent background"
            }
        
        elif category == 'dental_service':
            return {
                "main": "modern dental clinic interior, dental chairs, professional dental office environment",
                "about1": "dentist examining patient, dental procedure, professional dental care",
                "about2": "dental equipment and tools, modern dental technology, clinical dental instruments",
                "about3": "dental consultation room, oral health examination, professional dental service",
                "review1": "patient with perfect smile after dental treatment, dental care success, happy smile",
                "review2": "satisfied family after dental checkup, professional dental care, healthy teeth",
                "review3": "dental patient consultation, oral health satisfaction, professional dental advice",
                "favicon": "tooth icon, dental symbol, dental care, clean medical design, transparent background"
            }
        
        elif category == 'medical_service':
            return {
                "main": "modern medical clinic interior, clean professional environment, medical equipment",
                "about1": "professional doctor in white coat, medical expertise, confident portrait",
                "about2": "modern medical equipment, healthcare technology, clinical setting",
                "about3": "medical consultation room, doctor-patient interaction, professional care",
                "review1": "recovered patient with doctor, successful treatment, grateful expression",
                "review2": "healthy family after medical care, satisfied patients, medical success",
                "review3": "elderly patient with caring doctor, medical compassion, healthcare quality",
                "favicon": "medical cross icon, healthcare symbol, clean design, professional, transparent background"
            }
        
        elif category == 'beauty_service':
            return {
                "main": "luxury beauty salon interior, elegant design, professional atmosphere",
                "about1": "professional makeup artist working, beauty transformation, artistic process",
                "about2": "spa treatment room, relaxing atmosphere, wellness and beauty",
                "about3": "hairstyling session, professional hairdresser, beauty salon environment",
                "review1": "beautiful woman after salon treatment, glowing skin, satisfied client",
                "review2": "elegant lady with new hairstyle, confident and happy, beauty success",
                "review3": "group of women enjoying beauty services, friendship and self-care",
                "favicon": "lipstick icon, beauty symbol, elegant design, feminine style, transparent background"
            }
        
        elif category == 'fitness_service':
            return {
                "main": "modern fitness gym interior, equipment visible, bright lighting, spacious",
                "about1": "professional gym equipment, dumbbells and machines, clean modern design",
                "about2": "personal trainer working with client, professional fitness coaching",
                "about3": "group fitness class, people exercising, energetic atmosphere",
                "review1": "fit athletic man after workout, happy expression, gym background",
                "review2": "athletic woman in sportswear, successful fitness transformation, confident pose",
                "review3": "group of people celebrating fitness goals, happy healthy lifestyle",
                "favicon": "dumbbell icon, fitness symbol, simple modern design, vector style, transparent background"
            }
        
        elif category == 'tech_service':
            return {
                "main": "modern tech office, computers and gadgets, innovative workspace environment",
                "about1": "cutting-edge technology devices, smartphones and laptops, tech innovation",
                "about2": "software development team working, coding and collaboration, tech environment",
                "about3": "server room or data center, technology infrastructure, digital innovation",
                "review1": "satisfied tech professional, successful IT specialist, confident expression",
                "review2": "entrepreneur with tech startup success, innovation achievement, modern office",
                "review3": "team of developers celebrating project success, tech collaboration",
                "favicon": "gear or chip icon, technology symbol, modern design, digital style, transparent background"
            }
        
        elif category == 'construction':
            return {
                "main": "construction site with workers, heavy machinery, building project in progress, professional construction",
                "about1": "construction workers with blueprints, architectural planning, building project consultation",
                "about2": "construction equipment and machinery, building tools, professional construction site",
                "about3": "completed building project, construction success, architectural achievement",
                "review1": "satisfied homeowner with construction team, building project completion, happy customer",
                "review2": "construction manager explaining project to client, professional building consultation",
                "review3": "family in front of completed house, construction project success, building satisfaction",
                "favicon": "construction icon, building symbol, hard hat and tools, industrial design, transparent background"
            }
        
        elif category == 'restaurant_service':
            return {
                "main": "elegant restaurant interior, dining tables, warm ambient lighting",
                "about1": "gourmet dish presentation, fine dining, professional food photography",
                "about2": "chef cooking in professional kitchen, culinary expertise, action shot",
                "about3": "wine collection and bar area, premium beverages, elegant atmosphere",
                "review1": "satisfied customer enjoying meal, happy dining experience, restaurant setting",
                "review2": "couple on romantic dinner, elegant restaurant ambiance, joyful moment",
                "review3": "family dinner celebration, happy customers, restaurant atmosphere",
                "favicon": "fork and knife icon, restaurant symbol, elegant design, minimalist, transparent background"
            }
        
        elif category == 'culinary_education':
            return {
                "main": "professional cooking school kitchen, chef instructors and students, culinary training environment",
                "about1": "chef instructor demonstrating cooking techniques, professional kitchen, culinary education",
                "about2": "students practicing cooking skills, hands-on culinary training, professional cooking equipment",
                "about3": "beautifully plated dishes created by students, culinary arts showcase, food presentation",
                "review1": "proud culinary student with chef hat, successful cooking course completion, kitchen background",
                "review2": "group of culinary students celebrating graduation, chef certificates, culinary achievement",
                "review3": "satisfied student chef presenting signature dish, culinary success story, professional kitchen",
                "favicon": "chef hat icon, culinary symbol, cooking cap, transparent background"
            }
        
        elif category == 'language_courses':
            return {
                "main": "modern language classroom, international flags, interactive learning environment",
                "about1": "language teacher with world map, multicultural learning, language education",
                "about2": "students practicing conversation, language exchange, communication skills",
                "about3": "language learning materials and books, study resources, educational tools",
                "review1": "confident student speaking foreign language, language learning success, classroom setting",
                "review2": "multicultural group of language students, international communication, language diversity",
                "review3": "happy student with language certificate, achievement in language learning, proud moment",
                "favicon": "speech bubble icon, language symbol, communication bubble, transparent background"
            }
        
        elif category == 'music_education':
            return {
                "main": "music studio with various instruments, piano, guitars, professional music learning environment",
                "about1": "music teacher with student at piano, music lesson, instrumental instruction",
                "about2": "recording studio equipment, microphones, music production, audio technology",
                "about3": "sheet music and musical notes, music theory, composition materials",
                "review1": "talented student performing on stage, musical achievement, concert performance",
                "review2": "music students in ensemble, group performance, musical collaboration",
                "review3": "proud music graduate with instrument, musical education success, artistic accomplishment",
                "favicon": "musical note icon, music symbol, treble clef, transparent background"
            }
        
        elif category == 'art_education':
            return {
                "main": "bright art studio with easels, paintings, creative workspace, artistic learning environment",
                "about1": "art teacher demonstrating painting technique, artistic instruction, creative process",
                "about2": "art supplies and brushes, painting materials, colorful palette, artistic tools",
                "about3": "student artwork gallery, creative exhibitions, artistic achievements showcase",
                "review1": "proud art student with their painting, artistic success, studio background",
                "review2": "group of art students working on projects, creative collaboration, artistic community",
                "review3": "satisfied artist with completed artwork, creative achievement, artistic fulfillment",
                "favicon": "paint brush icon, art symbol, creative tool, transparent background"
            }
        
        elif category == 'photography_courses':
            return {
                "main": "photography studio with professional lighting, cameras, photo equipment, creative workspace",
                "about1": "photography instructor with professional camera, teaching photography techniques",
                "about2": "portrait photography session, model and photographer, studio lighting setup",
                "about3": "photo editing workstation, computer with photo software, digital photography workflow",
                "review1": "photographer with professional camera equipment, photography course graduate, confident pose",
                "review2": "photography student capturing perfect shot, creative moment, artistic photography",
                "review3": "group of photography students on photo walk, learning expedition, camera equipment",
                "favicon": "camera icon, photography symbol, lens aperture, transparent background"
            }
        
        elif category == 'business_education':
            return {
                "main": "modern business classroom, presentation screen, professional learning environment",
                "about1": "business instructor presenting to students, professional education, business concepts",
                "about2": "business students in group discussion, teamwork, collaborative learning",
                "about3": "business plan documents and charts, entrepreneurship materials, strategic planning",
                "review1": "successful business graduate in professional attire, entrepreneurial achievement",
                "review2": "business team celebrating project success, professional accomplishment, business education",
                "review3": "confident entrepreneur with business plan, startup success, business development",
                "favicon": "briefcase icon, business symbol, professional bag, transparent background"
            }
        
        elif category == 'general_education':
            return {
                "main": "modern classroom or lecture hall, students and teacher, educational environment",
                "about1": "professional teacher explaining lesson, whiteboard, educational setting",
                "about2": "students studying together, collaborative learning, modern classroom",
                "about3": "graduation ceremony, academic success, celebration of education",
                "review1": "successful graduate with diploma, proud achievement, academic attire",
                "review2": "happy student with books, educational success, confident expression",
                "review3": "group of successful students, teamwork in education, celebration",
                "favicon": "graduation cap icon, education symbol, academic design, simple, transparent background"
            }
        
        # Для других категорий генерируем контекстные промпты
        return self._generate_contextual_prompts(category, environment, details, keywords, original_input)
    
    def _generate_contextual_prompts(self, category, environment, details, keywords, original_input):
        """Генерация контекстных промптов"""
        
        # Базовые элементы для промптов
        main_activity = keywords[0] if keywords else category.replace('_', ' ')
        specific_detail = details[0] if details else 'professional service'
        service_type = details[1] if len(details) > 1 else 'consultation'
        
        return {
            "main": f"professional {environment}, {main_activity} workspace, modern business interior, overview shot",
            "about1": f"{main_activity} professional demonstration, {specific_detail} process, expert at work",
            "about2": f"{environment} equipment and tools, {service_type} setup, professional workplace",
            "about3": f"{main_activity} consultation area, client service environment, professional meeting",
            "review1": f"satisfied customer after {main_activity} service, successful {specific_detail}, happy client",
            "review2": f"professional {main_activity} consultation, expert advice, customer satisfaction",
            "review3": f"group of happy customers, {main_activity} success stories, positive service experience",
            "favicon": f"{main_activity} icon, {category.replace('_', ' ')} symbol, professional minimalist design, transparent background"
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

class ImageGenerator:
    def __init__(self, silent_mode=False):
        """
        Простой и надежный генератор изображений без вотермарков
        
        Args:
            silent_mode (bool): Если True, не выводит сообщения в консоль
        """
        self.silent_mode = silent_mode
        
        if not silent_mode:
            print("🎨 AI Генератор Изображений")
            print("=" * 50)
            print("✨ Высококачественные изображения без вотермарков")
        
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
    
    def generate_via_dezgo(self, prompt):
        """Генерация через DezGO API - без вотермарков"""
        try:
            enhanced_prompt = f"{prompt}, high quality, detailed, masterpiece"
            
            if not self.silent_mode:
                print(f"📝 Промпт: {enhanced_prompt}")
                print("⏳ Генерация через DezGO (без вотермарков)...")
            
            api_url = "https://api.dezgo.com/text2image"
            
            data = {
                'prompt': enhanced_prompt,
                'model': 'epic_realism',
                'width': 1024,
                'height': 1024,
                'guidance': 7.5,
                'steps': 25,
                'format': 'png'
            }
            
            response = requests.post(api_url, data=data, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            else:
                if not self.silent_mode:
                    print(f"❌ DezGO недоступен: {response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка DezGO: {e}")
            return None
    
    def generate_via_huggingface_clean(self, prompt):
        """Улучшенный метод через HF без вотермарков"""
        try:
            enhanced_prompt = f"{prompt}, high quality, detailed, masterpiece, professional photography"
            
            if not self.silent_mode:
                print(f"📝 Промпт: {enhanced_prompt}")
                print("⏳ Генерация через Hugging Face...")
            
            # Используем более современную модель
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            
            headers = {"Content-Type": "application/json"}
            data = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "negative_prompt": "watermark, text, logo, signature, blurry, low quality",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "width": 1024,
                    "height": 1024
                }
            }
            
            response = requests.post(api_url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            elif response.status_code == 503:
                if not self.silent_mode:
                    print("⏳ Модель загружается, попробуйте через минуту")
                return None
            else:
                if not self.silent_mode:
                    print(f"❌ HF недоступен: {response.status_code}")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка HF: {e}")
            return None

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
            
            # Добавляем рандомизацию для уникальности (кроме фавиконки)
            if image_name != "favicon":
                prompt = thematic_gen.add_randomization(prompt)
            
            # Специальные настройки для фавиконки
            if image_name == "favicon":
                prompt += ", icon design, vector style, flat design, simple logo, transparent PNG, alpha channel, no background, white cutout, isolated on transparent"
            
            # Выбираем метод генерации
            if method == "2":
                image = self.generate_via_dezgo(prompt)
            elif method == "3":
                image = self.generate_via_huggingface_clean(prompt)
            else:
                image = self.generate_via_pollinations_clean(prompt)
            
            if image:
                # Для фавиконки делаем размер 512x512 (потом можно уменьшить)
                if image_name == "favicon":
                    image = image.resize((512, 512), Image.Resampling.LANCZOS)
                
                filename = os.path.join(media_dir, f"{image_name}.png")
                image.save(filename)
                results[image_name] = filename
                
                if not self.silent_mode:
                    print(f"✅ Сохранено: {filename}")
                
                # Небольшая задержка между запросами
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
    
    print("\n🌟 Выберите режим работы:")
    print("1. Одиночная генерация изображения")
    print("2. Тематический набор для лендинга (8 изображений)")
    print()
    
    mode = input("Выберите режим (1-2): ").strip()
    
    if mode == "2":
        # Тематический режим
        print("\n🎯 РЕЖИМ: Генерация тематического набора")
        print("=" * 50)
        print("Примеры тематик:")
        print("  • автосалон, недвижимость, фитнес")
        print("  • ресторан, образование, медицина")
        print("  • красота, технологии, или любая другая")
        print()
        
        theme_input = input("Введите тематику вашего бизнеса: ").strip()
        
        if not theme_input:
            print("❌ Тематика не указана!")
            return
        
        print("\n🎨 Выберите метод генерации:")
        print("1. Pollinations + удаление вотермарка (рекомендуется)")
        print("2. DezGO (чистые изображения)")
        print("3. Hugging Face SDXL")
        
        method_choice = input("Выбор (1-3 или Enter для метода 1): ").strip()
        
        # Генерируем набор
        results = generator.generate_thematic_set(theme_input, "media", method_choice)
        
        print(f"\n💡 Теперь вы можете использовать созданные изображения в своем лендинге!")
        print("   Просто скопируйте папку 'media' в ваш проект.")
        
    else:
        # Обычный режим (одиночная генерация)
        print("\n🎨 РЕЖИМ: Одиночная генерация")
        print("=" * 40)
        
        while True:
            print("\n📝 Введите описание изображения:")
            prompt = input("Промпт (или 'выход' для завершения): ").strip()
            
            if prompt.lower() in ['выход', 'exit', 'quit']:
                print("👋 До свидания!")
                break
                
            if not prompt:
                continue
            
            # Переводим если нужно
            if any(ord(char) > 127 for char in prompt):
                english_prompt = generator.translate_prompt(prompt)
                print(f"🔄 Перевод: {english_prompt}")
            else:
                english_prompt = prompt
            
            # Выбор метода
            print("\n🎨 Выберите метод:")
            print("1. Pollinations + удаление вотермарка (рекомендуется)")
            print("2. DezGO (чистые изображения)")
            print("3. Hugging Face SDXL")
            
            method_choice = input("Выбор (1-3 или Enter для метода 1): ").strip()
            
            # Генерируем
            if method_choice == "2":
                image = generator.generate_via_dezgo(english_prompt)
            elif method_choice == "3":
                image = generator.generate_via_huggingface_clean(english_prompt)
            else:
                image = generator.generate_via_pollinations_clean(english_prompt)
            
            if image:
                os.makedirs("generated_images", exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_images/image_{timestamp}.png"
                image.save(filename)
                
                print(f"\n🎉 Готово! Изображение сохранено: {filename}")
                
                # Спрашиваем, хочет ли пользователь продолжить
                continue_choice = input("\nСоздать еще одно изображение? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no', 'нет']:
                    break
            else:
                print("❌ Не удалось создать изображение")

if __name__ == "__main__":
    main()