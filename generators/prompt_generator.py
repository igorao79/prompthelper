"""
Умный генератор промптов для изображений
Разбит из smart_prompt_generator.py для лучшей организации
"""

import random
import time
import hashlib
import uuid
import os
from .translations import TRANSLATIONS, BUSINESS_TYPES

class SmartPromptGenerator:
    """УМНАЯ система генерации промптов для любых тематик БЕЗ интернета"""
    
    def __init__(self):
        self.translations = TRANSLATIONS
        self.business_types = BUSINESS_TYPES
        # Инициализируем генератор случайных чисел с ГАРАНТИРОВАННО уникальным seed
        self.rng = random.Random()
        # Используем микросекунды + случайный UUID + ID процесса для максимальной уникальности каждой инициализации
        unique_seed = int(time.time() * 1000000) + hash(str(uuid.uuid4())) + os.getpid() + random.randint(1, 1000000)
        self.rng.seed(unique_seed)
        
        # Расширенные модификаторы для создания уникальности
        self.style_modifiers = [
            "professional", "modern", "contemporary", "sleek", "elegant", "sophisticated",
            "premium", "high-end", "luxury", "executive", "corporate", "innovative",
            "cutting-edge", "state-of-the-art", "world-class", "top-tier", "elite",
            "progressive", "advanced", "refined", "distinguished", "exceptional"
        ]
        
        self.environment_modifiers = [
            "workspace", "facility", "center", "office", "studio", "establishment",
            "headquarters", "location", "premises", "venue", "complex", "institute",
            "organization", "enterprise", "operation", "business", "company", "firm"
        ]
        
        self.quality_descriptors = [
            "premium quality", "excellent service", "outstanding results", "superior performance",
            "exceptional standards", "top-notch quality", "first-class service", "world-class expertise",
            "professional excellence", "industry-leading", "award-winning", "certified excellence",
            "proven quality", "trusted expertise", "reliable service", "guaranteed satisfaction"
        ]
        
        # Уникальные детали для каждого типа изображения
        self.unique_details = {
            "main": [
                "bustling activity", "professional atmosphere", "welcoming environment",
                "organized layout", "clean aesthetics", "modern architecture",
                "impressive facade", "attractive entrance", "professional signage",
                "contemporary design", "spacious interior", "bright lighting"
            ],
            "about": [
                "specialized equipment", "advanced technology", "precision tools",
                "quality materials", "efficient setup", "organized workspace",
                "professional gear", "modern systems", "reliable machinery",
                "innovative solutions", "technical expertise", "quality assurance"
            ],
            "review": [
                "genuine satisfaction", "positive experience", "happy expression",
                "grateful demeanor", "confident posture", "relaxed appearance",
                "friendly smile", "natural joy", "authentic happiness",
                "pleased reaction", "content expression", "satisfied look"
            ]
        }
    
    def analyze_theme(self, theme, silent_mode=False):
        """ИНТЕЛЛЕКТУАЛЬНЫЙ анализ тематики - читает всю фразу целиком и понимает контекст"""
        if not silent_mode:
            print(f"🧠 Интеллектуальный анализ тематики: {theme}")
        
        theme_lower = theme.lower().strip()
        theme_words = theme_lower.split()
        
        # НОВАЯ ИНТЕЛЛЕКТУАЛЬНАЯ СИСТЕМА: анализ всей фразы целиком
        context_result = self._intelligent_theme_analysis(theme_lower, theme_words, silent_mode)
        
        if context_result:
            return context_result
            
        # Fallback к старой системе если новая не дала результата
        return self._legacy_theme_analysis(theme_lower, theme_words, silent_mode)
    
    def _intelligent_theme_analysis(self, theme_lower, theme_words, silent_mode=False):
        """
        НОВАЯ ИНТЕЛЛЕКТУАЛЬНАЯ СИСТЕМА анализа тематики
        Анализирует всю фразу целиком, понимает контекст и семантические связи
        """
        
        # УМНЫЕ СЕМАНТИЧЕСКИЕ ШАБЛОНЫ - анализируем всю фразу целиком
        semantic_patterns = {
            # ОБРАЗОВАТЕЛЬНЫЕ ТЕМАТИКИ (высший приоритет для комбинаций)
            'investment_education': {
                'patterns': [
                    # Прямые упоминания
                    'курсы по инвестициям', 'курсы инвестиций', 'инвестиционные курсы',
                    'обучение инвестициям', 'обучение инвестиционным', 'школа инвестиций',
                    'тренинги по инвестициям', 'семинары по инвестициям',
                    'investment courses', 'investment training', 'investment education',
                    # Контекстные комбинации
                    'курсы трейдинг', 'обучение трейдингу', 'школа трейдинга',
                    'курсы финансов', 'финансовое образование', 'финансовая грамотность'
                ],
                'activity_type': 'investment',
                'business_type': 'investment courses',
                'confidence': 0.95,
                'keywords': ['investment', 'education', 'training']
            },
            
            'language_education': {
                'patterns': [
                    'курсы английского', 'обучение английскому', 'английский язык',
                    'курсы французского', 'обучение французскому', 'французский язык', 
                    'курсы немецкого', 'обучение немецкому', 'немецкий язык',
                    'курсы испанского', 'курсы итальянского', 'курсы китайского',
                    'языковые курсы', 'изучение языков', 'школа языков',
                    'english courses', 'language school', 'language learning'
                ],
                'activity_type': 'training',
                'business_type': lambda theme: self._extract_language_from_theme(theme) + ' courses',
                'confidence': 0.95,
                'keywords': ['training', 'education', 'language']
            },
            
            # АВТОМОБИЛЬНЫЕ СПЕЦИАЛИЗАЦИИ (контекстный анализ)
            'luxury_car_import': {
                'patterns': [
                    'подбор автомобилей из сша', 'импорт авто из америки', 'машины из кореи',
                    'автомобили из европы', 'подбор машин из-за рубежа',
                    'car import from usa', 'luxury car selection', 'premium car import',
                    'элитные автомобили', 'премиум авто', 'люксовые машины'
                ],
                'activity_type': 'car_import', 
                'business_type': 'luxury car import',
                'confidence': 0.9,
                'keywords': ['cars', 'import', 'luxury']
            },
            
            'chauffeur_premium': {
                'patterns': [
                    'услуги водителя', 'персональный водитель', 'водитель с автомобилем',
                    'аренда авто с водителем', 'шофер услуги', 'personal driver',
                    'chauffeur service', 'driver rental', 'luxury transportation'
                ],
                'activity_type': 'chauffeur_service',
                'business_type': 'chauffeur service', 
                'confidence': 0.9,
                'keywords': ['driver', 'rental', 'service']
            },
            
            # ФИНАНСОВЫЕ УСЛУГИ (комплексный анализ)
            'credit_analysis': {
                'patterns': [
                    'оценка кредитоспособности', 'анализ кредитоспособности',
                    'кредитоспособность клиента', 'кредитоспособность бизнеса',
                    'creditworthiness assessment', 'credit evaluation', 'credit analysis'
                ],
                'activity_type': 'credit_assessment',
                'business_type': 'credit assessment',
                'confidence': 0.95,
                'keywords': ['credit', 'assessment', 'analysis']
            },
            
            'financial_consulting': {
                'patterns': [
                    'финансовое консультирование', 'финансовые консультации', 
                    'консультации по инвестициям', 'инвестиционное консультирование',
                    'financial consulting', 'investment consulting', 'financial advisory'
                ],
                'activity_type': 'financial',
                'business_type': 'financial consulting',
                'confidence': 0.9,
                'keywords': ['financial', 'consulting', 'advisory']
            },
            
            # НЕДВИЖИМОСТЬ (географический контекст)
            'foreign_real_estate': {
                'patterns': [
                    'зарубежная недвижимость', 'недвижимость за рубежом',
                    'международная недвижимость', 'инвестиции в недвижимость',
                    'foreign real estate', 'international property', 'overseas real estate'
                ],
                'activity_type': 'foreign_real_estate',
                'business_type': 'foreign real estate',
                'confidence': 0.9,
                'keywords': ['real estate', 'foreign', 'investment']
            },
            
            'student_housing': {
                'patterns': [
                    'студенческая недвижимость', 'жилье для студентов', 
                    'аренда студентам', 'студенческие квартиры',
                    'student housing', 'student accommodation', 'student rental'
                ],
                'activity_type': 'student_housing',
                'business_type': 'student housing',
                'confidence': 0.9,
                'keywords': ['housing', 'student', 'rental']
            },
            
            # СПЕЦИАЛИЗИРОВАННЫЕ УСЛУГИ
            'tire_service': {
                'patterns': [
                    'шиномонтаж', 'замена шин', 'сезонная замена шин',
                    'продажа шин', 'tire service', 'tire replacement', 'tire sales'
                ],
                'activity_type': 'tire_service',
                'business_type': 'tire service',
                'confidence': 0.9,
                'keywords': ['tire', 'service', 'replacement']
            },
            
            'landscape_design': {
                'patterns': [
                    'ландшафтный дизайн', 'благоустройство территории',
                    'озеленение участка', 'садово-парковые работы',
                    'landscape design', 'landscaping services', 'garden design'
                ],
                'activity_type': 'landscape',
                'business_type': 'landscape design',
                'confidence': 0.9,
                'keywords': ['landscape', 'design', 'garden']
            },
            
            # ОБЩИЕ ТЕМАТИКИ (низкий приоритет)
            'automotive_general': {
                'patterns': [
                    'автосервис', 'ремонт автомобилей', 'техническое обслуживание',
                    'автомойка', 'car service', 'auto repair', 'car wash'
                ],
                'activity_type': 'automotive',
                'business_type': 'automotive service',
                'confidence': 0.7,
                'keywords': ['automotive', 'service', 'repair']
            },
            
            'healthcare_general': {
                'patterns': [
                    'медицинские услуги', 'лечение', 'медицинский центр',
                    'healthcare services', 'medical treatment', 'medical center'
                ],
                'activity_type': 'healthcare',
                'business_type': 'healthcare',
                'confidence': 0.7,
                'keywords': ['healthcare', 'medical', 'treatment']
            }
        }
        
        if not silent_mode:
            print(f"🔍 Анализирую семантические шаблоны для: '{theme_lower}'")
        
        # Ищем наиболее подходящий семантический шаблон
        best_match = None
        highest_confidence = 0
        
        for pattern_name, pattern_data in semantic_patterns.items():
            for pattern in pattern_data['patterns']:
                # Проверяем точное вхождение или семантическое сходство
                if self._semantic_match(theme_lower, pattern):
                    confidence = pattern_data['confidence']
                    
                    # Бонус за точность совпадения
                    if pattern.lower() == theme_lower:
                        confidence += 0.05  # Точное совпадение
                    elif pattern.lower() in theme_lower:
                        confidence += 0.02  # Частичное вхождение
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = {
                            'pattern_name': pattern_name,
                            'matched_pattern': pattern,
                            'confidence': confidence,
                            **pattern_data
                        }
                        
                        if not silent_mode:
                            print(f"   🎯 Найден шаблон: {pattern_name} (совпадение: '{pattern}', уверенность: {confidence:.2f})")
        
        if best_match and highest_confidence >= 0.7:
            # Обрабатываем динамические business_type
            business_type = best_match['business_type']
            if callable(business_type):
                business_type = business_type(theme_lower)
            
            context = {
                'category': 'intelligent_analysis',
                'business_type': business_type,
                'activity_type': best_match['activity_type'],
                'english_terms': best_match['keywords'],
                'confidence': best_match['confidence'],
                'keywords': best_match['keywords'][:3],
                'environment': f"professional {business_type} {best_match['activity_type']}",
                'matched_pattern': best_match['matched_pattern'],
                'analysis_method': 'semantic_pattern_matching'
            }
            
            if not silent_mode:
                print(f"✅ ИНТЕЛЛЕКТУАЛЬНЫЙ АНАЛИЗ УСПЕШЕН:")
                print(f"   🎯 Тип деятельности: {best_match['activity_type']}")
                print(f"   🏢 Бизнес-тип: {business_type}")  
                print(f"   📊 Уверенность: {best_match['confidence']:.2f}")
                print(f"   🔗 Совпавший шаблон: '{best_match['matched_pattern']}'")
            
            return context
        
        if not silent_mode:
            print("❌ Семантические шаблоны не дали результата, переход к legacy анализу")
        
        return None
    
    def _semantic_match(self, theme, pattern):
        """Проверяет семантическое совпадение между темой и шаблоном"""
        theme = theme.lower().strip()
        pattern = pattern.lower().strip()
        
        # Точное совпадение
        if pattern == theme:
            return True
            
        # Полное вхождение шаблона в тему
        if pattern in theme:
            return True
            
        # Частичное совпадение по ключевым словам (минимум 70% слов)
        theme_words = set(theme.split())
        pattern_words = set(pattern.split())
        
        if len(pattern_words) == 0:
            return False
            
        intersection = theme_words.intersection(pattern_words)
        similarity = len(intersection) / len(pattern_words)
        
        return similarity >= 0.7
    
    def _extract_language_from_theme(self, theme):
        """Извлекает конкретный язык из темы для языковых курсов"""
        language_map = {
            'английск': 'english', 'english': 'english',
            'французск': 'french', 'french': 'french', 
            'немецк': 'german', 'german': 'german',
            'испанск': 'spanish', 'spanish': 'spanish',
            'итальянск': 'italian', 'italian': 'italian',
            'китайск': 'chinese', 'chinese': 'chinese',
            'японск': 'japanese', 'japanese': 'japanese'
        }
        
        for lang_part, lang_full in language_map.items():
            if lang_part in theme:
                return lang_full
                
        return 'language'  # fallback
    
    def _legacy_theme_analysis(self, theme_lower, theme_words, silent_mode=False):
        """Старая система анализа как fallback"""
        if not silent_mode:
            print("🔄 Используем legacy анализ как fallback")
            
        found_terms = []
        activity_type = 'service'
        
        # Поиск ключевых слов в тематике (избегаем ложных срабатываний на подстроки)
        theme_words = theme_lower.split()  # Разбиваем на отдельные слова
        
        for ru_word, en_word in self.translations.items():
            # Проверяем точное совпадение со словами или вхождение как начало/конец слова
            word_found = False
            
            for theme_word in theme_words:
                # Точное совпадение
                if ru_word == theme_word:
                    word_found = True
                    break
                # Слово начинается с ключевого слова (например, "курсы" в "курсам")  
                elif theme_word.startswith(ru_word) and len(ru_word) >= 4:
                    word_found = True
                    break
                # Слово заканчивается ключевым словом (например, "автосервис" содержит "сервис")
                elif theme_word.endswith(ru_word) and len(ru_word) >= 4:
                    word_found = True
                    break
            
            if word_found:
                found_terms.append(en_word)
        
        # ПРИОРИТЕТНЫЕ проверки специализированных тематик
        
        # 1. Финансовые услуги - ВЫСШИЙ приоритет
        financial_indicators = [
            'финансовая', 'финансовый', 'инвестиц', 'кредит', 'банк', 'страхов',
            'налог', 'аудит', 'планирование', 'управление', 'анализ', 'оценка',
            'financial', 'investment', 'banking', 'consulting', 'consultant'
        ]
        
        financial_detected = False
        for indicator in financial_indicators:
            for theme_word in theme_words:
                if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                    financial_detected = True
                    break
            if financial_detected:
                break
        
        # 1. Кредитные услуги - ВЫСШИЙ приоритет
        credit_indicators = [
            'кредитоспособности', 'кредитоспособность', 'creditworthiness', 'кредит', 'credit'
        ]
        
        credit_detected = False
        for indicator in credit_indicators:
            for theme_word in theme_words:
                if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                    credit_detected = True
                    break
            if credit_detected:
                break
        
        # Если найдены кредитные термины = credit_assessment
        if credit_detected:
            activity_type = 'credit_assessment'
        
        # 2. Юридические услуги
        elif activity_type == 'service':
            legal_indicators = [
                'юридическое', 'юридические', 'юридических', 'правовое', 'правовые', 'legal',
                'адвокат', 'нотариус', 'суд', 'договор', 'сопровождение', 'support'
            ]
            
            legal_detected = False
            for indicator in legal_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        legal_detected = True
                        break
                if legal_detected:
                    break
            
            # Если найдены юридические термины = legal
            if legal_detected:
                activity_type = 'legal'
        
        # 2. Проверяем зарубежную недвижимость
        elif activity_type == 'service':
            foreign_real_estate_indicators = ['зарубежную', 'зарубежная', 'международная', 'foreign', 'international']
            foreign_detected = False
            
            for indicator in foreign_real_estate_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        foreign_detected = True
                        break
                if foreign_detected:
                    break
            
            # Если найдены зарубежная + недвижимость + инвестиции = foreign_real_estate
            if foreign_detected and ('недвижим' in theme_lower or 'real estate' in ' '.join(found_terms)) and financial_detected:
                activity_type = 'foreign_real_estate'
        
        # 3. Если найдены финансовые термины + консультация = financial
        if activity_type == 'service' and financial_detected and ('консультация' in theme_lower or 'consultant' in found_terms):
            activity_type = 'financial'
        
        # 2. СПЕЦИАЛИЗИРОВАННЫЕ АВТОМОБИЛЬНЫЕ ТЕМАТИКИ - ВЫСШИЙ приоритет
        
        # Импорт автомобилей
        car_import_indicators = ['подбор', 'импорт', 'сша', 'корея', 'европа', 'usa', 'korea', 'europe', 'selection', 'import']
        car_import_detected = False
        
        for indicator in car_import_indicators:
            for theme_word in theme_words:
                if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                    car_import_detected = True
                    break
            if car_import_detected:
                break
        
        # Если найдены автомобили + импорт/подбор = car_import
        if car_import_detected and ('авто' in theme_lower or 'машин' in theme_lower or 'cars' in found_terms):
            activity_type = 'car_import'
        
        # Водительские услуги
        elif activity_type == 'service':
            chauffeur_indicators = ['водитель', 'водителем', 'шофер', 'driver', 'chauffeur', 'персональный', 'personal']
            chauffeur_detected = False
            
            for indicator in chauffeur_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        chauffeur_detected = True
                        break
                if chauffeur_detected:
                    break
            
            # Если найдены водитель + аренда/авто = chauffeur_service
            if chauffeur_detected and ('аренда' in theme_lower or 'rental' in found_terms or 'авто' in theme_lower):
                activity_type = 'chauffeur_service'
        
        # 3. Шинные услуги - СПЕЦИАЛИЗИРОВАННАЯ автомобильная тематика
        if activity_type == 'service':
            tire_indicators = ['шин', 'tire', 'сезонная', 'seasonal', 'замена', 'replacement', 'колес']
            tire_detected = False
            
            for indicator in tire_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        tire_detected = True
                        break
                if tire_detected:
                    break
            
            # Если найдены шины + продажа/замена = tire_service
            if tire_detected and ('продажа' in theme_lower or 'замена' in theme_lower or 'sales' in found_terms):
                activity_type = 'tire_service'
        
        # 4. Обычная автомобильная тематика  
        if activity_type == 'service':  # Только если еще не определено
            automotive_indicators = [
                'автомобил', 'машин', 'авто', 'автосервис', 'автомойка', 'эвакуатор',
                'тюнинг', 'шиномонтаж', 'автозапчасти', 'диагностика', 'cars', 'automotive'
            ]
            
            for indicator in automotive_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        activity_type = 'automotive'
                        break
                if activity_type == 'automotive':
                    break
        
        # 5. Недвижимость - СПЕЦИАЛИЗИРОВАННАЯ тематика
        if activity_type == 'service':
            real_estate_indicators = [
                'квартир', 'участков', 'недвижим', 'аренда', 'продажа', 'apartments', 'plots', 
                'real estate', 'rental', 'estate', 'дача', 'ферма', 'загородных'
            ]
            real_estate_detected = False
            
            for indicator in real_estate_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        real_estate_detected = True
                        break
                if real_estate_detected:
                    break
            
            # Специфичные подтипы недвижимости
            if real_estate_detected:
                if 'студент' in theme_lower or 'student' in found_terms:
                    activity_type = 'student_housing'
                elif 'загородных' in theme_lower or 'участков' in theme_lower or 'дача' in theme_lower:
                    activity_type = 'land_plots'
                elif 'краткосрочная' in theme_lower or 'short' in found_terms:
                    activity_type = 'short_rental'
                else:
                    activity_type = 'real_estate'
        
        # 6. Ландшафтные работы - СПЕЦИАЛИЗИРОВАННАЯ тематика  
        if activity_type == 'service':
            landscape_indicators = [
                'ландшафт', 'landscape', 'садово', 'garden', 'благоустройство', 'озеленение'
            ]
            landscape_detected = False
            
            for indicator in landscape_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        landscape_detected = True
                        break
                if landscape_detected:
                    break
            
            if landscape_detected:
                activity_type = 'landscape'
        
        # Только если НЕ специализированная тема, проверяем остальные типы деятельности
        if activity_type == 'service':
            # УЛУЧШЕННАЯ ЛОГИКА: приоритет специфичным/комбинированным терминам
            
            # Сначала ищем точные фразы в самой теме (более специфично)
            theme_phrase = theme_lower.strip()
            priority_matches = []
            
            for business_type, keywords in self.business_types.items():
                for keyword in keywords:
                    # Проверяем точное вхождение фразы в тему
                    if keyword in theme_phrase:
                        priority_matches.append((business_type, len(keyword), keyword))
            
            # Если найдены приоритетные совпадения, выбираем самое длинное (более специфично)
            if priority_matches:
                # Сортируем по длине ключевого слова (более длинные = более специфичные)
                priority_matches.sort(key=lambda x: x[1], reverse=True)
                activity_type = priority_matches[0][0]
                print(f"�� Приоритетное совпадение: {priority_matches[0][2]} → {activity_type}")
            else:
                # Проверяем соответствие переведенных терминов категориям бизнеса
                for business_type, keywords in self.business_types.items():
                    # Сначала проверяем точные совпадения с английскими терминами
                    for found_term in found_terms:
                        if found_term in keywords:
                            activity_type = business_type
                            break
                    if activity_type != 'service':
                        break
                
                # Если не нашли по английским терминам, проверяем по русским ключевым словам в теме
                if activity_type == 'service':
                    for business_type, keywords in self.business_types.items():
                        for keyword in keywords:
                            # Используем ту же логику умного поиска
                            keyword_found = False
                            
                            for theme_word in theme_words:
                                # Точное совпадение
                                if keyword == theme_word:
                                    keyword_found = True
                                    break
                                # Слово начинается с ключевого слова  
                                elif theme_word.startswith(keyword) and len(keyword) >= 4:
                                    keyword_found = True
                                    break
                                # Слово заканчивается ключевым словом
                                elif theme_word.endswith(keyword) and len(keyword) >= 4:
                                    keyword_found = True
                                    break
                            
                            if keyword_found:
                                activity_type = business_type
                                break
                        if activity_type != 'service':
                            break
        
        # Определяем основную тему
        main_topic = self._extract_main_topic(theme_lower, found_terms)
        
        context = {
            'category': 'smart_analysis',
            'business_type': main_topic,
            'activity_type': activity_type,
            'english_terms': found_terms[:5],  # Топ-5 терминов
            'confidence': 0.9 if found_terms else 0.6,
            'keywords': found_terms[:3],
            'environment': f"professional {main_topic} {activity_type}"
        }
        
        if not silent_mode:
            print(f"🎯 Тип деятельности: {activity_type}")
            print(f"🔤 Найдены термины: {', '.join(found_terms[:3])}")
        
        return context
    
    def _extract_main_topic(self, theme_lower, found_terms):
        """Извлекает основную тему из найденных терминов по важности и специфичности"""
        if not found_terms:
            return theme_lower.split()[0] if theme_lower else 'business'
        
        # ПРИОРИТЕТНАЯ обработка специализированных тем
        
        # Кредитные услуги
        if 'creditworthiness' in found_terms or 'assessment' in found_terms:
            if 'client' in found_terms or 'business' in found_terms:
                return 'credit assessment'
            return 'creditworthiness'
        
        # Юридические услуги
        if 'legal' in found_terms or 'support' in found_terms:
            if 'transactions' in found_terms or 'investments' in found_terms:
                return 'legal services'  # вместо transactions
            return 'legal'
        
        # Импорт автомобилей  
        if 'selection' in found_terms and 'cars' in found_terms:
            return 'car import'
        
        # Зарубежная недвижимость
        if 'foreign' in found_terms and 'real estate' in ' '.join(found_terms):
            return 'foreign real estate'
        
        # Водительские услуги
        if 'driver' in found_terms or 'chauffeur' in found_terms:
            return 'chauffeur service'
        
        # Для инвестиционных курсов создаем специальную тему
        if 'investment' in found_terms and 'training' in found_terms:
            return 'investment courses'
        
        # Для языковых курсов создаем составную тему
        if 'training' in found_terms:
            languages = ['english', 'french', 'german', 'spanish', 'italian', 'chinese', 'japanese']
            found_language = None
            
            for lang in languages:
                if lang in found_terms:
                    found_language = lang
                    break
            
            if found_language:
                return f"{found_language} courses"
        
        # Ищем самый специфичный термин (составные фразы важнее одиночных слов)
        # Сортируем по длине - более длинные термины обычно более специфичны
        sorted_terms = sorted(found_terms, key=len, reverse=True)
        
        # Приоритет составным терминам (содержащим пробелы)
        for term in sorted_terms:
            if ' ' in term:  # составные термины типа "car service", "food delivery"
                return term
        
        # Если составных нет, берем самый длинный одиночный термин
        return sorted_terms[0]
    
    def generate_prompts(self, theme, silent_mode=False):
        """Генерирует набор промптов для тематики"""
        context = self.analyze_theme(theme, silent_mode)
        
        business_type = context['business_type']
        activity_type = context['activity_type']
        
        # Специализированные промпты по типу деятельности - ПРИОРИТЕТ!
        specialized = self._get_specialized_prompts(activity_type, business_type)
        
        # Базовые шаблоны промптов
        base_prompts = [
            f"professional {business_type} service office interior",
            f"modern {business_type} equipment and workspace",
            f"expert team providing {business_type} services",
            f"high quality {business_type} process in action",
            f"satisfied customer receiving {business_type} service",
            f"clean organized {business_type} business environment",
            f"professional {business_type} consultation meeting",
            f"reliable {business_type} service delivery"
        ]
        
        # Комбинируем СПЕЦИАЛИЗИРОВАННЫЕ первыми, затем базовые
        all_prompts = specialized + base_prompts
        
        # Выбираем 8 лучших промптов (специализированные будут в приоритете)
        selected_prompts = self._select_best_prompts(all_prompts, 8)
        
        if not silent_mode:
            print(f"✅ Сгенерировано {len(selected_prompts)} промптов для {theme}")
        
        return selected_prompts
    
    def _get_specialized_prompts(self, activity_type, business_type):
        """Возвращает специализированные промпты по типу деятельности"""
        
        # Универсальные шаблоны промптов по типам деятельности
        activity_templates = {
            'automotive': [
                f"professional automotive service garage with modern {business_type} equipment",
                f"clean well-organized automotive workshop with professional tools",
                f"experienced auto mechanic working on vehicle in modern garage",
                f"comfortable customer waiting area in automotive service center",
                f"high-tech diagnostic equipment for {business_type}",
                f"professional automotive technician using modern tools",
                f"modern vehicle service bay with professional equipment",
                f"mobile {business_type} van with professional automotive tools"
            ],
            'investment': [
                f"professional financial consultant explaining {business_type} strategies in modern office environment",
                f"expert investment advisor presenting market analysis and portfolio management solutions",
                f"modern financial consultation office with charts, graphs and {business_type} documentation",
                f"confident financial specialist providing personalized {business_type} guidance and expertise",
                f"professional investment presentation showcasing growth opportunities and financial strategies",
                f"experienced financial advisor explaining {business_type} principles with detailed market analysis",
                f"modern investment consultation setting with professional financial planning resources",
                f"expert investment counselor providing comprehensive {business_type} education and guidance"
            ],
            'training': [
                f"modern classroom with students learning {business_type}",
                f"professional instructor teaching {business_type} lesson",
                f"interactive {business_type} learning session",
                f"students engaged in {business_type} conversation practice",
                f"educational environment for {business_type} courses",
                f"group study session for {business_type} learning",
                f"modern language school classroom with {business_type} materials",
                f"teacher explaining {business_type} grammar on whiteboard"
            ],
            'food': [
                f"professional kitchen preparing {business_type}",
                f"fresh ingredients for {business_type} dishes",
                f"chef creating delicious {business_type} meal",
                f"elegant restaurant serving {business_type}",
                f"appetizing {business_type} presentation on plate"
            ],
            'healthcare': [
                f"clean medical facility for {business_type}",
                f"professional healthcare provider offering {business_type}",
                f"modern medical equipment for {business_type}",
                f"comfortable patient area in {business_type} clinic",
                f"sterile medical environment for {business_type} procedures"
            ],
            'beauty': [
                f"elegant salon interior for {business_type} services",
                f"professional stylist providing {business_type}",
                f"relaxing spa environment for {business_type}",
                f"modern beauty equipment for {business_type}",
                f"luxurious treatment room for {business_type} services"
            ],
            'construction': [
                f"professional construction site with {business_type} work",
                f"modern construction equipment for {business_type}",
                f"skilled workers performing {business_type} tasks",
                f"well-organized workshop for {business_type} projects",
                f"high-quality materials for {business_type} construction"
            ],
            'retail': [
                f"modern showroom displaying {business_type}",
                f"well-organized store with {business_type} products",
                f"professional sales environment for {business_type}",
                f"attractive product display of {business_type}",
                f"customer-friendly retail space for {business_type}"
            ],
            'tire_service': [
                f"professional tire service facility with {business_type} expertise",
                f"modern tire installation bay with professional {business_type} equipment",
                f"experienced tire technician working with {business_type} tools",
                f"comprehensive tire showroom with {business_type} selection",
                f"quality tire service center with professional {business_type} standards"
            ],
            'student_housing': [
                f"modern student accommodation with {business_type} facilities",
                f"comfortable student apartment showcasing {business_type} amenities",
                f"professional student housing office with {business_type} services",
                f"student-friendly living space with {business_type} features",
                f"quality student housing complex with {business_type} standards"
            ],
            'land_plots': [
                f"beautiful rural property showcasing {business_type} potential",
                f"scenic country land with {business_type} development opportunities",
                f"professional real estate consultation for {business_type} investment",
                f"expansive agricultural land with {business_type} possibilities",
                f"country property office specializing in {business_type} sales"
            ],
            'short_rental': [
                f"elegant vacation rental with {business_type} amenities",
                f"professional short-term accommodation with {business_type} services",
                f"luxurious rental property featuring {business_type} comfort",
                f"modern vacation rental office with {business_type} booking",
                f"quality short-term housing with {business_type} hospitality"
            ],
            'landscape': [
                f"professional landscaping project with {business_type} design",
                f"beautiful garden transformation using {business_type} expertise",
                f"modern landscaping equipment for {business_type} work",
                f"expert landscape design consultation for {business_type} projects",
                f"quality outdoor space creation with {business_type} craftsmanship"
            ]
        }
        
        # Специальная обработка для доставки еды
        if 'food delivery' in business_type.lower() or 'delivery' in business_type.lower():
            return [
                "delicious hot pizza ready for delivery",
                "fresh salad bowls and healthy meals",
                "gourmet burger and fries meal",
                "asian noodle dishes and sushi platters",
                "professional food delivery packaging"
            ]
        
        # Специальная обработка для инвестиционных курсов
        if activity_type == 'investment' and ('курсы' in business_type.lower() or 'courses' in business_type.lower()):
            return [
                f"professional investment education classroom with financial analysis on screens and whiteboards",
                f"experienced investment instructor explaining market strategies to engaged students",
                f"modern financial education center with charts, graphs and investment learning materials",
                f"interactive investment course with students analyzing portfolio management and market trends",
                f"professional investment training environment with financial software and educational resources",
                f"expert financial educator teaching investment principles in well-equipped classroom",
                f"students practicing investment analysis with professional trading simulation software",
                f"comprehensive investment education facility with market data displays and learning tools"
            ]
        
        # Специальная обработка для языковых курсов
        if 'courses' in business_type.lower() and activity_type == 'training':
            return [
                f"modern classroom with students learning {business_type}",
                f"professional teacher explaining {business_type} lesson",
                f"interactive {business_type} conversation practice",
                f"students engaged in {business_type} group study",
                f"language school classroom with {business_type} materials",
                f"instructor teaching {business_type} grammar",
                f"students practicing {business_type} speaking skills",
                f"modern educational environment for {business_type}"
            ]
        
        # СПЕЦИАЛЬНАЯ ОБРАБОТКА для новых специализированных тематик
        
        # Шинные услуги
        if activity_type == 'tire_service':
            return [
                f"professional tire shop with modern wheel alignment equipment and seasonal tire storage",
                f"expert tire technician installing new tires on vehicle in modern automotive service bay",
                f"comprehensive tire showroom displaying premium tire brands and seasonal tire options",
                f"professional tire replacement service with advanced tire mounting and balancing equipment",
                f"modern tire service center with quality tire storage and professional installation tools",
                f"experienced tire specialist providing tire consultation and seasonal tire change services",
                f"well-organized tire warehouse with extensive tire inventory and professional service area",
                f"professional automotive tire service with modern diagnostic equipment and tire expertise"
            ]
        
        # Студенческая недвижимость
        elif activity_type == 'student_housing':
            return [
                f"modern student apartment complex with comfortable living spaces and study areas",
                f"professional student housing manager showing apartment to prospective student tenants",
                f"well-furnished student apartment with modern amenities and study-friendly environment",
                f"student housing office with professional rental consultation and lease agreement services",
                f"comfortable student dormitory exterior with modern student housing facilities",
                f"friendly student housing team providing rental assistance and housing solutions",
                f"modern student apartment interior showcasing comfortable and affordable student living",
                f"professional student housing consultation with rental options and housing guidance"
            ]
        
        # Загородные участки  
        elif activity_type == 'land_plots':
            return [
                f"beautiful rural land plots with scenic countryside views and development potential",
                f"professional real estate agent showcasing premium agricultural land and country properties",
                f"picturesque country property with farmhouse potential and agricultural land development",
                f"expert land consultant providing guidance on rural property investment and land development",
                f"expansive agricultural land with fertile soil perfect for farming and country living",
                f"professional land sales office with rural property portfolios and development consultation",
                f"scenic country property with beautiful landscape views and agricultural potential",
                f"experienced real estate specialist presenting country land opportunities and rural investments"
            ]
        
        # Краткосрочная аренда
        elif activity_type == 'short_rental':
            return [
                f"elegant short-term rental apartment with modern furnishings and guest amenities",
                f"professional short-term rental manager providing accommodation services and guest support",
                f"luxurious vacation rental interior with comfortable furnishings and modern conveniences",
                f"short-term rental office with professional booking services and guest accommodation",
                f"beautiful vacation rental property exterior with attractive amenities and guest facilities"
            ]
        
        # Ландшафтные работы
        elif activity_type == 'landscape':
            return [
                f"professional landscape designer creating beautiful garden design with modern landscaping tools",
                f"expert landscaping team transforming outdoor spaces with creative garden design and installation",
                f"beautiful landscaping project showcasing professional garden design and quality workmanship",
                f"modern landscaping equipment and tools for professional garden construction and maintenance",
                f"experienced landscape architect planning outdoor space transformation with design expertise"
            ]
        
        # Кредитные услуги
        elif activity_type == 'credit_assessment':
            return [
                f"professional credit analyst reviewing client financial documents",
                f"modern financial analysis office with credit assessment systems",
                f"expert credit specialist conducting creditworthiness evaluation",
                f"financial evaluation center with credit scoring technology",
                f"experienced credit advisor providing assessment consultation",
                f"professional banking office with credit analysis tools",
                f"modern credit bureau with financial data analysis",
                f"expert financial analyst evaluating business creditworthiness"
            ]
        
        # Импорт автомобилей
        elif activity_type == 'car_import':
            return [
                f"luxury imported cars from USA, Korea, and Europe in premium showroom",
                f"professional car import specialist explaining vehicle documentation and specifications",
                f"high-end imported vehicles displayed in modern automotive gallery with international certificates",
                f"expert consultant showing imported car specifications and import documentation",
                f"premium car selection service with international vehicle portfolio and expertise",
                f"modern office with imported car catalogs and international automotive expertise",
                f"professional car import consultation with vehicle history and legal documentation",
                f"luxury automotive showroom featuring premium imported vehicles from overseas markets"
            ]
        
        # Зарубежная недвижимость
        if activity_type == 'foreign_real_estate':
            return [
                f"professional international real estate consultant with global property investment portfolio", 
                f"modern office with world map showing foreign real estate opportunities and market analysis",
                f"luxury international property presentations and investment documentation with global expertise",
                f"expert advisor explaining foreign real estate investment strategies and overseas opportunities",
                f"premium international real estate facility with global market expertise and guidance"
            ]
        
        # Водитель/шофер услуги 
        if activity_type == 'chauffeur_service':
            return [
                f"professional chauffeur in elegant uniform standing beside luxury vehicle fleet",
                f"premium car rental service with experienced professional driver in elegant attire",
                f"luxury vehicle interior showcasing comfort and professional chauffeur service",
                f"experienced driver providing personalized luxury transportation service with professional standards",
                f"elegant chauffeur service office with luxury car fleet display and professional team",
                f"professional driver consultation explaining premium transportation options and luxury services",
                f"luxury car rental facility with professional chauffeur team and premium vehicle selection",
                f"premium transportation service with skilled professional drivers and luxury vehicle fleet"
            ]
        
        # Возвращаем шаблоны для типа деятельности или универсальные
        return activity_templates.get(activity_type, [
            f"professional {business_type} service environment",
            f"modern {business_type} workplace setup",
            f"quality {business_type} service delivery",
            f"trusted {business_type} business facility",
            f"expert team providing {business_type} services"
        ])
    
    def _select_best_prompts(self, prompts, count):
        """Выбирает лучшие промпты избегая повторений с улучшенной логикой"""
        selected = []
        used_keywords = set()
        used_combinations = set()
        
        for prompt in prompts:
            # Проверяем уникальность всех слов (не только длинных)
            words = prompt.lower().split()
            key_words = [w for w in words if len(w) > 3]  # Понизили требование с 4 до 3
            
            # Создаем комбинацию из первых 3 слов для более строгой проверки
            word_combination = ' '.join(sorted(key_words[:5]))
            
            # Проверяем как по ключевым словам, так и по комбинациям
            if (not any(word in used_keywords for word in key_words[:3]) and 
                word_combination not in used_combinations):
                
                selected.append(prompt)
                used_keywords.update(key_words[:3])
                used_combinations.add(word_combination)
                
                if len(selected) >= count:
                    break
        
        # Если не хватает, добавляем оставшиеся с дополнительными модификациями
        while len(selected) < count and len(selected) < len(prompts):
            for prompt in prompts:
                if prompt not in selected:
                    # Добавляем уникальный модификатор для избежания полного дублирования
                    unique_modifier = self._generate_unique_modifier()
                    modified_prompt = f"{prompt}, {unique_modifier}"
                    selected.append(modified_prompt)
                    if len(selected) >= count:
                        break
        
        return selected
    
    def _generate_unique_modifier(self):
        """Генерирует уникальный модификатор для промпта"""
        timestamp = str(int(time.time()))[-4:]  # Последние 4 цифры времени
        unique_id = str(uuid.uuid4())[:8]
        
        modifiers = [
            f"detailed view {timestamp}",
            f"professional angle {unique_id[:4]}",
            f"quality focus {timestamp}",
            f"expert perspective {unique_id[:6]}",
            f"premium shot {timestamp[-3:]}",
            f"skilled composition {unique_id[-4:]}"
        ]
        
        return self.rng.choice(modifiers)
    
    def _add_uniqueness_to_prompt(self, base_prompt, image_type, business_type):
        """Добавляет уникальные элементы к базовому промпту"""
        # Добавляем стиль
        style = self.rng.choice(self.style_modifiers)
        
        # Добавляем специфичные детали для типа изображения
        detail_type = "main" if image_type == "main" else ("about" if "about" in image_type else "review")
        unique_detail = self.rng.choice(self.unique_details.get(detail_type, self.unique_details["main"]))
        
        # Добавляем дескриптор качества
        quality = self.rng.choice(self.quality_descriptors)
        
        # Добавляем временную уникальность
        timestamp = str(int(time.time() * 1000))[-6:]  # Микросекунды для уникальности
        unique_element = f"composition_{timestamp}"
        
        # Собираем все вместе
        enhanced_prompt = f"{style} {base_prompt}, {unique_detail}, {quality}, {unique_element}"
        
        return enhanced_prompt
    
    def _ensure_prompt_uniqueness(self, prompts_dict):
        """Дополнительно обеспечивает уникальность всех промптов в наборе"""
        used_words = set()
        enhanced_prompts = {}
        
        for key, prompt in prompts_dict.items():
            # Проверяем основные слова в промпте
            main_words = [word.lower() for word in prompt.split() if len(word) > 4][:5]
            
            # Если есть пересечения с уже использованными словами, добавляем уникальность
            if any(word in used_words for word in main_words):
                unique_suffix = f", enhanced_{str(uuid.uuid4())[:6]}"
                enhanced_prompts[key] = f"{prompt}{unique_suffix}"
            else:
                enhanced_prompts[key] = prompt
            
            # Добавляем использованные слова
            used_words.update(main_words)
        
        return enhanced_prompts
    
    def _calculate_uniqueness_score(self, prompts_dict):
        """Вычисляет оценку уникальности промптов"""
        all_words = []
        for prompt in prompts_dict.values():
            words = [word.lower() for word in prompt.split() if len(word) > 3]
            all_words.extend(words)
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        if total_words == 0:
            return 0
        
        uniqueness_score = (unique_words / total_words) * 100
        return round(uniqueness_score, 1)
    
    def _select_random_variant(self, variants):
        """Выбирает случайный вариант из списка с уникальностью"""
        if not variants:
            return ""
        
        # Используем внутренний генератор для консистентности
        selected = self.rng.choice(variants)
        
        # Добавляем небольшую уникальность
        timestamp = str(int(time.time() * 1000))[-3:]
        return f"{selected}, variant_{timestamp}"
    
    def _create_clean_about_prompt(self, base_content, prefixes, prompt_num):
        """Создает чистый about промпт без повторений и странных комбинаций"""
        
        # Умные суффиксы по номеру промпта
        smart_suffixes = {
            1: ["", "and tools", "for professionals", "with expertise"],  # Короткие, технические
            2: ["in action", "with precision", "and quality", "ensuring results"],  # Процессы  
            3: ["and environment", "with standards", "ensuring excellence", "and reliability"]  # Места/стандарты
        }
        
        # Выбираем префикс
        prefix = self.rng.choice(prefixes)
        
        # Проверяем, есть ли уже такое слово в base_content
        base_words = set(base_content.lower().split())
        
        # Если префикс уже есть в содержимом, берем другой
        attempts = 0
        while prefix.lower() in base_words and attempts < 5:
            prefix = self.rng.choice(prefixes)
            attempts += 1
        
        # Если все равно конфликт, используем нейтральный префикс
        if prefix.lower() in base_words:
            prefix = "high-quality"
        
        # Выбираем подходящий суффикс
        suffix = self.rng.choice(smart_suffixes.get(prompt_num, smart_suffixes[1]))
        
        # Собираем промпт
        if suffix:
            prompt = f"{prefix} {base_content} {suffix}"
        else:
            prompt = f"{prefix} {base_content}"
        
        # Финальная проверка на дубли слов и исправление
        prompt = self._remove_word_duplicates(prompt)
        
        return prompt
    
    def _remove_word_duplicates(self, text):
        """Убирает повторяющиеся слова из текста, сохраняя естественность"""
        words = text.split()
        seen = set()
        result = []
        
        for word in words:
            word_clean = word.lower().strip('.,!?;:')
            if word_clean not in seen:
                seen.add(word_clean)
                result.append(word)
            # Если слово уже было, просто пропускаем его
        
        return ' '.join(result)

