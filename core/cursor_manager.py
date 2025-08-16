# -*- coding: utf-8 -*-

"""
Модуль для работы с Cursor AI
Кроссплатформенная версия (Windows/Linux/macOS)
"""

import os
import subprocess
import time
import platform
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# Проверяем доступность pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui недоступен, автовставка промптов отключена")

# Импорт для генерации изображений
try:
    from generators.image_generator import ImageGenerator
    IMAGE_GENERATION_AVAILABLE = True
except ImportError as e:
    IMAGE_GENERATION_AVAILABLE = False
    print(f"⚠️ Модуль генерации изображений недоступен: {e}")


class CursorManager:
    """Кроссплатформенный класс для управления Cursor AI"""
    
    def __init__(self):
        self.cursor_paths = [
            "cursor",
            "code"
        ]
        self.cached_cursor_path = None  # Кэш найденного пути
        self.os_type = platform.system().lower()
        
        print(f"🖥️ Определена ОС: {self.os_type}")
        
        # Генерируем пути поиска в зависимости от ОС
        self.search_paths = self._get_platform_search_paths()

    def _get_platform_search_paths(self):
        """Получает пути поиска Cursor для текущей ОС"""
        if self.os_type == 'windows':
            return self._get_windows_search_paths()
        elif self.os_type == 'linux':
            return self._get_linux_search_paths()
        elif self.os_type == 'darwin':  # macOS
            return self._get_macos_search_paths()
        else:
            return []

    def _get_windows_search_paths(self):
        """Возвращает пути поиска для Windows"""
        username = os.getenv('USERNAME', os.getenv('USER', ''))
        return [
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

    def _get_linux_search_paths(self):
        """Возвращает пути поиска для Linux"""
        username = os.getenv('USER', '')
        home = Path.home()
        
        return [
            # AppImage в домашней папке
            str(home / "cursor.AppImage"),
            str(home / "Cursor.AppImage"),
            str(home / "Downloads/cursor.AppImage"),
            str(home / "Downloads/Cursor.AppImage"),
            str(home / "Applications/cursor.AppImage"),
            str(home / "Applications/Cursor.AppImage"),
            
            # Snap установка
            "/snap/cursor/current/cursor",
            f"/home/{username}/snap/cursor/current/cursor",
            
            # Flatpak установка
            "/var/lib/flatpak/app/com.cursor.Cursor/current/active/files/cursor",
            f"/home/{username}/.local/share/flatpak/app/com.cursor.Cursor/current/active/files/cursor",
            
            # Традиционные Linux пути
            "/usr/bin/cursor",
            "/usr/local/bin/cursor",
            "/opt/cursor/cursor",
            "/opt/Cursor/cursor",
            
            # В домашней папке
            str(home / ".local/bin/cursor"),
            str(home / ".local/share/cursor/cursor"),
            str(home / "bin/cursor"),
            
            # Deb пакет
            "/usr/share/cursor/cursor",
            
            # Tar.gz архив
            str(home / "cursor/cursor"),
            str(home / "Cursor/cursor"),
        ]

    def _get_macos_search_paths(self):
        """Возвращает пути поиска для macOS"""
        username = os.getenv('USER', '')
        home = Path.home()
        
        return [
            # Стандартная установка приложения
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
            f"/Users/{username}/Applications/Cursor.app/Contents/MacOS/Cursor",
            
            # Homebrew
            "/usr/local/bin/cursor",
            "/opt/homebrew/bin/cursor",
            
            # В домашней папке
            str(home / "Applications/Cursor.app/Contents/MacOS/Cursor"),
            str(home / "Downloads/Cursor.app/Contents/MacOS/Cursor"),
        ]

    @staticmethod
    def get_desktop_path():
        """Возвращает путь к рабочему столу пользователя кроссплатформенно"""
        system = platform.system().lower()
        home = Path.home()
        
        if system == 'windows':
            # Для Windows
            desktop_paths = [
                home / "Desktop",
                home / "Рабочий стол",  # Русская локализация
            ]
        elif system == 'linux':
            # Для Linux
            desktop_paths = [
                home / "Desktop",
                home / "Рабочий стол",  # Русская локализация
                home / "Рабочий_стол",
                home / ".local/share/desktop",  # Альтернативный путь
            ]
        elif system == 'darwin':  # macOS
            desktop_paths = [
                home / "Desktop",
            ]
        else:
            desktop_paths = [home / "Desktop"]
        
        # Возвращаем первый существующий путь
        for path in desktop_paths:
            if path.exists():
                return str(path)
        
        # Если ничего не найдено, возвращаем стандартный
        return str(home / "Desktop")

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
        Глубокий поиск Cursor по основным директориям (кроссплатформенный)
        
        Returns:
            str: Путь к Cursor AI или None если не найден
        """
        search_dirs = self._get_search_directories()
        
        # Убираем None значения и проверяем существование
        search_dirs = [d for d in search_dirs if d and os.path.exists(d)]
        
        for search_dir in search_dirs:
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Ограничиваем глубину поиска для скорости
                    if root.count(os.sep) - search_dir.count(os.sep) > 3:
                        continue
                        
                    for file in files:
                        if self._is_cursor_file(file):
                            full_path = os.path.join(root, file)
                            if self._test_cursor_executable(full_path):
                                print(f"Найден Cursor AI: {full_path}")
                                return full_path
            except (PermissionError, OSError):
                continue
        return None
    
    def _get_search_directories(self):
        """Возвращает директории для поиска в зависимости от ОС"""
        if self.os_type == 'windows':
            username = os.getenv('USERNAME', os.getenv('USER', ''))
            return [
                r"C:\Program Files",
                r"C:\Program Files (x86)", 
                fr"C:\Users\{username}\AppData\Local\Programs",
                fr"C:\Users\{username}\AppData\Roaming",
                r"C:\ProgramData",
                r"D:\Program Files" if os.path.exists("D:") else None
            ]
        elif self.os_type == 'linux':
            home = Path.home()
            return [
                "/usr/bin",
                "/usr/local/bin", 
                "/opt",
                "/snap",
                "/var/lib/flatpak",
                str(home / ".local"),
                str(home / "Applications"),
                str(home / "Downloads"),
                str(home),
            ]
        elif self.os_type == 'darwin':  # macOS
            home = Path.home()
            return [
                "/Applications",
                "/usr/local/bin",
                "/opt/homebrew/bin",
                str(home / "Applications"),
                str(home / "Downloads"),
            ]
        else:
            return []
    
    def _is_cursor_file(self, filename):
        """Проверяет, является ли файл потенциально Cursor AI"""
        filename_lower = filename.lower()
        
        if self.os_type == 'windows':
            return filename_lower in ['cursor.exe', 'cursor']
        elif self.os_type == 'linux':
            return filename_lower in ['cursor', 'cursor.appimage'] or 'cursor' in filename_lower
        elif self.os_type == 'darwin':  # macOS
            return filename_lower in ['cursor'] or 'cursor' in filename_lower
        else:
            return 'cursor' in filename_lower
    
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
                                  capture_output=True, timeout=3,
                                  encoding='utf-8', errors='ignore')
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
                                      capture_output=True, text=True, timeout=5,
                                      encoding='utf-8', errors='ignore')
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
        
        # 3. Поиск через системно-специфичные методы
        if self.os_type == 'windows':
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
        
        # 5. Поиск в системно-специфичных местах
        if self.os_type == 'windows':
            print("Поиск в Start Menu...")
            start_menu_result = self.find_cursor_in_start_menu()
            if start_menu_result:
                self.cached_cursor_path = start_menu_result
                return start_menu_result
        elif self.os_type == 'linux':
            print("Поиск через which/whereis...")
            linux_result = self.find_cursor_linux_commands()
            if linux_result:
                self.cached_cursor_path = linux_result
                return linux_result
        
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
    
    def find_cursor_linux_commands(self):
        """
        Поиск Cursor через Linux команды which/whereis
        
        Returns:
            str: Путь к Cursor AI или None
        """
        try:
            # Пробуем команду which
            result = subprocess.run(['which', 'cursor'], 
                                  capture_output=True, text=True, timeout=5,
                                  encoding='utf-8', errors='ignore')
            if result.returncode == 0 and result.stdout.strip():
                cursor_path = result.stdout.strip()
                print(f"Найден Cursor через which: {cursor_path}")
                return cursor_path
        except:
            pass
        
        try:
            # Пробуем команду whereis
            result = subprocess.run(['whereis', 'cursor'], 
                                  capture_output=True, text=True, timeout=5,
                                  encoding='utf-8', errors='ignore')
            if result.returncode == 0 and result.stdout.strip():
                # whereis возвращает несколько путей, берем первый исполняемый
                paths = result.stdout.strip().split()[1:]  # Убираем "cursor:"
                for path in paths:
                    if os.path.exists(path) and self._test_cursor_executable(path):
                        print(f"Найден Cursor через whereis: {path}")
                        return path
        except:
            pass
        
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
                # Адаптируем диалог под ОС
                if self.os_type == 'windows':
                    filetypes = [
                        ("Cursor executable", "Cursor.exe"),
                        ("Executable files", "*.exe"),
                        ("Link files", "*.lnk"),
                        ("All files", "*.*")
                    ]
                    initialdir = "C:\\Program Files"
                elif self.os_type == 'linux':
                    filetypes = [
                        ("Cursor AppImage", "*.AppImage"),
                        ("Cursor executable", "cursor"),
                        ("All files", "*")
                    ]
                    initialdir = str(Path.home())
                elif self.os_type == 'darwin':  # macOS
                    filetypes = [
                        ("Cursor app", "Cursor"),
                        ("Application", "*.app"),
                        ("All files", "*")
                    ]
                    initialdir = "/Applications"
                else:
                    filetypes = [("All files", "*")]
                    initialdir = str(Path.home())
                
                file_path = filedialog.askopenfilename(
                    title=f"Выберите Cursor ({self.os_type})",
                    filetypes=filetypes,
                    initialdir=initialdir
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
        
        # Универсальная проверка на уже запущенный Cursor (для всех ОС)
        if self._is_cursor_already_running_with_project(project_path):
            print(f"Cursor уже запущен с проектом: {project_path}")
            return True
        
        try:
            # Адаптируем команду запуска под ОС
            if self.os_type == 'windows':
                return self._launch_cursor_windows(cursor_exe, project_path)
            elif self.os_type == 'linux':
                return self._launch_cursor_linux(cursor_exe, project_path)
            elif self.os_type == 'darwin':  # macOS
                return self._launch_cursor_macos(cursor_exe, project_path)
            else:
                # Универсальный запуск
                return self._launch_cursor_generic(cursor_exe, project_path)
        except Exception as e:
            print(f"Ошибка запуска Cursor: {e}")
            return False
    
    def _launch_cursor_windows(self, cursor_exe, project_path):
        """Запуск Cursor в Windows"""
        try:
            if cursor_exe in ["cursor", "code"]:
                # Команды в PATH
                subprocess.Popen([cursor_exe, str(project_path)], shell=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cursor_exe.endswith('.lnk'):
                # Для .lnk файлов используем start
                subprocess.Popen(['start', cursor_exe, str(project_path)], shell=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Прямой путь к .exe
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"Cursor AI запущен (Windows): {cursor_exe}")
            return True
        except Exception as e:
            print(f"Ошибка запуска Cursor в Windows: {e}")
            return False
    
    def _launch_cursor_linux(self, cursor_exe, project_path):
        """Запуск Cursor в Linux"""
        try:
            if cursor_exe in ["cursor", "code"]:
                # Команды в PATH
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cursor_exe.endswith('.AppImage'):
                # AppImage файлы
                # Делаем AppImage исполняемым если нужно
                os.chmod(cursor_exe, 0o755)
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif '/snap/' in cursor_exe:
                # Snap пакет
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif '/flatpak/' in cursor_exe:
                # Flatpak
                subprocess.Popen(['flatpak', 'run', 'com.cursor.Cursor', str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Обычный исполняемый файл
                # Делаем файл исполняемым если нужно
                try:
                    os.chmod(cursor_exe, 0o755)
                except:
                    pass
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"Cursor AI запущен (Linux): {cursor_exe}")
            return True
        except Exception as e:
            print(f"Ошибка запуска Cursor в Linux: {e}")
            return False
    
    def _is_cursor_already_running_with_project(self, project_path):
        """Проверяет, запущен ли уже Cursor с данным проектом"""
        try:
            project_name = str(project_path).split('/')[-1] if '/' in str(project_path) else str(project_path).split('\\')[-1]
            project_full_path = str(project_path)
            
            if self.os_type == 'windows':
                # Для Windows используем tasklist
                try:
                    result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                                          capture_output=True, text=True, timeout=5,
                                          encoding='utf-8', errors='ignore')
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'cursor' in line.lower() or 'Cursor' in line:
                                # Дополнительная проверка через wmic для получения командной строки
                                try:
                                    wmic_result = subprocess.run(['wmic', 'process', 'where', 
                                                                f'name="Cursor.exe"', 'get', 'CommandLine'], 
                                                               capture_output=True, text=True, timeout=3,
                                                               encoding='utf-8', errors='ignore')
                                    if project_name in wmic_result.stdout or project_full_path in wmic_result.stdout:
                                        print(f"Найден запущенный Cursor с проектом: {project_name}")
                                        return True
                                except:
                                    pass
                except:
                    pass
                    
            elif self.os_type == 'linux':
                # Для Linux используем ps
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5,
                                       encoding='utf-8', errors='ignore')
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    cursor_processes = []
                    for line in lines:
                        if 'cursor' in line.lower() or 'Cursor' in line:
                            cursor_processes.append(line)
                    
                    # Проверяем каждый процесс Cursor
                    for process_line in cursor_processes:
                        # Проверяем по имени папки или полному пути
                        if project_name in process_line or project_full_path in process_line:
                            print(f"Найден запущенный Cursor с проектом: {project_name}")
                            return True
                    
                    # Дополнительная проверка через pgrep если доступен
                    try:
                        pgrep_result = subprocess.run(['pgrep', '-f', f'cursor.*{project_name}'], 
                                                    capture_output=True, text=True, timeout=3,
                                                    encoding='utf-8', errors='ignore')
                        if pgrep_result.returncode == 0 and pgrep_result.stdout.strip():
                            print(f"pgrep нашел Cursor с проектом: {project_name}")
                            return True
                    except:
                        pass
                        
            elif self.os_type == 'darwin':  # macOS
                # Для macOS используем ps
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5,
                                       encoding='utf-8', errors='ignore')
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'cursor' in line.lower() or 'Cursor' in line:
                            if project_name in line or project_full_path in line:
                                print(f"Найден запущенный Cursor с проектом: {project_name}")
                                return True
                    
            return False
        except Exception as e:
            print(f"Ошибка проверки процессов: {e}")
            return False
    
    def _launch_cursor_macos(self, cursor_exe, project_path):
        """Запуск Cursor в macOS"""
        try:
            if cursor_exe in ["cursor", "code"]:
                # Команды в PATH
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif '.app' in cursor_exe:
                # macOS приложение
                subprocess.Popen(['open', '-a', cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Обычный исполняемый файл
                subprocess.Popen([cursor_exe, str(project_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"Cursor AI запущен (macOS): {cursor_exe}")
            return True
        except Exception as e:
            print(f"Ошибка запуска Cursor в macOS: {e}")
            return False
    
    def _launch_cursor_generic(self, cursor_exe, project_path):
        """Универсальный запуск Cursor"""
        try:
            subprocess.Popen([cursor_exe, str(project_path)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Cursor AI запущен (generic): {cursor_exe}")
            return True
        except Exception as e:
            print(f"Ошибка универсального запуска Cursor: {e}")
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
        if PYAUTOGUI_AVAILABLE:
            try:
                time.sleep(delay_seconds)
                pyautogui.hotkey('ctrl', 'v')
            except Exception as e:
                print(f"Ошибка автовставки: {e}")
        else:
            print("Автовставка промптов отключена из-за отсутствия pyautogui")
    
    def create_project_structure(self, domain, desktop_path=None, theme=None, progress_callback=None, generate_images=False):
        """
        Создает структуру папок проекта и генерирует тематические изображения
        
        Args:
            domain (str): Название домена
            desktop_path (Path): Путь к директории для создания проекта (опционально)
            theme (str): Тематика для генерации изображений (опционально)
            progress_callback (callable): Функция обратного вызова для обновления прогресса
            generate_images (bool): Генерировать ли изображения (по умолчанию False)
            
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
            progress_callback("📁 Создание папок проекта...")
        
        project_path.mkdir(exist_ok=True)
        media_path.mkdir(exist_ok=True)
        
        # Генерация тематических изображений
        if theme and IMAGE_GENERATION_AVAILABLE and generate_images:
            try:
                if progress_callback:
                    progress_callback("🎨 Запуск генерации изображений...")
                
                # Создаем генератор в тихом режиме 
                from generators.image_generator import ImageGenerator
                image_generator = ImageGenerator(silent_mode=True)
                
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
        
        elif theme and not IMAGE_GENERATION_AVAILABLE and generate_images:
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