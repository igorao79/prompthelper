# -*- coding: utf-8 -*-

"""
Модуль для создания структуры проектов лендингов
"""

import os
import time
from pathlib import Path
from typing import Optional, Callable, Any, List, Tuple

# Импорт для генерации изображений
try:
    from generators.ideogram_generator import IdeogramGenerator
    from generators.template_manager import TemplateManager
    IMAGE_GENERATION_AVAILABLE = True
    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False
    TEMPLATE_MANAGER_AVAILABLE = False


class ProjectCreator:
    """Класс для создания структуры проектов лендингов"""
    
    def __init__(self):
        self.image_generator = None
        self.template_manager = None
        
        if IMAGE_GENERATION_AVAILABLE:
            try:
                self.image_generator = IdeogramGenerator()
            except Exception as e:
                print(f"⚠️ Ошибка инициализации генератора изображений: {e}")
        
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                self.template_manager = TemplateManager()
            except Exception as e:
                print(f"⚠️ Ошибка инициализации менеджера шаблонов: {e}")
    
    def _safe_progress_callback(self, callback: Callable, message: str, progress: int = 0):
        """Безопасный вызов progress_callback с поддержкой старого API"""
        if not callback:
            return
        
        try:
            # Пробуем вызвать с двумя аргументами (новый API)
            callback(message, progress)
        except TypeError:
            try:
                # Если не получилось, пробуем с одним аргументом (старый API)
                callback(message)
            except Exception as e:
                print(f"⚠️ Ошибка вызова progress_callback: {e}")
    
    @staticmethod
    def get_desktop_path() -> str:
        """Получает путь к рабочему столу"""
        if os.name == 'nt':  # Windows
            import winreg
            try:
                # Пытаемся получить путь из реестра
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                winreg.CloseKey(key)
                return desktop_path
            except:
                # Fallback к стандартному пути
                return os.path.join(os.path.expanduser("~"), "Desktop")
        else:  # Linux/macOS
            return os.path.join(os.path.expanduser("~"), "Desktop")
    
    @staticmethod
    def check_directory_exists(base_path: str, dir_name: str) -> bool:
        """Проверяет существование директории"""
        full_path = os.path.join(base_path, dir_name)
        return os.path.exists(full_path) and os.path.isdir(full_path)
    
    def create_project_structure(self, domain: str, desktop_path: Optional[str] = None, 
                                theme: Optional[str] = None, progress_callback: Optional[Callable] = None,
                                generate_images: bool = False, cancel_check: Optional[Callable] = None):
        """
        Создает структуру папок проекта и генерирует тематические изображения (СТАРАЯ ЛОГИКА)
        
        Args:
            domain: Название домена
            desktop_path: Путь к директории для создания проекта (опционально)
            theme: Тематика для генерации изображений (опционально)
            progress_callback: Функция обратного вызова для обновления прогресса
            generate_images: Генерировать ли изображения (по умолчанию False)
            cancel_check: Функция для проверки отмены
            
        Returns:
            tuple: (project_path, media_path)
        """
        if desktop_path is None:
            desktop_path = self.get_desktop_path()
        
        # Убираем дублирование проверки существования папки - она уже выполнена в GUI
        project_path = Path(desktop_path) / domain
        media_path = project_path / "media"
        
        # Создаем папки
        if progress_callback:
            self._safe_progress_callback(progress_callback, "📁 Создание папок проекта...")
        
        project_path.mkdir(exist_ok=True)
        media_path.mkdir(exist_ok=True)
        
        # Генерация тематических изображений
        if theme and IMAGE_GENERATION_AVAILABLE and generate_images:
            try:
                if progress_callback:
                    self._safe_progress_callback(progress_callback, "🎨 Запуск генерации изображений...")
                
                # Читаем выбранную модель из настроек
                try:
                    from shared.settings_manager import SettingsManager
                    sm = SettingsManager()
                    mdl = sm.settings.get("ideogram_model", "3.0 Turbo")
                    # Отключаем Magic Prompt по умолчанию, чтобы модель не уводила тему (корабли и т.п.)
                    mpo = sm.settings.get("ideogram_magic_prompt_option", "OFF")
                except Exception:
                    mdl = "3.0 Turbo"
                    mpo = "OFF"
                # Читаем API ключ
                try:
                    key = sm.get_ideogram_api_key()
                except Exception:
                    key = ""
                
                ideogram = IdeogramGenerator(api_key=key, silent_mode=False, model=mdl, magic_prompt_option=mpo)

                if cancel_check and cancel_check():
                    return project_path, media_path

                # Оборачиваем progress_callback для совместимости с Ideogram API
                def wrapped_progress(message: str):
                    if progress_callback:
                        self._safe_progress_callback(progress_callback, message)

                # Используем новую систему генерации 8 изображений с случайными наборами названий
                # Промпт формируется минимально для всей темы
                theme_prompt = f"{theme}, professional real photo, realistic lighting, no text, no words, no letters, no watermark, no caption"
                
                # Генерируем 8 изображений - Ideogram сам выберет случайный набор названий
                saved_count = ideogram.generate_eight_images(theme_prompt, str(media_path), wrapped_progress)
                
                if progress_callback:
                    self._safe_progress_callback(progress_callback, f"Генерация завершена: {saved_count}/8 изображений")
                
                print(f"✅ Генерация завершена: {saved_count}/8 изображений")
            
            except Exception as e:
                print(f"❌ Ошибка генерации изображений: {e}")
                if progress_callback:
                    self._safe_progress_callback(progress_callback, f"Ошибка генерации: {e}")
        
        return project_path, media_path
