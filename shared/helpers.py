"""
Вспомогательные функции
Выделены из utils.py для лучшей организации
"""

import datetime
import zipfile
from .settings_manager import get_desktop_path
import os
import re
import subprocess
import sys
from pathlib import Path
messagebox = None  # Tkinter удалён

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
        "Канада": "en",
        "Филиппины": "fil"
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
        "Канада": "английский (Канада)",
        "Филиппины": "филиппинский (Филиппины)"
    }
    
    return language_display_map.get(country, f"английский ({country})")

def get_language_name_by_code(code: str) -> str:
    """
    Возвращает человеко-понятное название языка по коду (ISO 639-1, с поддержкой регионов)
    """
    try:
        code = (code or "en").strip()
        mapping = {
            "en": "английский",
            "ru": "русский",
            "uk": "украинский",
            "be": "белорусский",
            "kk": "казахский",
            "de": "немецкий",
            "fr": "французский",
            "it": "итальянский",
            "es": "испанский",
            "pl": "польский",
            "cs": "чешский",
            "tr": "турецкий",
            "zh": "китайский",
            "ja": "японский",
            "ko": "корейский",
            "hi": "хинди",
            "pt": "португальский",
            "fil": "филиппинский",
            # Региональные варианты (если придут)
            "en-US": "английский",
            "en-GB": "английский",
            "pt-BR": "португальский",
            "en-CA": "английский",
            "es-MX": "испанский",
            "es-CL": "испанский",
            "es-PE": "испанский",
        }
        if code in mapping:
            return mapping[code]
        base = code.split('-')[0]
        return mapping.get(base, code)
    except Exception:
        return code or "en"

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

def get_country_short_code(country):
    """
    Возвращает краткий код страны (2-3 кириллических символа) для имени ZIP.
    Если страна неизвестна — возвращает первые две согласные в верхнем регистре,
    либо первые две буквы.
    """
    mapping = {
        "Россия": "РФ",
        "Украина": "УК",
        "Беларусь": "БЛ",
        "Казахстан": "КЗ",
        "США": "СШ",
        "Великобритания": "ВБ",
        "Германия": "ГЕ",
        "Франция": "ФР",
        "Италия": "ИТ",
        "Испания": "ИС",
        "Польша": "ПЛ",
        "Перу": "ПР",
        "Чехия": "ЧХ",
        "Чили": "ЧЛ",
        "Турция": "ТР",
        "Китай": "КТ",
        "Япония": "ЯП",
        "Корея": "КР",
        "Индия": "ИН",
        "Бразилия": "БР",
        "Мексика": "МК",
        "Канада": "КА",
        "Филиппины": "ФЛ",
    }
    if country in mapping:
        return mapping[country]
    # Автоматическое правило для неизвестных: первые две согласные/буквы
    vowels = set("аеёиоуыэюяAEIOUYaeiouy")
    letters = [ch for ch in country if ch.isalpha()]
    consonants = [ch for ch in letters if ch not in vowels]
    base = (consonants[:2] or letters[:2] or [country[:1]])
    return "".join(base).upper()

def ensure_empty_zip_for_landing(save_dir, country, theme, model=None):
    """
    Создает ПУСТОЙ ZIP-файл в выбранной папке (или на рабочем столе),
    именем: <КодСтраны>_<Тематика>_<ДД.ММ.ГГГГ>_<Модель>.zip или <КодСтраны>_<Тематика>_<ДД.ММ.ГГГГ>.zip
    Важно: если уже существует ZIP для этой страны и тематики (любая дата), новый не создается.

    Args:
        save_dir: Путь к папке сохранения
        country: Название страны
        theme: Тематика
        model: Модель (опционально)

    Returns:
        Path | None: Путь к созданному ZIP или None, если создание не требовалось/невозможно.
    """
    try:
        base_dir = Path(save_dir) if save_dir else get_desktop_path()
        base_dir.mkdir(parents=True, exist_ok=True)

        country_code = get_country_short_code(country)
        # Проверка существования любого ZIP с этой страной и тематикой
        safe_theme = sanitize_filename(theme)
        pattern = f"{country_code}_{safe_theme}_*.zip"
        existing = list(base_dir.glob(pattern))
        if existing:
            return None

        today = datetime.datetime.now().strftime("%d.%m.%Y")
        # Добавляем модель к имени, если она указана
        if model and model.strip():
            safe_model = sanitize_filename(model.strip())
            zip_name = f"{country_code}_{safe_theme}_{today}_{safe_model}.zip"
        else:
            zip_name = f"{country_code}_{safe_theme}_{today}.zip"
        zip_path = base_dir / zip_name

        # Создаем пустой ZIP
        with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            pass
        return zip_path
    except Exception as e:
        print(f"Ошибка создания ZIP: {e}")
        return None

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
    # Tkinter редактор удалён. Возвращаем исходный текст без изменений.
    return text


def create_special_mode_structure(base_save_path):
    """
    Создает структуру папок для особого режима и возвращает следующий номер сайта.
    Автоматически адаптируется к любому количеству существующих сайтов.
    
    Args:
        base_save_path (str): Базовый путь для сохранения
    
    Returns:
        tuple: (landings_path, next_site_number, site_name)
    """
    try:
        landings_path = Path(base_save_path) / "landings_special"
        landings_path.mkdir(parents=True, exist_ok=True)
        
        # Находим все существующие сайты (s0001, s0002, s0050, s1000 и т.д.)
        existing_sites = []
        if landings_path.exists():
            for item in landings_path.iterdir():
                if item.is_dir() and item.name.startswith('s') and len(item.name) == 5:
                    try:
                        site_num = int(item.name[1:])  # Убираем 's' и преобразуем в число
                        existing_sites.append(site_num)
                    except ValueError:
                        continue
        
        # Определяем следующий номер (автоматически продолжает с любого количества)
        next_site_number = max(existing_sites) + 1 if existing_sites else 1
        
        # Форматируем имя сайта (например, s0001, s0021, s0100 и т.д.)
        site_name = f"s{next_site_number:04d}"
        
        return str(landings_path), next_site_number, site_name
        
    except Exception as e:
        print(f"Ошибка создания структуры особого режима: {e}")
        # Возвращаем базовое значение в случае ошибки
        return str(Path(base_save_path) / "landings_special"), 1, "s0001"


def create_special_mode_zip(landings_path, site_name):
    """
    Создает ZIP-архив для особого режима
    
    Args:
        landings_path (str): Путь к папке landings
        site_name (str): Имя сайта (например, s0001)
    
    Returns:
        str: Путь к созданному ZIP-архиву
    """
    try:
        zip_path = Path(landings_path) / f"{site_name}.zip"
        
        # Создаем пустой ZIP-архив
        with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED):
            pass
        
        return str(zip_path)
        
    except Exception as e:
        print(f"Ошибка создания ZIP-архива для особого режима: {e}")
        return None