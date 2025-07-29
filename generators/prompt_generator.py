"""
Умный генератор промптов для изображений
Разбит из smart_prompt_generator.py для лучшей организации
"""

import random
from .translations import TRANSLATIONS, BUSINESS_TYPES

class SmartPromptGenerator:
    """УМНАЯ система генерации промптов для любых тематик БЕЗ интернета"""
    
    def __init__(self):
        self.translations = TRANSLATIONS
        self.business_types = BUSINESS_TYPES
    
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
                f"premium international real estate consultation with global market analysis and investment guidance",
                f"professional meeting discussing overseas property investment opportunities with market experts",
                f"modern real estate office with international property listings and global investment documentation",
                f"experienced consultant presenting foreign real estate investment options with legal compliance"
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
        """Выбирает лучшие промпты избегая повторений"""
        selected = []
        used_keywords = set()
        
        for prompt in prompts:
            # Проверяем уникальность ключевых слов
            words = prompt.lower().split()
            key_words = [w for w in words if len(w) > 4]
            
            if not any(word in used_keywords for word in key_words[:3]):
                selected.append(prompt)
                used_keywords.update(key_words[:3])
                
                if len(selected) >= count:
                    break
        
        # Если не хватает, добавляем оставшиеся
        while len(selected) < count and len(selected) < len(prompts):
            for prompt in prompts:
                if prompt not in selected:
                    selected.append(prompt)
                    if len(selected) >= count:
                        break
        
        return selected
    
    def _select_random_variant(self, variants):
        """Выбирает случайный вариант из списка"""
        return random.choice(variants) if variants else ""

# Функция для совместимости с другими модулями
def create_thematic_prompts(theme_input):
    """Создает тематические промпты для изображений - использует СУПЕР ИИ-генератор"""
    # ПРИОРИТЕТ 1: СУПЕР ИИ-УСИЛИТЕЛЬ
    try:
        from .super_ai_enhancer import create_super_ai_prompts
        super_prompts = create_super_ai_prompts(theme_input)
        return [super_prompts['main'], super_prompts['about1'], super_prompts['about2'], super_prompts['about3']]
    except Exception:
        # ПРИОРИТЕТ 2: Локальный ИИ-генератор
        try:
            from .ai_prompt_generator import AIPromptGenerator
            generator = AIPromptGenerator()
            # Генерируем промпты через ИИ и извлекаем только основные
            prompts = generator.generate_intelligent_prompts(theme_input)
            return [prompts['main'], prompts['about1'], prompts['about2'], prompts['about3']]
        except ImportError:
            # Fallback на старую систему
            generator = SmartPromptGenerator()
            return generator.generate_prompts(theme_input, silent_mode=True)

def create_human_focused_review_prompts():
    """
    Создает промпты для review изображений, которые ГАРАНТИРОВАННО показывают людей
    Использует СУПЕР ИИ-генератор для максимального качества
    """
    # ПРИОРИТЕТ 1: СУПЕР ИИ-УСИЛИТЕЛЬ для review промптов
    try:
        from .super_ai_enhancer import create_super_ai_prompts
        super_prompts = create_super_ai_prompts("satisfied customer")
        if 'review1' in super_prompts:
            return [super_prompts['review1'], super_prompts['review2'], super_prompts['review3']]
    except Exception:
        pass
    
    # ПРИОРИТЕТ 2: Локальный ИИ-генератор
    try:
        from .ai_prompt_generator import AIPromptGenerator
        generator = AIPromptGenerator()
        # Генерируем 3 review промпта через ИИ
        return [
            generator._generate_review_prompt(),
            generator._generate_review_prompt(),
            generator._generate_review_prompt()
        ]
    except ImportError:
        # Fallback на старую логику
        import random
        
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
        
        # Генерируем 3 уникальных review промпта
        review_prompts = []
        for i in range(3):
            person = random.choice(person_types)
            age = random.choice(ages)
            expression = random.choice(expressions)
            background = random.choice(backgrounds)
            
            prompt = (
                f"portrait photo of {person}, {age}, {expression}, "
                f"HUMAN FACE ONLY, NO OBJECTS, civilian clothes, "
                f"{background}, professional headshot style"
            )
            
            review_prompts.append(prompt)
        
        return review_prompts

