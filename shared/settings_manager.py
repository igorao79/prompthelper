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
        # Файл-локатор, который указывает где хранится основной файл настроек
        self.locator_file = Path.home() / ".landing_generator_settings_locator.json"
        # Определяем путь к файлу настроек: из локатора или по умолчанию
        self.settings_file = self._resolve_settings_file_path()
        self.settings = self.load_settings()
    
    def _resolve_settings_file_path(self) -> Path:
        """Определяет путь к файлу настроек, читая локатор, если он существует."""
        try:
            if self.locator_file.exists():
                with open(self.locator_file, 'r', encoding='utf-8') as f:
                    import json as _json
                    data = _json.load(f) or {}
                    p = data.get("settings_path")
                    if p:
                        sp = Path(p)
                        # Если путь существует (или хотя бы директория существует) — используем
                        if sp.exists() or sp.parent.exists():
                            return sp
        except Exception as _e:
            print(f"⚠️ Не удалось прочитать локатор настроек: {_e}")
        # По умолчанию — в домашней папке
        return Path.home() / "landing_generator_settings.json"

    def _save_locator(self):
        """Сохраняет файл-локатор с текущим путём к настройкам."""
        try:
            with open(self.locator_file, 'w', encoding='utf-8') as f:
                import json as _json
                _json.dump({"settings_path": str(self.settings_file)}, f, ensure_ascii=False, indent=2)
        except Exception as _e:
            print(f"⚠️ Не удалось сохранить локатор настроек: {_e}")

    def load_settings(self):
        """Загружает настройки из файла"""
        default_settings = {
            "favorite_countries": [],
            "theme_history": [],
            "default_save_path": str(get_desktop_path()),
            "last_save_path": str(get_desktop_path()),
            "custom_prompt": "",
            "last_selected_country": "",
            "landing_history": [],  # [{"domain": str, "prompt": str, "ts": int}]
            "special_landing_history": [],  # [{"domain": str, "prompt": str, "ts": int}] для особого режима
            "auto_check_updates": True,
            "last_update_sha": "",
            # Настройки Ideogram
            "ideogram_model": "3.0 Turbo",
            "ideogram_magic_prompt_option": "OFF",  # OFF | AUTO | ON
            "ideogram_api_key": "",
            # Поведение Cursor
            "auto_paste_prompt": True,
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
                # Создаем файл и локатор с дефолтными настройками
                self.save_settings()
                self._save_locator()
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"✅ Настройки сохранены в: {self.settings_file}")
            # Обновляем локатор на всякий случай
            self._save_locator()
            
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
    
    def set_last_selected_country(self, country):
        """Сохраняет последнюю выбранную страну"""
        self.settings["last_selected_country"] = country
        self.save_settings()
        print(f"💾 Сохранена последняя выбранная страна: {country}")
    
    def get_last_selected_country(self):
        """Возвращает последнюю выбранную страну"""
        return self.settings.get("last_selected_country", "") 

    # --- История последних лендингов ---
    def add_landing_to_history(self, domain: str, prompt: str):
        try:
            from time import time
            entry = {"domain": domain.strip(), "prompt": prompt or "", "ts": int(time())}
            hist = self.settings.get("landing_history", [])
            # сохраняем все записи, даже с одинаковым доменом (не теряем промпты)
            hist.insert(0, entry)
            self.settings["landing_history"] = hist[:10]
            self.save_settings()
        except Exception as e:
            print(f"❌ Ошибка обновления истории лендингов: {e}")

    def get_landing_history(self):
        return self.settings.get("landing_history", [])
    
    # --- История особых лендингов ---
    def add_special_landing_to_history(self, domain: str, prompt: str):
        try:
            from time import time
            entry = {"domain": domain.strip(), "prompt": prompt or "", "ts": int(time())}
            hist = self.settings.get("special_landing_history", [])
            # сохраняем все записи, даже с одинаковым доменом (не теряем промпты)
            hist.insert(0, entry)
            self.settings["special_landing_history"] = hist[:10]
            self.save_settings()
        except Exception as e:
            print(f"❌ Ошибка обновления истории особых лендингов: {e}")

    def get_special_landing_history(self):
        return self.settings.get("special_landing_history", [])

    # --- Обновления ---
    def get_auto_check_updates(self) -> bool:
        return bool(self.settings.get("auto_check_updates", True))

    def set_auto_check_updates(self, value: bool):
        self.settings["auto_check_updates"] = bool(value)
        self.save_settings()

    def get_last_update_sha(self) -> str:
        return self.settings.get("last_update_sha", "")

    def set_last_update_sha(self, sha: str):
        self.settings["last_update_sha"] = sha or ""
        self.save_settings()

    # --- Ideogram API key ---
    def get_ideogram_api_key(self) -> str:
        try:
            return str(self.settings.get("ideogram_api_key", ""))
        except Exception:
            return ""

    def set_ideogram_api_key(self, api_key: str):
        self.settings["ideogram_api_key"] = (api_key or "").strip()
        self.save_settings()

    # --- Cursor behavior ---
    def get_auto_paste_prompt(self) -> bool:
        try:
            return bool(self.settings.get("auto_paste_prompt", True))
        except Exception:
            return True

    def set_auto_paste_prompt(self, value: bool):
        self.settings["auto_paste_prompt"] = bool(value)
        self.save_settings()

    # --- Перенос файла настроек ---
    def relocate_settings_file(self, new_directory: str) -> bool:
        """
        Переносит файл настроек в новую директорию. Создает директорию при необходимости.
        Обновляет локатор и путь к файлу. Возвращает True при успехе.
        """
        try:
            new_dir = Path(new_directory)
            new_dir.mkdir(parents=True, exist_ok=True)
            new_path = new_dir / self.settings_file.name
            # Сохраняем текущие настройки в новый файл
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            # Обновляем путь и локатор
            self.settings_file = new_path
            self._save_locator()
            print(f"✅ Файл настроек перенесён в: {self.settings_file}")
            return True
        except Exception as e:
            print(f"❌ Не удалось перенести файл настроек: {e}")
            return False