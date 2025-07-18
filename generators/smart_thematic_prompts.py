#!/usr/bin/env python3
"""
Умный генератор тематических промптов
Исправляет проблемы с неподходящими изображениями и дубляжами
С ДИНАМИЧЕСКОЙ РАНДОМИЗАЦИЕЙ для разнообразия
"""

import random
from typing import Dict, Any, Callable, Union

class SmartThematicPrompts:
    """Генератор правильных тематических промптов с рандомизацией"""
    
    def __init__(self):
        # РАСШИРЕННЫЕ ДИНАМИЧЕСКИЕ ВАРИАНТЫ для доставки еды
        self.food_delivery_options = {
            'main_dishes': [
                'fresh delicious pizza with melted cheese and toppings',
                'gourmet burger with fresh vegetables and fries', 
                'asian noodle soup with chopsticks steaming hot',
                'healthy salad bowl with colorful vegetables',
                'fresh sushi rolls on wooden board beautifully arranged',
                'hot pasta dish with herbs and cheese',
                'sandwich with fresh ingredients and sides',
                'warm soup bowl with bread and garnish',
                'crispy fried chicken with spicy sauce',
                'grilled fish with lemon and herbs',
                'mexican tacos with fresh toppings',
                'indian curry with basmati rice',
                'chinese stir-fry with vegetables',
                'italian risotto with mushrooms',
                'greek salad with feta cheese',
                'thai pad thai with peanuts',
                'korean bibimbap with kimchi',
                'japanese ramen with soft egg',
                'vietnamese pho with beef strips',
                'american BBQ ribs with coleslaw',
                'fresh seafood platter with sauce',
                'homemade dumplings with dipping sauce',
                'wood-fired pizza with artisan toppings',
                'gourmet sandwich with premium ingredients',
                'healthy smoothie bowl with fruits',
                'traditional breakfast with eggs and bacon',
                'exotic fruit salad with yogurt',
                'spicy wings with ranch dressing',
                'fresh wrap with grilled chicken',
                'artisan bread with olive oil'
            ],
            'delivery_actions': [
                'courier delivering hot food to door',
                'delivery person with insulated bag',
                'motorcycle delivery with food containers',
                'contactless delivery at doorstep',
                'delivery driver handing over order',
                'bicycle food delivery service',
                'car delivery with branded uniform',
                'drone food delivery concept',
                'delivery packaging being opened',
                'food delivery app on smartphone',
                'delivery scooter with thermal bags',
                'professional delivery service team',
                'express delivery with time guarantee',
                'eco-friendly delivery packaging',
                'delivery tracking in real-time',
                'customer receiving hot meal',
                'delivery person in branded outfit',
                'food delivery van with logo',
                'quick delivery service action',
                'safe food transport containers'
            ],
            'service_aspects': [
                'professional kitchen preparing delivery order',
                'food packaging for safe transport',
                'delivery tracking and GPS navigation',
                'restaurant partnership with delivery service',
                'quality control for delivered meals',
                'customer rating and feedback system',
                'express delivery guarantee service',
                'eco-friendly delivery packaging',
                'mobile app ordering interface',
                'chef preparing gourmet meals',
                'food safety and hygiene standards',
                'delivery route optimization',
                'customer service support team',
                'meal customization options',
                'nutritional information display',
                'special dietary requirements',
                'bulk order catering service',
                'loyalty program rewards',
                'fresh ingredient sourcing',
                'temperature-controlled delivery'
            ]
        }
        
        # РАСШИРЕННЫЕ ДИНАМИЧЕСКИЕ ВАРИАНТЫ для автосалона
        self.car_dealership_options = {
            'showroom_scenes': [
                'modern car dealership showroom with luxury vehicles',
                'bright car showroom with premium automobiles',
                'elegant auto salon with new cars display',
                'contemporary car dealership with modern lighting',
                'spacious automotive showroom with vehicle collection',
                'luxury car showroom with exotic vehicles',
                'family car dealership with SUVs and sedans',
                'electric vehicle showroom with charging stations',
                'vintage car collection in elegant showroom',
                'sports car dealership with performance vehicles',
                'outdoor car lot with diverse vehicle selection',
                'premium dealership with VIP customer lounge',
                'eco-friendly car showroom with hybrid vehicles',
                'certified pre-owned vehicle display area',
                'automotive service center with modern equipment'
            ],
            'sales_process': [
                'professional car salesperson showing vehicle features',
                'car inspection and test drive preparation',
                'car keys handover to happy customer',
                'car documentation and warranty discussion',
                'financing consultation at dealership office',
                'car delivery ceremony at dealership',
                'vehicle customization and options selection',
                'trade-in evaluation and appraisal',
                'insurance and extended warranty consultation',
                'car maintenance schedule explanation',
                'vehicle history and certification review',
                'payment processing and contract signing',
                'car registration and title transfer',
                'dealership service department introduction',
                'customer satisfaction survey completion'
            ],
            'customer_interaction': [
                'satisfied customer with new car keys',
                'happy family with their new car',
                'pleased customer shaking hands with dealer',
                'excited customer receiving car keys',
                'satisfied buyer with new vehicle',
                'delighted customer with dream car',
                'grateful family with reliable vehicle',
                'confident customer with luxury car',
                'pleased buyer with eco-friendly vehicle',
                'happy customer with sports car',
                'satisfied customer with SUV purchase',
                'excited customer with first car',
                'grateful customer with trade-in deal',
                'delighted customer with financing approval',
                'pleased customer with extended warranty'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для других тематик
        self.general_business_options = {
            'office_scenes': [
                'modern professional office environment',
                'contemporary workspace with team collaboration',
                'clean business facility with modern equipment',
                'bright office interior with professional atmosphere',
                'organized workplace with quality standards'
            ],
            'service_delivery': [
                'professional team providing quality service',
                'expert consultation and client meeting',
                'service process demonstration and explanation',
                'quality results and project completion',
                'client satisfaction and feedback session'
            ],
            'customer_reviews': [
                'happy customer with excellent service experience',
                'satisfied client with quality results',
                'pleased customer recommending service',
                'grateful client with successful outcome',
                'delighted customer with professional service'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для недвижимости
        self.real_estate_options = {
            'property_types': [
                'modern real estate office with property listings',
                'elegant property showcase with modern home',
                'luxury apartment complex with landscaping',
                'contemporary house with architectural design',
                'real estate agency with digital displays',
                'property investment consultation office'
            ],
            'services': [
                'real estate agent showing property details',
                'property viewing and inspection tour',
                'real estate contract signing and keys',
                'property photography and listing',
                'real estate market analysis and pricing',
                'property sale negotiation and closing',
                'mortgage consultation and financing',
                'property investment strategy meeting'
            ],
            'success_stories': [
                'happy homeowner with new property',
                'satisfied client with real estate purchase',
                'pleased customer with property investment',
                'excited family with new home keys',
                'successful property sale completion',
                'satisfied seller with property sale'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для фитнеса
        self.fitness_options = {
            'gym_scenes': [
                'modern gym with fitness equipment and trainers',
                'professional fitness studio with workout area',
                'personal training zone with exercise machines',
                'group fitness class with energetic atmosphere',
                'wellness center with comprehensive facilities',
                'sports performance training facility'
            ],
            'training_activities': [
                'personal training and exercise instruction',
                'fitness assessment and workout planning',
                'fitness progress tracking and goals',
                'group exercise class and motivation',
                'strength training and muscle building',
                'cardio workout and endurance training',
                'yoga and flexibility sessions',
                'nutrition counseling and meal planning'
            ],
            'fitness_results': [
                'fit person with training results',
                'healthy client with fitness achievement',
                'satisfied member with gym experience',
                'motivated athlete with performance improvement',
                'confident person with body transformation',
                'energetic client with wellness success'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для стоматологии
        self.dental_options = {
            'clinic_scenes': [
                'modern dental office with professional equipment',
                'contemporary dental clinic with advanced technology',
                'dental practice with comfortable patient area',
                'orthodontic office with specialized equipment',
                'dental surgery suite with modern facilities',
                'pediatric dental office with child-friendly design'
            ],
            'treatments': [
                'dental examination and oral health check',
                'dental treatment and procedure',
                'dental consultation and care plan',
                'teeth cleaning and preventive care',
                'dental restoration and repair work',
                'orthodontic treatment and braces',
                'dental implant consultation and planning',
                'cosmetic dentistry and smile makeover'
            ],
            'patient_satisfaction': [
                'satisfied patient with dental care',
                'happy patient with healthy smile',
                'pleased patient with dental service',
                'confident patient with beautiful smile',
                'grateful patient with pain relief',
                'delighted patient with dental transformation'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для парикмахерской
        self.salon_options = {
            'salon_scenes': [
                'modern hair salon with professional equipment',
                'contemporary beauty salon with stylish interior',
                'high-end hair studio with luxury amenities',
                'busy barbershop with skilled barbers',
                'spa salon with relaxing atmosphere',
                'trendy styling studio with modern design'
            ],
            'services': [
                'hair cutting and styling service',
                'hair coloring and treatment',
                'hair consultation and style advice',
                'professional hair washing and care',
                'hair styling for special occasions',
                'hair extension and volume enhancement',
                'scalp treatment and hair therapy',
                'bridal hair and makeup service'
            ],
            'happy_clients': [
                'satisfied client with new hairstyle',
                'happy customer with hair service',
                'pleased client with salon experience',
                'confident customer with stylish look',
                'delighted client with hair transformation',
                'grateful customer with professional styling'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для строительства
        self.construction_options = {
            'construction_sites': [
                'construction site with modern building equipment',
                'home construction project with skilled workers',
                'commercial building development with cranes',
                'renovation project with professional tools',
                'architectural construction with modern design',
                'infrastructure project with heavy machinery'
            ],
            'construction_process': [
                'construction workers and building process',
                'construction planning and project management',
                'construction completion and quality inspection',
                'foundation work and structural building',
                'roofing and exterior construction',
                'interior finishing and detail work',
                'electrical and plumbing installation',
                'final inspection and project handover'
            ],
            'project_success': [
                'satisfied homeowner with construction',
                'happy client with building project',
                'pleased customer with construction service',
                'proud property owner with new building',
                'delighted client with renovation results',
                'grateful customer with quality construction'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для образования
        self.education_options = {
            'learning_environments': [
                'modern classroom with interactive technology',
                'online learning platform with video conference',
                'educational workshop with hands-on activities',
                'study group with collaborative learning',
                'library with students and research materials',
                'training center with professional equipment'
            ],
            'educational_services': [
                'personalized tutoring and academic support',
                'interactive lessons and skill development',
                'educational assessment and progress tracking',
                'certificate programs and skill certification',
                'career counseling and guidance',
                'educational consulting and curriculum design',
                'test preparation and exam coaching',
                'academic mentoring and study strategies'
            ],
            'learning_success': [
                'successful student with academic achievement',
                'happy learner with educational progress',
                'confident graduate with new skills',
                'accomplished student with certification',
                'motivated learner with career advancement',
                'satisfied student with knowledge gain'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для кафе
        self.cafe_options = {
            'cafe_scenes': [
                'cozy coffee shop with aromatic atmosphere',
                'modern cafe with specialty coffee equipment',
                'artisan bakery with fresh pastries display',
                'trendy bistro with comfortable seating',
                'coffee roastery with beans and brewing equipment',
                'outdoor cafe terrace with pleasant ambiance'
            ],
            'cafe_offerings': [
                'barista crafting specialty coffee drinks',
                'fresh pastries and baked goods preparation',
                'coffee tasting and brewing demonstration',
                'breakfast and lunch menu presentation',
                'dessert and cake display showcase',
                'coffee beans selection and roasting process',
                'latte art and beverage presentation',
                'catering services and event planning'
            ],
            'cafe_satisfaction': [
                'happy customer enjoying morning coffee',
                'satisfied patron with delicious pastry',
                'coffee enthusiast with perfect brew',
                'pleased customer with cafe atmosphere',
                'regular customer with favorite drink',
                'delighted guest with exceptional service'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для автомойки
        self.car_wash_options = {
            'wash_facilities': [
                'modern car wash with automated equipment',
                'professional detailing bay with tools',
                'eco-friendly car wash with water recycling',
                'full-service car wash with hand washing',
                'express car wash with quick service',
                'luxury car spa with premium treatments'
            ],
            'washing_services': [
                'exterior washing and waxing service',
                'interior cleaning and vacuuming',
                'engine bay cleaning and detailing',
                'tire cleaning and shine treatment',
                'paint protection and ceramic coating',
                'headlight restoration and polishing',
                'upholstery cleaning and conditioning',
                'complete car detailing package'
            ],
            'clean_results': [
                'satisfied customer with spotless car',
                'happy car owner with shiny vehicle',
                'pleased customer with detailed interior',
                'delighted client with protected paint',
                'grateful customer with clean car',
                'impressed owner with professional service'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для юридических услуг
        self.legal_options = {
            'legal_offices': [
                'professional law office with legal library',
                'modern law firm with conference facilities',
                'attorney consultation room with privacy',
                'legal clinic with community access',
                'courthouse with legal proceedings',
                'mediation center with neutral environment'
            ],
            'legal_services': [
                'legal consultation and case evaluation',
                'contract drafting and review',
                'court representation and advocacy',
                'legal document preparation',
                'dispute resolution and negotiation',
                'legal research and case analysis',
                'compliance consulting and advice',
                'legal education and training'
            ],
            'legal_success': [
                'satisfied client with legal victory',
                'happy customer with resolved case',
                'pleased client with legal protection',
                'grateful customer with successful outcome',
                'confident client with legal guidance',
                'relieved customer with legal solution'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для банковских услуг
        self.banking_options = {
            'banking_facilities': [
                'modern bank office with customer service area',
                'financial consultation room with privacy',
                'banking center with professional advisors',
                'investment office with financial planning desk',
                'premium banking lounge with VIP service',
                'digital banking center with modern technology'
            ],
            'banking_services': [
                'personal financial consultation and planning',
                'investment portfolio review and advice',
                'mortgage and loan application process',
                'credit card and payment solutions',
                'savings and deposit account management',
                'business banking and commercial solutions',
                'insurance and protection product consultation',
                'retirement planning and pension advice'
            ],
            'banking_success': [
                'satisfied customer with approved loan',
                'happy client with investment growth',
                'pleased customer with financial security',
                'grateful client with banking solution',
                'confident customer with financial plan',
                'relieved client with debt management'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для медицины
        self.medical_options = {
            'medical_facilities': [
                'modern medical clinic with advanced equipment',
                'hospital with comprehensive care facilities',
                'family practice with welcoming atmosphere',
                'specialist clinic with focused treatment',
                'urgent care center with quick service',
                'wellness center with holistic approach'
            ],
            'medical_services': [
                'comprehensive health examination',
                'diagnostic testing and lab work',
                'treatment planning and therapy',
                'preventive care and wellness checkups',
                'specialist consultation and referral',
                'medical procedure and surgery',
                'rehabilitation and recovery support',
                'health education and lifestyle counseling'
            ],
            'health_outcomes': [
                'healthy patient with successful treatment',
                'recovered patient with improved health',
                'satisfied patient with quality care',
                'grateful patient with medical support',
                'confident patient with health plan',
                'relieved patient with diagnosis'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для технологий
        self.technology_options = {
            'tech_environments': [
                'modern IT office with cutting-edge equipment',
                'software development workspace with monitors',
                'tech support center with help desk',
                'data center with servers and networking',
                'innovation lab with research equipment',
                'tech startup with collaborative space'
            ],
            'tech_services': [
                'software development and programming',
                'IT support and technical assistance',
                'system administration and maintenance',
                'cybersecurity and data protection',
                'cloud computing and migration',
                'digital transformation consulting',
                'web development and design',
                'mobile app development'
            ],
            'tech_success': [
                'satisfied client with IT solution',
                'happy customer with technical support',
                'pleased business with system upgrade',
                'successful company with digital transformation',
                'confident client with secure systems',
                'grateful customer with improved efficiency'
            ]
        }
        
        # ДИНАМИЧЕСКИЕ ВАРИАНТЫ для хендмейд товаров
        self.handmade_options = {
            'craft_workshops': [
                'artisan workshop with handmade crafts',
                'creative studio with artistic tools',
                'craft fair with handmade products',
                'maker space with DIY equipment',
                'artisan market with unique items',
                'creative workspace with materials'
            ],
            'handmade_products': [
                'handcrafted jewelry and accessories',
                'custom artwork and paintings',
                'handmade pottery and ceramics',
                'artisan textiles and fabrics',
                'wooden crafts and furniture',
                'handmade soaps and cosmetics',
                'custom leather goods',
                'personalized gifts and items'
            ],
            'craft_satisfaction': [
                'satisfied customer with unique handmade item',
                'happy collector with artisan piece',
                'pleased customer with custom creation',
                'delighted client with personalized gift',
                'grateful customer with quality craftsmanship',
                'impressed buyer with artistic work'
            ]
        }
        
        # РАСШИРЕННЫЕ ДИНАМИЧЕСКИЕ ВАРИАНТЫ для зоомагазина
        self.pet_store_options = {
            'pet_environments': [
                'modern pet store with animal displays',
                'pet grooming salon with professional equipment',
                'veterinary clinic with animal care',
                'pet boarding facility with comfort',
                'pet training center with activity areas',
                'pet supply store with wide selection',
                'aquarium store with tropical fish',
                'bird specialty store with exotic birds',
                'reptile store with terrariums',
                'small animal rescue center',
                'pet adoption facility with happy animals',
                'luxury pet spa with premium services',
                'pet daycare with play areas',
                'animal hospital with modern equipment',
                'pet photography studio'
            ],
            'pet_services': [
                'pet grooming and styling services',
                'pet health checkups and vaccinations',
                'pet training and behavior modification',
                'pet boarding and daycare',
                'pet adoption and rescue services',
                'pet nutrition and feeding consultation',
                'pet accessories and toy selection',
                'pet insurance and healthcare plans',
                'professional pet photography',
                'pet behavioral counseling',
                'emergency veterinary care',
                'pet dental cleaning services',
                'pet microchipping and identification',
                'pet exercise and fitness programs',
                'pet socialization classes',
                'pet travel and relocation services',
                'pet memorial and cremation services',
                'exotic pet care specialists',
                'pet wellness and preventive care',
                'pet breeding consultation'
            ],
            'pet_happiness': [
                'happy pet owner with healthy animal',
                'satisfied customer with pet care',
                'delighted family with new pet',
                'grateful customer with pet services',
                'pleased pet parent with grooming',
                'confident owner with pet training',
                'joyful child with new puppy',
                'relieved owner with pet health',
                'excited family with adopted pet',
                'proud owner with well-trained pet',
                'grateful customer with pet rescue',
                'satisfied owner with pet insurance',
                'delighted customer with pet photography',
                'pleased owner with pet boarding',
                'happy customer with pet supplies'
            ]
        }
        
        # СИСТЕМА СМЕШАННОЙ РАНДОМИЗАЦИИ
        self.randomization_patterns = {
            'high_variety': {
                'main_selection': 'random_from_all',
                'about_selection': 'diverse_mix',
                'review_selection': 'emotional_variety'
            },
            'thematic_focus': {
                'main_selection': 'category_focused',
                'about_selection': 'service_focused', 
                'review_selection': 'satisfaction_focused'
            },
            'balanced_mix': {
                'main_selection': 'balanced_random',
                'about_selection': 'balanced_random',
                'review_selection': 'balanced_random'
            }
        }
        
        # ДОПОЛНИТЕЛЬНЫЕ ВАРИАНТЫ ДЛЯ УВЕЛИЧЕНИЯ РАЗНООБРАЗИЯ
        self.universal_modifiers = {
            'quality_adjectives': [
                'professional', 'premium', 'luxury', 'modern', 'innovative',
                'expert', 'specialized', 'certified', 'experienced', 'trusted',
                'award-winning', 'top-rated', 'industry-leading', 'cutting-edge',
                'state-of-the-art', 'world-class', 'exceptional', 'outstanding'
            ],
            'service_aspects': [
                'with excellent customer service',
                'with satisfaction guarantee',
                'with 24/7 support',
                'with personalized approach',
                'with competitive pricing',
                'with fast delivery',
                'with quality assurance',
                'with expert consultation',
                'with comprehensive warranty',
                'with eco-friendly practices'
            ],
            'customer_emotions': [
                'extremely satisfied', 'highly pleased', 'completely delighted',
                'thoroughly impressed', 'genuinely grateful', 'absolutely thrilled',
                'totally confident', 'remarkably happy', 'exceptionally content',
                'incredibly relieved', 'perfectly satisfied', 'wonderfully surprised'
            ]
        }
        
        # Специальные статичные промпты для тематик где нужна точность
        self.special_prompts: Dict[str, Union[Dict[str, str], Callable[[], Dict[str, str]]]] = {
            # === АВТОМОБИЛЬНАЯ ТЕМАТИКА ===
            'автосалон': self._get_dynamic_car_prompts,
            'автосалона': self._get_dynamic_car_prompts,
            'продажа авто': self._get_dynamic_car_prompts,
            'продажа автомобилей': self._get_dynamic_car_prompts,
            'дитейлинг': {
                'main': 'professional car detailing service with clean shiny vehicle',
                'about1': 'car washing and polishing professional process',
                'about2': 'interior cleaning and leather care service',
                'about3': 'paint protection and ceramic coating application',
                'review1': 'satisfied customer with perfectly clean car',
                'review2': 'happy car owner with detailed vehicle',
                'review3': 'pleased customer with car detailing results'
            },
            'детейлинг': {
                'main': 'professional car detailing service with clean shiny vehicle',
                'about1': 'car washing and polishing professional process',
                'about2': 'interior cleaning and leather care service',
                'about3': 'paint protection and ceramic coating application',
                'review1': 'satisfied customer with perfectly clean car',
                'review2': 'happy car owner with detailed vehicle',
                'review3': 'pleased customer with car detailing results'
            },
            'детейлинг авто': {
                'main': 'professional car detailing service with clean shiny vehicle',
                'about1': 'car washing and polishing professional process',
                'about2': 'interior cleaning and leather care service',
                'about3': 'paint protection and ceramic coating application',
                'review1': 'satisfied customer with perfectly clean car',
                'review2': 'happy car owner with detailed vehicle',
                'review3': 'pleased customer with car detailing results'
            },
            
            # === ДОСТАВКА И ПИТАНИЕ ===
            'доставка еды': self._get_dynamic_food_delivery_prompts,
            'доставки еды': self._get_dynamic_food_delivery_prompts,
            'доставка питания': self._get_dynamic_food_delivery_prompts,
            'доставка здорового питания': self._get_dynamic_food_delivery_prompts,
            
            # === ДИНАМИЧЕСКИЕ ТЕМАТИКИ ===
            'недвижимость': self._get_dynamic_real_estate_prompts,
            'продажа недвижимости': self._get_dynamic_real_estate_prompts,
            'фитнес': self._get_dynamic_fitness_prompts,
            'стоматология': self._get_dynamic_dental_prompts,
            'парикмахерская': self._get_dynamic_salon_prompts,
            'строительство': self._get_dynamic_construction_prompts,
            'ремонт': self._get_dynamic_construction_prompts,
            'зоомагазин': self._get_dynamic_pet_store_prompts,
            
            # === НОВЫЕ ДИНАМИЧЕСКИЕ ТЕМАТИКИ ===
            'образование': self._get_dynamic_education_prompts,
            'курсы английского': self._get_dynamic_education_prompts,
            'курсы по инвестициям': self._get_dynamic_education_prompts,
            'курсы по экономике': self._get_dynamic_education_prompts,
            'кафе': self._get_dynamic_cafe_prompts,
            'кофейня': self._get_dynamic_cafe_prompts,
            'автомойка': self._get_dynamic_car_wash_prompts,
            'услуги юристов': self._get_dynamic_legal_prompts,
            'миграционные консультации': self._get_dynamic_legal_prompts,
            'бухгалтерские услуги': self._get_dynamic_legal_prompts,
            'консультации по банковским продуктам': self._get_dynamic_banking_prompts,
            'банковские консультации': self._get_dynamic_banking_prompts,
            'банковские продукты': self._get_dynamic_banking_prompts,
            'медицина': self._get_dynamic_medical_prompts,
            'технологии': self._get_dynamic_technology_prompts,
            'хендмейд товары': self._get_dynamic_handmade_prompts,
            
            # === ОСТАЛЬНЫЕ ТЕМАТИКИ (статичные) ===
            'эвакуатор': {
                'main': 'flatbed tow truck with broken car loading',
                'about1': 'professional roadside assistance service',
                'about2': 'tow truck driver helping stranded motorist',
                'about3': 'vehicle recovery and transportation',
                'review1': 'grateful customer with car rescue',
                'review2': 'satisfied motorist with roadside help',
                'review3': 'pleased customer with towing service'
            },
            'диагностика авто': {
                'main': 'automotive diagnostic equipment and computer scan',
                'about1': 'professional mechanic using diagnostic tools',
                'about2': 'car engine inspection and analysis',
                'about3': 'diagnostic report and repair recommendations',
                'review1': 'satisfied customer with car diagnosis',
                'review2': 'happy car owner with problem solved',
                'review3': 'pleased customer with diagnostic service'
            },
            'дитейлинг авто': {
                'main': 'professional car detailing service with clean shiny vehicle',
                'about1': 'car washing and polishing professional process',
                'about2': 'interior cleaning and leather care service',
                'about3': 'paint protection and ceramic coating application',
                'review1': 'satisfied customer with perfectly clean car',
                'review2': 'happy car owner with detailed vehicle',
                'review3': 'pleased customer with car detailing results'
            },
            'страховка авто': {
                'main': 'car insurance consultation and policy review',
                'about1': 'insurance agent explaining coverage options',
                'about2': 'accident claim processing and support',
                'about3': 'insurance policy documentation and signing',
                'review1': 'protected customer with insurance coverage',
                'review2': 'satisfied client with claim settlement',
                'review3': 'pleased customer with insurance service'
            },
            'автомастерская': {
                'main': 'professional auto repair shop with lifted car',
                'about1': 'skilled mechanic performing car maintenance',
                'about2': 'engine repair and component replacement',
                'about3': 'quality inspection and service completion',
                'review1': 'satisfied customer with fixed car',
                'review2': 'happy car owner with quality repair',
                'review3': 'pleased customer with auto service'
            },
            'аренда авто': {
                'main': 'car rental office with vehicle selection',
                'about1': 'rental agent showing available vehicles',
                'about2': 'car rental agreement and key handover',
                'about3': 'vehicle inspection and rental process',
                'review1': 'satisfied customer with rental car',
                'review2': 'happy traveler with vehicle rental',
                'review3': 'pleased customer with rental service'
            },
            'тюнинг': {
                'main': 'car tuning workshop with modified vehicle',
                'about1': 'performance modification and upgrade',
                'about2': 'custom car styling and enhancement',
                'about3': 'tuning consultation and project planning',
                'review1': 'excited customer with tuned car',
                'review2': 'satisfied owner with performance upgrade',
                'review3': 'pleased customer with custom modification'
            },
            'автомойка': {
                'main': 'car wash facility with cleaning equipment',
                'about1': 'professional car washing and detailing',
                'about2': 'interior cleaning and vacuum service',
                'about3': 'car wax and polish application',
                'review1': 'satisfied customer with clean car',
                'review2': 'happy car owner with detailing service',
                'review3': 'pleased customer with car wash'
            },
            
            # === КУЛИНАРНЫЕ КУРСЫ ===
            'кулинарные курсы': {
                'main': 'professional cooking class with chef instructor',
                'about1': 'students learning knife skills and techniques',
                'about2': 'cooking workshop with fresh ingredients',
                'about3': 'culinary graduation and certificate ceremony',
                'review1': 'proud student with cooking achievement',
                'review2': 'happy amateur chef with new skills',
                'review3': 'satisfied student with culinary certificate'
            },
            'мастер-классы по кулинарии': {
                'main': 'hands-on cooking masterclass with professional chef',
                'about1': 'cooking techniques demonstration and practice',
                'about2': 'recipe creation and food presentation',
                'about3': 'culinary skills assessment and feedback',
                'review1': 'enthusiastic student with cooking success',
                'review2': 'happy participant with new recipe',
                'review3': 'satisfied learner with culinary confidence'
            },
            
            # === ОСТАЛЬНЫЕ КУРСЫ ===
            'курсы по инвестициям': {
                'main': 'investment education classroom with financial charts',
                'about1': 'stock market analysis and trading strategies',
                'about2': 'portfolio management and risk assessment',
                'about3': 'investment planning and goal setting',
                'review1': 'successful student with investment knowledge',
                'review2': 'confident investor with portfolio growth',
                'review3': 'satisfied learner with financial success'
            },
            'курсы по экономике': {
                'main': 'economics classroom with graphs and charts',
                'about1': 'economic theory and practical applications',
                'about2': 'market analysis and business economics',
                'about3': 'economic research and case studies',
                'review1': 'accomplished student with economics degree',
                'review2': 'successful graduate with economic knowledge',
                'review3': 'satisfied learner with career prospects'
            },
            'курсы английского': {
                'main': 'English language classroom with international students',
                'about1': 'conversation practice and speaking skills',
                'about2': 'grammar lessons and writing exercises',
                'about3': 'language certification and testing',
                'review1': 'confident student speaking English fluently',
                'review2': 'successful learner with language certificate',
                'review3': 'satisfied student with communication skills'
            },
            
            # === РАЗНОЕ ===
            'экономика': {
                'main': 'economic analysis and financial planning office',
                'about1': 'business economic consulting and strategy',
                'about2': 'market research and economic forecasting',
                'about3': 'economic policy analysis and recommendations',
                'review1': 'successful business with economic growth',
                'review2': 'satisfied client with financial improvement',
                'review3': 'pleased customer with economic strategy'
            },
            'погрузчик': {
                'main': 'forklift operator working in warehouse efficiently',
                'about1': 'cargo loading and unloading operations',
                'about2': 'warehouse organization and inventory management',
                'about3': 'logistics and transportation coordination',
                'review1': 'satisfied customer with cargo handling',
                'review2': 'happy client with warehouse efficiency',
                'review3': 'pleased customer with logistics service'
            },
            'установка солнечных панелей': {
                'main': 'solar panel installation on modern house roof',
                'about1': 'renewable energy consultation and planning',
                'about2': 'solar system design and configuration',
                'about3': 'energy efficiency and savings calculation',
                'review1': 'happy homeowner with solar energy',
                'review2': 'satisfied customer with energy savings',
                'review3': 'pleased client with green energy solution'
            },
            'йога': {
                'main': 'peaceful yoga class with instructor and students',
                'about1': 'yoga poses and breathing techniques',
                'about2': 'meditation and mindfulness practice',
                'about3': 'yoga therapy and wellness consultation',
                'review1': 'relaxed student with yoga practice',
                'review2': 'healthy practitioner with flexibility',
                'review3': 'satisfied client with stress relief'
            },
            'пилатес': {
                'main': 'pilates studio with equipment and instructor',
                'about1': 'core strengthening and body alignment',
                'about2': 'pilates exercises and technique training',
                'about3': 'fitness assessment and progress tracking',
                'review1': 'strong student with improved posture',
                'review2': 'healthy client with core strength',
                'review3': 'satisfied practitioner with fitness goals'
            },
            'ландшафтный дизайн': {
                'main': 'beautiful landscape design with gardens and plants',
                'about1': 'garden planning and design consultation',
                'about2': 'landscape installation and planting',
                'about3': 'garden maintenance and care services',
                'review1': 'happy homeowner with beautiful garden',
                'review2': 'satisfied customer with landscape design',
                'review3': 'pleased client with garden transformation'
            },
            'финансы': {
                'main': 'financial consulting office with charts and graphs',
                'about1': 'financial planning and investment advice',
                'about2': 'budget analysis and financial strategy',
                'about3': 'financial consultation and goal setting',
                'review1': 'successful client with financial growth',
                'review2': 'satisfied customer with investment returns',
                'review3': 'pleased client with financial planning'
            }
        }
    
    def _get_dynamic_food_delivery_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для доставки еды с улучшенной рандомизацией"""
        # Выбираем паттерн рандомизации
        pattern = random.choice(list(self.randomization_patterns.keys()))
        
        # Случайно выбираем 4 разных блюда
        main_dishes = random.sample(self.food_delivery_options['main_dishes'], 4)
        
        # Случайно выбираем аспекты доставки
        delivery_actions = random.sample(self.food_delivery_options['delivery_actions'], 2)
        service_aspects = random.sample(self.food_delivery_options['service_aspects'], 2)
        
        # Добавляем модификаторы для разнообразия
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        
        # Генерируем промпты с модификаторами
        prompts = {
            'main': f"{quality_modifier} {main_dishes[0]}",
            'about1': f"{delivery_actions[0]} {service_modifier}",
            'about2': f"{service_aspects[0]} with modern technology",
            'about3': f"{main_dishes[1]} prepared by expert chefs",
            'review1': f"{random.choice(self.universal_modifiers['customer_emotions'])} customer enjoying delivered meal",
            'review2': f"satisfied customer with {random.choice(['fast', 'reliable', 'quality'])} food delivery",
            'review3': f"pleased customer with {random.choice(['excellent', 'outstanding', 'perfect'])} delivery service"
        }
        
        return prompts
    
    def _get_dynamic_car_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для автосалона с улучшенной рандомизацией"""
        # Выбираем элементы с большим разнообразием
        showroom = random.choice(self.car_dealership_options['showroom_scenes'])
        sales_processes = random.sample(self.car_dealership_options['sales_process'], 3)
        customer_interactions = random.sample(self.car_dealership_options['customer_interaction'], 3)
        
        # Добавляем модификаторы
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        
        return {
            'main': f"{quality_modifier} {showroom}",
            'about1': f"{sales_processes[0]} {service_modifier}",
            'about2': f"{sales_processes[1]} with expert guidance",
            'about3': f"{sales_processes[2]} and comprehensive support",
            'review1': f"{random.choice(self.universal_modifiers['customer_emotions'])} {customer_interactions[0]}",
            'review2': f"{customer_interactions[1]} with exceptional service",
            'review3': f"{customer_interactions[2]} and complete satisfaction"
        }
    
    def _get_dynamic_real_estate_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для недвижимости с улучшенной рандомизацией"""
        property_types = random.sample(self.real_estate_options['property_types'], 3)
        services = random.sample(self.real_estate_options['services'], 3)
        success_stories = random.sample(self.real_estate_options['success_stories'], 3)
        
        # Добавляем модификаторы
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        emotion_modifier = random.choice(self.universal_modifiers['customer_emotions'])
        
        return {
            'main': f"{quality_modifier} {property_types[0]}",
            'about1': f"{services[0]} {service_modifier}",
            'about2': f"{services[1]} with professional expertise",
            'about3': f"{services[2]} and market knowledge",
            'review1': f"{emotion_modifier} {success_stories[0]}",
            'review2': f"{success_stories[1]} with excellent service",
            'review3': f"{success_stories[2]} and complete satisfaction"
        }
    
    def _get_dynamic_fitness_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для фитнеса с улучшенной рандомизацией"""
        gym_scenes = random.sample(self.fitness_options['gym_scenes'], 3)
        activities = random.sample(self.fitness_options['training_activities'], 3)
        results = random.sample(self.fitness_options['fitness_results'], 3)
        
        # Добавляем модификаторы
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        emotion_modifier = random.choice(self.universal_modifiers['customer_emotions'])
        
        return {
            'main': f"{quality_modifier} {gym_scenes[0]}",
            'about1': f"{activities[0]} {service_modifier}",
            'about2': f"{activities[1]} with certified trainers",
            'about3': f"{activities[2]} and personalized programs",
            'review1': f"{emotion_modifier} {results[0]}",
            'review2': f"{results[1]} with outstanding results",
            'review3': f"{results[2]} and health improvement"
        }
    
    def _get_dynamic_dental_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для стоматологии с улучшенной рандомизацией"""
        clinic_scenes = random.sample(self.dental_options['clinic_scenes'], 3)
        treatments = random.sample(self.dental_options['treatments'], 3)
        satisfaction = random.sample(self.dental_options['patient_satisfaction'], 3)
        
        # Добавляем модификаторы
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        emotion_modifier = random.choice(self.universal_modifiers['customer_emotions'])
        
        return {
            'main': f"{quality_modifier} {clinic_scenes[0]}",
            'about1': f"{treatments[0]} {service_modifier}",
            'about2': f"{treatments[1]} with gentle care",
            'about3': f"{treatments[2]} and pain-free experience",
            'review1': f"{emotion_modifier} {satisfaction[0]}",
            'review2': f"{satisfaction[1]} with professional treatment",
            'review3': f"{satisfaction[2]} and beautiful smile"
        }
    
    def _get_dynamic_salon_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для парикмахерской"""
        salon_scene = random.choice(self.salon_options['salon_scenes'])
        services = random.sample(self.salon_options['services'], 3)
        happy_clients = random.sample(self.salon_options['happy_clients'], 3)
        
        return {
            'main': salon_scene,
            'about1': services[0],
            'about2': services[1],
            'about3': services[2],
            'review1': happy_clients[0],
            'review2': happy_clients[1],
            'review3': happy_clients[2]
        }
    
    def _get_dynamic_construction_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для строительства"""
        construction_site = random.choice(self.construction_options['construction_sites'])
        process = random.sample(self.construction_options['construction_process'], 3)
        success = random.sample(self.construction_options['project_success'], 3)
        
        return {
            'main': construction_site,
            'about1': process[0],
            'about2': process[1],
            'about3': process[2],
            'review1': success[0],
            'review2': success[1],
            'review3': success[2]
        }
    
    def _get_dynamic_education_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для образования"""
        learning_environments = random.sample(self.education_options['learning_environments'], 3)
        educational_services = random.sample(self.education_options['educational_services'], 3)
        learning_success = random.sample(self.education_options['learning_success'], 3)
        
        return {
            'main': learning_environments[0],
            'about1': educational_services[0],
            'about2': educational_services[1],
            'about3': educational_services[2],
            'review1': learning_success[0],
            'review2': learning_success[1],
            'review3': learning_success[2]
        }
    
    def _get_dynamic_cafe_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для кафе"""
        cafe_scene = random.choice(self.cafe_options['cafe_scenes'])
        cafe_offerings = random.sample(self.cafe_options['cafe_offerings'], 3)
        cafe_satisfaction = random.sample(self.cafe_options['cafe_satisfaction'], 3)
        
        return {
            'main': cafe_scene,
            'about1': cafe_offerings[0],
            'about2': cafe_offerings[1],
            'about3': cafe_offerings[2],
            'review1': cafe_satisfaction[0],
            'review2': cafe_satisfaction[1],
            'review3': cafe_satisfaction[2]
        }
    
    def _get_dynamic_car_wash_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для автомойки"""
        wash_facilities = random.sample(self.car_wash_options['wash_facilities'], 3)
        washing_services = random.sample(self.car_wash_options['washing_services'], 3)
        clean_results = random.sample(self.car_wash_options['clean_results'], 3)
        
        return {
            'main': wash_facilities[0],
            'about1': washing_services[0],
            'about2': washing_services[1],
            'about3': washing_services[2],
            'review1': clean_results[0],
            'review2': clean_results[1],
            'review3': clean_results[2]
        }
    
    def _get_dynamic_legal_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для юридических услуг"""
        legal_offices = random.sample(self.legal_options['legal_offices'], 3)
        legal_services = random.sample(self.legal_options['legal_services'], 3)
        legal_success = random.sample(self.legal_options['legal_success'], 3)
        
        return {
            'main': legal_offices[0],
            'about1': legal_services[0],
            'about2': legal_services[1],
            'about3': legal_services[2],
            'review1': legal_success[0],
            'review2': legal_success[1],
            'review3': legal_success[2]
        }
    
    def _get_dynamic_banking_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для банковских услуг"""
        banking_facilities = random.sample(self.banking_options['banking_facilities'], 3)
        banking_services = random.sample(self.banking_options['banking_services'], 3)
        banking_success = random.sample(self.banking_options['banking_success'], 3)
        
        return {
            'main': banking_facilities[0],
            'about1': banking_services[0],
            'about2': banking_services[1],
            'about3': banking_services[2],
            'review1': banking_success[0],
            'review2': banking_success[1],
            'review3': banking_success[2]
        }
    
    def _get_dynamic_medical_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для медицины"""
        medical_facilities = random.sample(self.medical_options['medical_facilities'], 3)
        medical_services = random.sample(self.medical_options['medical_services'], 3)
        health_outcomes = random.sample(self.medical_options['health_outcomes'], 3)
        
        return {
            'main': medical_facilities[0],
            'about1': medical_services[0],
            'about2': medical_services[1],
            'about3': medical_services[2],
            'review1': health_outcomes[0],
            'review2': health_outcomes[1],
            'review3': health_outcomes[2]
        }
    
    def _get_dynamic_technology_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для технологий"""
        tech_environments = random.sample(self.technology_options['tech_environments'], 3)
        tech_services = random.sample(self.technology_options['tech_services'], 3)
        tech_success = random.sample(self.technology_options['tech_success'], 3)
        
        return {
            'main': tech_environments[0],
            'about1': tech_services[0],
            'about2': tech_services[1],
            'about3': tech_services[2],
            'review1': tech_success[0],
            'review2': tech_success[1],
            'review3': tech_success[2]
        }
    
    def _get_dynamic_handmade_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для хендмейд товаров"""
        craft_workshops = random.sample(self.handmade_options['craft_workshops'], 3)
        handmade_products = random.sample(self.handmade_options['handmade_products'], 3)
        craft_satisfaction = random.sample(self.handmade_options['craft_satisfaction'], 3)
        
        return {
            'main': craft_workshops[0],
            'about1': handmade_products[0],
            'about2': handmade_products[1],
            'about3': handmade_products[2],
            'review1': craft_satisfaction[0],
            'review2': craft_satisfaction[1],
            'review3': craft_satisfaction[2]
        }
    
    def _get_dynamic_pet_store_prompts(self) -> Dict[str, Any]:
        """Динамически генерирует промпты для зоомагазина с улучшенной рандомизацией"""
        # Выбираем элементы с максимальным разнообразием
        pet_environments = random.sample(self.pet_store_options['pet_environments'], 3)
        pet_services = random.sample(self.pet_store_options['pet_services'], 4)
        pet_happiness = random.sample(self.pet_store_options['pet_happiness'], 3)
        
        # Добавляем модификаторы для уникальности
        quality_modifier = random.choice(self.universal_modifiers['quality_adjectives'])
        service_modifier = random.choice(self.universal_modifiers['service_aspects'])
        emotion_modifier = random.choice(self.universal_modifiers['customer_emotions'])
        
        return {
            'main': f"{quality_modifier} {pet_environments[0]}",
            'about1': f"{pet_services[0]} {service_modifier}",
            'about2': f"{pet_services[1]} with caring professionals",
            'about3': f"{pet_services[2]} and comprehensive pet care",
            'review1': f"{emotion_modifier} {pet_happiness[0]}",
            'review2': f"{pet_happiness[1]} with excellent pet care",
            'review3': f"{pet_happiness[2]} and outstanding service"
        }
    
    def get_prompts_for_theme(self, theme) -> Dict[str, Any]:
        """Получает правильные промпты для тематики"""
        theme_lower = theme.lower().strip()
        
        # Проверяем специальные случаи
        for key, prompts_or_function in self.special_prompts.items():
            if key in theme_lower:
                # Если это функция - вызываем её
                if callable(prompts_or_function):
                    return prompts_or_function()
                else:
                    # Это словарь, возвращаем его как есть
                    return prompts_or_function
        
        # Fallback промпты для неизвестных тематик
        return {
            'main': f'professional {theme} service, modern business environment',
            'about1': f'quality {theme} team working professionally',
            'about2': f'modern {theme} equipment and technology',
            'about3': f'successful {theme} results and achievements',
            'review1': f'happy {theme} customer with excellent service',
            'review2': f'satisfied {theme} client with quality results',
            'review3': f'pleased {theme} customer recommending service'
        }
    
    def get_specific_prompt(self, theme, image_name) -> str:
        """Получает конкретный промпт для изображения"""
        prompts = self.get_prompts_for_theme(theme)
        return prompts.get(image_name, f'professional {theme} service')

# Функция для использования в основном коде
def create_smart_thematic_prompts(theme_input) -> list[str]:
    """Создает умные тематические промпты"""
    generator = SmartThematicPrompts()
    prompts_dict = generator.get_prompts_for_theme(theme_input)
    
    # Возвращаем в виде списка для совместимости
    return [
        prompts_dict['main'],
        prompts_dict['about1'], 
        prompts_dict['about2'],
        prompts_dict['about3'],
        prompts_dict.get('review1', 'happy customer'),
        prompts_dict.get('review2', 'satisfied customer'),
        prompts_dict.get('review3', 'pleased customer'),
        'business icon'  # для фавиконки
    ]

if __name__ == "__main__":
    # Тестирование
    generator = SmartThematicPrompts()
    
    # Тестируем доставку еды
    print("=== ТЕСТ ДОСТАВКИ ЕДЫ ===")
    for i in range(3):
        prompts = generator.get_prompts_for_theme("доставка еды")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем автосалон
    print("=== ТЕСТ АВТОСАЛОНА ===")
    for i in range(3):
        prompts = generator.get_prompts_for_theme("автосалон")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем недвижимость
    print("=== ТЕСТ НЕДВИЖИМОСТИ ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("недвижимость")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем фитнес
    print("=== ТЕСТ ФИТНЕСА ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("фитнес")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем стоматологию
    print("=== ТЕСТ СТОМАТОЛОГИИ ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("стоматология")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем парикмахерскую
    print("=== ТЕСТ ПАРИКМАХЕРСКОЙ ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("парикмахерская")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем строительство
    print("=== ТЕСТ СТРОИТЕЛЬСТВА ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("строительство")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем кафе
    print("=== ТЕСТ КАФЕ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("кафе")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем автомойку
    print("=== ТЕСТ АВТОМОЙКИ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("автомойка")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем образование
    print("=== ТЕСТ ОБРАЗОВАНИЯ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("образование")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем юристов
    print("=== ТЕСТ ЮРИСТОВ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("услуги юристов")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем медицину
    print("=== ТЕСТ МЕДИЦИНЫ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("медицина")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем технологии
    print("=== ТЕСТ ТЕХНОЛОГИЙ (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("технологии")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем хендмейд
    print("=== ТЕСТ ХЕНДМЕЙДА (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("хендмейд товары")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print()
    
    # Тестируем зоомагазин
    print("=== ТЕСТ ЗООМАГАЗИНА (НОВОЕ) ===")
    for i in range(2):
        prompts = generator.get_prompts_for_theme("зоомагазин")
        print(f"Вариант {i+1}:")
        print(f"Main: {prompts['main']}")
        print(f"About1: {prompts['about1']}")
        print(f"About2: {prompts['about2']}")
        print(f"About3: {prompts['about3']}")
        print() 