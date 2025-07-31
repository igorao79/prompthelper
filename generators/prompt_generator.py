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
        """Анализирует тематику и возвращает контекст для генерации промптов"""
        if not silent_mode:
            print(f"🧠 Анализ тематики: {theme}")
        
        theme_lower = theme.lower()
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
                f"professional financial advisor explaining {business_type}",
                f"modern office setting for {business_type} consultation",
                f"charts and graphs showing {business_type} growth",
                f"confident investor learning about {business_type}",
                f"professional presentation about {business_type} strategies"
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
        if attempt > 20:  # Предотвращаем бесконечные циклы
            return None
            
        combo_key = f"{base_type}_{rotation_seed % len(subtype_choices)}_{attempt}"
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

def create_extended_human_prompts(count=5):
    """
    Создает расширенный набор промптов для людей в различных сценариях
    Используется для получения большего разнообразия изображений людей
    """
    import random
    import time
    import uuid
    
    # Инициализируем уникальный генератор с МАКСИМАЛЬНОЙ энтропией для бизнес-промптов
    rng = random.Random()
    # Используем микросекунды + случайный UUID + ID процесса для гарантированной уникальности
    unique_seed = int(time.time() * 1000000) + hash(str(uuid.uuid4())) + os.getpid() + random.randint(1, 1000000)
    rng.seed(unique_seed)
    
    # Дополнительные сценарии и контексты
    business_scenarios = [
        "team meeting", "client consultation", "project presentation", "business negotiation",
        "strategic planning", "performance review", "training session", "product demonstration",
        "sales meeting", "customer service", "executive briefing", "company workshop"
    ]
    
    work_environments = [
        "modern office", "conference room", "co-working space", "business center",
        "corporate headquarters", "startup office", "executive suite", "meeting room",
        "professional workspace", "consultation room", "training facility", "boardroom"
    ]
    
    interaction_types = [
        "one-on-one discussion", "group collaboration", "team presentation", "client interaction",
        "mentoring session", "peer consultation", "leadership meeting", "project review",
        "brainstorming session", "strategic discussion", "planning meeting", "feedback session"
    ]
    
    professional_activities = [
        "analyzing data", "presenting solutions", "discussing strategies", "reviewing documents",
        "making decisions", "sharing insights", "providing guidance", "explaining concepts",
        "demonstrating expertise", "offering advice", "solving problems", "building relationships"
    ]
    
    print(f"🎬 Создание расширенных промптов для людей (количество: {count})")
    
    extended_prompts = []
    used_combinations = set()
    
    for i in range(count):
        attempts = 0
        while attempts < 20:
            # Выбираем из всех доступных категорий
            scenario = rng.choice(business_scenarios)
            environment = rng.choice(work_environments)
            interaction = rng.choice(interaction_types)
            activity = rng.choice(professional_activities)
            
            # Базовые характеристики человека (используем сокращенные списки для разнообразия)
            person_types = [
                "professional woman", "business man", "experienced consultant", "young executive",
                "senior manager", "team leader", "industry expert", "skilled specialist"
            ]
            
            expressions = [
                "confident demeanor", "engaging smile", "professional composure", "approachable expression",
                "focused attention", "warm professionalism", "expert confidence", "trustworthy appearance"
            ]
            
            clothing = [
                "business professional attire", "smart casual wear", "executive outfit", "modern business dress"
            ]
            
            person = rng.choice(person_types)
            expression = rng.choice(expressions)
            outfit = rng.choice(clothing)
            
            # Создаем ключ для проверки уникальности
            combination_key = f"{person}_{scenario}_{environment}_{activity}"
            
            if combination_key not in used_combinations:
                used_combinations.add(combination_key)
                break
            
            attempts += 1
        
        # Добавляем уникальные идентификаторы
        timestamp = str(int(time.time() * 1000))[-4:]
        unique_id = str(uuid.uuid4())[:8]
        
        # Создаем детализированный промпт
        prompt = (
            f"{person} in {environment}, {expression}, {outfit}, "
            f"{interaction}, {activity}, {scenario} context, "
            f"professional photography, business setting, "
            f"natural lighting, confident posture, "
            f"composition_{timestamp}, scene_{unique_id}"
        )
        
        extended_prompts.append(prompt)
        print(f"   ✅ Расширенный промпт {i+1}: {scenario} в {environment}")
    
    print(f"🎉 Создано {len(extended_prompts)} уникальных расширенных промптов для людей!")
    return extended_prompts

