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
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False


class ProjectCreator:
    """Класс для создания структуры проектов лендингов"""
    
    def __init__(self):
        self.image_generator = None
        if IMAGE_GENERATION_AVAILABLE:
            try:
                self.image_generator = IdeogramGenerator()
            except Exception as e:
                print(f"⚠️ Ошибка инициализации генератора изображений: {e}")
    
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
                
                # Ideogram: промпт формируем детально для каждого типа изображения
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
                # Стабильные сфокусированные промпты без дополнительных генераторов
                def _p(_name: str, fallback: str) -> str:
                    # Жёсткая анти-текст оговорка
                    return f"{fallback}, no text, no words, no letters, no watermark, no caption"

                if cancel_check and cancel_check():
                    return project_path, media_path

                # Подготовка заданий
                tasks: list[tuple[str, str]] = []
                # Основные изображения — максимально релевантные
                tasks.append(("main", _p("main", f"{theme}, professional real photo, realistic lighting")))
                tasks.append(("about1", _p("about1", f"{theme}, team at work, realistic")))
                tasks.append(("about2", _p("about2", f"{theme}, service process, realistic")))
                tasks.append(("about3", _p("about3", f"{theme}, satisfied client, realistic")))

                # Галерея — фокус на реальный процесс и детали, без абстракций
                gallery_prompts = [
                    f"{theme}, wide angle workspace view, realistic, documentary style",
                    f"{theme}, action shot of work in progress, realistic",
                    f"{theme}, equipment and tools close-up, product focus, realistic",
                ]
                tasks.append(("gallery1", _p("gallery1", gallery_prompts[0])))
                tasks.append(("gallery2", _p("gallery2", gallery_prompts[1])))
                tasks.append(("gallery3", _p("gallery3", gallery_prompts[2])))

                # Favicon — минималистичный логотип
                tasks.append(("favicon", _p("favicon", f"{theme} minimalist icon logo, simple, flat, high contrast")))

                # Параллельная генерация (ускорение): число воркеров из env IDEOGRAM_CONCURRENCY (по умолчанию 6)
                try:
                    concurrency = max(1, int(os.getenv("IDEOGRAM_CONCURRENCY", "6")))
                except Exception:
                    concurrency = 6

                from concurrent.futures import ThreadPoolExecutor, as_completed

                def _gen_one(name: str, prompt_text: str):
                    if cancel_check and cancel_check():
                        return
                    
                    # Оборачиваем progress_callback для совместимости с Ideogram API
                    def wrapped_progress(message: str):
                        if progress_callback:
                            self._safe_progress_callback(progress_callback, message)
                    
                    return ideogram.generate_single_image(prompt_text, name, str(media_path), wrapped_progress)

                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    futures = [pool.submit(_gen_one, name, pr) for name, pr in tasks]
                    for _ in as_completed(futures):
                        pass
                
                # Подсчитываем успешные генерации
                try:
                    generated_count = sum(1 for f in media_path.glob("*.jpg"))
                    total_expected = len(tasks)
                    print(f"✅ Генерация завершена: {generated_count}/{total_expected} изображений")
                    
                    if progress_callback:
                        self._safe_progress_callback(progress_callback, f"Генерация завершена: {generated_count}/{total_expected} изображений")
                
                except Exception as e:
                    print(f"⚠️ Ошибка подсчёта изображений: {e}")
            
            except Exception as e:
                print(f"❌ Ошибка генерации изображений: {e}")
                if progress_callback:
                    self._safe_progress_callback(progress_callback, f"Ошибка генерации: {e}")
        
        return project_path, media_path
