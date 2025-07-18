#!/usr/bin/env python3
"""
Умный генератор вариативных промптов
Создает разные варианты каждый раз, но исключает проблемные слова
"""

import random

class SmartVariativePrompts:
    """Генератор вариативных промптов с умными исключениями"""
    
    def __init__(self):
        # Базовые элементы для конструирования промптов
        self.business_elements = {
            'доставка еды': {
                'objects': ['delicious pizza delivery', 'fresh sushi delivery', 'gourmet burger delivery', 'hot pasta delivery', 'asian noodles takeout', 'healthy salad delivery', 'italian cuisine delivery', 'mexican food delivery', 'chinese takeout delivery', 'french pastry delivery'],
                'actions': ['preparing for delivery', 'packing for delivery', 'delivering food', 'food delivery service', 'takeout preparation', 'delivery packaging', 'courier delivering food', 'delivering hot food'],
                'qualities': ['fresh delivered', 'hot delivery', 'fast delivery', 'gourmet delivery', 'home delivery', 'quick delivery', 'express delivery', 'premium delivery'],
                'environments': ['delivery kitchen', 'takeout restaurant', 'food delivery counter', 'delivery preparation area', 'courier service area'],
                'delivery_elements': ['delivery bag', 'delivery scooter', 'takeout container', 'delivery service', 'food courier', 'delivery process', 'delivery man with food'],
                'banned_words': [],  # Убираем бан-слова для доставки
                'favicon_symbols': ['🍕', '🍔', '🥘', '🚚', '🛵', '📦']
            },
            'продажа авто': {
                'objects': ['luxury car', 'new vehicle', 'sports car', 'sedan', 'suv', 'car interior', 'dashboard', 'steering wheel', 'car seats'],
                'actions': ['displaying', 'showcasing', 'presenting', 'consulting', 'demonstrating'],
                'qualities': ['premium', 'luxury', 'modern', 'elegant', 'sleek', 'sophisticated'],
                'environments': ['showroom', 'dealership', 'car lot', 'sales office', 'exhibition hall'],
                'banned_words': ['mechanic', 'repair', 'tool', 'механик', 'ремонт'],  # СТРОГО ЗАПРЕЩЕНО для about2
                'about2_safe': ['car interior', 'leather seats', 'dashboard design', 'comfort features', 'modern controls'],
                'favicon_symbols': ['🚗', '🚙', '🏎️', '🔑', '🛞', '🚘']
            },
            'недвижимость': {
                'objects': ['luxury apartment', 'modern house', 'commercial property', 'residential building', 'office space', 'cozy home interior', 'elegant living room', 'modern kitchen', 'spacious bedroom'],
                'actions': ['showcasing', 'presenting', 'consulting', 'touring', 'displaying'],
                'qualities': ['premium', 'luxury', 'modern', 'spacious', 'comfortable', 'elegant', 'prestigious', 'well-located'],
                'environments': ['real estate office', 'property showroom', 'consultation room', 'property viewing area', 'sales office'],
                'banned_words': ['car', 'vehicle', 'авто', 'машин'],  # СТРОГО ЗАПРЕЩЕНО упоминание автомобилей
                'about2_safe': ['home interior', 'apartment layout', 'property features', 'room design', 'living space'],
                'favicon_symbols': ['🏠', '🏡', '🏢', '🏘️', '🗝️', '📋']
            },
            'кафе': {
                'objects': ['coffee cup', 'espresso', 'cappuccino', 'latte art', 'coffee beans', 'pastry', 'croissant'],
                'actions': ['brewing', 'serving', 'enjoying', 'relaxing', 'socializing'],
                'qualities': ['aromatic', 'fresh', 'premium', 'artisan', 'cozy', 'warm'],
                'environments': ['coffee shop', 'cafe interior', 'coffee bar', 'seating area', 'barista station'],
                'favicon_symbols': ['☕', '🍰', '🥐', '🫘', '🧁', '🍪']
            },
            'автомойка': {
                'objects': ['clean car', 'washing equipment', 'soap foam', 'shiny vehicle', 'water spray'],
                'actions': ['washing', 'cleaning', 'polishing', 'detailing', 'drying'],
                'qualities': ['spotless', 'gleaming', 'professional', 'thorough', 'careful'],
                'environments': ['car wash bay', 'service area', 'cleaning station', 'wash tunnel'],
                'favicon_symbols': ['🚿', '🧽', '🚗', '💧', '��', '✨']
            },
            'эвакуатор': {
                'objects': ['tow truck', 'recovery vehicle', 'flatbed truck', 'evacuation service', 'roadside assistance', 'emergency vehicle', 'rescue truck', 'towing equipment'],
                'actions': ['towing', 'evacuating', 'rescuing', 'transporting', 'helping', 'emergency response', 'roadside assistance', 'vehicle recovery'],
                'qualities': ['reliable', 'fast emergency', '24/7 available', 'professional rescue', 'prompt response', 'careful handling', 'emergency ready'],
                'environments': ['emergency scene', 'roadside', 'towing yard', 'dispatch center', 'service garage'],
                'favicon_symbols': ['🚚', '🛠️', '🆘', '🚨', '⚡', '🔧']
            },
            'стоматология': {
                'objects': ['dental chair', 'modern dental equipment', 'dental tools', 'healthy teeth', 'dental office', 'x-ray equipment', 'dental implants', 'dental treatment'],
                'actions': ['examining', 'treating', 'cleaning', 'consulting', 'diagnosing', 'providing care', 'restoring teeth', 'dental procedures'],
                'qualities': ['professional dental', 'pain-free', 'modern technology', 'experienced care', 'gentle treatment', 'sterile conditions', 'advanced methods'],
                'environments': ['dental office', 'treatment room', 'dental clinic', 'consultation area', 'sterilization room'],
                'favicon_symbols': ['🦷', '🏥', '⚕️', '🩺', '💊', '🔬']
            },
            'парикмахерская': {
                'objects': ['barber chair', 'styling tools', 'hair dryer', 'scissors', 'hair products', 'mirror station', 'styling equipment', 'hair salon'],
                'actions': ['cutting hair', 'styling', 'coloring', 'treating hair', 'consulting', 'creating hairstyles', 'hair care', 'professional styling'],
                'qualities': ['stylish', 'trendy', 'professional styling', 'modern techniques', 'creative design', 'personalized service', 'fashion-forward'],
                'environments': ['hair salon', 'styling station', 'barber shop', 'beauty salon', 'hair studio'],
                'favicon_symbols': ['✂️', '💇', '💅', '🪒', '🎀', '💄']
            },
            'фитнес': {
                'objects': ['gym equipment', 'dumbbells', 'treadmill', 'fitness machines', 'exercise bikes', 'weight training', 'cardio equipment', 'fitness space'],
                'actions': ['working out', 'training', 'exercising', 'coaching', 'fitness instruction', 'muscle building', 'cardio training', 'personal training'],
                'qualities': ['energetic', 'motivating', 'professional training', 'modern equipment', 'healthy lifestyle', 'fit and strong', 'active training'],
                'environments': ['gym interior', 'fitness studio', 'training area', 'exercise room', 'sports facility'],
                'favicon_symbols': ['💪', '🏋️', '🤸', '🏃', '⚽', '🏅']
            },
            'строительство': {
                'objects': ['construction site', 'building tools', 'construction equipment', 'hard hats', 'building materials', 'construction crane', 'building process', 'construction workers'],
                'actions': ['building', 'constructing', 'renovating', 'designing', 'engineering', 'project management', 'site supervision', 'quality control'],
                'qualities': ['professional construction', 'quality building', 'reliable work', 'experienced team', 'modern methods', 'safety focused', 'timely completion'],
                'environments': ['construction site', 'building office', 'project site', 'construction yard', 'planning office'],
                'favicon_symbols': ['🔨', '🔧', '🏗️', '⚒️', '🧱', '📐']
            },
            'юрист': {
                'objects': ['law office', 'legal documents', 'law books', 'court room', 'legal consultation', 'contracts', 'legal briefcase', 'justice scale'],
                'actions': ['legal consulting', 'representing clients', 'legal advice', 'document preparation', 'court representation', 'legal analysis', 'contract review'],
                'qualities': ['professional legal', 'experienced counsel', 'reliable advice', 'expert knowledge', 'confidential service', 'successful representation'],
                'environments': ['law office', 'courtroom', 'legal library', 'consultation room', 'legal chambers'],
                'favicon_symbols': ['⚖️', '📜', '🏛️', '📋', '🔍', '📝']
            },
            'медицина': {
                'objects': ['medical equipment', 'stethoscope', 'medical consultation', 'hospital room', 'medical devices', 'health checkup', 'medical treatment', 'clinic interior'],
                'actions': ['medical examination', 'treating patients', 'health consultation', 'medical diagnosis', 'providing care', 'health monitoring', 'medical procedures'],
                'qualities': ['professional medical', 'experienced care', 'modern medicine', 'patient-focused', 'quality treatment', 'health expertise', 'caring approach'],
                'environments': ['medical office', 'hospital ward', 'clinic room', 'examination room', 'medical center'],
                'favicon_symbols': ['🏥', '💊', '🩺', '⚕️', '🔬', '🚑']
            },
            'образование': {
                'objects': ['classroom', 'educational materials', 'books', 'school supplies', 'learning environment', 'educational technology', 'study materials', 'academic resources'],
                'actions': ['teaching', 'learning', 'studying', 'educational guidance', 'knowledge sharing', 'skill development', 'academic support', 'tutoring'],
                'qualities': ['educational excellence', 'knowledge-focused', 'inspiring learning', 'academic quality', 'student-centered', 'innovative teaching'],
                'environments': ['classroom', 'lecture hall', 'study room', 'educational center', 'academic facility'],
                'favicon_symbols': ['📚', '🎓', '🎒', '📝', '🔬', '📖']
            },
            'финансы': {
                'objects': ['bank office', 'financial documents', 'calculator', 'financial charts', 'investment portfolio', 'money management', 'financial planning', 'banking services'],
                'actions': ['financial consulting', 'investment planning', 'money management', 'financial analysis', 'banking services', 'wealth planning', 'financial advice'],
                'qualities': ['financial expertise', 'trustworthy service', 'profitable solutions', 'secure investments', 'professional advice', 'reliable banking'],
                'environments': ['bank office', 'financial center', 'investment office', 'consultation room', 'trading floor'],
                'favicon_symbols': ['💰', '💳', '🏦', '📊', '💎', '💵']
            },
            'технологии': {
                'objects': ['computer equipment', 'software development', 'tech devices', 'digital solutions', 'IT infrastructure', 'modern technology', 'tech workspace', 'digital tools'],
                'actions': ['developing software', 'IT consulting', 'tech support', 'system administration', 'digital transformation', 'technology implementation'],
                'qualities': ['cutting-edge technology', 'innovative solutions', 'reliable IT services', 'modern approach', 'tech expertise', 'digital excellence'],
                'environments': ['tech office', 'development center', 'IT department', 'server room', 'innovation lab'],
                'favicon_symbols': ['💻', '📱', '⌚', '🖥️', '🔧', '⚙️']
            },
            'диагностика авто': {
                'objects': ['diagnostic equipment', 'car scanner', 'engine analysis', 'vehicle checkup', 'computer diagnosis', 'automotive testing', 'diagnostic tools', 'car inspection'],
                'actions': ['diagnosing', 'testing', 'analyzing', 'checking systems', 'computer scanning', 'fault detection', 'performance testing', 'system evaluation'],
                'qualities': ['accurate diagnosis', 'professional testing', 'modern equipment', 'precise analysis', 'reliable results', 'expert evaluation', 'thorough inspection'],
                'environments': ['diagnostic center', 'auto service', 'testing bay', 'inspection station', 'diagnostic facility'],
                'favicon_symbols': ['🔍', '🖥️', '🔧', '📊', '⚡', '🚗']
            },
            'страховка авто': {
                'objects': ['insurance policy', 'car protection', 'coverage plan', 'insurance documents', 'policy agreement', 'protection service', 'insurance office', 'claim processing'],
                'actions': ['insuring vehicles', 'providing coverage', 'policy consultation', 'claim assistance', 'risk assessment', 'insurance planning', 'coverage evaluation'],
                'qualities': ['comprehensive coverage', 'reliable protection', 'affordable rates', 'fast claims', 'trusted insurance', 'full protection', 'secure coverage'],
                'environments': ['insurance office', 'consultation room', 'policy center', 'claims department', 'insurance agency'],
                'favicon_symbols': ['🛡️', '🚗', '📋', '💼', '🔐', '📄']
            },
            'автомастерская': {
                'objects': ['repair shop', 'mechanic tools', 'car lift', 'workshop equipment', 'spare parts', 'repair bay', 'automotive tools', 'service equipment'],
                'actions': ['repairing vehicles', 'mechanical service', 'car maintenance', 'engine repair', 'brake service', 'technical support', 'automotive fixing'],
                'qualities': ['expert repair', 'quality service', 'skilled mechanics', 'reliable fixing', 'professional maintenance', 'trusted repair', 'experienced service'],
                'environments': ['repair shop', 'service bay', 'mechanic garage', 'workshop floor', 'automotive center'],
                'favicon_symbols': ['🔧', '⚙️', '🛠️', '🚗', '🔩', '⚡']
            },
            'аренда авто': {
                'objects': ['rental car', 'vehicle fleet', 'rental office', 'car keys', 'rental agreement', 'rental service', 'vehicle selection', 'rental desk'],
                'actions': ['renting vehicles', 'car rental service', 'fleet management', 'booking cars', 'rental consultation', 'vehicle delivery', 'rental processing'],
                'qualities': ['convenient rental', 'flexible terms', 'modern fleet', 'competitive rates', 'reliable vehicles', 'excellent service', 'quick booking'],
                'environments': ['rental office', 'car lot', 'rental counter', 'vehicle showroom', 'rental facility'],
                'favicon_symbols': ['🚗', '🔑', '📋', '🏢', '📅', '🛣️']
            },
            'тюнинг': {
                'objects': ['tuned car', 'performance parts', 'custom modifications', 'upgraded engine', 'styling elements', 'tuning equipment', 'modified vehicle', 'performance upgrade'],
                'actions': ['tuning vehicles', 'performance enhancement', 'custom modification', 'styling upgrade', 'engine tuning', 'vehicle customization', 'performance optimization'],
                'qualities': ['custom design', 'performance boost', 'unique styling', 'professional tuning', 'high-end modifications', 'expert customization', 'quality upgrades'],
                'environments': ['tuning shop', 'modification bay', 'custom garage', 'performance center', 'tuning facility'],
                'favicon_symbols': ['🏎️', '⚡', '🔧', '🎨', '💨', '🚗']
            },
            'кулинарные курсы': {
                'objects': ['cooking class', 'chef instruction', 'culinary lesson', 'cooking equipment', 'recipe book', 'kitchen studio', 'cooking demonstration', 'culinary workshop'],
                'actions': ['teaching cooking', 'culinary instruction', 'recipe demonstration', 'cooking techniques', 'skill development', 'food preparation', 'culinary education'],
                'qualities': ['professional instruction', 'hands-on learning', 'expert guidance', 'practical skills', 'culinary mastery', 'creative cooking', 'gourmet techniques'],
                'environments': ['cooking studio', 'culinary classroom', 'teaching kitchen', 'workshop space', 'chef academy'],
                'favicon_symbols': ['👨‍🍳', '🍳', '📚', '🔪', '🥘', '🎓']
            },
            'курсы по инвестициям': {
                'objects': ['investment course', 'financial education', 'portfolio management', 'market analysis', 'investment strategy', 'financial planning', 'trading education', 'wealth building'],
                'actions': ['teaching investing', 'financial education', 'portfolio guidance', 'market analysis', 'investment planning', 'wealth strategies', 'financial literacy'],
                'qualities': ['expert instruction', 'proven strategies', 'practical knowledge', 'market insights', 'profitable techniques', 'professional guidance', 'wealth building'],
                'environments': ['training center', 'financial classroom', 'investment office', 'learning facility', 'education center'],
                'favicon_symbols': ['📈', '💰', '🎓', '📊', '💼', '📚']
            },
            'погрузчик': {
                'objects': ['forklift', 'loading equipment', 'warehouse machinery', 'cargo handling', 'lifting device', 'material handling', 'loading dock', 'industrial equipment'],
                'actions': ['loading cargo', 'material handling', 'warehouse operations', 'cargo transportation', 'freight loading', 'equipment operation', 'logistics support'],
                'qualities': ['efficient loading', 'safe operation', 'reliable equipment', 'heavy-duty performance', 'professional service', 'quick loading', 'industrial strength'],
                'environments': ['warehouse', 'loading dock', 'industrial facility', 'cargo area', 'storage facility'],
                'favicon_symbols': ['🏗️', '📦', '🚛', '⚙️', '🔧', '🏭']
            },
            'бухгалтерские услуги': {
                'objects': ['accounting office', 'financial documents', 'bookkeeping', 'tax preparation', 'financial reports', 'accounting software', 'business accounting', 'financial records'],
                'actions': ['accounting services', 'bookkeeping', 'tax preparation', 'financial reporting', 'audit support', 'business consultation', 'financial management'],
                'qualities': ['accurate accounting', 'professional service', 'tax expertise', 'reliable bookkeeping', 'financial accuracy', 'business support', 'expert guidance'],
                'environments': ['accounting office', 'business center', 'tax office', 'financial center', 'consultation room'],
                'favicon_symbols': ['📊', '💼', '📋', '🧮', '📈', '💰']
            },
            'миграционные консультации': {
                'objects': ['immigration office', 'visa documents', 'legal consultation', 'migration paperwork', 'passport services', 'immigration advice', 'visa processing', 'legal support'],
                'actions': ['immigration consulting', 'visa assistance', 'document preparation', 'legal guidance', 'migration support', 'application processing', 'legal advice'],
                'qualities': ['expert consultation', 'legal expertise', 'reliable guidance', 'professional support', 'successful applications', 'trusted advice', 'experienced service'],
                'environments': ['immigration office', 'legal center', 'consultation room', 'visa center', 'legal office'],
                'favicon_symbols': ['🌍', '📄', '✈️', '🏛️', '📋', '🗺️']
            },
            'установка солнечных панелей': {
                'objects': ['solar panels', 'renewable energy', 'solar installation', 'green technology', 'energy system', 'solar array', 'photovoltaic system', 'eco-friendly power'],
                'actions': ['installing solar panels', 'renewable energy setup', 'green installation', 'solar system design', 'energy consultation', 'eco-friendly solutions', 'sustainable energy'],
                'qualities': ['eco-friendly', 'sustainable energy', 'cost-effective', 'renewable power', 'green technology', 'energy efficient', 'environmentally conscious'],
                'environments': ['solar installation site', 'rooftop installation', 'energy center', 'green technology office', 'renewable energy facility'],
                'favicon_symbols': ['☀️', '🔋', '🌱', '⚡', '🏠', '🌍']
            },
            'курсы английского языка': {
                'objects': ['english classroom', 'language learning', 'english textbooks', 'conversation practice', 'language study', 'english lessons', 'language course', 'speaking practice'],
                'actions': ['teaching english', 'language instruction', 'conversation practice', 'grammar lessons', 'speaking training', 'language development', 'english education'],
                'qualities': ['fluent english', 'effective learning', 'native speakers', 'interactive lessons', 'practical skills', 'conversational fluency', 'professional instruction'],
                'environments': ['language school', 'classroom', 'learning center', 'english academy', 'educational facility'],
                'favicon_symbols': ['🇬🇧', '📚', '🎓', '💬', '🗣️', '📖']
            },
            'йога': {
                'objects': ['yoga practice', 'meditation session', 'yoga poses', 'wellness training', 'mindfulness practice', 'yoga instruction', 'peaceful yoga', 'spiritual practice'],
                'actions': ['practicing yoga', 'meditation guidance', 'wellness instruction', 'mindfulness training', 'stress relief', 'body alignment', 'spiritual practice'],
                'qualities': ['peaceful yoga', 'mind-body wellness', 'stress relief', 'spiritual growth', 'meditation focused', 'wellness oriented', 'holistic health'],
                'environments': ['yoga studio', 'wellness center', 'meditation room', 'fitness studio', 'peaceful space'],
                'favicon_symbols': ['🧘', '🕉️', '🌸', '💆', '🧘‍♀️', '🌿']
            },
            'ландшафтный дизайн': {
                'objects': ['garden design', 'landscape architecture', 'outdoor space', 'garden planning', 'landscape project', 'outdoor design', 'garden elements', 'landscape features'],
                'actions': ['landscape design', 'garden planning', 'outdoor designing', 'landscape architecture', 'garden creation', 'outdoor beautification', 'landscape consultation'],
                'qualities': ['beautiful landscapes', 'creative design', 'natural beauty', 'sustainable design', 'outdoor elegance', 'garden artistry', 'landscape excellence'],
                'environments': ['design studio', 'garden center', 'landscape office', 'outdoor space', 'design workshop'],
                'favicon_symbols': ['🌳', '🌺', '🏡', '🌿', '🎨', '🌷']
            },
            'доставка здорового питания': {
                'objects': ['healthy meals', 'organic food delivery', 'nutritious dishes', 'fitness nutrition', 'diet meals', 'healthy food boxes', 'wellness nutrition', 'clean eating'],
                'actions': ['delivering healthy food', 'nutrition planning', 'meal preparation', 'healthy cooking', 'diet consultation', 'wellness delivery', 'nutritious meal service'],
                'qualities': ['nutritious meals', 'organic ingredients', 'healthy lifestyle', 'balanced nutrition', 'fresh preparation', 'wellness focused', 'diet-friendly'],
                'environments': ['healthy kitchen', 'nutrition center', 'wellness facility', 'organic kitchen', 'health food preparation'],
                'delivery_elements': ['eco-friendly packaging', 'nutrition delivery', 'healthy meal box', 'wellness courier', 'diet delivery service'],
                'favicon_symbols': ['🥗', '🍃', '💚', '🥑', '🏃', '💪']
            },
            'хендмейд товары': {
                'objects': ['handmade products', 'artisan crafts', 'natural cosmetics', 'handmade candles', 'organic soap', 'craft workshop', 'artisan goods', 'handcrafted items'],
                'actions': ['handcrafting', 'artisan creation', 'natural production', 'craft making', 'handmade design', 'artisan work', 'creative crafting'],
                'qualities': ['handmade quality', 'artisan crafted', 'natural ingredients', 'unique design', 'eco-friendly', 'authentic handmade', 'creative artistry'],
                'environments': ['craft studio', 'artisan workshop', 'handmade shop', 'creative space', 'craft center'],
                'favicon_symbols': ['🕯️', '🧼', '🎨', '✋', '🌿', '💝']
            },
            'зоомагазин': {
                'objects': ['pet store', 'pet accessories', 'animal care products', 'pet food', 'pet toys', 'animal supplies', 'pet care items', 'pet equipment'],
                'actions': ['pet care', 'animal care consultation', 'pet product sales', 'pet advice', 'animal care guidance', 'pet supply service', 'pet care support'],
                'qualities': ['quality pet care', 'animal-friendly', 'trusted products', 'pet health focused', 'caring service', 'professional advice', 'pet wellness'],
                'environments': ['pet store', 'animal care center', 'pet shop', 'veterinary supply', 'pet care facility'],
                'favicon_symbols': ['🐕', '🐈', '🐾', '🦴', '🏪', '❤️']
            }
        }
        
        # Общие элементы для неизвестных тематик
        self.general_elements = {
            'objects': ['service', 'workspace', 'equipment', 'facility', 'interior'],
            'actions': ['working', 'providing', 'delivering', 'maintaining', 'operating'],
            'qualities': ['professional', 'modern', 'quality', 'efficient', 'reliable'],
            'environments': ['office', 'workplace', 'service area', 'facility', 'center'],
            'favicon_symbols': ['🏢', '🔧', '⚙️', '📊', '💼', '🎯']
        }
        
        # Стили и композиции для разнообразия
        self.styles = ['professional photography', 'commercial style', 'high quality', 'studio lighting', 'natural lighting']
        self.compositions = ['centered composition', 'close-up view', 'wide angle', 'detailed shot', 'atmospheric']
        self.moods = ['bright', 'warm', 'inviting', 'modern', 'elegant', 'clean', 'vibrant']
        
        # Вариативные стили для фавиконов
        self.favicon_styles = ['flat design', 'minimal design', 'geometric', 'modern icon', 'clean symbol', 'vector style']
        self.favicon_colors = ['blue gradient', 'orange gradient', 'green gradient', 'purple gradient', 'red gradient', 'teal gradient']
    
    def generate_prompts(self, theme_input):
        """Генерирует вариативные промпты для тематики"""
        theme_lower = theme_input.lower().strip()
        
        # Находим подходящие элементы
        elements = self._get_theme_elements(theme_lower)
        
        # Генерируем промпты для каждого типа изображения
        prompts = {}
        
        # Main - главное изображение бизнеса
        prompts['main'] = self._generate_main_prompt(elements, theme_input, theme_lower)
        
        # About1 - первое изображение о услуге  
        prompts['about1'] = self._generate_about1_prompt(elements, theme_input, theme_lower)
        
        # About2 - КРИТИЧЕСКОЕ - здесь НЕ ДОЛЖНО быть механиков для авто
        prompts['about2'] = self._generate_about2_prompt(elements, theme_input, theme_lower)
        
        # About3 - третье изображение
        prompts['about3'] = self._generate_about3_prompt(elements, theme_input, theme_lower)
        
        # Review изображения - люди
        prompts['review1'] = self._generate_review_prompt()
        prompts['review2'] = self._generate_review_prompt() 
        prompts['review3'] = self._generate_review_prompt()
        
        # Favicon - ВАРИАТИВНЫЙ символ
        prompts['favicon'] = self._generate_favicon_prompt(elements, theme_input, theme_lower)
        
        return prompts
    
    def _get_theme_elements(self, theme_lower):
        """Получает элементы для тематики"""
        
        # СНАЧАЛА проверяем приоритетные специфические фразы
        # Недвижимость имеет ВЫСШИЙ приоритет
        if any(phrase in theme_lower for phrase in ['продажа недвижимости', 'продажа квартир', 'продажа домов', 'продажа жилья']):
            return self.business_elements['недвижимость']
        
        # Проверяем другие специфические фразы недвижимости
        if any(word in theme_lower for word in ['недвижим', 'квартир', 'дом', 'домов', 'жилье', 'жилищ', 'реалт', 'риелт', 'property', 'real estate', 'apartment', 'house']):
            return self.business_elements['недвижимость']
        
        # Проверяем точные совпадения (кроме проблемного "продажа авто")
        for key, elements in self.business_elements.items():
            if key == 'продажа авто':
                # Для продажи авто требуем ТОЧНОЕ совпадение или явное упоминание авто
                if (key in theme_lower or 
                    'автосалон' in theme_lower or
                    ('продаж' in theme_lower and any(auto_word in theme_lower for auto_word in ['авто', 'машин', 'car', 'vehicle']))):
                    return elements
            else:
                # Для остальных - обычная проверка
                if key in theme_lower or any(word in theme_lower for word in key.split()):
                    return elements
                
        # Дополнительные проверки для вариаций - ПОРЯДОК ВАЖЕН!
        
        # АВТОМОБИЛЬНЫЕ УСЛУГИ - СПЕЦИФИЧЕСКИЕ СНАЧАЛА
        
        # Проверяем эвакуатор - КРИТИЧЕСКИ ВАЖНО!
        if any(word in theme_lower for word in ['эвакуатор', 'эвакуация', 'эвакуации', 'эвакуаторы', 'tow truck', 'towing']):
            return self.business_elements['эвакуатор']
        
        # Проверяем диагностику авто
        elif any(word in theme_lower for word in ['диагностик', 'диагноз', 'сканер', 'чек', 'diagnostic', 'scan']):
            return self.business_elements['диагностика авто']
        
        # Проверяем страховку авто
        elif any(word in theme_lower for word in ['страховк', 'страхован', 'каско', 'осаго', 'insurance']) and any(word in theme_lower for word in ['авто', 'машин', 'car', 'vehicle']):
            return self.business_elements['страховка авто']
        
        # Проверяем автомастерскую
        elif any(word in theme_lower for word in ['автомастерск', 'мастерск', 'workshop', 'garage']) or ('ремонт' in theme_lower and any(word in theme_lower for word in ['авто', 'машин', 'car'])):
            return self.business_elements['автомастерская']
        
        # Проверяем аренду авто
        elif any(word in theme_lower for word in ['аренд', 'rental', 'прокат']) and any(word in theme_lower for word in ['авто', 'машин', 'car', 'vehicle']):
            return self.business_elements['аренда авто']
        
        # Проверяем тюнинг
        elif any(word in theme_lower for word in ['тюнинг', 'tuning', 'модификац', 'кастом', 'чип']):
            return self.business_elements['тюнинг']
        
        # ОБРАЗОВАНИЕ И КУРСЫ - СПЕЦИФИЧЕСКИЕ СНАЧАЛА
        
        # Проверяем кулинарные курсы
        elif any(word in theme_lower for word in ['кулинарн', 'повар', 'готовк', 'cooking', 'chef', 'culinary']) and any(word in theme_lower for word in ['курс', 'обучен', 'мастер-класс', 'course', 'class']):
            return self.business_elements['кулинарные курсы']
        
        # Проверяем курсы по инвестициям
        elif any(word in theme_lower for word in ['инвестиц', 'investment', 'торговл', 'trading', 'фондов']) and any(word in theme_lower for word in ['курс', 'обучен', 'course']):
            return self.business_elements['курсы по инвестициям']
        
        # Проверяем курсы английского
        elif any(word in theme_lower for word in ['английск', 'english', 'язык']) and any(word in theme_lower for word in ['курс', 'обучен', 'изучен', 'course', 'lesson']):
            return self.business_elements['курсы английского языка']
        
        # ДОСТАВКА ЕДЫ - СПЕЦИФИЧЕСКИЕ ВИДЫ
        
        # Проверяем доставку здорового питания
        elif any(word in theme_lower for word in ['здоров', 'фитнес', 'веган', 'детокс', 'диет', 'healthy', 'organic']) and any(word in theme_lower for word in ['питан', 'еда', 'food', 'доставк', 'delivery']):
            return self.business_elements['доставка здорового питания']
        
        # Проверяем обычную доставку еды
        elif any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            return self.business_elements['доставка еды']
        
        # МЕДИЦИНА И ЗДОРОВЬЕ
        
        # Проверяем стоматологию
        elif any(word in theme_lower for word in ['стоматолог', 'стоматология', 'зубн', 'dental', 'дентал', 'зубы', 'имплант']):
            return self.business_elements['стоматология']
        
        # Проверяем йогу/пилатес
        elif any(word in theme_lower for word in ['йог', 'пилатес', 'медитац', 'yoga', 'pilates', 'meditation']):
            return self.business_elements['йога']
        
        # Проверяем фитнес/спорт (кроме йоги)
        elif any(word in theme_lower for word in ['фитнес', 'спортзал', 'gym', 'тренаж', 'спорт', 'тренер', 'тренировк']):
            return self.business_elements['фитнес']
        
        # Проверяем медицину (кроме стоматологии)
        elif any(word in theme_lower for word in ['медицин', 'больниц', 'поликлиник', 'врач', 'доктор', 'клиник', 'терапевт', 'лечен']):
            return self.business_elements['медицина']
        
        # УСЛУГИ И КОНСУЛЬТАЦИИ
        
        # Проверяем парикмахерскую/салон красоты
        elif any(word in theme_lower for word in ['парикмахер', 'салон', 'стрижк', 'прическ', 'маникюр', 'педикюр', 'барбершоп', 'beauty']):
            return self.business_elements['парикмахерская']
        
        # Проверяем бухгалтерские услуги
        elif any(word in theme_lower for word in ['бухгалтер', 'accounting', 'налог', 'отчетност', 'bookkeeping']):
            return self.business_elements['бухгалтерские услуги']
        
        # Проверяем миграционные консультации
        elif any(word in theme_lower for word in ['миграцион', 'виз', 'immigration', 'visa', 'citizenship', 'гражданств']):
            return self.business_elements['миграционные консультации']
        
        # Проверяем юридические услуги
        elif any(word in theme_lower for word in ['юрист', 'юридическ', 'адвокат', 'lawyer', 'legal', 'правов', 'нотариус']):
            return self.business_elements['юрист']
        
        # СПЕЦИАЛЬНЫЕ УСЛУГИ
        
        # Проверяем установку солнечных панелей
        elif any(word in theme_lower for word in ['солнечн', 'solar', 'панел', 'panel', 'энергосбережен', 'renewable']):
            return self.business_elements['установка солнечных панелей']
        
        # Проверяем ландшафтный дизайн
        elif any(word in theme_lower for word in ['ландшафт', 'landscape', 'сад', 'garden', 'дизайн сада', 'озеленен']):
            return self.business_elements['ландшафтный дизайн']
        
        # Проверяем погрузчик
        elif any(word in theme_lower for word in ['погрузчик', 'forklift', 'погрузк', 'loading', 'склад', 'warehouse']):
            return self.business_elements['погрузчик']
        
        # Проверяем хендмейд товары
        elif any(word in theme_lower for word in ['хендмейд', 'handmade', 'рукодел', 'ручн', 'craft', 'свеч', 'мыло', 'косметик']):
            return self.business_elements['хендмейд товары']
        
        # Проверяем зоомагазин
        elif any(word in theme_lower for word in ['зоомагазин', 'pet', 'животн', 'корм', 'аксессуар']):
            return self.business_elements['зоомагазин']
        
        # ОБЩИЕ КАТЕГОРИИ
        
        # Проверяем строительство/ремонт
        elif any(word in theme_lower for word in ['строительств', 'ремонт', 'стройк', 'construction', 'renovation', 'монтаж', 'отделк']) and 'авто' not in theme_lower:
            return self.business_elements['строительство']
        
        # Проверяем образование (общее)
        elif any(word in theme_lower for word in ['образован', 'школ', 'учеб', 'курс', 'обучен', 'репетитор', 'university', 'education']) and not any(spec in theme_lower for spec in ['кулинарн', 'инвестиц', 'английск']):
            return self.business_elements['образование']
        
        # Проверяем финансы/банки (кроме специфических)
        elif any(word in theme_lower for word in ['финанс', 'банк', 'кредит', 'financial', 'banking', 'ипотек', 'экономик']) and not any(spec in theme_lower for spec in ['инвестиц', 'бухгалтер']):
            return self.business_elements['финансы']
        
        # Проверяем технологии/IT
        elif any(word in theme_lower for word in ['технолог', 'IT', 'айти', 'програм', 'сайт', 'приложен', 'софт', 'computer', 'digital']):
            return self.business_elements['технологии']
        
        # Проверяем кафе/кофе
        elif any(word in theme_lower for word in ['кофе', 'coffee', 'кафе', 'cafe']):
            return self.business_elements['кафе']
        
        # Проверяем автомойку (ТРЕБУЕТ упоминания машин/авто)
        elif any(word in theme_lower for word in ['мойка', 'wash', 'clean']) and any(word in theme_lower for word in ['авто', 'машин', 'car', 'vehicle']):
            return self.business_elements['автомойка']
        
        return self.general_elements
    
    def _generate_main_prompt(self, elements, theme, theme_lower):
        """Генерирует главный промпт"""
        obj = random.choice(elements['objects'])
        quality = random.choice(elements['qualities'])
        env = random.choice(elements['environments'])
        style = random.choice(self.styles)
        
        # Добавляем доставочные элементы для еды
        if any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            delivery_element = random.choice(elements.get('delivery_elements', []))
            return f"{quality} {obj} with {delivery_element} in {env}, {style}"
        
        return f"{quality} {obj} in {env}, {style}"
    
    def _generate_about1_prompt(self, elements, theme, theme_lower):
        """Генерирует первый about промпт"""
        obj = random.choice(elements['objects'])
        action = random.choice(elements['actions'])
        mood = random.choice(self.moods)
        
        return f"{action} {obj}, {mood} atmosphere, professional quality"
    
    def _generate_about2_prompt(self, elements, theme, theme_lower):
        """КРИТИЧЕСКИЙ метод - генерирует about2 БЕЗ механиков для авто"""
        # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ АВТО ТЕМАТИК
        if any(word in theme_lower for word in ['авто', 'машин', 'car', 'продаж', 'салон']):
            # Для авто используем ТОЛЬКО безопасные объекты
            if 'about2_safe' in elements:
                safe_obj = random.choice(elements['about2_safe'])
                quality = random.choice(elements['qualities'])
                return f"{quality} {safe_obj}, interior design, comfort features"
            else:
                return "elegant car interior with leather seats, premium comfort"
        
        # Для доставки еды - добавляем доставочные элементы
        if any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            delivery_element = random.choice(elements.get('delivery_elements', []))
            obj = random.choice(elements['objects'])
            comp = random.choice(self.compositions)
            return f"{delivery_element} with {obj}, {comp}, delivery service"
        
        # Для остальных тематик - обычная генерация
        obj = random.choice(elements['objects'])
        quality = random.choice(elements['qualities'])
        comp = random.choice(self.compositions)
        
        # Проверяем на запрещенные слова
        prompt = f"{quality} {obj}, {comp}, detailed view"
        
        if 'banned_words' in elements:
            for banned in elements['banned_words']:
                if banned.lower() in prompt.lower():
                    # Заменяем на безопасный вариант
                    return self._generate_safe_about2(elements, theme)
        
        return prompt
    
    def _generate_safe_about2(self, elements, theme):
        """Генерирует безопасный about2 промпт"""
        quality = random.choice(elements['qualities'])
        comp = random.choice(self.compositions)
        
        # Безопасные варианты
        safe_variants = [
            f"{quality} service environment, {comp}",
            f"professional workspace, {quality} facilities",
            f"{quality} interior design, modern setup"
        ]
        
        return random.choice(safe_variants)
    
    def _generate_about3_prompt(self, elements, theme, theme_lower):
        """Генерирует третий about промпт"""
        obj = random.choice(elements['objects'])
        action = random.choice(elements['actions'])
        style = random.choice(self.styles)
        
        # Добавляем доставочные элементы для еды
        if any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            delivery_element = random.choice(elements.get('delivery_elements', []))
            return f"{action} {obj} via {delivery_element}, results showcase, {style}"
        
        return f"{action} {obj}, results showcase, {style}"
    
    def _generate_review_prompt(self):
        """Генерирует промпты для отзывов - только люди"""
        people_variants = [
            "happy satisfied customer smiling",
            "pleased client with positive expression", 
            "delighted customer showing satisfaction",
            "cheerful person expressing joy",
            "content customer with thumbs up",
            "satisfied client in consultation",
            "happy customer receiving service"
        ]
        
        return random.choice(people_variants)
    
    def _generate_favicon_prompt(self, elements, theme, theme_lower):
        """Генерирует вариативный фавикон промпт"""
        # Получаем символ для тематики
        if 'favicon_symbols' in elements:
            symbol = random.choice(elements['favicon_symbols'])
        else:
            symbol = random.choice(self.general_elements['favicon_symbols'])
        
        # Получаем стиль и цвет
        style = random.choice(self.favicon_styles)
        color = random.choice(self.favicon_colors)
        
        # Генерируем описание
        if any(word in theme_lower for word in ['недвижим', 'квартир', 'дом', 'домов', 'жилье', 'жилищ', 'реалт', 'риелт', 'property', 'real estate', 'apartment', 'house']):
            base_name = 'real estate'
        elif any(word in theme_lower for word in ['еда', 'еды', 'food', 'delivery', 'доставк']):
            base_name = 'food delivery'
        elif any(word in theme_lower for word in ['авто', 'машин', 'car', 'vehicle']) and any(word in theme_lower for word in ['продаж', 'салон', 'дилер']):
            base_name = 'car sales'
        elif any(word in theme_lower for word in ['кофе', 'coffee', 'кафе', 'cafe']):
            base_name = 'coffee shop'
        elif any(word in theme_lower for word in ['мойка', 'wash', 'clean']) and any(word in theme_lower for word in ['авто', 'машин', 'car']):
            base_name = 'car wash'
        else:
            base_name = 'business'
        
        return f"{base_name} icon {symbol}, {style}, {color}, professional logo"