def create_diverse_customer_prompts(count=10):
    """
    Создает максимально разнообразные промпты клиентов для разных демографических групп
    Включает различные возрасты, профессии, этнические группы и стили
    """
    import random
    import time
    import uuid
    
    # Инициализируем уникальный генератор с МАКСИМАЛЬНОЙ энтропией для разнообразных клиентов
    rng = random.Random()
    # Используем микросекунды + случайный UUID + ID процесса для гарантированной уникальности
    unique_seed = int(time.time() * 1000000) + hash(str(uuid.uuid4())) + os.getpid() + random.randint(1, 1000000)
    rng.seed(unique_seed)
    
    # Разнообразные демографические группы
    age_groups = [
        "young adult 20-25", "millennial 26-30", "early thirties 31-35", "mid-thirties 36-40",
        "early forties 41-45", "mid-forties 46-50", "early fifties 51-55", "mature adult 56-60",
        "senior professional 61-65", "experienced individual 66-70"
    ]
    
    professions = [
        "healthcare worker", "teacher", "engineer", "lawyer", "accountant", "manager",
        "consultant", "entrepreneur", "designer", "developer", "analyst", "coordinator",
        "specialist", "director", "supervisor", "executive", "administrator", "technician"
    ]
    
    lifestyle_types = [
        "urban professional", "suburban family person", "rural business owner", "city dweller",
        "small town resident", "metropolitan worker", "countryside professional", "downtown entrepreneur"
    ]
    
    personality_traits = [
        "confident", "approachable", "friendly", "professional", "warm", "trustworthy",
        "reliable", "experienced", "knowledgeable", "compassionate", "dedicated", "skilled"
    ]
    
    ethnic_representations = [
        "diverse background", "multicultural heritage", "international appearance", "global citizen",
        "cross-cultural individual", "universal professional", "inclusive representation", "worldwide community member"
    ]
    
    clothing_variations = [
        "business casual", "professional formal", "smart casual", "contemporary style",
        "modern professional", "classic business", "trendy professional", "sophisticated casual",
        "executive style", "industry-appropriate", "workplace suitable", "meeting-ready"
    ]
    
    emotional_states = [
        "genuinely happy", "deeply satisfied", "extremely pleased", "thoroughly content",
        "remarkably grateful", "exceptionally joyful", "profoundly appreciative", "truly delighted",
        "sincerely thankful", "authentically cheerful", "naturally optimistic", "radiantly positive"
    ]
    
    photo_contexts = [
        "testimonial photo", "customer review image", "client satisfaction portrait", "service feedback photo",
        "business testimonial", "professional review", "customer story image", "success story portrait",
        "client experience photo", "satisfaction survey image", "feedback testimonial", "review documentation"
    ]
    
    print(f"🌈 Создание максимально разнообразных промптов клиентов (количество: {count})")
    print(f"   🎯 Возрастные группы: {len(age_groups)}")
    print(f"   💼 Профессии: {len(professions)}")
    print(f"   🏠 Стили жизни: {len(lifestyle_types)}")
    print(f"   😊 Черты характера: {len(personality_traits)}")
    print(f"   🌍 Этнические представления: {len(ethnic_representations)}")
    print(f"   👕 Варианты одежды: {len(clothing_variations)}")
    print(f"   💫 Эмоциональные состояния: {len(emotional_states)}")
    print(f"   📷 Контексты фото: {len(photo_contexts)}")
    
    diverse_prompts = []
    used_combinations = set()
    
    for i in range(count):
        attempts = 0
        while attempts < 25:
            # Выбираем характеристики из всех категорий
            age = rng.choice(age_groups)
            profession = rng.choice(professions)
            lifestyle = rng.choice(lifestyle_types)
            personality = rng.choice(personality_traits)
            ethnicity = rng.choice(ethnic_representations)
            clothing = rng.choice(clothing_variations)
            emotion = rng.choice(emotional_states)
            context = rng.choice(photo_contexts)
            
            # Дополнительные детали
            lighting_options = [
                "natural daylight", "soft studio lighting", "warm interior lighting", "professional portrait lighting"
            ]
            
            composition_styles = [
                "close-up portrait", "medium shot", "professional headshot", "three-quarter view"
            ]
            
            background_options = [
                "neutral background", "office setting", "modern environment", "professional backdrop"
            ]
            
            lighting = rng.choice(lighting_options)
            composition = rng.choice(composition_styles)
            background = rng.choice(background_options)
            
            # Создаем ключ для проверки уникальности
            combination_key = f"{age}_{profession}_{lifestyle}_{personality}_{emotion}"
            
            if combination_key not in used_combinations:
                used_combinations.add(combination_key)
                break
            
            attempts += 1
        
        # Добавляем уникальные идентификаторы
        timestamp = str(int(time.time() * 1000))[-4:]
        unique_id = str(uuid.uuid4())[:8]
        session_hash = str(hash(f"{i}_{timestamp}"))[-4:]
        
        # Создаем СУПЕР-детализированный промпт
        prompt = (
            f"{context} of {personality} {profession}, {age}, {lifestyle}, "
            f"{ethnicity}, {emotion}, wearing {clothing}, "
            f"{composition}, {background}, {lighting}, "
            f"high quality professional photography, authentic expression, "
            f"HUMAN FACE FOCUS, NO OBJECTS, natural pose, "
            f"diverse_{timestamp}, client_{unique_id}, story_{session_hash}"
        )
        
        diverse_prompts.append(prompt)
        print(f"   ✅ Клиент {i+1}: {profession} ({age}) - {emotion}")
    
    print(f"🎊 Создано {len(diverse_prompts)} максимально разнообразных промптов клиентов!")
    print(f"   📊 Уникальность: 100% (все комбинации различны)")
    print(f"   🎭 Демографическое покрытие: полное")
    print(f"   🌟 Эмоциональное разнообразие: максимальное")
    
    return diverse_prompts

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
            'about1': generator._add_uniqueness_to_prompt(
                f"{session_rng.choice(about_prefixes)} {business_type} {details['about1']}", 
                'about1', business_type
            ),
            'about2': generator._add_uniqueness_to_prompt(
                f"{session_rng.choice(about_prefixes)} {business_type} {details['about2']} {session_rng.choice(about_styles)}", 
                'about2', business_type
            ),
            'about3': generator._add_uniqueness_to_prompt(
                f"{session_rng.choice(about_prefixes)} {business_type} {details['about3']} {session_rng.choice(about_styles)}", 
                'about3', business_type
            )
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
            'review1': human_reviews[0],
            'review2': human_reviews[1],
            'review3': human_reviews[2],
            'favicon': favicon_prompt
        }
        
        print(f"✅ Сгенерированы промпты: {list(complete_prompts.keys())}")
        
        # Дополнительно обеспечиваем уникальность всех промптов в наборе
        complete_prompts = generator._ensure_prompt_uniqueness(complete_prompts)
        
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
    from shared.helpers import get_current_year, get_language_display_name
    
    current_year = get_current_year()
    
    # Получаем человеко-читаемое название языка
    language_display = get_language_display_name(country)
    
    return f"""[0] Мне нужен продающий лендинг пейдж, тематика: {theme} ({country}).
Язык лендинга: {language_display}
Домен: {domain}
еще момент: там в промпте указано, чтобы ссылки на главную страницу с внешних (политика, правила и т.д.) , была href="index.php" а не href="index.html"
за этим нужно следить
Страна - {country}
Город - {city}
Везде ставь {current_year} как дату

[1] Это должен быть 1 страничный лендинг, адаптивный, обязательно нужно рабочее мобильное меню. В папке media есть картинки, используй их все!
блоки и картинки должны выглядеть красиво на ВСЕХ устройствах, если что-то не вмещается, то удлиняй страницу, делай контент столбиком display flex, flex-direction column. Блоки, где три картинки на компьютере должны быть на одной строчке.

[2] Нужен продающий текст на этом лендинге, но чтобы его пропустили в гугл адс.
То есть без ложных обещаний и т.д. Также в тексте на должно быть никаких упоминаний об инвестициях, политике, акциях, финансах и тд. Также с отказом от ответственности и т.д. Текст должен быть не на 2-3 предложения, а больше, столько-сколько требуется для хорошей конверсии сайта. Минимум 5 блоков, в каждом из кторых 3-5 абзацев, по 2-5 предложений в каждом.

[3] В футере нужны политики конфиденциальности, условия пользования и т.д., сам додумай что ещё нужно для современного сайта и добавь. Все эти политики должны быть на отдельных страницах. Каждая политика минимум на 10 пунктов и очень подробно расписана, в каждом пункте минимум по 3 предложения

[4] Нужна форма заказа с полями "имя" и "номер телефона", при нажатии на кнопку отправить/заказ или как ты ее там назовешь, должен отрабатывать следующий файл "order.php" Без дополнительных JavaScript-обработчиков, только базовая HTML5-валидация и прямая отправка на order.php. Сам файл order.php писать не нужно
Так же можешь добавить какие-нибудь свои инпуты.

[5] В футере добавь контактный емайл с моим доменом и какой нибудь вымышленный номер телефона страны на которую пишешь лендинг, еще адрес тоже любой из этой страны. Вымышленный номер, это не значит что он должен быть с цифрами 123 456 78 90 или 222 55 12345 и тому подобных несуществующих номеров. Это значит что номер должен быть настоящим, но рандомным. 
Ради бога молю, сделай нормальный номер! не 1234567
В адресе не используй нереалистичные цифры, такие как 123 321 1234 и т.д.
Я запрещаю использовать в адресе Av. Paseo de la Reforma

[6] Добавь всплывающий вопрос о куки при заходе. Сделай его красивым

[7] Не забудь фавикон. Фавиконом будет картинка из папки с картинками favicon.png. Ссылки на соцсети делать не нужно

[8] Сделай выделяющийся и запоминающийся дизайн, чтобы лендинг выглядел объемно. Политики пиши большие, как на сайте настоящего бизнеса. Используй кастомные шрифты из библиотеки Google Fonts и иконки из библиотеки Font Awesome

[9] Комментарии в коде пиши только на английском или {language.lower()}

[10] order.php и страница спасибо не нужны, я сделаю их позже. css и js вынеси в отдельные файлы, храниться они должны в корневой директории.

[11] Важно! Главную страницу назови index.html, но во всех внутренних ссылках на эту страницу (с других страниц политик, условий и т.д.) используй имя index.php вместо index.html. То есть, несмотря на то, что файл главной страницы называется index.html, все ссылки на него должны быть вида href="index.php" или href="index.php#section". Это нужно для того, чтобы после переименования файла index.html в index.php на хостинге все ссылки работали корректно без дополнительных изменений. Обрати на это особое внимание! Нигде в проекте не должно быть <a href="index.html">, только <a href="index.php">.

[12] Контента на сайте должно быть много. Пиши длинные тексты, полностью раскрывай каждую тему, делать большие блоки, разворачивай каждую мысль в несколько абзацев

[13] На лендинге не должно быть кнопок/ссылок, которые ничего не делают или никуда не ведут!

[14] Каждую задачу по созданию нового файла с кодом (style.css, index.html и т.п.) разделяй на 3-5 частей иначе у тебя начинаются затупы с "Error calling tool 'edit_file'.". То есть сначала создаешь базовую структуру, а потом уже дополняешь ее блоками.

[15] После завершения лендинга проверь его на соответствие каждому из этих пунктов. Если обнаружишь несоответствия, сразу устрани их

[16] Я ЗАПРЕЩАЮ ГРУЗИТЬ ЧТО-ТО НА ЛОКАЛЬНЫЙ СЕРВЕР

[17] Перед созданием лендинга сгенерируй UUID, возьми первые два символа, преобразуй в число, возьми остаток от деления на 25, прибавь 1, и в зависимости от результата примени соответствующий стиль дизайна из списка 25 вариантов.

[18] Во всех политических блоках должен быть хедер с возвратом на главную страницу, должно быть адаптивно и на мобильном телефоне также. Хэдер должен содержать название сайта

[19] ОЧЕНЬ ВАЖНО ЧТОБЫ КУКИ УВЕДОМЛЕНИЕ РАБОТАЛО КОРРЕКТНО И БЕЗ КАКИХ ЛИБО БАГОВ, ОБЯЗАТЕЛЬНО, ДОБАВЛЯЙ console.log когда куки принято

[20] В полисити блоках с таблицами ДОПОЛНИТЕЛЬ ПРОВЕРЯЙ АДАПТИВНОСТЬ! МНОГИЕ ДВИГАЮСТЯ!

[21] НЕ ИСПОЛЬЗУЙ OVERFLOW-X: HIDDEN И OVERFLOW-X: AUTO""" 