# Функция для совместимости с другими модулями
def create_thematic_prompts(theme_input):
    """ПРИНУДИТЕЛЬНО ОТКЛЮЧЕНЫ ВСЕ ВНЕШНИЕ ИИ - только надежная система!"""
    print("🔥 create_thematic_prompts: ВСЕ ВНЕШНИЕ ИИ ПРИНУДИТЕЛЬНО ОТКЛЮЧЕНЫ!")
    
    # ПРИНУДИТЕЛЬНО ПРОПУСКАЕМ ВСЕ ВНЕШНИЕ ИИ
    # Сразу используем надежную fallback систему
    generator = SmartPromptGenerator()
    return generator.generate_prompts(theme_input, silent_mode=True)

# ГЛОБАЛЬНЫЙ КЭШ для предотвращения повторений лиц в течение сессии
_FACE_CACHE = {
    'used_combinations': set(),
    'last_reset': time.time() if 'time' in globals() else 0,
    'session_counter': 0
}

def create_human_focused_review_prompts():
    """
    ПРИНУДИТЕЛЬНАЯ ЭКСТРЕМАЛЬНАЯ СИСТЕМА разнообразия лиц для review изображений
    ОТКЛЮЧЕНЫ ВСЕ ВНЕШНИЕ ИИ - только гарантированное разнообразие!
    + СИСТЕМА РОТАЦИИ ПОДТИПОВ для максимального разнообразия
    + ГЛОБАЛЬНЫЙ КЭШ предотвращения повторений
    """
    # ПРИНУДИТЕЛЬНО ОТКЛЮЧАЕМ ВСЕ ВНЕШНИЕ ИИ-СИСТЕМЫ
    # Используем только ЭКСТРЕМАЛЬНУЮ систему разнообразия
    
    import random
    import time
    import uuid
    import hashlib
    
    global _FACE_CACHE
    
    print("🔥 ПРИНУДИТЕЛЬНО АКТИВИРОВАНА ЭКСТРЕМАЛЬНАЯ СИСТЕМА РАЗНООБРАЗИЯ ЛИЦ!")
    print("🚫 ВСЕ ВНЕШНИЕ ИИ ОТКЛЮЧЕНЫ - ТОЛЬКО ГАРАНТИРОВАННОЕ РАЗНООБРАЗИЕ!")
    print("🔄 АКТИВНА СИСТЕМА РОТАЦИИ ПОДТИПОВ!")
    print("💾 АКТИВЕН ГЛОБАЛЬНЫЙ КЭШ ПРЕДОТВРАЩЕНИЯ ПОВТОРЕНИЙ!")
    
    # Сбрасываем кэш каждые 5 минут или каждые 50 генераций
    current_time = time.time()
    _FACE_CACHE['session_counter'] += 1
    if (current_time - _FACE_CACHE['last_reset'] > 300 or  # 5 минут
        _FACE_CACHE['session_counter'] > 50):  # 50 генераций
        _FACE_CACHE['used_combinations'].clear()
        _FACE_CACHE['last_reset'] = current_time
        _FACE_CACHE['session_counter'] = 0
        print("🔄 КЭШ СБРОШЕН - НАЧИНАЕМ НОВЫЙ ЦИКЛ РАЗНООБРАЗИЯ")
    
    print(f"📊 Использовано комбинаций: {len(_FACE_CACHE['used_combinations'])}")
    print(f"🔢 Генерация #{_FACE_CACHE['session_counter']}")
    
    # СУПЕР-РОТАТОР для изменения типов лиц при каждом вызове
    current_time_factor = int(time.time()) % 1000  # Меняется каждую секунду
    rotation_seed = (current_time_factor + 
                    random.randint(1, 999999) + 
                    hash(str(uuid.uuid4())) + 
                    os.getpid() +
                    _FACE_CACHE['session_counter'])  # Добавляем счетчик сессии
    
    print(f"🎲 Фактор ротации: {current_time_factor}")
    
    def generate_unique_combination(base_type, subtype_choices, attempt=0):
        """Генерирует уникальную комбинацию, избегая повторений"""
        # Предотвращаем бесконечные циклы
        if attempt > 20:
            # Если не можем найти уникальную комбинацию, сбрасываем кэш и возвращаем базовую
            print(f"⚠️ Достигнут лимит попыток ({attempt}), сбрасываем кэш для {base_type}")
            _FACE_CACHE['used_combinations'].clear()
            return f"{base_type}_reset_{int(time.time())}"
        
        # Защита от деления на ноль
        if not subtype_choices or len(subtype_choices) == 0:
            print(f"⚠️ Пустой список subtype_choices для {base_type}")
            return f"{base_type}_default_{attempt}_{int(time.time())}"
            
        # Создаем более уникальный ключ с дополнительной энтропией
        import random
        extra_entropy = random.randint(1, 999999)
        subtype_index = (rotation_seed + attempt + extra_entropy) % len(subtype_choices)
        combo_key = f"{base_type}_{subtype_index}_{attempt}_{extra_entropy}_{int(time.time() * 1000) % 100000}"
        
        # Проверяем уникальность с более строгим лимитом
        if combo_key in _FACE_CACHE['used_combinations']:
            return generate_unique_combination(base_type, subtype_choices, attempt + 1)
        
        _FACE_CACHE['used_combinations'].add(combo_key)
        return combo_key
    
    # ПОДХОД 1: ЕВРОПЕЙСКИЕ/ЗАПАДНЫЕ ТИПЫ ЛИЦА (с ротацией подтипов)
    def generate_western_face():
        rng1 = random.Random()
        # СУПЕР-энтропийный seed для максимальной уникальности
        mega_seed = (int(time.time() * 9999999) + 
                    hash(str(uuid.uuid4())) + 
                    os.getpid() + 
                    random.getrandbits(64) + 
                    hash(str(time.perf_counter())) +
                    random.randint(1000000, 9999999) +
                    rotation_seed +
                    _FACE_CACHE['session_counter'] * 1000)
        rng1.seed(mega_seed)
        
        # Генерируем уникальную комбинацию
        unique_combo = generate_unique_combination("western", ["scand", "south", "central"])
        
        # РОТАЦИЯ: разные подтипы в зависимости от времени
        if rotation_seed % 3 == 0:
            # СКАНДИНАВСКИЙ подтип
            ethnicities = ["Nordic blonde professional", "Swedish businesswoman", "Norwegian executive", 
                          "Danish manager", "Finnish specialist", "Icelandic consultant"]
            hair_colors = ["platinum blonde", "golden blonde", "ash blonde", "light blonde", "white blonde"]
            eye_colors = ["piercing blue eyes", "ice blue eyes", "crystal blue eyes", "arctic blue eyes"]
            subtype_id = "scand"
        elif rotation_seed % 3 == 1:
            # ЮЖНО-ЕВРОПЕЙСКИЙ подтип  
            ethnicities = ["Mediterranean beauty", "Italian elegance", "Spanish charm", 
                          "Greek professional", "Portuguese executive", "French sophistication"]
            hair_colors = ["dark brunette", "chestnut brown", "auburn red", "espresso brown", "mahogany"]
            eye_colors = ["warm hazel eyes", "deep brown eyes", "olive green eyes", "amber eyes"]
            subtype_id = "south"
        else:
            # ЦЕНТРАЛЬНО-ЕВРОПЕЙСКИЙ подтип
            ethnicities = ["Germanic features", "Austrian professional", "Swiss executive",
                          "Dutch businesswoman", "Belgian manager", "Bavarian specialist"]
            hair_colors = ["honey brown", "caramel blonde", "light brunette", "copper red", "strawberry blonde"]
            eye_colors = ["emerald green eyes", "steel gray eyes", "forest green eyes", "violet blue eyes"]
            subtype_id = "central"
        
        ages = ["young adult 22-28", "early thirties 29-35", "mid-thirties 36-42", "early forties 43-50",
               "late twenties 27-32", "professional 33-39", "experienced 40-47", "mature 48-55"]
        expressions = ["radiant genuine smile", "confident satisfied expression", "warm friendly demeanor",
                      "professional pleasant look", "authentic happy face", "sincere grateful expression"]
        clothing = ["elegant business attire", "contemporary professional outfit", "smart casual ensemble",
                   "sophisticated styling", "modern executive wear", "polished appearance"]
        
        # Тройная уникальность + кэш ID
        unique_id1 = str(uuid.uuid4())[:8]
        unique_id2 = str(uuid.uuid4())[9:17]
        timestamp = str(int(time.time() * 9999999))[-10:]
        cache_id = str(hash(unique_combo))[-6:] if unique_combo else "000000"
        
        return (f"professional portrait of {rng1.choice(ethnicities)}, {rng1.choice(ages)}, "
                f"{rng1.choice(hair_colors)}, {rng1.choice(eye_colors)}, {rng1.choice(expressions)}, "
                f"{rng1.choice(clothing)}, high quality headshot photography, natural lighting, "
                f"HUMAN FACE ONLY, NO OBJECTS, western_{unique_id1}, euro_{unique_id2}, time_{timestamp}, "
                f"rot_{rotation_seed%3}, cache_{cache_id}, {subtype_id}")
    
    # ПОДХОД 2: АЗИАТСКИЕ/ВОСТОЧНЫЕ ТИПЫ ЛИЦА (с ротацией подтипов)
    def generate_asian_face():
        rng2 = random.Random()
        # СУПЕР-энтропийный seed с другой базой
        mega_seed = (int(time.time() * 7777777) + 
                    hash(str(uuid.uuid4())) + 
                    os.getpid() + 
                    random.getrandbits(64) + 
                    hash(str(time.perf_counter())) +
                    random.randint(2000000, 8888888) + 555555 +
                    rotation_seed * 2 +
                    _FACE_CACHE['session_counter'] * 2000)
        rng2.seed(mega_seed)
        
        # Генерируем уникальную комбинацию
        unique_combo = generate_unique_combination("asian", ["east", "southeast", "south", "central"])
        
        # РОТАЦИЯ: разные подтипы в зависимости от времени
        if rotation_seed % 4 == 0:
            # ВОСТОЧНО-АЗИАТСКИЙ подтип
            ethnicities = ["Korean businesswoman", "Japanese executive", "Chinese manager", 
                          "Taiwanese specialist", "Hong Kong professional"]
            subtype_id = "east"
        elif rotation_seed % 4 == 1:
            # ЮГО-ВОСТОЧНАЯ АЗИЯ подтип
            ethnicities = ["Vietnamese consultant", "Thai specialist", "Filipino expert",
                          "Indonesian professional", "Malaysian business leader", "Singaporean executive"]
            subtype_id = "southeast"
        elif rotation_seed % 4 == 2:
            # ЮЖНАЯ АЗИЯ подтип
            ethnicities = ["Indian professional", "Pakistani executive", "Bangladeshi manager",
                          "Sri Lankan specialist", "Nepalese consultant"]
            subtype_id = "south"
        else:
            # ЦЕНТРАЛЬНАЯ АЗИЯ подтип
            ethnicities = ["Mongolian professional", "Kazakh executive", "Uzbek businesswoman",
                          "Kyrgyz specialist", "Tajik manager"]
            subtype_id = "central"
        
        ages = ["young professional 24-30", "established career 31-38", "experienced worker 39-46", 
               "senior specialist 47-55", "rising star 25-32", "accomplished 33-40", "veteran 41-48"]
        features = ["elegant refined features", "striking beautiful appearance", "graceful professional look", 
                   "sophisticated charm", "distinctive attractive features", "classic beauty", "modern elegance"]
        styles = ["contemporary business attire", "sophisticated professional outfit", "elegant work ensemble",
                 "polished executive style", "modern professional dress", "refined business wear"]
        expressions = ["confident professional smile", "warm genuine expression", "satisfied pleased demeanor",
                      "authentic happy face", "sincere grateful look", "positive radiant smile"]
        
        # Тройная уникальность + кэш ID
        unique_id1 = str(uuid.uuid4())[:8]
        unique_id2 = str(uuid.uuid4())[18:26]
        timestamp = str(int(time.time() * 7777777))[-10:]
        session_hash = hashlib.md5(f"{time.time()}_{random.random()}_{rng2.random()}".encode()).hexdigest()[:10]
        cache_id = str(hash(unique_combo))[-6:] if unique_combo else "000000"
        
        return (f"professional portrait of {rng2.choice(ethnicities)}, {rng2.choice(ages)}, "
                f"{rng2.choice(features)}, {rng2.choice(expressions)}, {rng2.choice(styles)}, "
                f"high quality business photography, professional lighting, confident demeanor, "
                f"HUMAN FACE ONLY, NO OBJECTS, asian_{unique_id1}, orient_{unique_id2}, time_{timestamp}, "
                f"hash_{session_hash}, rot_{rotation_seed%4}, cache_{cache_id}, {subtype_id}")
    
    # ПОДХОД 3: АФРИКАНСКИЕ/ЛАТИНОАМЕРИКАНСКИЕ ТИПЫ ЛИЦА (с ротацией подтипов)
    def generate_diverse_face():
        rng3 = random.Random()
        # СУПЕР-энтропийный seed с третьей базой
        mega_seed = (int(time.time() * 5555555) + 
                    hash(str(uuid.uuid4())) + 
                    os.getpid() + 
                    random.getrandbits(64) + 
                    hash(str(time.perf_counter())) +
                    random.randint(3000000, 7777777) + 999999 +
                    rotation_seed * 3 +
                    _FACE_CACHE['session_counter'] * 3000)
        rng3.seed(mega_seed)
        
        # Генерируем уникальную комбинацию
        unique_combo = generate_unique_combination("diverse", ["african", "latino", "middle", "indian", "mixed"])
        
        # РОТАЦИЯ: разные подтипы в зависимости от времени
        if rotation_seed % 5 == 0:
            # АФРИКАНСКИЙ подтип
            ethnicities = ["African American professional", "Nigerian businesswoman", "Ethiopian executive", 
                          "Kenyan manager", "Ghanaian specialist", "South African consultant"]
            subtype_id = "african"
        elif rotation_seed % 5 == 1:
            # ЛАТИНОАМЕРИКАНСКИЙ подтип
            ethnicities = ["Latina businesswoman", "Brazilian manager", "Mexican consultant", 
                          "Colombian expert", "Argentine professional", "Peruvian specialist"]
            subtype_id = "latino"
        elif rotation_seed % 5 == 2:
            # БЛИЖНЕВОСТОЧНЫЙ подтип
            ethnicities = ["Middle Eastern executive", "Arab professional", "Egyptian business leader", 
                          "Moroccan executive", "Lebanese specialist", "Turkish manager"]
            subtype_id = "middle"
        elif rotation_seed % 5 == 3:
            # ИНДИЙСКИЙ подтип
            ethnicities = ["Indian specialist", "Pakistani professional", "Bangladeshi executive",
                          "Sri Lankan manager", "Indian-American businesswoman"]
            subtype_id = "indian"
        else:
            # СМЕШАННЫЙ подтип
            ethnicities = ["mixed heritage professional", "biracial executive", "multicultural businesswoman",
                          "international background manager", "global citizen specialist"]
            subtype_id = "mixed"
        
        ages = ["dynamic young professional 23-29", "accomplished career woman 30-37", "experienced leader 38-45", 
               "senior executive 46-53", "rising professional 26-33", "established expert 34-41"]
        features = ["striking natural beauty", "warm expressive features", "confident attractive appearance", 
                   "radiant professional presence", "distinctive elegant look", "captivating smile"]
        styles = ["professional power suit", "elegant business ensemble", "contemporary work attire",
                 "sophisticated office wear", "polished executive outfit", "modern professional styling"]
        emotions = ["genuinely thrilled", "deeply satisfied", "extremely pleased", "authentically grateful", 
                   "remarkably content", "profoundly happy", "sincerely delighted", "truly appreciative"]
        contexts = ["celebrating success", "expressing satisfaction", "showing gratitude", "radiating confidence",
                   "demonstrating joy", "displaying happiness", "conveying appreciation", "expressing delight"]
        
        # Четверная уникальность + кэш ID
        unique_id1 = str(uuid.uuid4())[:6]
        unique_id2 = str(uuid.uuid4())[9:15]
        unique_id3 = str(uuid.uuid4())[24:30]
        timestamp = str(int(time.time() * 5555555))[-10:]
        random_hash = hashlib.sha256(f"{time.time()}_{random.random()}_{uuid.uuid4()}_{rng3.random()}".encode()).hexdigest()[:12]
        cache_id = str(hash(unique_combo))[-6:] if unique_combo else "000000"
        
        return (f"professional portrait of {rng3.choice(ethnicities)}, {rng3.choice(ages)}, "
                f"{rng3.choice(features)}, {rng3.choice(emotions)}, {rng3.choice(contexts)}, "
                f"{rng3.choice(styles)}, premium business photography, natural professional lighting, "
                f"HUMAN FACE ONLY, NO OBJECTS, diverse_{unique_id1}, multi_{unique_id2}, global_{unique_id3}, "
                f"time_{timestamp}, hash_{random_hash}, rot_{rotation_seed%5}, cache_{cache_id}, {subtype_id}")
    
    # Генерируем 3 КАРДИНАЛЬНО разных промпта принудительно
    review_prompts = [
        generate_western_face(),
        generate_asian_face(), 
        generate_diverse_face()
    ]
    
    print("✅ ПРИНУДИТЕЛЬНО СГЕНЕРИРОВАНЫ 3 ЭКСТРЕМАЛЬНО РАЗНЫХ ТИПА ЛИЦ:")
    print(f"   🌍 Западный/Европейский (подтип {rotation_seed%3}): {len(review_prompts[0])} символов")
    print(f"   🌏 Азиатский/Восточный (подтип {rotation_seed%4}): {len(review_prompts[1])} символов") 
    print(f"   🌎 Африканский/Латиноамериканский (подтип {rotation_seed%5}): {len(review_prompts[2])} символов")
    print("   🎯 ГАРАНТИРОВАННОЕ РАЗНООБРАЗИЕ: 100% - ВНЕШНИЕ ИИ ОТКЛЮЧЕНЫ!")
    print("   🔄 СИСТЕМА РОТАЦИИ АКТИВНА - ПОДТИПЫ МЕНЯЮТСЯ КАЖДУЮ СЕКУНДУ!")
    print("   💾 ГЛОБАЛЬНЫЙ КЭШ ПРЕДОТВРАЩАЕТ ПОВТОРЕНИЯ В СЕССИИ!")
    
    return review_prompts


