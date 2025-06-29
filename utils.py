# -*- coding: utf-8 -*-

"""
Вспомогательные функции
"""

import random
import os
import sys
import json
import datetime
from pathlib import Path
from data import COUNTRIES_DATA
import subprocess
from tkinter import messagebox


class CityGenerator:
    """Генератор городов"""
    
    def __init__(self):
        self.cities_by_country = {
            "Россия": ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"],
            "Украина": ["Киев", "Харьков", "Одесса", "Днепр", "Львов"],
            "Беларусь": ["Минск", "Гомель", "Могилев", "Витебск", "Гродно"],
            "Казахстан": ["Алматы", "Нур-Султан", "Шымкент", "Караганда", "Актобе"],
            "США": ["Нью-Йорк", "Лос-Анджелес", "Чикаго", "Хьюстон", "Филадельфия"],
            "Великобритания": ["Лондон", "Манчестер", "Бирмингем", "Глазго", "Ливерпуль"],
            "Германия": ["Берлин", "Гамбург", "Мюнхен", "Кёльн", "Франкфурт"],
            "Франция": ["Париж", "Марсель", "Лион", "Тулуза", "Ницца"],
            "Италия": ["Рим", "Милан", "Неаполь", "Турин", "Палермо"],
            "Испания": ["Мадрид", "Барселона", "Валенсия", "Севилья", "Сарагоса"],
            "Польша": ["Варшава", "Краков", "Лодзь", "Вроцлав", "Познань"],
            "Чехия": ["Прага", "Брно", "Острава", "Пльзень", "Либерец"],
            "Турция": ["Стамбул", "Анкара", "Измир", "Бурса", "Анталья"],
            "Китай": ["Пекин", "Шанхай", "Гуанчжоу", "Шэньчжэнь", "Тяньцзинь"],
            "Япония": ["Токио", "Осака", "Нагоя", "Саппоро", "Фукуока"],
            "Корея": ["Сеул", "Пусан", "Инчхон", "Тэгу", "Дэджон"],
            "Индия": ["Мумбаи", "Дели", "Бангалор", "Хайдарабад", "Ахмадабад"],
            "Бразилия": ["Сан-Паулу", "Рио-де-Жанейро", "Бразилиа", "Салвадор", "Форталеза"],
            "Мексика": ["Мехико", "Гвадалахара", "Монтеррей", "Пуэбла", "Тихуана"],
            "Канада": ["Торонто", "Монреаль", "Ванкувер", "Калгари", "Оттава"]
        }
    
    def get_random_city(self, country):
        """Возвращает случайный город для страны"""
        if country in self.cities_by_country:
            return random.choice(self.cities_by_country[country])
        return "Неизвестный город"


class SettingsManager:
    """Менеджер настроек программы"""
    
    def __init__(self):
        # Храним настройки в домашней папке пользователя
        self.settings_file = Path.home() / "landing_generator_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Загружает настройки из файла"""
        default_settings = {
            "favorite_countries": [],
            "theme_history": [],
            "default_save_path": str(get_desktop_path()),
            "last_save_path": str(get_desktop_path()),
            "custom_prompt": ""
        }
        
        print(f"🔍 Загрузка настроек из: {self.settings_file}")
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Объединяем с дефолтными настройками
                    default_settings.update(saved_settings)
                print(f"✅ Настройки загружены успешно")
                print(f"📊 Избранных стран: {len(default_settings['favorite_countries'])}")
                print(f"📝 Тематик в истории: {len(default_settings['theme_history'])}")
            else:
                print(f"ℹ️ Файл настроек не найден, используются значения по умолчанию")
                self.save_settings()  # Создаем файл с дефолтными настройками
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"✅ Настройки сохранены в: {self.settings_file}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек: {e}")
    
    def add_favorite_country(self, country):
        """Добавляет страну в избранные"""
        if country not in self.settings["favorite_countries"]:
            self.settings["favorite_countries"].insert(0, country)
            # Ограничиваем количество избранных
            self.settings["favorite_countries"] = self.settings["favorite_countries"][:10]
            self.save_settings()
    
    def remove_favorite_country(self, country):
        """Удаляет страну из избранных"""
        if country in self.settings["favorite_countries"]:
            self.settings["favorite_countries"].remove(country)
            self.save_settings()
    
    def add_theme_to_history(self, theme):
        """Добавляет тематику в историю"""
        theme = theme.strip()
        if theme and theme not in self.settings["theme_history"]:
            self.settings["theme_history"].insert(0, theme)
            # Ограничиваем историю до 10 элементов
            self.settings["theme_history"] = self.settings["theme_history"][:10]
            self.save_settings()
    
    def get_favorite_countries(self):
        """Возвращает список избранных стран"""
        return self.settings.get("favorite_countries", [])
    
    def get_theme_history(self):
        """Возвращает историю тематик"""
        return self.settings.get("theme_history", [])
    
    def set_save_path(self, path):
        """Устанавливает путь для сохранения"""
        self.settings["last_save_path"] = str(path)
        self.save_settings()
    
    def get_save_path(self):
        """Возвращает последний путь для сохранения"""
        return self.settings.get("last_save_path", str(get_desktop_path()))

    def save_prompt(self, prompt):
        """Сохраняет пользовательский промпт"""
        self.settings["custom_prompt"] = prompt
        self.save_settings()
        
    def get_prompt(self):
        """Возвращает сохраненный промпт"""
        return self.settings.get("custom_prompt", "")


