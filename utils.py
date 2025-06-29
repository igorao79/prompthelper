# -*- coding: utf-8 -*-

"""
Вспомогательные функции
"""

import random
from data import COUNTRIES_DATA


class CityGenerator:
    """Генератор городов без повторов"""
    
    def __init__(self):
        self.last_cities = {}  # {country: last_city}
    
    def get_random_city(self, country):
        """
        Возвращает случайный город для страны, исключая предыдущий
        
        Args:
            country (str): Название страны
            
        Returns:
            str: Название города
        """
        if country not in COUNTRIES_DATA:
            return ""
        
        cities = COUNTRIES_DATA[country]["cities"]
        last_city = self.last_cities.get(country, "")
        
        # Исключаем предыдущий город
        available_cities = [city for city in cities if city != last_city]
        
        # Если все города использованы, сбрасываем
        if not available_cities:
            available_cities = cities
        
        new_city = random.choice(available_cities)
        self.last_cities[country] = new_city
        
        return new_city


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
    """
    Возвращает язык для указанной страны
    
    Args:
        country (str): Название страны
        
    Returns:
        str: Язык страны или пустая строка
    """
    if country in COUNTRIES_DATA:
        return COUNTRIES_DATA[country]["language"]
    return ""


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
        "safe_domain": sanitize_filename(domain)
    } 