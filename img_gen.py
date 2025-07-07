import requests
import datetime
import os
from PIL import Image, ImageDraw
from io import BytesIO
import json
import time

class ThematicImageGenerator:
    def __init__(self, silent_mode=False):
        """
        Умный генератор тематических изображений для лендингов
        
        Args:
            silent_mode (bool): Если True, не выводит сообщения в консоль
        """
        self.silent_mode = silent_mode
        
        if not silent_mode:
            print("🎨 AI Генератор Тематических Изображений для Лендингов")
            print("=" * 60)
            print("✨ Автоматическая генерация 8 изображений под любую тематику")
        
        # Определения тематических промптов
        self.theme_prompts = {
            "автосалон": {
                "main": "modern car dealership showroom, luxury cars displayed, professional lighting, wide view",
                "about1": "luxury sports car in showroom, red ferrari, professional photography",
                "about2": "business sedan in elegant showroom, BMW or Mercedes, side view",
                "about3": "SUV car in modern showroom, premium interior visible",
                "review1": "happy businessman in suit near luxury car, smiling, professional photo",
                "review2": "young woman with keys of new car, joy expression, car dealership background",
                "review3": "family of three near new SUV, satisfied customers, dealership setting",
                "favicon": "simple car icon, modern design, vector style, clean minimalist"
            },
            "недвижимость": {
                "main": "modern real estate office, elegant interior, property photos on walls",
                "about1": "luxury apartment interior, modern design, living room with city view",
                "about2": "beautiful house exterior, contemporary architecture, garden landscape",
                "about3": "commercial office building, glass facade, professional photography",
                "review1": "happy couple with house keys, new homeowners, smiling portrait",
                "review2": "businessman in suit holding property documents, satisfied client",
                "review3": "young family in front of new house, joyful expression, real estate success",
                "favicon": "house icon, simple modern design, real estate symbol, minimalist"
            },
            "фитнес": {
                "main": "modern fitness gym interior, equipment visible, bright lighting, spacious",
                "about1": "professional gym equipment, dumbbells and machines, clean modern design",
                "about2": "group fitness class, people exercising, energetic atmosphere",
                "about3": "personal trainer working with client, professional fitness coaching",
                "review1": "fit athletic man after workout, happy expression, gym background",
                "review2": "athletic woman in sportswear, successful fitness transformation, confident pose",
                "review3": "group of people celebrating fitness goals, happy healthy lifestyle",
                "favicon": "dumbbell icon, fitness symbol, simple modern design, vector style"
            },
            "ресторан": {
                "main": "elegant restaurant interior, dining tables, warm ambient lighting",
                "about1": "gourmet dish presentation, fine dining, professional food photography",
                "about2": "chef cooking in professional kitchen, culinary expertise, action shot",
                "about3": "wine collection and bar area, premium beverages, elegant atmosphere",
                "review1": "satisfied customer enjoying meal, happy dining experience, restaurant setting",
                "review2": "couple on romantic dinner, elegant restaurant ambiance, joyful moment",
                "review3": "family dinner celebration, happy customers, restaurant atmosphere",
                "favicon": "fork and knife icon, restaurant symbol, elegant design, minimalist"
            },
            "образование": {
                "main": "modern classroom or lecture hall, students and teacher, educational environment",
                "about1": "professional teacher explaining lesson, whiteboard, educational setting",
                "about2": "students studying together, collaborative learning, modern classroom",
                "about3": "graduation ceremony, academic success, celebration of education",
                "review1": "successful graduate with diploma, proud achievement, academic attire",
                "review2": "happy student with books, educational success, confident expression",
                "review3": "group of successful students, teamwork in education, celebration",
                "favicon": "graduation cap icon, education symbol, academic design, simple"
            },
            "медицина": {
                "main": "modern medical clinic interior, clean professional environment, medical equipment",
                "about1": "professional doctor in white coat, medical expertise, confident portrait",
                "about2": "modern medical equipment, healthcare technology, clinical setting",
                "about3": "medical consultation room, doctor-patient interaction, professional care",
                "review1": "recovered patient with doctor, successful treatment, grateful expression",
                "review2": "healthy family after medical care, satisfied patients, medical success",
                "review3": "elderly patient with caring doctor, medical compassion, healthcare quality",
                "favicon": "medical cross icon, healthcare symbol, clean design, professional"
            },
            "красота": {
                "main": "luxury beauty salon interior, elegant design, professional atmosphere",
                "about1": "professional makeup artist working, beauty transformation, artistic process",
                "about2": "spa treatment room, relaxing atmosphere, wellness and beauty",
                "about3": "hairstyling session, professional hairdresser, beauty salon environment",
                "review1": "beautiful woman after salon treatment, glowing skin, satisfied client",
                "review2": "elegant lady with new hairstyle, confident and happy, beauty success",
                "review3": "group of women enjoying beauty services, friendship and self-care",
                "favicon": "lipstick icon, beauty symbol, elegant design, feminine style"
            },
            "технологии": {
                "main": "modern tech office, computers and gadgets, innovative workspace environment",
                "about1": "cutting-edge technology devices, smartphones and laptops, tech innovation",
                "about2": "software development team working, coding and collaboration, tech environment",
                "about3": "server room or data center, technology infrastructure, digital innovation",
                "review1": "satisfied tech professional, successful IT specialist, confident expression",
                "review2": "entrepreneur with tech startup success, innovation achievement, modern office",
                "review3": "team of developers celebrating project success, tech collaboration",
                "favicon": "gear or chip icon, technology symbol, modern design, digital style"
            }
        }

    def detect_theme_from_input(self, user_input):
        """Определяет тематику на основе пользовательского ввода"""
        user_input_lower = user_input.lower()
        
        theme_keywords = {
            "автосалон": ["автосалон", "машина", "автомобиль", "дилер", "авто", "car", "auto"],
            "недвижимость": ["недвижимость", "дом", "квартира", "риэлтор", "агентство", "real estate"],
            "фитнес": ["фитнес", "спорт", "тренировка", "зал", "fitness", "gym", "спортзал"],
            "ресторан": ["ресторан", "кафе", "еда", "кухня", "повар", "restaurant", "food"],
            "образование": ["образование", "школа", "университет", "курсы", "обучение", "education"],
            "медицина": ["медицина", "клиника", "врач", "лечение", "здоровье", "medical", "doctor"],
            "красота": ["красота", "салон", "косметика", "макияж", "beauty", "salon", "spa"],
            "технологии": ["технологии", "IT", "софт", "разработка", "программирование", "tech"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return theme
        
        return "общий бизнес"  # По умолчанию

    def generate_custom_prompts(self, theme_description):
        """Генерирует кастомные промпты для неизвестной тематики"""
        base_prompts = {
            "main": f"professional {theme_description} business interior, modern design, overview shot",
            "about1": f"{theme_description} professional service, high quality, detailed view",
            "about2": f"{theme_description} equipment or products, professional presentation",
            "about3": f"{theme_description} workspace or environment, business setting",
            "review1": f"satisfied customer of {theme_description} service, happy expression, professional photo",
            "review2": f"successful client using {theme_description} service, positive experience",
            "review3": f"group of happy customers, {theme_description} business success story",
            "favicon": f"{theme_description} icon, simple modern design, business symbol, minimalist"
        }
        return base_prompts

    def get_theme_prompts(self, theme_input):
        """Получает промпты для конкретной тематики"""
        detected_theme = self.detect_theme_from_input(theme_input)
        
        if detected_theme in self.theme_prompts:
            if not self.silent_mode:
                print(f"🎯 Определена тематика: {detected_theme}")
            return self.theme_prompts[detected_theme], detected_theme
        else:
            if not self.silent_mode:
                print(f"🎯 Создаю кастомные промпты для тематики: {theme_input}")
            custom_prompts = self.generate_custom_prompts(theme_input)
            return custom_prompts, theme_input

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
            
            # Специальные настройки для фавиконки
            if image_name == "favicon":
                prompt += ", 32x32 pixels, icon design, simple, clean"
            
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