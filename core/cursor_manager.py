# -*- coding: utf-8 -*-

"""
Модуль для работы с Cursor AI
"""

import os
import subprocess
import time
import pyautogui
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# Импорт для генерации изображений
try:
    from generators.image_generator import ImageGenerator
    IMAGE_GENERATION_AVAILABLE = True
except ImportError as e:
    IMAGE_GENERATION_AVAILABLE = False
    print(f"⚠️ Модуль генерации изображений недоступен: {e}")


class CursorManager:
    """Класс для управления Cursor AI"""
    
    def __init__(self):
        self.cursor_paths = [
            "cursor",
            "code"
        ]
        self.cached_cursor_path = None  # Кэш найденного пути
        
        # Генерируем больше возможных путей
        username = os.getenv('USERNAME')
        self.search_paths = [
            # Стандартные места установки
            fr"C:\Users\{username}\AppData\Local\Programs\cursor\Cursor.exe",
            r"C:\Program Files\Cursor\Cursor.exe", 
            r"C:\Program Files (x86)\Cursor\Cursor.exe",
            
            # Возможные места в меню Пуск
            fr"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Cursor.lnk",
            fr"C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Cursor.lnk",
            
            # Альтернативные места
            fr"C:\Users\{username}\AppData\Roaming\Cursor\Cursor.exe",
            fr"C:\Users\{username}\Desktop\Cursor.exe",
            fr"C:\Users\{username}\Desktop\Cursor.lnk",
            
            # Другие возможные места
            r"D:\Program Files\Cursor\Cursor.exe",
            r"D:\Cursor\Cursor.exe",
            fr"C:\Users\{username}\Downloads\Cursor.exe"
        ]

    @staticmethod
    def get_desktop_path():
        """Возвращает путь к рабочему столу пользователя"""
        return str(Path.home() / "Desktop")

    @staticmethod
    def check_directory_exists(base_path, dir_name):
        """
        Проверяет существование директории
        
        Args:
            base_path (str): Базовый путь
            dir_name (str): Имя директории
            
        Returns:
            tuple: (exists, full_path) - существует ли и полный путь
        """
        full_path = Path(base_path) / dir_name
        return full_path.exists(), str(full_path)
    
    def find_cursor_in_directories(self):
        """
        Глубокий поиск Cursor по основным директориям
        
        Returns:
            str: Путь к Cursor AI или None если не найден
        """
        search_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)", 
            fr"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Programs",
            fr"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming",
            r"C:\ProgramData",
            r"D:\Program Files" if os.path.exists("D:") else None
        ]
        
        # Убираем None значения
        search_dirs = [d for d in search_dirs if d and os.path.exists(d)]
        
        for search_dir in search_dirs:
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Ограничиваем глубину поиска для скорости
                    if root.count(os.sep) - search_dir.count(os.sep) > 3:
                        continue
                        
                    for file in files:
                        if file.lower() in ['cursor.exe', 'cursor']:
                            full_path = os.path.join(root, file)
                            if self._test_cursor_executable(full_path):
                                print(f"Найден Cursor AI: {full_path}")
                                return full_path
            except (PermissionError, OSError):
                continue
        return None
    
    def _test_cursor_executable(self, path):
        """
        Проверяет, является ли файл рабочим Cursor
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            bool: True если это рабочий Cursor
        """
        try:
            if not os.path.exists(path):
                return False
            # Простая проверка - пытаемся запустить с --help
            result = subprocess.run([path, "--help"], 
                                  capture_output=True, timeout=3)
            return result.returncode in [0, 1]  # 0 или 1 может быть нормальным
        except:
            return False
    
    def find_cursor_executable(self):
        """
        Ищет исполняемый файл Cursor AI - улучшенная версия
        
        Returns:
            str: Путь к Cursor AI или None если не найден
        """
        # Проверяем кэш
        if self.cached_cursor_path and os.path.exists(self.cached_cursor_path):
            print(f"Используется кэшированный путь: {self.cached_cursor_path}")
            return self.cached_cursor_path
        
        print("Поиск Cursor AI...")
        
        # 1. Проверяем команды в PATH
        for cmd in self.cursor_paths:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"Найден Cursor в PATH: {cmd}")
                    self.cached_cursor_path = cmd
                    return cmd
            except:
                continue
        
        # 2. Проверяем известные пути
        for path in self.search_paths:
            try:
                if path.endswith('.lnk'):
                    # Для .lnk файлов попробуем извлечь реальный путь
                    if os.path.exists(path):
                        print(f"Найдена ссылка Cursor: {path}")
                        self.cached_cursor_path = path
                        return path
                elif os.path.exists(path) and self._test_cursor_executable(path):
                    print(f"Найден Cursor: {path}")
                    self.cached_cursor_path = path
                    return path
            except:
                continue
        
        # 3. Поиск через реестр Windows
        print("Поиск в реестре Windows...")
        registry_result = self.find_cursor_in_registry()
        if registry_result:
            self.cached_cursor_path = registry_result
            return registry_result
        
        # 4. Глубокий поиск по системе
        print("Выполняется глубокий поиск по системе...")
        deep_search_result = self.find_cursor_in_directories()
        if deep_search_result:
            self.cached_cursor_path = deep_search_result
            return deep_search_result
        
        # 5. Поиск в Start Menu
        print("Поиск в Start Menu...")
        start_menu_result = self.find_cursor_in_start_menu()
        if start_menu_result:
            self.cached_cursor_path = start_menu_result
            return start_menu_result
        
        print("Cursor AI не найден автоматически")
        return self.ask_for_cursor_path()
    
    def find_cursor_in_registry(self):
        """
        Поиск Cursor в реестре Windows
        
        Returns:
            str: Путь к Cursor AI или None
        """
        try:
            import winreg
            
            # Ищем в стандартных местах реестра
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for hkey, path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        if "cursor" in display_name.lower():
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                            cursor_path = os.path.join(install_location, "Cursor.exe")
                                            if os.path.exists(cursor_path):
                                                print(f"Найден Cursor в реестре: {cursor_path}")
                                                return cursor_path
                                    except FileNotFoundError:
                                        pass
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue
        except ImportError:
            pass
        except Exception as e:
            print(f"Ошибка поиска в реестре: {e}")
        return None
    
    def find_cursor_in_start_menu(self):
        """
        Поиск Cursor в Start Menu
        
        Returns:
            str: Путь к Cursor AI или None
        """
        start_menu_paths = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            fr"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
        ]
        
        for start_path in start_menu_paths:
            try:
                if os.path.exists(start_path):
                    for root, dirs, files in os.walk(start_path):
                        for file in files:
                            if "cursor" in file.lower() and file.endswith('.lnk'):
                                full_path = os.path.join(root, file)
                                print(f"Найдена ссылка Cursor в Start Menu: {full_path}")
                                return full_path
            except (PermissionError, OSError):
                continue
        return None
    
    def ask_for_cursor_path(self):
        """
        Просит пользователя указать путь к Cursor AI вручную
        
        Returns:
            str: Путь к Cursor AI или None
        """
        try:
            # Создаем временное окно для диалога
            root = tk.Tk()
            root.withdraw()  # Скрываем основное окно
            
            result = messagebox.askyesno(
                "Cursor AI не найден",
                "Cursor AI не найден автоматически.\n\n"
                "Хотите указать путь к Cursor вручную?\n\n"
                "Нажмите 'Да' чтобы выбрать файл Cursor.exe\n"
                "Нажмите 'Нет' чтобы продолжить без Cursor"
            )
            
            if result:
                file_path = filedialog.askopenfilename(
                    title="Выберите Cursor.exe",
                    filetypes=[
                        ("Cursor executable", "Cursor.exe"),
                        ("Executable files", "*.exe"),
                        ("Link files", "*.lnk"),
                        ("All files", "*.*")
                    ],
                    initialdir="C:\\Program Files"
                )
                
                if file_path and os.path.exists(file_path):
                    if self._test_cursor_executable(file_path) or file_path.endswith('.lnk'):
                        print(f"Пользователь выбрал Cursor: {file_path}")
                        self.cached_cursor_path = file_path
                        root.destroy()
                        return file_path
                    else:
                        messagebox.showerror("Ошибка", "Выбранный файл не является рабочим Cursor")
            
            root.destroy()
            return None
            
        except Exception as e:
            print(f"Ошибка диалога выбора файла: {e}")
            return None
    
    def open_cursor_with_project(self, project_path):
        """
        Открывает Cursor AI с указанным проектом
        
        Args:
            project_path (Path): Путь к проекту
            
        Returns:
            bool: True если успешно, False иначе
        """
        cursor_exe = self.find_cursor_executable()
        
        if not cursor_exe:
            return False
        
        try:
            if cursor_exe in ["cursor", "code"]:
                # Команды в PATH
                subprocess.Popen([cursor_exe, str(project_path)], shell=True)
            elif cursor_exe.endswith('.lnk'):
                # Для .lnk файлов используем start
                subprocess.Popen(['start', cursor_exe, str(project_path)], shell=True)
            else:
                # Прямой путь к .exe
                subprocess.Popen([cursor_exe, str(project_path)])
            
            print(f"Cursor AI запущен: {cursor_exe}")
            return True
        except Exception as e:
            print(f"Ошибка запуска Cursor: {e}")
            return False
    
    def copy_to_clipboard(self, text, root_widget):
        """
        Копирует текст в буфер обмена
        
        Args:
            text (str): Текст для копирования
            root_widget: Корневой виджет Tkinter
        """
        root_widget.clipboard_clear()
        root_widget.clipboard_append(text)
        root_widget.update()
    
    def auto_paste_prompt(self, delay_seconds=3):
        """
        Автоматически вставляет промпт в Cursor AI
        
        Args:
            delay_seconds (int): Задержка перед вставкой
        """
        try:
            time.sleep(delay_seconds)
            pyautogui.hotkey('ctrl', 'v')
        except Exception as e:
            print(f"Ошибка автовставки: {e}")
    
    def create_project_structure(self, domain, desktop_path=None, theme=None, progress_callback=None):
        """
        Создает структуру папок проекта и генерирует тематические изображения
        
        Args:
            domain (str): Название домена
            desktop_path (Path): Путь к директории для создания проекта (опционально)
            theme (str): Тематика для генерации изображений (опционально)
            progress_callback (callable): Функция обратного вызова для обновления прогресса
            
        Returns:
            tuple: (project_path, media_path)
        """
        if desktop_path is None:
            desktop_path = self.get_desktop_path()
        
        # Проверяем существует ли папка
        exists, full_path = self.check_directory_exists(desktop_path, domain)
        if exists:
            result = messagebox.askyesno(
                "Папка существует",
                f"Папка '{domain}' уже существует в:\n{desktop_path}\n\n"
                f"Хотите перезаписать содержимое?"
            )
            if not result:
                raise Exception("Операция отменена пользователем")
        
        project_path = Path(desktop_path) / domain
        media_path = project_path / "media"
        
        # Создаем папки
        if progress_callback:
            progress_callback("📁 Создание папок проекта...")
        
        project_path.mkdir(exist_ok=True)
        media_path.mkdir(exist_ok=True)
        
        # Генерация тематических изображений
        if theme and IMAGE_GENERATION_AVAILABLE:
            try:
                if progress_callback:
                    progress_callback("🎨 Запуск генерации изображений...")
                
                # Создаем генератор в тихом режиме с поддержкой Icons8
                image_generator = ImageGenerator(silent_mode=True, use_icons8_for_favicons=True)
                
                # Генерируем изображения
                results = image_generator.generate_thematic_set(
                    theme_input=theme,
                    media_dir=str(media_path),
                    method="1",  # По умолчанию Pollinations
                    progress_callback=progress_callback
                )
                
                # Подсчитываем успешные генерации
                successful_count = results if isinstance(results, int) else 0
                
                if progress_callback:
                    progress_callback(f"✅ Генерация изображений завершена: {successful_count}/8")
                
                print(f"🎨 Сгенерировано {successful_count}/8 тематических изображений")
                
            except Exception as e:
                error_msg = f"Ошибка генерации изображений: {str(e)}"
                print(f"⚠️ {error_msg}")
                if progress_callback:
                    progress_callback(f"⚠️ {error_msg}")
        
        elif theme and not IMAGE_GENERATION_AVAILABLE:
            if progress_callback:
                progress_callback("⚠️ Модуль генерации изображений недоступен")
        
        return project_path, media_path
    
    def open_project_and_paste_prompt(self, project_path, prompt, root_widget, 
                                    auto_paste=True, paste_delay=5):
        """
        Полный цикл: открытие проекта и вставка промпта
        
        Args:
            project_path (Path): Путь к проекту
            prompt (str): Промпт для вставки
            root_widget: Корневой виджет Tkinter
            auto_paste (bool): Автоматически вставлять промпт
            paste_delay (int): Задержка перед вставкой
            
        Returns:
            tuple: (success, message)
        """
        # Всегда копируем в буфер обмена
        self.copy_to_clipboard(prompt, root_widget)
        
        # Пытаемся открыть Cursor
        if self.open_cursor_with_project(project_path):
            if auto_paste:
                # Автоматическая вставка
                self.auto_paste_prompt(paste_delay)
            
            return True, "Cursor AI запущен успешно"
        else:
            return False, "Cursor AI не найден. Промпт скопирован в буфер обмена"