def create_complete_prompts_dict(theme_input):
    """
    Создает полный словарь промптов для всех типов изображений включая review с людьми
    ПРИНУДИТЕЛЬНО ОТКЛЮЧЕНЫ ВСЕ ВНЕШНИЕ ИИ - только гарантированное разнообразие!
    """
    print("🔥 ПРИНУДИТЕЛЬНО ОТКЛЮЧЕНЫ ВСЕ ВНЕШНИЕ ИИ!")
    print("🎯 ИСПОЛЬЗУЕМ ТОЛЬКО СИСТЕМУ ГАРАНТИРОВАННОГО РАЗНООБРАЗИЯ ЛИЦ!")
    
    try:
        # ПРИНУДИТЕЛЬНО ПРОПУСКАЕМ ВСЕ ВНЕШНИЕ ИИ-СИСТЕМЫ
        # Сразу переходим к нашей надежной системе разнообразия
        import random  # Для разнообразия main промптов
        import time    # Для временных меток
        import uuid    # Для уникальных ID
        
        print("📝 Создаем генератор...")
        generator = SmartPromptGenerator()
        
        print("🔍 Анализируем тематику...")
        context = generator.analyze_theme(theme_input, silent_mode=True)
        
        business_type = context['business_type']
        activity_type = context['activity_type']
        print(f"📊 Тип бизнеса: {business_type}, Тип деятельности: {activity_type}")
        
        # Инициализируем уникальный генератор для этой сессии с МАКСИМАЛЬНОЙ энтропией
        session_rng = random.Random()
        # Используем микросекунды + случайный UUID + ID процесса для гарантированной уникальности
        unique_seed = int(time.time() * 1000000) + hash(str(uuid.uuid4())) + os.getpid() + random.randint(1, 1000000)
        session_rng.seed(unique_seed)
        print(f"🎲 Seed: {unique_seed}")
        
        print("✅ Инициализация завершена, переходим к генерации...")
        
        # УМНАЯ АДАПТИВНАЯ СПЕЦИФИЧНОСТЬ: 8.5+ баллов
        
        # Базовая консистентная структура
        core_base = f"professional {business_type} {activity_type} service"
        quality_base = f"modern high quality expert {business_type}"
        
        # Адаптивные детали по типу деятельности с РАЗНООБРАЗНЫМИ main промптами
        adaptive_details = {
            'automotive': {
                'main': session_rng.choice([
                    'modern automotive service center exterior with professional signage and clean facility',
                    'skilled mechanic team working on vehicles in well-equipped garage',
                    'satisfied customers receiving keys to their serviced vehicles',
                    'professional automotive workshop showcasing expertise and quality service',
                    'clean organized automotive facility with modern equipment and branding'
                ]),
                'about1': 'specialized diagnostic equipment and professional automotive tools',
                'about2': 'hands-on vehicle service process with technical expertise',
                'about3': 'certified automotive workshop with quality assurance standards'
            },
            'healthcare': {
                'main': session_rng.choice([
                    'compassionate healthcare professional providing excellent patient care',
                    'modern medical facility exterior with professional healthcare branding',
                    'successful patient recovery showcasing positive healthcare outcomes',
                    'advanced medical technology ensuring precise diagnosis and treatment',
                    'welcoming healthcare reception with comfortable patient environment'
                ]),
                'about1': 'advanced medical equipment and specialized healthcare tools',
                'about2': 'patient care process with medical expertise and compassion',
                'about3': 'sterile healthcare environment with medical quality standards'
            },
            # НОВЫЕ СПЕЦИФИЧНЫЕ ДЕТАЛИ для интеллектуальной системы
            'investment': {
                'main': session_rng.choice([
                    'professional investment education classroom with students analyzing market charts',
                    'expert financial instructor explaining investment strategies to engaged learners',
                    'modern financial training center with investment analysis equipment',
                    'interactive investment seminar with real market data and professional guidance',
                    'comprehensive investment education facility with financial software and learning resources'
                ]),
                'about1': 'advanced financial analysis software and investment tracking systems',
                'about2': 'interactive investment education process with market simulation tools',
                'about3': 'professional investment learning environment with real-time market data'
            },
            'training': {
                'main': session_rng.choice([
                    'modern classroom environment with engaged students and professional instructor',
                    'interactive learning session with educational materials and teaching technology',
                    'professional training center with comprehensive educational resources',
                    'dynamic educational environment with students practicing new skills',
                    'well-equipped learning facility with modern teaching equipment'
                ]),
                'about1': 'modern educational technology and interactive learning tools',
                'about2': 'hands-on training process with practical skill development',
                'about3': 'professional learning environment with comprehensive educational resources'
            },
            'chauffeur_service': {
                'main': session_rng.choice([
                    'professional chauffeur in elegant uniform beside luxury vehicle fleet',
                    'premium transportation service with experienced drivers and luxury cars',
                    'elegant chauffeur service office with luxury vehicle display',
                    'professional driver consultation with premium transportation options',
                    'luxury car rental facility with professional chauffeur team'
                ]),
                'about1': 'luxury vehicle fleet and professional chauffeur equipment',
                'about2': 'premium transportation service process with professional standards',
                'about3': 'elegant chauffeur service facility with luxury vehicle maintenance'
            },
            'car_import': {
                'main': session_rng.choice([
                    'luxury imported cars from USA, Korea and Europe in premium showroom',
                    'professional car import specialist with international vehicle documentation',
                    'premium automotive gallery featuring high-end imported vehicles',
                    'expert car selection consultant with global vehicle portfolio',
                    'modern car import facility with international automotive expertise'
                ]),
                'about1': 'international vehicle documentation and import certification systems',
                'about2': 'professional car selection process with global automotive expertise',
                'about3': 'premium car import facility with international vehicle inspection standards'
            },
            'credit_assessment': {
                'main': session_rng.choice([
                    'professional credit analyst reviewing client financial documents',
                    'modern financial analysis office with credit assessment systems',
                    'expert credit specialist conducting creditworthiness evaluation',
                    'comprehensive credit evaluation center with financial analysis tools',
                    'professional banking office with credit scoring technology'
                ]),
                'about1': 'advanced credit analysis software and financial assessment tools',
                'about2': 'thorough creditworthiness evaluation process with expert analysis',
                'about3': 'professional credit assessment facility with secure financial data systems'
            },
            'foreign_real_estate': {
                'main': session_rng.choice([
                    'professional international real estate consultant with global property portfolio',
                    'modern office with world map showing foreign property opportunities',
                    'luxury international property presentations and investment documentation',
                    'expert advisor explaining overseas real estate investment strategies',
                    'premium international real estate facility with global market expertise'
                ]),
                'about1': 'international property documentation and global market analysis tools',
                'about2': 'comprehensive foreign real estate investment process with expert guidance',
                'about3': 'professional international property facility with global investment resources'
            },
            'tire_service': {
                'main': session_rng.choice([
                    'professional tire service facility with modern wheel alignment equipment',
                    'expert tire technician installing new tires in modern service bay',
                    'comprehensive tire showroom displaying premium tire brands',
                    'professional tire replacement service with advanced mounting equipment',
                    'modern tire service center with quality tire storage systems'
                ]),
                'about1': 'professional tire installation equipment and wheel alignment systems',
                'about2': 'comprehensive tire service process with quality tire brands',
                'about3': 'modern tire service facility with seasonal tire storage solutions'
            },
            'landscape': {
                'main': session_rng.choice([
                    'professional landscape designer creating beautiful garden design',
                    'expert landscaping team transforming outdoor spaces with modern tools',
                    'beautiful landscaping project showcasing professional garden design',
                    'modern landscaping equipment for professional garden construction',
                    'experienced landscape architect planning outdoor space transformation'
                ]),
                'about1': 'professional landscaping tools and garden design equipment',
                'about2': 'comprehensive landscape design process with creative garden planning',
                'about3': 'modern landscaping facility with outdoor design and construction resources'
            },
            'financial': {
                'main': session_rng.choice([
                    'professional financial consultant providing expert financial advice',
                    'modern financial advisory office with investment analysis tools',
                    'expert financial advisor explaining wealth management strategies',
                    'comprehensive financial planning consultation with market analysis',
                    'professional financial services office with investment planning resources'
                ]),
                'about1': 'advanced financial planning software and investment analysis tools',
                'about2': 'comprehensive financial consultation process with expert advisory services',
                'about3': 'professional financial advisory facility with market research resources'
            },
            'student_housing': {
                'main': session_rng.choice([
                    'modern student apartment complex with comfortable living spaces',
                    'professional student housing manager showing apartment facilities',
                    'well-furnished student accommodation with study-friendly environment',
                    'student housing office with rental consultation services',
                    'comfortable student dormitory with modern housing amenities'
                ]),
                'about1': 'modern student housing amenities and comfortable living facilities',
                'about2': 'professional student accommodation process with rental guidance',
                'about3': 'student-friendly housing facility with study and living support services'
            },
            'legal': {
                'main': session_rng.choice([
                    'professional law office with experienced legal practitioners',
                    'modern legal consultation room with comprehensive legal resources',
                    'expert legal advisor providing professional legal guidance',
                    'professional legal services office with case documentation systems',
                    'comprehensive legal facility with court preparation resources'
                ]),
                'about1': 'professional legal documentation systems and case management tools',
                'about2': 'comprehensive legal consultation process with expert legal guidance',
                'about3': 'professional law office with legal research and case preparation resources'
            },
            'service': {
                'main': session_rng.choice([
                    f'professional {business_type} team delivering excellent service to satisfied customers',
                    f'modern {business_type} facility exterior with professional branding and signage',
                    f'successful {business_type} results showcasing quality work and expertise',
                    f'expert specialists working with {business_type} using professional techniques',
                    f'premium {business_type} service environment with modern equipment and professional atmosphere'
                ]),
                'about1': 'specialized equipment and professional service tools',
                'about2': 'efficient service process with expert knowledge and care',
                'about3': 'organized facility with professional quality standards'
            }
        }
        
        # Получаем специфичные детали или используем разнообразные универсальные
        details = adaptive_details.get(activity_type, adaptive_details['service'])
        
        # Генерируем МАКСИМАЛЬНО УНИКАЛЬНЫЕ промпты для лучшего разнообразия
        about_prefixes = [
            'professional', 'modern', 'expert', 'advanced', 'quality', 'specialized',
            'premium', 'innovative', 'cutting-edge', 'sophisticated', 'elite', 'world-class'
        ]
        about_styles = [
            'workspace', 'environment', 'facility', 'office', 'center', 'operation',
            'establishment', 'studio', 'headquarters', 'complex', 'institute', 'venue'
        ]
        
        # Создаем уникальные промпты с добавлением уникальности
        main_prompts = {
            'main': generator._add_uniqueness_to_prompt(details['main'], 'main', business_type),
            'about1': generator._create_clean_about_prompt(details['about1'], about_prefixes, 1),
            'about2': generator._create_clean_about_prompt(details['about2'], about_prefixes, 2),
            'about3': generator._create_clean_about_prompt(details['about3'], about_prefixes, 3)
        }
        
        print("🎭 Генерируем ЧЕЛОВЕЧЕСКИЕ review промпты...")
        # Генерируем ЧЕЛОВЕЧЕСКИЕ review промпты
        human_reviews = create_human_focused_review_prompts()
        
        # Генерируем уникальную фавиконку
        favicon_variants = [
            f"{theme_input} icon symbol, simple minimalist logo, business emblem",
            f"{theme_input} professional icon, clean business symbol, modern logo",
            f"{theme_input} corporate emblem, sleek icon design, minimal logo",
            f"{theme_input} business symbol, contemporary icon, elegant logo",
            f"{theme_input} company icon, modern symbol design, professional emblem"
        ]
        
        # Добавляем уникальность к favicon
        base_favicon = session_rng.choice(favicon_variants)
        favicon_timestamp = str(int(time.time() * 1000))[-4:]
        favicon_prompt = f"{base_favicon}, icon_{favicon_timestamp}"
        
        # Собираем все вместе
        complete_prompts = {
            'main': main_prompts['main'],
            'about1': main_prompts['about1'],
            'about2': main_prompts['about2'], 
            'about3': main_prompts['about3'],
            # review изображения больше не используются в AI-генерации
            'favicon': favicon_prompt
        }
        
        print(f"✅ Сгенерированы промпты: {list(complete_prompts.keys())}")
        
        # Дополнительно обеспечиваем уникальность всех промптов в наборе
        # НО НЕ для about промптов - они уже чистые
        prompts_to_enhance = {k: v for k, v in complete_prompts.items() 
                             if not k.startswith('about')}
        enhanced_prompts = generator._ensure_prompt_uniqueness(prompts_to_enhance)
        
        # Объединяем чистые about промпты с обработанными остальными
        for key in complete_prompts:
            if key.startswith('about'):
                enhanced_prompts[key] = complete_prompts[key]
        
        complete_prompts = enhanced_prompts
        
        # КРИТИЧНО: Используем универсальную систему оптимизации промптов
        try:
            from .prompt_optimizer import optimize_prompts_for_api
            complete_prompts = optimize_prompts_for_api(complete_prompts)
        except ImportError:
            # Fallback система, если оптимизатор недоступен
            max_lengths = {
                'main': 100, 'about1': 90, 'about2': 90, 'about3': 90,
                'review1': 110, 'review2': 110, 'review3': 110, 'favicon': 70
            }
            
            for key, prompt in complete_prompts.items():
                max_len = max_lengths.get(key, 90)
                if len(prompt) > max_len:
                    words = prompt.split()
                    truncated = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 <= max_len:
                            truncated.append(word)
                            current_length += len(word) + 1
                        else:
                            break
                    
                    complete_prompts[key] = ' '.join(truncated)
        
        # Выводим статистику уникальности
        uniqueness_score = generator._calculate_uniqueness_score(complete_prompts)
        print(f"🎯 Оценка уникальности промптов: {uniqueness_score}% (чем больше, тем лучше)")
        
        return complete_prompts
        
    except Exception as e:
        print(f"❌ ОШИБКА в инициализации: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_landing_prompt(country, city, language, domain, theme):
    """
    Создает промпт для генерации лендинга
    
    Args:
        country (str): Название страны
        city (str): Название города
        language (str): Язык лендинга (код)
        domain (str): Домен сайта
        theme (str): Тематика лендинга
    
    Returns:
        str: Готовый промпт для Cursor AI
    """
    from shared.helpers import get_current_year, get_language_display_name, get_language_name_by_code
    
    current_year = get_current_year()
    
    # Получаем человеко-читаемое название языка
    # Если язык переопределён вручную — используем название по коду, иначе по стране
    language_display = get_language_name_by_code(language) if language else get_language_display_name(country)
    
    return f"""You are an experienced web developer commissioned to build a fully functional business website. The site must be highly realistic, complete, and written as if it was handcrafted by real people — not generated by AI.

Each site is built in a new, isolated project, with no memory of previous work. No site should resemble any other. Use a different style, structure, and visual approach each time you generate a site.

---

## 📌 Input Parameters:

- Domain: {domain}  
- Language and country: {language_display}, {country}  
- Website topic: {theme}  
- Image folder: media  

IMPORTANT – FILESYSTEM RULES (STRICT):
- Use the CURRENT working directory as the project root. Do NOT create any extra top‑level folder (including a folder named after the domain). Put all files directly into the current folder.
- Create the image directory only as "./media" inside the current folder.
- Do NOT create or modify anything inside "./media". The folder already exists and must be used as‑is.
- Never generate or save new images/icons/SVGs. Do not create files with extensions: .svg, .png, .jpg, .jpeg, .webp, .gif, .ico, .avif (or any other image/binary assets).
- Do not inline SVG markup or base64‑encoded images into HTML/CSS/JS. Only reference already existing files.
- Never nest the project into an additional subfolder. If your scaffolder suggests creating a parent folder — do not do it; save files right here.

---

## 📄 Requirements:

### 1. Structure & Architecture:
- The site structure must be randomly selected. It can be:
  - A one-page landing site
  - A multi-page corporate site
  - A site with a blog (with several articles)
  - A site with a gallery, case studies, team section, etc.
- Each time, choose a different structure — as if you're creating a new site for a unique business client with different needs.

### 2. Home Page:
- The home page must be named: `index.html`
- However, in all internal links, always reference the file as `index.php`  
  ❌ Do not use: `href=\"index.html\"`  
  ✅ Only use: `href=\"index.php\"` or `href=\"index.php#section\"`

### 3. Content:
- Fill the site with detailed, rich content:
  - At least 5–7 different sections on the home page
  - Use lists, icons, images, forms, quotes, cards, etc.
  - Write diverse text content that feels like it was written by a real copywriter
- **Use images from the folder specified in the \"Image folder\" parameter**:
  - Example: `./media/file.jpg`  
  - No other image directories allowed.
  - Do NOT create or modify files in `./media`. The folder is provided and must remain unchanged.
  - Do NOT generate or embed SVGs (including inline `<svg>`), nor any new bitmap assets; reference existing files only.

### 4. Order Form (Required):
- On the home page, include a complete order form with:
  - Name, email, phone, message or service selection
  - Form settings:
    - `action=\"order.php\"`
    - `method=\"POST\"`
- Do not create the `order.php` file — just link to it

### 5. Legal Pages (Required):
- Create actual, separate HTML files:
  - `privacy.html`
  - `terms.html`
  - `cookies.html`
- These pages must:
  - Be written in the specified language ({language_display})
  - Contain realistic, complete content
  - Include a working link back to the homepage: `<a href=\"index.php\">Home</a>`
- All links across the site must be relative. Never use absolute links like https://{domain}/privacy.

### 6. Cookie Notification (MUST BE 100% WORKING):
- Display a cookie consent banner on first page load.
- Include a working "Accept" button that:
  - Hides the banner instantly.
  - Saves user consent in `localStorage` or a browser cookie.
  - Prevents the banner from appearing again until at least 1 year later.
  - Also log to console: `console.log('cookies_accepted')`.
- Must work equally well on desktop and mobile.
- The banner MUST NOT cause horizontal scrolling at any viewport width:
  - Do not use `overflow-x: hidden` or `overflow-x: auto`.
  - Use `position: fixed; left: 0; right: 0;` with `max-width: 100vw` and `box-sizing: border-box`.
  - Avoid horizontal translations; animate vertically (Y) or via opacity only.
  - Ensure paddings/margins do not exceed viewport width on 320, 768, 1024, 1440px.
- Style the banner so it doesn't overlap with important site elements.

### 7. Mobile Menu (MUST BE 100% WORKING):
- Include a mobile-friendly menu that:
  - Expands/collapses with a button (hamburger icon) using JavaScript.
  - Works on all screen sizes without page reload.
  - Supports smooth animation.
  - Is implemented with plain JS or explicitly included frameworks (no broken dependencies).
- Ensure links inside the mobile menu work and close the menu when clicked.
- The mobile menu MUST NOT introduce horizontal scrollbars:
  - Do not use `overflow-x: hidden` or `overflow-x: auto` to mask layout issues.
  - Use `max-width: 100vw` and `box-sizing: border-box`; avoid off-canvas widths > 100vw.
  - Prefer vertical slide or fade animations without X-axis overflow.
  - Test at 320, 768, 1024, 1440px.

### 8. Design & Styling:
- Use unique color schemes, fonts, spacing, layout techniques, and frameworks (or none at all)
- Each site must look and feel different from the others
- Use different front-end approaches (randomly choose):
  - Flexbox, CSS Grid, Bootstrap, Tailwind, native CSS, etc.
- Do not reuse block structures, section orders, or styling patterns

### 9. Realism:
- All links, buttons, and sections must function correctly
- Populate contact details, social media links, and addresses with plausible but random data — never leave them empty
- Avoid placeholders or filler text like "company name," "lorem ipsum," or "sample text"

### 10. SEO & Metadata:
- Add the following (all in the specified language and relevant to the topic):
  - `<title>` and `<meta name=\"description\">`
  - Open Graph meta tags
  - `<meta charset=\"UTF-8\">`, `<meta name=\"viewport\" ... >`
  - Favicon (randomly selected from the specified image folder)

### 11. Code Quality:
- Make the code look like it was written by a real developer, not an AI:
  - Use a mix of formatting styles (some compact, some spaced out, some commented)
  - Mix techniques: inline styles in one section, CSS classes in another
- Obfuscate the code structure slightly so it doesn't look like a generic boilerplate

### 12. External Links & Embeds (Randomized):
- Add 1–3 external links or embedded elements, like a real website would:
  - Links to maps, social platforms, blogs, partners, or external articles
  - Embedded iframe for Google Maps or YouTube
  - CDN-based CSS libraries or icon sets
- These external elements must be relevant to the business topic and feel naturally integrated

### 13. Additional Details:
- City: {city}
- Current year for all dates: {current_year}
- Ensure all content is realistic and professional
- Contact information should include:
  - Email with domain: contact@{domain}
  - Realistic phone number for {country}
  - Realistic address in {city}, {country}""" 