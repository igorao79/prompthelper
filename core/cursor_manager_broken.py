# -*- coding: utf-8 -*-

"""
Упрощенный CursorManager, использующий разбитые компоненты
"""

import os
import platform
from typing import Optional, Callable, Any

from .cursor_finder import CursorFinder
from .cursor_launcher import CursorLauncher
from .window_manager import WindowManager
from .clipboard_manager import ClipboardManager
from .prompt_inserter import PromptInserter
from .project_creator import ProjectCreator
from .auto_prompt_processor import AutoPromptProcessor


class CursorManager:
    """Основной класс для управления Cursor AI с разбитой архитектурой"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        
        # Проверяем, запущен ли как EXE
        self._is_exe = self._detect_exe_mode()
        if self._is_exe:
            print("🔧 Обнаружен запуск через EXE - активирована улучшенная совместимость")
        
        # Инициализируем компоненты
        self.finder = CursorFinder()
        self.launcher = CursorLauncher()
        self.window_manager = WindowManager()
        self.clipboard_manager = ClipboardManager()
        self.prompt_inserter = PromptInserter(self.clipboard_manager, self.window_manager)
        self.project_creator = ProjectCreator()
        self.auto_processor = AutoPromptProcessor(self.window_manager, self.clipboard_manager, self.prompt_inserter)
        
        # Кэш найденного пути к Cursor
        self.cached_cursor_path = None
        
        print(f"✅ CursorManager инициализирован для {self.os_type}")

    def _detect_exe_mode(self) -> bool:
        """Определяет, запущено ли приложение как EXE"""
        try:
            import sys
            # Если запущено как EXE, то sys.frozen будет True
            return getattr(sys, 'frozen', False)
        except Exception:
            return False

    def set_window_hint(self, hint: str | None):
        """Устанавливает подсказку для выбора окна Cursor"""
        self.window_manager.set_window_hint(hint)
    
    def find_cursor_executable(self) -> Optional[str]:
        """Находит исполняемый файл Cursor"""
        if self.cached_cursor_path and os.path.isfile(self.cached_cursor_path):
            return self.cached_cursor_path
        
        cursor_path = self.finder.find_cursor_executable()
        if not cursor_path:
            cursor_path = self.finder.ask_for_cursor_path()
        
        if cursor_path:
            self.cached_cursor_path = cursor_path
            print(f"✅ Найден Cursor: {cursor_path}")
        
        return cursor_path
    
    def open_cursor_with_project(self, project_path: str) -> bool:
        """Открывает Cursor с указанным проектом"""
        cursor_exe = self.find_cursor_executable()
        if not cursor_exe:
            print("❌ Не найден исполняемый файл Cursor")
            return False
        
        return self.launcher.open_cursor_with_project(project_path, cursor_exe)
    
    def copy_to_clipboard(self, text: str, root_widget=None) -> bool:
        """Копирует текст в буфер обмена"""
        return self.clipboard_manager.copy_to_clipboard(text, root_widget)
    
    def auto_paste_prompt(self, delay_seconds: int = 5) -> bool:
        """Автоматически вставляет промпт в активное окно Cursor"""
        return self.prompt_inserter.auto_paste_prompt(delay_seconds)
    
    def create_project_structure(self, domain: str, desktop_path: Optional[str] = None, 
                                theme: Optional[str] = None, progress_callback: Optional[Callable] = None,
                                generate_images: bool = False, cancel_check: Optional[Callable] = None):
        """Создает структуру проекта лендинга (возвращает tuple как в старом коде)"""
        result = self.project_creator.create_project_structure(
            domain, desktop_path, theme, progress_callback, generate_images, cancel_check
        )
        
        return result
    
    def start_auto_processing(self):
        """Запускает автоматическую обработку промптов из истории"""
        return self.auto_processor.start_auto_processing()
    
    def get_auto_processing_status(self):
        """Возвращает статус автообработки"""
        return self.auto_processor.get_processing_status()
    
    def should_start_auto_processing(self) -> bool:
        """Проверяет, готова ли система к автообработке"""
        return self.auto_processor.should_start_processing()
    
    def open_project_and_paste_prompt(self, project_path, prompt, root_widget, 
                                    auto_paste=True, paste_delay=5):
        """
        Полный цикл: открытие проекта и вставка промпта (совместимость со старым API)
        
        Args:
            project_path: Путь к проекту
            prompt: Промпт для вставки
            root_widget: Корневой виджет
            auto_paste: Автоматически вставлять промпт
            paste_delay: Задержка перед вставкой
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Копируем в буфер обмена
            if not self.copy_to_clipboard(prompt, root_widget):
                return False, "Ошибка копирования в буфер обмена"
            
            # Открываем Cursor
            if not self.open_cursor_with_project(project_path):
                return False, "Ошибка открытия проекта в Cursor"
            
            if auto_paste:
                # Автоматически вставляем промпт
                cursor_exe = self.find_cursor_executable()
                if not cursor_exe:
                    return False, "Не найден исполняемый файл Cursor"
                
                success = self.prompt_inserter.open_project_and_paste_prompt(
                    project_path, prompt, root_widget, cursor_exe, paste_delay, 3
                )
                
                if success:
                    return True, "Промпт успешно вставлен"
                else:
                    return False, "Ошибка вставки промпта"
                    else:
                return True, "Проект открыт, автовставка отключена"

        except Exception as e:
            print(f"❌ Ошибка в open_project_and_paste_prompt: {e}")
            return False, f"Ошибка: {e}"
    
    # Статические методы из проектного компонента
    @staticmethod
    def get_desktop_path() -> str:
        """Получает путь к рабочему столу"""
        return ProjectCreator.get_desktop_path()
    
    @staticmethod
    def check_directory_exists(base_path: str, dir_name: str) -> bool:
        """Проверяет существование директории"""
        return ProjectCreator.check_directory_exists(base_path, dir_name)
    
    # Методы для совместимости со старым API
    def _bring_cursor_window_to_front_old(self):
        """Совместимость: активация окна Cursor"""
        return self.window_manager._bring_cursor_window_to_front_old()
    
    def _ensure_window_active(self, hwnd, timeout_s: float = 2.0):
        """Совместимость: активация указанного окна"""
        return self.window_manager._ensure_window_active(hwnd, timeout_s)
    
    def _wait_for_cursor_app_ready(self, timeout_sec: int = 30):
        """Совместимость: ожидание готовности Cursor"""
        return self.window_manager._wait_for_cursor_app_ready(timeout_sec)
    
    def get_all_cursor_windows(self):
        """Получает список всех окон Cursor"""
        return self.window_manager.get_all_cursor_windows()
    
    def get_status_info(self) -> dict:
        """Возвращает информацию о состоянии системы"""
        cursor_path = self.cached_cursor_path
        cursor_available = cursor_path and os.path.isfile(cursor_path)
        cursor_windows = self.get_all_cursor_windows()
        
        return {
            "cursor_found": cursor_available,
            "cursor_path": cursor_path,
            "cursor_windows_count": len(cursor_windows),
            "cursor_windows": cursor_windows,
            "os_type": self.os_type,
            "exe_mode": self._is_exe,
            "clipboard_methods": self.clipboard_manager.methods,
        }
    
    def print_status(self):
        """Выводит статус системы"""
        status = self.get_status_info()
        
        print("\n" + "="*50)
        print("📊 СТАТУС CURSOR MANAGER")
        print("="*50)
        
        print(f"🖥️ Операционная система: {status['os_type']}")
        print(f"📦 Режим EXE: {'✅' if status['exe_mode'] else '❌'}")
        print(f"🎯 Cursor найден: {'✅' if status['cursor_found'] else '❌'}")
        
        if status['cursor_path']:
            print(f"📁 Путь к Cursor: {status['cursor_path']}")
        
        print(f"🖼️ Окон Cursor: {status['cursor_windows_count']}")
        if status['cursor_windows']:
            for i, window in enumerate(status['cursor_windows'], 1):
                print(f"   {i}. {window['title']}")
        
        print(f"📋 Методы буфера обмена: {', '.join(status['clipboard_methods'])}")
        
        print("="*50)
