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
        
        # Если найдены финансовые термины + консультация = financial
        if financial_detected and ('консультация' in theme_lower or 'consultant' in found_terms):
            activity_type = 'financial'
        
        # 2. Автомобильная тематика  
        automotive_indicators = [
            'автомобил', 'машин', 'авто', 'автосервис', 'автомойка', 'эвакуатор',
            'тюнинг', 'шиномонтаж', 'автозапчасти', 'диагностика', 'cars', 'automotive'
        ]
        
        if activity_type == 'service':  # Только если еще не определено
            for indicator in automotive_indicators:
                for theme_word in theme_words:
                    if theme_word == indicator or theme_word.startswith(indicator) or theme_word.endswith(indicator):
                        activity_type = 'automotive'
                        break
                if activity_type == 'automotive':
                    break
        
        # Только если НЕ автомобильная тема, проверяем остальные типы деятельности
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
        
        # Специализированные промпты по типу деятельности
        specialized = self._get_specialized_prompts(activity_type, business_type)
        
        # Комбинируем базовые и специализированные
        all_prompts = base_prompts + specialized
        
        # Выбираем 8 лучших промптов
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
    """Создает тематические промпты для изображений"""
    generator = SmartPromptGenerator()
    return generator.generate_prompts(theme_input, silent_mode=True)

def create_human_focused_review_prompts():
    """
    Создает промпты для review изображений, которые ГАРАНТИРОВАННО показывают людей
    """
    # КРИТИЧНО: Только обычные люди-клиенты, НЕ РАБОТНИКИ!
    person_types = [
        "happy customer", "satisfied client", "pleased woman", "smiling man",
        "grateful person", "content customer", "cheerful client", "positive person",
        "thankful customer", "delighted client", "appreciative woman", "joyful man",
        "happy female customer", "satisfied male client", "pleased young woman", 
        "smiling young man", "grateful middle-aged person", "content elderly customer"
    ]
    
    ages = [
        "young adult", "middle-aged person", "mature adult", "30-40 years old",
        "25-35 years old", "40-50 years old", "adult person", "20-30 years old",
        "35-45 years old", "mature woman", "mature man"
    ]
    
    expressions = [
        "genuine smile", "happy expression", "satisfied look", "positive facial expression",
        "authentic joy", "natural smile", "pleased appearance", "grateful expression",
        "bright smile", "warm expression", "joyful face", "content expression"
    ]
    
    backgrounds = [
        "clean background", "neutral background", "simple background", "white background",
        "professional background", "minimal background", "soft background"
    ]
    
    # Генерируем 3 уникальных review промпта
    review_prompts = []
    for i in range(3):
        person = random.choice(person_types)
        age = random.choice(ages)
        expression = random.choice(expressions)
        background = random.choice(backgrounds)
        
        # РАДИКАЛЬНЫЙ промпт - ТОЛЬКО ЛЮДИ!
        prompt = (
            f"portrait photo of {person}, {age}, {expression}, "
            f"HUMAN FACE ONLY, PERSON ONLY, NO OBJECTS VISIBLE, NO EQUIPMENT, "
            f"NO BUSINESS ITEMS, NO WORK TOOLS, NO UNIFORMS, NO PROFESSIONAL GEAR, "
            f"civilian clothes, casual clothing, regular person, everyday clothes, "
            f"customer testimonial portrait, {background}, "
            f"professional headshot style, natural lighting, "
            f"close-up face shot, human portrait only, customer review photo"
        )
        
        review_prompts.append(prompt)
    
    return review_prompts

def create_complete_prompts_dict(theme_input):
    """
    Создает полный словарь промптов для всех типов изображений включая review с людьми
    """
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
                'modern legal office with professional consultation environment'
            ]),
            'about1': 'comprehensive legal research tools and professional law library',
            'about2': 'detailed legal consultation process with expert jurisprudence',
            'about3': 'certified law practice with professional ethics standards'
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
    
    # Генерируем умные адаптивные промпты с разнообразными main изображениями
    main_prompts = {
        'main': f"{core_base}, {quality_base} {details['main']}",
        'about1': f"{core_base} equipment workspace, {quality_base} {details['about1']}", 
        'about2': f"{core_base} active operations, {quality_base} {details['about2']}",
        'about3': f"{core_base} facility environment, {quality_base} {details['about3']}"
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