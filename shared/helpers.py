"""
Вспомогательные функции
Выделены из utils.py для лучшей организации
"""

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path
from tkinter import messagebox

def get_current_year():
    """
    Возвращает текущий год
    
    Returns:
        int: Текущий год
    """
    return datetime.datetime.now().year

def validate_domain(domain):
    """
    Проверяет корректность доменного имени и исправляет кириллические символы
    
    Args:
        domain (str): Доменное имя для проверки
        
    Returns:
        tuple: (bool, str, str) - (валидность, сообщение об ошибке, исправленный домен)
    """
    if not domain:
        return False, "Доменное имя не может быть пустым", domain
    
    if len(domain) < 3:
        return False, "Доменное имя слишком короткое (минимум 3 символа)", domain
    
    if len(domain) > 253:
        return False, "Доменное имя слишком длинное (максимум 253 символа)", domain
    
    # Автоматическая замена похожих кириллических символов на латинские
    cyrillic_to_latin = {
        'а': 'a', 'А': 'A',
        'е': 'e', 'Е': 'E', 
        'о': 'o', 'О': 'O',
        'р': 'p', 'Р': 'P',
        'с': 'c', 'С': 'C',
        'у': 'u', 'У': 'U',
        'х': 'x', 'Х': 'X',
        'м': 'm', 'М': 'M',
        'н': 'n', 'Н': 'N',
        'к': 'k', 'К': 'K',
        'т': 't', 'Т': 'T'
    }
    
    # Заменяем кириллические символы на латинские
    corrected_domain = domain
    for cyrillic, latin in cyrillic_to_latin.items():
        corrected_domain = corrected_domain.replace(cyrillic, latin)
    
    # Проверяем формат домена
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    
    if not re.match(domain_pattern, corrected_domain):
        return False, "Некорректный формат доменного имени", corrected_domain
    
    return True, "", corrected_domain

def check_directory_exists(path, domain):
    """
    Проверяет существование директории проекта
    
    Args:
        path (str): Путь к директории
        domain (str): Доменное имя
        
    Returns:
        tuple: (bool, Path) - (существует ли, полный путь)
    """
    project_path = Path(path) / domain
    return project_path.exists(), project_path

def format_status_message(text, status_type="info"):
    """
    Форматирует сообщение для статуса
    
    Args:
        text (str): Текст сообщения
        status_type (str): Тип сообщения (info, success, warning, error)
        
    Returns:
        str: Отформатированное сообщение
    """
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌",
        "progress": "🔄"
    }
    
    icon = icons.get(status_type, "ℹ️")
    return f"{icon} {text}"

def get_language_by_country(country):
    """
    Возвращает основной язык для страны
    
    Args:
        country (str): Название страны
        
    Returns:
        str: Код языка
    """
    language_map = {
        "Россия": "ru",
        "Украина": "uk", 
        "Беларусь": "be",
        "Казахстан": "kk",
        "США": "en",
        "Великобритания": "en",
        "Германия": "de",
        "Франция": "fr",
        "Италия": "it", 
        "Испания": "es",
        "Польша": "pl",
        "Перу": "es",
        "Чехия": "cs",
        "Чили": "es",
        "Турция": "tr",
        "Китай": "zh",
        "Япония": "ja",
        "Корея": "ko",
        "Индия": "hi",
        "Бразилия": "pt",
        "Мексика": "es",
        "Канада": "en"
    }
    
    return language_map.get(country, "en")

def get_html_lang_code(country):
    """Возвращает HTML lang код для страны"""
    return get_language_by_country(country)

def get_language_display_name(country):
    """
    Возвращает красивое название языка для отображения в интерфейсе
    
    Args:
        country (str): Название страны
        
    Returns:
        str: Человеко-понятное название языка
    """
    language_display_map = {
        "Россия": "русский (Россия)",
        "Украина": "украинский (Украина)", 
        "Беларусь": "белорусский (Беларусь)",
        "Казахстан": "казахский (Казахстан)",
        "США": "английский (США)",
        "Великобритания": "английский (Великобритания)",
        "Германия": "немецкий (Германия)",
        "Франция": "французский (Франция)",
        "Италия": "итальянский (Италия)", 
        "Испания": "испанский (Испания)",
        "Польша": "польский (Польша)",
        "Перу": "испанский (Перу)",
        "Чехия": "чешский (Чехия)",
        "Чили": "испанский (Чили)",
        "Турция": "турецкий (Турция)",
        "Китай": "китайский (Китай)",
        "Япония": "японский (Япония)",
        "Корея": "корейский (Корея)",
        "Индия": "хинди (Индия)",
        "Бразилия": "португальский (Бразилия)",
        "Мексика": "испанский (Мексика)",
        "Канада": "английский (Канада)"
    }
    
    return language_display_map.get(country, f"английский ({country})")

def sanitize_filename(filename):
    """
    Очищает имя файла от недопустимых символов
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Очищенное имя файла
    """
    # Удаляем недопустимые символы для имени файла
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Заменяем пробелы на подчеркивания
    filename = filename.replace(' ', '_')
    
    # Ограничиваем длину
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def create_project_info(country, city, language, domain, theme):
    """
    Создает информацию о проекте
    
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
        'country': country,
        'city': city,
        'language': language,
        'domain': domain,
        'theme': theme,
        'created_at': datetime.datetime.now().isoformat(),
        'year': get_current_year()
    }

def open_text_editor(text, title="Редактирование промпта"):
    """
    Открывает простое окно редактирования текста
    
    Args:
        text (str): Исходный текст
        title (str): Заголовок окна
        
    Returns:
        str: Отредактированный текст или None если отменено
    """
    try:
        import tkinter as tk
        from tkinter import scrolledtext
        
        root = tk.Tk()
        root.title(title)
        root.geometry("600x400")
        
        # Создаем текстовое поле с прокруткой
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
        text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Вставляем исходный текст
        text_area.insert(tk.END, text)
        
        result = {'text': None}
        
        def save_and_close():
            result['text'] = text_area.get('1.0', tk.END).strip()
            root.destroy()
        
        def cancel():
            root.destroy()
        
        # Кнопки
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Сохранить", command=save_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=cancel).pack(side=tk.LEFT, padx=5)
        
        root.mainloop()
        
        return result['text']
        
    except Exception as e:
        print(f"Ошибка открытия редактора: {e}")
        return text 