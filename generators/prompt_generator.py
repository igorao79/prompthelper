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
        
        # Поиск ключевых слов в тематике
        for ru_word, en_word in self.translations.items():
            if ru_word in theme_lower:
                found_terms.append(en_word)
        
        # Определение типа деятельности
        for business_type, keywords in self.business_types.items():
            for keyword in keywords:
                if keyword in theme_lower:
                    activity_type = business_type
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
        """Извлекает основную тему из найденных терминов"""
        if not found_terms:
            return theme_lower.split()[0] if theme_lower else 'business'
        
        # Приоритет специфичным терминам
        priority_terms = [
            'car wash', 'car sales', 'car insurance', 'tow truck',
            'investment', 'training', 'real estate', 'restaurant'
        ]
        
        for term in found_terms:
            if term in priority_terms:
                return term
        
        return found_terms[0]
    
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
        
        # СПЕЦИАЛЬНАЯ ОБРАБОТКА для доставки еды
        if 'food delivery' in business_type.lower() or 'delivery' in business_type.lower():
            return [
                "delicious hot pizza ready for delivery",
                "fresh salad bowls and healthy meals",
                "gourmet burger and fries meal",
                "asian noodle dishes and sushi platters",
                "homemade pasta and italian cuisine",
                "fresh sandwich and healthy lunch options",
                "hot soup and comfort food meals",
                "dessert and sweet treats selection"
            ]
        
        specialized_prompts = {
            'automotive': [
                f"modern car service garage with {business_type} equipment",
                f"clean professional automotive workshop for {business_type}",
                f"experienced mechanic working on car {business_type}",
                f"customer waiting area in {business_type} facility"
            ],
            'investment': [
                f"professional financial advisor explaining {business_type}",
                f"modern office setting for {business_type} consultation",
                f"charts and graphs showing investment growth",
                f"confident investor learning about {business_type}"
            ],
            'training': [
                f"modern classroom for {business_type} courses",
                f"professional instructor teaching {business_type}",
                f"students engaged in {business_type} learning",
                f"practical training session for {business_type}"
            ],
            'food': [
                f"professional kitchen preparing {business_type}",
                f"fresh ingredients for {business_type} dishes",
                f"chef creating delicious {business_type} meal",
                f"elegant restaurant serving {business_type}"
            ],
            'healthcare': [
                f"clean medical facility for {business_type}",
                f"professional healthcare provider offering {business_type}",
                f"modern medical equipment for {business_type}",
                f"comfortable patient area in {business_type} clinic"
            ],
            'beauty': [
                f"elegant salon interior for {business_type} services",
                f"professional stylist providing {business_type}",
                f"relaxing spa environment for {business_type}",
                f"modern beauty equipment for {business_type}"
            ]
        }
        
        return specialized_prompts.get(activity_type, [
            f"professional {business_type} service environment",
            f"modern {business_type} workplace setup",
            f"quality {business_type} service delivery",
            f"trusted {business_type} business facility"
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