def get_desktop_path():
    """
    Получает правильный путь к рабочему столу в Windows
    
    Returns:
        Path: Путь к рабочему столу
    """
    try:
        # Для Windows используем переменную USERPROFILE
        if os.name == 'nt':  # Windows
            # Пытаемся получить путь к рабочему столу через реестр
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                    return Path(desktop_path)
            except:
                pass
            
            # Альтернативные способы
            desktop_paths = [
                Path(os.path.expanduser("~/Desktop")),
                Path(os.path.expanduser("~/Рабочий стол")),
                Path(os.path.join(os.path.expanduser("~"), "Desktop")),
                Path(os.path.join(os.path.expanduser("~"), "Рабочий стол")),
                Path(os.environ.get('USERPROFILE', '')) / "Desktop",
                Path(os.environ.get('USERPROFILE', '')) / "Рабочий стол"
            ]
            
            for path in desktop_paths:
                if path.exists():
                    return path
        
        # Для других ОС
        return Path.home() / "Desktop"
        
    except Exception as e:
        print(f"Ошибка определения рабочего стола: {e}")
        return Path.home() / "Desktop"


def get_current_year():
    """
    Возвращает текущий год
    
    Returns:
        int: Текущий год
    """
    return datetime.datetime.now().year


def validate_domain(domain):
    """
    Проверяет корректность домена
    
    Args:
        domain (str): Домен для проверки
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not domain or not domain.strip():
        return False, "Домен не может быть пустым"
    
    domain = domain.strip()
    
    # Базовая проверка домена
    if len(domain) < 3:
        return False, "Домен слишком короткий"
    
    if len(domain) > 63:
        return False, "Домен слишком длинный"
    
    # Проверка на недопустимые символы
    invalid_chars = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in domain:
            return False, f"Домен содержит недопустимый символ: {char}"
    
    return True, ""


def check_directory_exists(path, domain):
    """
    Проверяет существует ли папка с таким доменом
    
    Args:
        path (Path): Путь к директории
        domain (str): Название домена
        
    Returns:
        tuple: (exists, full_path)
    """
    full_path = Path(path) / domain
    return full_path.exists(), full_path


def format_status_message(text, status_type="info"):
    """
    Форматирует статусное сообщение с эмодзи
    
    Args:
        text (str): Текст сообщения
        status_type (str): Тип статуса (info, success, error, warning)
        
    Returns:
        str: Отформатированное сообщение
    """
    emojis = {
        "info": "ℹ️",
        "success": "✅", 
        "error": "❌",
        "warning": "⚠️",
        "loading": "⏳",
        "rocket": "🚀",
        "gear": "⚙️",
        "folder": "📁",
        "document": "📝"
    }
    
    emoji = emojis.get(status_type, "")
    return f"{emoji} {text}" if emoji else text


def get_language_by_country(country):
    """Возвращает язык для страны"""
    language_names = {
        "ru": "Русский",
        "uk": "Украинский",
        "be": "Белорусский",
        "kk": "Казахский",
        "en": "Английский",
        "de": "Немецкий",
        "fr": "Французский",
        "it": "Итальянский",
        "es": "Испанский",
        "pl": "Польский",
        "cs": "Чешский",
        "tr": "Турецкий",
        "zh": "Китайский",
        "ja": "Японский",
        "ko": "Корейский",
        "hi": "Хинди",
        "pt": "Португальский"
    }
    
    lang_code = COUNTRIES_DATA.get(country)
    return language_names.get(lang_code, "Неизвестный язык")


def sanitize_filename(filename):
    """
    Очищает имя файла от недопустимых символов
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Очищенное имя файла
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Убираем множественные подчеркивания
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Убираем подчеркивания в начале и конце
    filename = filename.strip('_')
    
    return filename


def create_project_info(country, city, language, domain, theme):
    """
    Создает словарь с информацией о проекте
    
    Args:
        country (str): Страна
        city (str): Город
        language (str): Язык
        domain (str): Домен
        theme (str): Тематика
        
    Returns:
        dict: Информация о проекте
    """
    return {
        "country": country,
        "city": city, 
        "language": language,
        "domain": domain,
        "theme": theme,
        "project_name": f"{theme} - {country} ({city})",
        "safe_domain": sanitize_filename(domain),
        "year": get_current_year()
    }


def open_text_editor(text, title="Редактирование промпта"):
    """
    Открывает текст в системном редакторе
    
    Args:
        text (str): Текст для редактирования
        title (str): Заголовок окна
        
    Returns:
        str: Отредактированный текст или None при ошибке
    """
    try:
        # Создаем временный файл
        temp_dir = Path.home() / ".landing_generator"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / "temp_prompt.txt"
        
        # Сохраняем текст во временный файл
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text or "")
        
        # Открываем файл в редакторе
        if os.name == 'nt':  # Windows
            os.startfile(str(temp_file))
        else:  # Linux/Mac
            subprocess.run(['xdg-open', str(temp_file)])
        
        # Ждем пока пользователь закроет редактор
        result = messagebox.askokcancel(
            "Редактирование промпта",
            "Файл открыт в текстовом редакторе.\n\n"
            "1. Отредактируйте текст\n"
            "2. Сохраните файл (Ctrl+S)\n"
            "3. Закройте редактор\n"
            "4. Нажмите OK для сохранения изменений\n"
            "   или Отмена для отмены изменений"
        )
        
        if result:
            # Читаем обновленный текст
            with open(temp_file, 'r', encoding='utf-8') as f:
                edited_text = f.read()
            return edited_text
        
        return None
        
    except Exception as e:
        print(f"Ошибка работы с редактором: {e}")
        return None
    finally:
        # Удаляем временный файл
        try:
            if temp_file.exists():
                temp_file.unlink()
        except:
            pass 