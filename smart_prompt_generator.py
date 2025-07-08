class SmartPromptGenerator:
    """УМНАЯ система генерации промптов для любых тематик БЕЗ интернета"""
    
    def __init__(self):
        # Словарь переводов ключевых слов
        self.translations = {
            # Типы деятельности
            'продажа': 'sales', 'продаж': 'sales', 'продаем': 'sales', 'торговля': 'retail',
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
            'автосервис': 'car service', 'автомастерская': 'car workshop',
            'телефон': 'phones', 'смартфон': 'smartphones',
            'компьютер': 'computers', 'ноутбук': 'laptops',
            'холодильник': 'refrigerators', 'холодильников': 'refrigerators',
            'стиральн': 'washing machines', 'посудомоеч': 'dishwashers',
            'микроволнов': 'microwaves', 'пылесос': 'vacuum cleaners',
            'одежд': 'clothing', 'одежда': 'clothing', 'одежды': 'clothing',
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
            'погрузчик': 'loader', 'погрузчика': 'loader services', 'погрузчиков': 'loaders',
            'экскаватор': 'excavator', 'бульдозер': 'bulldozer', 'кран': 'crane',
            'грузчик': 'moving services', 'грузчиков': 'movers',
            'прицеп': 'trailers', 'полуприцеп': 'semi-trailers',
            'мотоцикл': 'motorcycles', 'скутер': 'scooters',
            'велосипед': 'bicycles', 'самокат': 'scooters',
            'лодк': 'boats', 'яхт': 'yachts', 'катер': 'boats',
            
            # Еда и напитки  
            'хлеб': 'bread', 'выпечка': 'bakery', 'торт': 'cakes',
            'мяс': 'meat', 'колбас': 'sausages',
            'молок': 'milk', 'сыр': 'cheese', 'творог': 'cottage cheese',
            'овощ': 'vegetables', 'фрукт': 'fruits',
            'кофе': 'coffee', 'кофейня': 'coffee shop', 'чай': 'tea', 'напитк': 'beverages',
            'еды': 'food', 'еда': 'food', 'блюд': 'dishes', 'питан': 'food',
            'ресторан': 'restaurant', 'кафе': 'cafe', 'пицц': 'pizza',
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
            'недвижимость': 'real estate', 'недвижимости': 'real estate',
            'квартир': 'apartments', 'дом': 'houses', 'коттедж': 'cottages',
            'офис': 'offices', 'склад': 'warehouses', 'гараж': 'garages',
            'участок': 'land plots', 'дач': 'country houses',
            'земл': 'land', 'участк': 'land plots', 'участков': 'land plots', 'домов': 'houses',
            'поселк': 'villages', 'поселки': 'residential complexes', 'коттедж': 'cottage communities',
            'аренд': 'rental', 'аренда': 'rental',
            
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
            
            # НОВЫЕ ПЕРЕВОДЫ ДЛЯ ВСЕХ ТЕМАТИК
            # Автомобильные услуги
            'автосалон': 'car dealership', 'автосалона': 'car dealership',
            'диагностика': 'diagnostic', 'диагностик': 'diagnostic',
            'эвакуатор': 'tow truck', 'эвакуатора': 'tow truck service',
            'тюнинг': 'tuning', 'тюнинга': 'car tuning',
            'автомойка': 'car wash', 'автомойки': 'car wash',
            
            # Финансовые и консультационные услуги
            'бухгалтерские': 'accounting', 'бухгалтерия': 'accounting',
            'бухгалтер': 'accountant', 'отчетность': 'financial reporting',
            'миграционные': 'immigration', 'миграция': 'immigration',
            'консультации': 'consulting', 'консультант': 'consultant',
            'экономика': 'economics', 'экономик': 'economics',
            'экономические': 'economic', 'финансы': 'finance',
            
            # Энергетика и техника
            'солнечных': 'solar', 'солнечные': 'solar', 'панели': 'panels',
            'панелей': 'solar panels', 'энергия': 'energy',
            'строительная': 'construction', 'техника': 'equipment',
            'технику': 'machinery', 'техники': 'equipment',
            
            # Образование и курсы  
            'кулинарные': 'culinary', 'кулинария': 'cooking',
            'мастер-класс': 'masterclass', 'мастер-классы': 'workshops',
            'английский': 'English', 'английского': 'English language',
            'язык': 'language', 'языки': 'languages',
            'онлайн': 'online', 'офлайн': 'offline',
            'занятия': 'classes', 'урок': 'lessons',
            
            # Дизайн и творчество
            'ландшафтный': 'landscape', 'ландшафт': 'landscaping',
            'сад': 'garden', 'садов': 'gardens', 'уход': 'care',
            'хендмейд': 'handmade', 'рукоделие': 'crafts',
            'свечи': 'candles', 'мыло': 'soap',
            'натуральная': 'natural', 'косметика': 'cosmetics',
            
            # Питание и здоровье
            'здорового': 'healthy', 'здоровое': 'healthy food',
            'питания': 'nutrition', 'питание': 'food',
            'фитнес': 'fitness', 'веган': 'vegan', 
            'детокс': 'detox', 'диета': 'diet',
            
            # Аксессуары и товары
            'часов': 'watches', 'часы': 'watches', 'брендовых': 'luxury',
            'аксессуары': 'accessories', 'аксессуаров': 'accessories',
            'каталог': 'catalog', 'обзор': 'review',
            'люкс': 'luxury', 'премиум': 'premium',
            
            # ИСПРАВЛЕНИЯ для пропущенных слов
            'услуги': 'services', 'услуг': 'services',
            'юристов': 'legal services', 'юриста': 'legal advice',
            'языка': 'language', 'языку': 'language',
            'экономике': 'economics', 'экономики': 'economics',
            'садами': 'gardens', 'садов': 'gardens',
            'товары': 'products', 'товаров': 'products',
            'йогой': 'yoga', 'пилатесом': 'pilates',
            'йогой/пилатесом': 'yoga and pilates',
            
            # Дополнительные предметы
            'домов': 'houses', 'коттеджей': 'cottages', 'бань': 'saunas',
            'офисов': 'offices', 'квартир': 'apartments',
        }
        
        # ОПТИМИЗИРОВАННЫЕ шаблоны промптов (убрано дублирование)
        self.activity_templates = {
            'sales': {
                'main': ["modern {product} showroom exterior", "elegant {product} sales center facade", "contemporary {product} store exterior"],
                'about1': ["{product} showroom interior with lighting", "spacious {product} exhibition hall", "bright {product} retail space"],
                'about2': ["sales consultant demonstrating {product}", "expert explaining {product} benefits", "salesperson providing {product} information"],
                'about3': ["premium {product} collection display", "wide selection of {product} models", "luxury {product} retail offering"],
                'review1': ["happy customer with new {product}", "satisfied buyer examining {product}", "delighted client with {product}"],
                'review2': ["{product} sales consultation meeting", "customer discussing {product} options", "professional {product} recommendation"],
                'review3': ["professional {product} sales team", "qualified {product} specialists", "experienced {product} staff"],
                'favicon': "{product} sales icon"
            },
            'manufacturing': {
                'main': "modern {product} manufacturing facility", 'about1': "{product} production workshop", 'about2': "skilled worker manufacturing {product}",
                'about3': "high quality manufactured {product}", 'review1': "satisfied customer with manufactured {product}", 'review2': "{product} manufacturing consultation",
                'review3': "professional {product} manufacturing team", 'favicon': "{product} manufacturing icon"
            },
            'repair': {
                'main': ["professional {product} repair shop", "modern {product} service center", "expert {product} repair workshop"],
                'about1': ["{product} repair workshop interior", "spacious {product} service area", "well-equipped {product} facility"],
                'about2': ["skilled technician repairing {product}", "expert mechanic fixing {product}", "specialist servicing {product}"],
                'about3': ["perfectly restored {product}", "fully repaired {product}", "expertly fixed {product}"],
                'review1': ["happy customer with repaired {product}", "pleased client with restored {product}", "satisfied customer with fixed {product}"],
                'review2': ["{product} repair consultation", "service advisor explaining {product} repair", "technician discussing {product} maintenance"],
                'review3': ["experienced {product} repair team", "qualified {product} specialists", "expert {product} technicians"],
                'favicon': "{product} repair icon"
            },
            'installation': {
                'main': "professional {product} installation service", 'about1': "{product} installation workshop", 'about2': "expert installing {product}",
                'about3': "perfectly installed {product}", 'review1': "satisfied customer with installed {product}", 'review2': "{product} installation consultation",
                'review3': "skilled {product} installation team", 'favicon': "{product} installation icon"
            },
            'construction': {
                'main': "{product} construction site", 'about1': "{product} construction process", 'about2': "construction worker building {product}",
                'about3': "completed {product} construction", 'review1': "satisfied client with constructed {product}", 'review2': "{product} construction consultation",
                'review3': "professional {product} construction team", 'favicon': "{product} construction icon"
            },
            'service': {
                'main': ["modern {product} service center", "welcoming {product} service building", "contemporary {product} service facility"],
                'about1': ["comfortable {product} service area", "professional {product} service environment", "spacious {product} service facility"],
                'about2': ["expert providing {product} service", "specialist working on {product} service", "skilled professional delivering {product} service"],
                'about3': ["excellent {product} service results", "high-quality {product} service outcome", "superior {product} service delivery"],
                'review1': ["delighted customer after {product} service", "happy client with {product} service", "satisfied customer praising {product} service"],
                'review2': ["{product} service consultation meeting", "professional {product} service discussion", "personalized {product} service consultation"],
                'review3': ["qualified {product} service team", "expert {product} service staff", "professional {product} service crew"],
                'favicon': "{product} service icon"
            },
            'consulting': {
                'main': "professional {product} consulting office", 'about1': "{product} consulting meeting room", 'about2': "consultant providing {product} advice",
                'about3': "successful {product} consulting results", 'review1': "satisfied client after {product} consultation", 'review2': "{product} consulting session",
                'review3': "experienced {product} consulting team", 'favicon': "{product} consulting icon"
            },
            'training': {
                'main': "modern {product} training center", 'about1': "{product} training classroom", 'about2': "instructor teaching {product}",
                'about3': "successful {product} training completion", 'review1': "satisfied student after {product} training", 'review2': "{product} training consultation",
                'review3': "qualified {product} training team", 'favicon': "{product} training icon"
            },
            'delivery': {
                'main': "professional {product} delivery service", 'about1': "{product} delivery warehouse", 'about2': "delivery worker handling {product}",
                'about3': "successful {product} delivery", 'review1': "satisfied customer receiving {product} delivery", 'review2': "{product} delivery consultation",
                'review3': "professional {product} delivery team", 'favicon': "{product} delivery icon"
            },
            'food_delivery': {
                'main': "modern {product} delivery restaurant", 'about1': "restaurant kitchen preparing {product}", 'about2': "delivery person with {product} orders",
                'about3': "satisfied customers enjoying delivered {product}", 'review1': "happy customer receiving {product} delivery", 'review2': "restaurant team preparing {product}",
                'review3': "professional {product} delivery courier", 'favicon': "{product} restaurant icon"
            },
            # НОВЫЕ КАТЕГОРИИ для всех тематик пользователя
            'automotive': {
                'main': ["modern {product} automotive center", "professional {product} car facility", "contemporary {product} auto service"],
                'about1': ["{product} automotive workshop", "professional {product} car service area", "spacious {product} automotive facility"], 
                'about2': ["expert {product} automotive specialist", "skilled {product} car technician", "professional {product} automotive service"],
                'about3': ["quality {product} automotive results", "excellent {product} car service", "superior {product} automotive care"],
                'review1': ["satisfied customer with {product} automotive service", "happy client with {product} car care", "pleased customer with {product} auto service"],
                'review2': ["{product} automotive consultation", "professional {product} car advice", "{product} automotive guidance meeting"],
                'review3': ["experienced {product} automotive team", "qualified {product} car specialists", "professional {product} auto experts"],
                'favicon': "{product} automotive icon"
            },
            'accounting': {
                'main': "professional {product} accounting office", 'about1': "{product} accounting workspace", 'about2': "accountant working on {product}",
                'about3': "accurate {product} financial results", 'review1': "satisfied client with {product} accounting", 'review2': "{product} accounting consultation",
                'review3': "qualified {product} accounting team", 'favicon': "{product} accounting icon"
            },
            'immigration': {
                'main': "professional {product} immigration office", 'about1': "{product} immigration consultation room", 'about2': "specialist providing {product} immigration advice",
                'about3': "successful {product} immigration process", 'review1': "satisfied client with {product} immigration help", 'review2': "{product} immigration consultation",
                'review3': "experienced {product} immigration team", 'favicon': "{product} immigration icon"
            },
            'energy': {
                'main': "modern {product} energy installation", 'about1': "{product} energy equipment area", 'about2': "technician installing {product} systems",
                'about3': "efficient {product} energy solution", 'review1': "satisfied customer with {product} energy system", 'review2': "{product} energy consultation",
                'review3': "qualified {product} energy specialists", 'favicon': "{product} energy icon"
            },
            'landscaping': {
                'main': "beautiful {product} landscape design", 'about1': "{product} garden planning area", 'about2': "landscaper working on {product} design",
                'about3': "stunning {product} landscape results", 'review1': "delighted customer with {product} landscape", 'review2': "{product} landscape consultation",
                'review3': "creative {product} landscape team", 'favicon': "{product} landscape icon"
            },
            'handmade': {
                'main': "cozy {product} handmade workshop", 'about1': "{product} crafting workspace", 'about2': "artisan creating {product} items",
                'about3': "beautiful {product} handmade products", 'review1': "happy customer with {product} handmade items", 'review2': "{product} handmade consultation",
                'review3': "talented {product} artisan team", 'favicon': "{product} handmade icon"
            },
            'real_estate': {
                'main': ["modern real estate agency exterior", "elegant real estate company facade", "contemporary property sales office"],
                'about1': ["real estate office interior", "spacious property showcase room", "modern realty office space"],
                'about2': ["real estate agent showing properties", "property specialist explaining options", "experienced realtor discussing investments"],
                'about3': ["beautiful residential properties", "premium property portfolio", "successful property deals"],
                'review1': ["happy homebuyer with new keys", "satisfied real estate client", "delighted property owner"],
                'review2': ["real estate consultation meeting", "property evaluation discussion", "personalized real estate guidance"],
                'review3': ["experienced real estate team", "qualified property specialists", "professional realty experts"],
                'favicon': "house icon"
            }
        }
    
    def analyze_theme(self, theme, silent_mode=False):
        """Анализирует тематику и возвращает английские термины"""
        if not silent_mode:
            print(f"🧠 Умный анализ тематики: {theme}")
        
        theme_lower = theme.lower()
        
        # Ищем переводы ключевых слов
        found_translations = []
        activity_type = 'service'  # по умолчанию
        
        for ru_word, en_translation in self.translations.items():
            if ru_word in theme_lower:
                found_translations.append(en_translation)
                
                # УМНОЕ определение типа деятельности (оптимизировано)
                if ru_word in ['продажа', 'продаж', 'продаем', 'торговля']:
                    activity_type = 'sales'
                elif ru_word in ['производство', 'производим', 'изготовление', 'изготавливаем']:
                    activity_type = 'manufacturing'
                elif ru_word in ['ремонт', 'ремонтируем', 'починка', 'диагностика', 'диагностик']:
                    activity_type = 'repair'
                elif ru_word in ['установка', 'устанавливаем', 'монтаж', 'монтируем']:
                    activity_type = 'installation'
                elif ru_word in ['строительство', 'строим', 'строительная', 'техника']:
                    activity_type = 'construction'
                elif ru_word in ['консультация', 'консультируем', 'консультации', 'миграционные', 'юрист']:
                    activity_type = 'consulting'
                elif ru_word in ['обучение', 'обучаем', 'курсы', 'мастер-класс', 'английский', 'кулинарные']:
                    activity_type = 'training'
                elif ru_word in ['доставка', 'доставляем', 'перевозка', 'перевозим']:
                    activity_type = 'delivery'
                # НОВЫЕ КАТЕГОРИИ
                elif ru_word in ['автосалон', 'тюнинг', 'эвакуатор', 'автомойка']:
                    activity_type = 'automotive'
                elif ru_word in ['бухгалтерские', 'бухгалтерия', 'бухгалтер', 'отчетность']:
                    activity_type = 'accounting'
                elif ru_word in ['миграционные', 'миграция', 'иммиграция']:
                    activity_type = 'immigration'
                elif ru_word in ['солнечных', 'солнечные', 'панели', 'панелей', 'энергия']:
                    activity_type = 'energy'
                elif ru_word in ['ландшафтный', 'ландшафт', 'сад', 'садов', 'уход']:
                    activity_type = 'landscaping'
                elif ru_word in ['хендмейд', 'рукоделие', 'свечи', 'мыло', 'натуральная']:
                    activity_type = 'handmade'
        
        # ИСПРАВЛЕННЫЕ специальные проверки (порядок важен!)
        # Сначала проверяем автомобильную аренду
        if 'аренда авто' in theme_lower or 'аренда автомобил' in theme_lower:
            activity_type = 'automotive'
        # Потом недвижимость
        elif any(word in theme_lower for word in ['недвижимост', 'недвижимости', 'квартир', 'домов', 'коттедж', 'участк', 'земл', 'поселк']):
            activity_type = 'real_estate'
        # Обычная аренда (не авто) = недвижимость  
        elif 'аренд' in theme_lower and not any(word in theme_lower for word in ['авто', 'автомобил', 'машин']):
            activity_type = 'real_estate'
        
        # Специальная проверка для доставки еды
        food_words = ['еды', 'еда', 'блюд', 'питан', 'пицц', 'суш', 'бургер', 'ресторан', 'кафе']
        if activity_type == 'delivery' and any(word in theme_lower for word in food_words):
            activity_type = 'food_delivery'
        
        # УЛУЧШЕННЫЙ алгоритм выбора основного продукта
        # Фильтруем переводы, исключая общие слова-действия
        exclude_activity_words = ['sales', 'manufacturing', 'repair', 'installation', 'construction', 'consulting', 'training', 'delivery', 'service', 'services']
        product_translations = [t for t in found_translations if t not in exclude_activity_words]
        
        if product_translations:
            # Приоритет составным терминам (длиннее = специфичнее)
            main_product = max(product_translations, key=len)
        else:
            # Fallback: пытаемся извлечь из последнего слова темы
            words = theme_lower.split()
            if words:
                last_word = words[-1]
                main_product = self.translations.get(last_word, 'business')
            else:
                main_product = 'business'
        
        if not silent_mode:
            print(f"🎯 Тип деятельности: {activity_type}")
            print(f"🔤 Основной продукт: {main_product}")
            print(f"📝 Найденные термины: {', '.join(found_translations[:3])}")
        
        return {
            'activity_type': activity_type,
            'main_product': main_product,
            'english_terms': found_translations,
            'original_theme': theme
        }
    
    def generate_prompts(self, theme, silent_mode=False):
        """Генерирует умные промпты для любой тематики"""
        analysis = self.analyze_theme(theme, silent_mode)
        
        activity_type = analysis['activity_type']
        main_product = analysis['main_product']
        
        # Получаем шаблоны для типа деятельности
        templates = self.activity_templates.get(activity_type, self.activity_templates['service'])
        
        # Генерируем промпты, выбирая случайные варианты
        prompts = {}
        for prompt_type, template in templates.items():
            if isinstance(template, list):
                # Выбираем случайный вариант из списка
                selected_template = self._select_random_variant(template)
                prompts[prompt_type] = selected_template.format(product=main_product)
            else:
                # Обрабатываем как строку (для обратной совместимости)
                prompts[prompt_type] = template.format(product=main_product)
        
        if not silent_mode:
            print(f"✅ Промпты созданы для: {activity_type} + {main_product}")
            print(f"🎲 Использована рандомизация для разнообразия")
        
        return prompts, analysis

    def _select_random_variant(self, variants):
        """Выбирает случайный вариант из списка"""
        import random
        return random.choice(variants) 