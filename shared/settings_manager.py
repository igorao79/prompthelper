"""
Менеджер настроек приложения
Выделен из utils.py для лучшей организации
"""

import json
import os
from pathlib import Path

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