# Функция для совместимости
def create_smart_thematic_prompts(theme_input):
    """Создает вариативные тематические промпты"""
    generator = SmartVariativePrompts()
    prompts_dict = generator.generate_prompts(theme_input)
    
    # Возвращаем в виде списка для совместимости
    return [
        prompts_dict['main'],
        prompts_dict['about1'], 
        prompts_dict['about2'],
        prompts_dict['about3'],
        prompts_dict['review1'],
        prompts_dict['review2'],
        prompts_dict['review3'],
        prompts_dict['favicon']
    ]

if __name__ == "__main__":
    # Тестирование вариативности
    generator = SmartVariativePrompts()
    
    test_themes = ["доставка еды", "продажа авто", "кафе"]
    
    for theme in test_themes:
        print(f"\n=== {theme.upper()} - ТЕСТ ВАРИАТИВНОСТИ ===")
        
        # Генерируем 3 разных набора для проверки вариативности
        for i in range(3):
            print(f"\nВариант {i+1}:")
            prompts = generator.generate_prompts(theme)
            
            for key, prompt in prompts.items():
                print(f"  {key}: {prompt}")
                
                # Проверяем на запрещенные слова
                if theme == "доставка еды":
                    if any(bad in prompt.lower() for bad in ['box', 'коробк']):
                        print(f"    ❌ НАЙДЕНЫ КОРОБКИ!")
                    elif 'delivery' in prompt.lower():
                        print(f"    ✅ Есть доставка!")
                    else:
                        print(f"    ⚠️ Нет доставки в промпте")
                elif theme == "продажа авто" and key == "about2" and any(bad in prompt.lower() for bad in ['mechanic', 'механик']):
                    print(f"    ❌ НАЙДЕН МЕХАНИК!")
                else:
                    print(f"    ✅ Промпт безопасен") 