def create_complete_prompts_dict(theme_input):
    """
    Создает полный словарь промптов для всех типов изображений включая review с людьми
    Использует СУПЕР ИИ-УСИЛИТЕЛЬ + fallback системы (БЕЗ OLLAMA)
    """
    # ПРИОРИТЕТ 1: СУПЕР ИИ-УСИЛИТЕЛЬ (множественные ИИ источники)
    try:
        from .super_ai_enhancer import create_super_ai_prompts
        super_prompts = create_super_ai_prompts(theme_input)
        print(f"🌟 Использован СУПЕР ИИ-УСИЛИТЕЛЬ для тематики: {theme_input}")
        return super_prompts
    except Exception as e:
        print(f"⚠️ Супер ИИ недоступен ({e}), переключаемся на обычный внешний ИИ")
    
    # ПРИОРИТЕТ 2: Обычный внешний ИИ-усилитель (Hugging Face)
    try:
        from .ai_enhancer import create_ai_enhanced_prompts
        enhanced_prompts = create_ai_enhanced_prompts(theme_input)
        print(f"🚀 Использован ВНЕШНИЙ ИИ-усилитель для тематики: {theme_input}")
        return enhanced_prompts
    except Exception as e:
        print(f"⚠️ Внешний ИИ недоступен ({e}), переключаемся на локальный ИИ")
    
    # ПРИОРИТЕТ 3: Локальный ИИ-генератор  
    try:
        from .ai_prompt_generator import create_ai_prompts
        local_prompts = create_ai_prompts(theme_input)
        print(f"🤖 Использован локальный ИИ-генератор для тематики: {theme_input}")
        return local_prompts
    except ImportError:
        print(f"⚠️ Локальный ИИ недоступен, используем fallback систему")
        # Fallback на старую систему если ИИ-генератор недоступен
        import random  # Для разнообразия main промптов
        
        generator = SmartPromptGenerator()
        context = generator.analyze_theme(theme_input, silent_mode=True)
    
    business_type = context['business_type']
    activity_type = context['activity_type']
    
    # УМНАЯ АДАПТИВНАЯ СПЕЦИФИЧНОСТЬ: 8.5+ баллов
    
    # Базовая консистентная структура
    core_base = f"professional {business_type} {activity_type} service"
    quality_base = f"modern high quality expert {business_type}"
    
    # Адаптивные детали по типу деятельности с РАЗНООБРАЗНЫМИ main промптами
    
    adaptive_details = {
        'automotive': {
            'main': random.choice([
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
        'training': {
            'main': random.choice([
                'professional instructor teaching engaged students in modern learning environment',
                'successful graduates celebrating completion of professional training program',
                'interactive educational session with expert knowledge sharing',
                'modern educational facility exterior with professional branding and signage',
                'diverse group of students actively participating in hands-on learning'
            ]),
            'about1': 'interactive learning equipment and educational technology tools',
            'about2': 'engaging teaching process with student-instructor interaction',
            'about3': 'accredited learning environment with educational quality standards'
        },
        'food': {
            'main': random.choice([
                'appetizing signature dishes beautifully presented on elegant dining table',
                'professional chef team preparing gourmet meals in modern kitchen',
                'welcoming restaurant exterior with attractive storefront and professional signage',
                'satisfied customers enjoying delicious meals in comfortable dining environment',
                'fresh high-quality ingredients artfully arranged for culinary preparation'
            ]),
            'about1': 'commercial kitchen equipment and professional culinary tools',
            'about2': 'food preparation process with culinary expertise and hygiene',
            'about3': 'certified food facility with health and safety standards'
        },
        'healthcare': {
            'main': random.choice([
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
        'financial': {
            'main': random.choice([
                'professional financial advisor consulting with satisfied clients in modern office',
                'expert financial consultant presenting investment strategies and portfolio analysis',
                'successful financial planning meeting with wealth management specialist',
                'prestigious financial services office with professional consulting environment',
                'experienced financial advisor providing personalized investment guidance'
            ]),
            'about1': 'advanced financial analysis software and professional investment tools',
            'about2': 'comprehensive financial planning process with expert market knowledge',
            'about3': 'certified financial advisory office with regulatory compliance standards'
        },
        'legal': {
            'main': random.choice([
                'professional legal consultation with experienced attorney in law office',
                'expert lawyer providing comprehensive legal advice to clients',
                'prestigious law firm exterior with professional legal branding',
                'successful legal team celebrating favorable case outcome',
                'modern legal office with professional consultation environment',
                'experienced attorney reviewing important legal documents and contracts',
                'professional legal team discussing complex investment transaction case',
                'elegant law firm conference room with legal consultation meeting',
                'expert legal advisor explaining contract terms to business clients',
                'sophisticated legal office with professional document management system',
                'senior lawyer providing specialized legal support for business deals',
                'modern law practice showcasing expertise in corporate legal matters'
            ]),
            'about1': random.choice([
                'comprehensive legal research tools and professional law library',
                'advanced legal documentation systems and case management tools',
                'specialized legal databases and professional research equipment',
                'modern legal technology and document preparation systems'
            ]),
            'about2': random.choice([
                'detailed legal consultation process with expert jurisprudence',
                'thorough legal analysis and strategic case development process',
                'comprehensive legal review and professional advisory services',
                'expert legal guidance and systematic case management approach'
            ]),
            'about3': random.choice([
                'certified law practice with professional ethics standards',
                'licensed legal facility with regulatory compliance protocols',
                'accredited law firm with professional quality assurance',
                'established legal practice with industry certification standards'
            ])
        },
        'marketing': {
            'main': random.choice([
                'creative marketing team developing innovative advertising campaigns',
                'successful brand promotion results showcasing marketing effectiveness',
                'modern marketing agency with dynamic creative workspace',
                'professional marketing consultant presenting strategic campaign plans',
                'digital marketing specialists analyzing campaign performance metrics'
            ]),
            'about1': 'advanced marketing analytics tools and creative design software',
            'about2': 'strategic marketing campaign development with creative expertise',
            'about3': 'results-driven marketing agency with proven success records'
        },
        'it_services': {
            'main': random.choice([
                'skilled software developers creating innovative technology solutions',
                'modern IT company office with advanced development infrastructure',
                'successful software deployment celebrating technical achievement',
                'professional IT consultants providing technology strategy guidance',
                'expert programmers collaborating on cutting-edge software projects'
            ]),
            'about1': 'state-of-the-art development equipment and programming tools',
            'about2': 'comprehensive software development process with technical expertise',
            'about3': 'certified IT services company with quality assurance standards'
        },
        'real_estate': {
            'main': random.choice([
                'professional real estate agent showcasing premium property portfolio',
                'successful property transaction with satisfied buyer and seller',
                'luxury real estate office with prestigious property listings',
                'expert property consultant providing market analysis and valuation',
                'modern real estate showroom with high-end property presentations'
            ]),
            'about1': 'advanced property management software and market analysis tools',
            'about2': 'comprehensive real estate transaction process with expert guidance',
            'about3': 'licensed real estate agency with professional certification standards'
        },
        'logistics': {
            'main': random.choice([
                'efficient logistics operation with modern warehouse and delivery fleet',
                'professional logistics team coordinating seamless supply chain management',
                'advanced logistics facility with automated storage and distribution systems',
                'successful cargo delivery showcasing reliable transportation services',
                'expert logistics consultants optimizing supply chain efficiency'
            ]),
            'about1': 'state-of-the-art logistics equipment and tracking technology',
            'about2': 'streamlined logistics process with precision delivery management',
            'about3': 'certified logistics facility with quality assurance protocols'
        },
        'tourism': {
            'main': random.choice([
                'amazing travel destination showcasing unforgettable tourism experiences',
                'professional tour guide leading engaging cultural exploration',
                'luxury travel agency office with premium vacation packages',
                'satisfied tourists enjoying expertly planned travel itinerary',
                'beautiful hotel reception welcoming international guests'
            ]),
            'about1': 'comprehensive travel planning tools and destination expertise',
            'about2': 'personalized tourism service with cultural immersion experience',
            'about3': 'certified travel agency with quality tourism standards'
        },
        'car_import': {
            'main': random.choice([
                'luxury imported vehicles displayed in premium automotive showroom with international certifications',
                'professional car import consultant reviewing documentation for overseas vehicle selection',
                'elegant automotive gallery showcasing high-end imported cars from USA, Korea, and Europe',
                'expert car selection specialist providing personalized import consultation services',
                'premium car import facility with international vehicle portfolio and expert guidance'
            ]),
            'about1': 'specialized import documentation tools and international automotive certification systems',
            'about2': 'comprehensive vehicle selection process with international sourcing expertise',
            'about3': 'certified car import facility with quality assurance and legal compliance standards'
        },
        'foreign_real_estate': {
            'main': random.choice([
                'professional international real estate consultant with global property investment portfolio',
                'modern investment office showcasing foreign real estate opportunities and market analysis',
                'luxury international property consultation with world-class investment documentation',
                'expert advisor presenting overseas real estate investment strategies and opportunities',
                'premium international real estate facility with global market expertise and guidance'
            ]),
            'about1': 'advanced international property analysis tools and global market research systems',
            'about2': 'comprehensive foreign real estate investment process with expert international guidance',
            'about3': 'certified international investment facility with legal compliance and market expertise'
        },
        'chauffeur_service': {
            'main': random.choice([
                'professional chauffeur in elegant uniform standing beside luxury vehicle fleet',
                'premium car rental service with experienced professional drivers and luxury vehicles',
                'elegant transportation facility showcasing luxury vehicle fleet and professional chauffeur team',
                'expert chauffeur service providing personalized luxury transportation with professional drivers',
                'luxury car rental office with premium vehicle selection and professional driver consultation'
            ]),
            'about1': 'professional driver training facilities and luxury vehicle maintenance systems',
            'about2': 'personalized chauffeur service process with luxury transportation expertise',
            'about3': 'certified transportation facility with professional driver standards and luxury vehicle fleet'
        },
        'credit_assessment': {
            'main': random.choice([
                'professional credit analyst reviewing client documents',
                'modern financial analysis office with assessment systems',
                'expert credit specialist conducting creditworthiness evaluation',
                'financial evaluation center with credit scoring technology',
                'experienced credit advisor providing assessment consultation',
                'professional banking office with credit analysis tools',
                'modern credit bureau with financial data analysis',
                'expert financial analyst evaluating business creditworthiness'
            ]),
            'about1': random.choice([
                'credit analysis software and assessment tools',
                'credit scoring systems and verification technology',
                'financial data analysis and reporting equipment',
                'credit evaluation tools and risk assessment systems'
            ]),
            'about2': random.choice([
                'credit assessment process with financial analysis',
                'creditworthiness evaluation with professional expertise',
                'financial review process with scoring methodology',
                'credit analysis approach with risk evaluation'
            ]),
            'about3': random.choice([
                'credit assessment facility with compliance standards',
                'financial analysis center with certification protocols', 
                'credit bureau with professional quality assurance',
                'financial evaluation practice with banking standards'
            ])
        },
        'tire_service': {
            'main': random.choice([
                'professional tire shop with modern wheel alignment equipment and seasonal tire storage',
                'expert tire technician installing new tires on vehicle in modern automotive service bay',
                'comprehensive tire showroom displaying premium tire brands and seasonal tire options',
                'professional tire replacement service with advanced tire mounting and balancing equipment',
                'modern tire service center with quality tire storage and professional installation tools'
            ]),
            'about1': 'specialized tire installation equipment and wheel alignment tools',
            'about2': 'professional tire service process with expert mounting and balancing',
            'about3': 'certified tire service facility with quality assurance and safety standards'
        },
        'student_housing': {
            'main': random.choice([
                'modern student apartment complex with comfortable living spaces and study areas',
                'professional student housing manager showing apartment to prospective student tenants',
                'well-furnished student apartment with modern amenities and study-friendly environment',
                'student housing office with professional rental consultation and lease agreement services',
                'comfortable student dormitory exterior with modern student housing facilities'
            ]),
            'about1': 'modern student apartment furnishings and study equipment',
            'about2': 'professional student housing rental process with lease consultation',
            'about3': 'certified student accommodation facility with quality housing standards'
        },
        'land_plots': {
            'main': random.choice([
                'beautiful rural land plots with scenic countryside views and development potential',
                'professional real estate agent showcasing premium agricultural land and country properties',
                'picturesque country property with farmhouse potential and agricultural land development',
                'expert land consultant providing guidance on rural property investment and land development',
                'expansive agricultural land with fertile soil perfect for farming and country living'
            ]),
            'about1': 'professional land surveying equipment and property development tools',
            'about2': 'comprehensive land evaluation process with development consultation',
            'about3': 'certified real estate facility with agricultural property expertise'
        },
        'short_rental': {
            'main': random.choice([
                'elegant short-term rental apartment with modern furnishings and guest amenities',
                'professional short-term rental manager providing accommodation services and guest support',
                'luxurious vacation rental interior with comfortable furnishings and modern conveniences',
                'short-term rental office with professional booking services and guest accommodation',
                'beautiful vacation rental property exterior with attractive amenities and guest facilities'
            ]),
            'about1': 'modern vacation rental furnishings and guest service amenities',
            'about2': 'professional short-term rental booking process with guest services',
            'about3': 'certified vacation rental facility with hospitality quality standards'
        },
        'landscape': {
            'main': random.choice([
                'professional landscape designer creating beautiful garden design with modern landscaping tools',
                'expert landscaping team transforming outdoor spaces with creative garden design and installation',
                'beautiful landscaping project showcasing professional garden design and quality workmanship',
                'modern landscaping equipment and tools for professional garden construction and maintenance',
                'experienced landscape architect planning outdoor space transformation with design expertise'
            ]),
            'about1': 'professional landscaping equipment and garden design tools',
            'about2': 'expert landscaping process with creative design and installation',
            'about3': 'certified landscaping facility with quality craftsmanship standards'
        }
    }
    
    # Получаем специфичные детали или используем разнообразные универсальные
    details = adaptive_details.get(activity_type, {
        'main': random.choice([
            f'professional {business_type} team delivering excellent service to satisfied customers',
            f'modern {business_type} facility exterior with professional branding and signage',
            f'successful {business_type} results showcasing quality work and expertise',
            f'expert specialists working with {business_type} using professional techniques',
            f'premium {business_type} service environment with modern equipment and professional atmosphere'
        ]),
        'about1': 'specialized equipment and professional service tools',
        'about2': 'efficient service process with expert knowledge and care',
        'about3': 'organized facility with professional quality standards'
    })
    
    # Генерируем РАЗНООБРАЗНЫЕ промпты для лучшей уникальности
    about_prefixes = ['professional', 'modern', 'expert', 'advanced', 'quality', 'specialized']
    about_styles = ['workspace', 'environment', 'facility', 'office', 'center', 'operation']
    
    main_prompts = {
        'main': f"{details['main']}",
        'about1': f"{random.choice(about_prefixes)} {business_type} {details['about1']}", 
        'about2': f"{random.choice(about_prefixes)} {business_type} {details['about2']} {random.choice(about_styles)}",
        'about3': f"{random.choice(about_prefixes)} {business_type} {details['about3']} {random.choice(about_styles)}"
    }
    
    # Генерируем ЧЕЛОВЕЧЕСКИЕ review промпты
    human_reviews = create_human_focused_review_prompts()
    
    # Генерируем фавиконку
    favicon_prompt = f"{theme_input} icon symbol, simple minimalist logo, business emblem"
    
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
        
        return complete_prompts

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