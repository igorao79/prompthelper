# -*- coding: utf-8 -*-

"""
Модуль для работы с Cursor AI
Кроссплатформенная версия (Windows/Linux/macOS)

Переменные окружения для настройки:
- CURSOR_CHAT_TEMPLATE: путь к изображению-шаблону области чата
- CURSOR_CHAT_CONFIDENCE: уровень уверенности для поиска шаблона (0.1-1.0, по умолчанию 0.8)
- CURSOR_LAUNCH_INTERVAL_SEC: интервал между запусками Cursor (по умолчанию 3.0)
- CURSOR_HWND_CLICK: использовать клик через hwnd (по умолчанию 1)

Для максимальной надежности в EXE режиме устанавливайте:
- CURSOR_CHAT_CONFIDENCE=0.7 (менее строгий поиск)
- CURSOR_HWND_CLICK=1 (прямой клик через окно)
"""

import os
import subprocess
import time
import platform
import ctypes
import threading
from ctypes import wintypes
from pathlib import Path
from typing import Optional
tk = None  # Tkinter больше не используется

# Включаем DPI-осведомленность процесса (важно для корректных координат в EXE)
if platform.system().lower() == 'windows':
    try:
        # PER_MONITOR_AWARE_V2 (лучше для мульти-DPI); может отсутствовать на ранних версиях
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            # Per-Monitor DPI Awareness (Win8.1+)
            shcore = ctypes.windll.shcore
            shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # System DPI Awareness (fallback)
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

# Проверяем доступность pyautogui
try:
    import pyautogui
    try:
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
    except Exception:
        pass
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui недоступен, автовставка промптов отключена")

# UI Automation (опционально)
try:
    import uiautomation as auto  # type: ignore
    UIA_AVAILABLE = True
except Exception:
    UIA_AVAILABLE = False

# Опциональные зависимости для поиска по скриншоту
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False
try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Импорт для генерации изображений (Ideogram)
try:
    from generators.ideogram_generator import IdeogramGenerator
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
        self._preferred_window_hint = None  # подсказка для выбора нужного окна Cursor
        # Троттлинг между запусками окон Cursor
        try:
            self._launch_interval_sec = float(os.getenv("CURSOR_LAUNCH_INTERVAL_SEC", "3.0"))
        except Exception:
            self._launch_interval_sec = 3.0
        self._launch_lock = threading.Lock()
        self._last_launch_monotonic = 0.0
        
        # Проверяем, запущен ли как EXE
        self._is_exe = self._detect_exe_mode()
        if self._is_exe:
            print("🔧 Обнаружен запуск через EXE - активирована улучшенная совместимость")
        
        print(f"🖥️ Определена ОС: {self.os_type}")
        
        # Генерируем пути поиска в зависимости от ОС
        self.search_paths = self._get_platform_search_paths()

    def _detect_exe_mode(self) -> bool:
        """
        Определяет, запущено ли приложение как EXE файл.
        Это помогает настроить дополнительные параметры для лучшей совместимости.
        """
        try:
            import sys
            # Проверяем несколько признаков EXE:
            # 1. sys.frozen (PyInstaller, cx_Freeze)
            # 2. sys.executable заканчивается на .exe
            # 3. __file__ не определен или путь к .exe
            
            is_frozen = getattr(sys, 'frozen', False)
            if is_frozen:
                return True
                
            if sys.executable.lower().endswith('.exe') and 'python' not in sys.executable.lower():
                return True
                
            # Проверяем __main__ модуль
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, '__file__'):
                main_file = main_module.__file__
                if main_file and main_file.lower().endswith('.exe'):
                    return True
            
            return False
        except Exception:
            return False

    def set_window_hint(self, hint: str | None):
        try:
            self._preferred_window_hint = (hint or "").strip().lower() or None
        except Exception:
            self._preferred_window_hint = None

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
        # Tkinter диалоги удалены; возвращаем None без запроса
        return None
    
    def open_cursor_with_project(self, project_path):
        """
        Открывает Cursor AI с указанным проектом
        
        Args:
            project_path (Path): Путь к проекту
            
        Returns:
            bool: True если успешно, False иначе
        """
        # Троттлинг перед запуском нового окна Cursor
        self._throttle_before_launch()

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
                # Для Windows используем tasklist, но без появления консольных окон
                try:
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    creationflags = 0x08000000  # CREATE_NO_WINDOW
                    result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                                          capture_output=True, text=True, timeout=5,
                                          encoding='utf-8', errors='ignore', startupinfo=si, creationflags=creationflags)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'cursor' in line.lower() or 'Cursor' in line:
                                # Дополнительная проверка через wmic для получения командной строки
                                try:
                                    wmic_result = subprocess.run(['wmic', 'process', 'where', 
                                                                f'name="Cursor.exe"', 'get', 'CommandLine'], 
                                                               capture_output=True, text=True, timeout=3,
                                                               encoding='utf-8', errors='ignore', startupinfo=si, creationflags=creationflags)
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
        """Копирует текст в буфер обмена (Tkinter/Qt/pyperclip/OS clip)."""
        # 1) Если передан Tk root
        try:
            if root_widget is not None:
                root_widget.clipboard_clear()
                root_widget.clipboard_append(text)
                root_widget.update()
                return True
        except Exception:
            pass

        # 2) Пытаемся через Qt (PySide6)
        try:
            from PySide6 import QtWidgets  # type: ignore
            cb = QtWidgets.QApplication.clipboard()
            if cb is not None:
                cb.setText(text)
                return True
        except Exception:
            pass

        # 3) Пытаемся через pyperclip
        try:
            import pyperclip  # type: ignore
            pyperclip.copy(text)
            return True
        except Exception:
            pass

        # 4) Windows: clip
        try:
            if platform.system().lower() == 'windows':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = 0x08000000  # CREATE_NO_WINDOW
                p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True, startupinfo=si, creationflags=creationflags)
                if p.stdin:
                    p.stdin.write(text.encode('utf-8'))
                    p.stdin.close()
                return True
        except Exception:
            pass

        return False
    
    def auto_paste_prompt(self, delay_seconds=5):
        """
        Автоматически вставляет промпт в Cursor AI
        
        Args:
            delay_seconds (int): Задержка перед вставкой
        """
        if PYAUTOGUI_AVAILABLE:
            try:
                # Запоминаем текущую позицию курсора, чтобы вернуть её после автоматизации
                try:
                    original_pos = pyautogui.position()
                except Exception:
                    original_pos = None
                # Пытаемся вывести окно Cursor на передний план перед вставкой
                hwnd = self._bring_cursor_window_to_front()
                # Гарантируем разворачивание и активность окна перед действиями
                try:
                    self._ensure_window_active(hwnd, timeout_s=max(1.0, float(os.getenv('CURSOR_ACTIVATE_TIMEOUT', '2.0'))))
                except Exception:
                    pass
                # Даём окну прогрузиться перед вставкой
                try:
                    env_delay = int(os.getenv('CURSOR_PASTE_DELAY_SEC', str(delay_seconds)))
                except Exception:
                    env_delay = delay_seconds
                time.sleep(max(0, env_delay))
                # Небольшая стабилизационная пауза после фокуса окна
                time.sleep(0.25)
                # Нормализуем позицию/размер, если включено
                try:
                    if isinstance(hwnd, int) and hwnd != 0:
                        self._normalize_window_rect(hwnd)
                except Exception:
                    pass
                # Сначала пробуем найти плейсхолдер чата и кликнуть по нему (точный таргет)
                focused = False
                try:
                    if isinstance(hwnd, int) and hwnd != 0:
                        focused = self._focus_chat_by_placeholder(hwnd)
                except Exception:
                    focused = False
                # Если не удалось — пробуем сфокусировать поле ввода через UIA по типу Edit
                if not focused:
                    try:
                        if isinstance(hwnd, int) and hwnd != 0:
                            focused = self._focus_chat_via_uia(hwnd)
                    except Exception:
                        focused = False
                # Если удалось сфокусировать через UIA и доступны методы ввода — сразу вставляем через UIA
                if focused and UIA_AVAILABLE:
                    try:
                        # Попытка найти активный Edit и вставить напрямую через ValuePattern
                        w = auto.ControlFromHandle(hwnd)
                        if w:
                            edit = None
                            edits = w.GetDescendants(controlType=auto.ControlType.Edit)
                            for ed in edits[::-1]:
                                try:
                                    if ed.IsEnabled and ed.IsOffscreen is False:
                                        edit = ed
                                        break
                                except Exception:
                                    continue
                            if edit:
                                # Текст для вставки берём из буфера, т.к. сюда попадает актуальный промпт (загружается в вызывающем коде)
                                # Если нужно вставить из параметра — можно переделать сигнатуру и хранить буфер в self.
                                try:
                                    # Попытаемся прочитать из буфера и вставить
                                    import pyperclip  # type: ignore
                                    text = pyperclip.paste()
                                except Exception:
                                    text = None
                                if text:
                                    try:
                                        vp = edit.GetValuePattern()
                                        if vp is not None:
                                            try:
                                                # Очищаем и устанавливаем значения
                                                vp.SetValue("")
                                                time.sleep(0.02)
                                                vp.SetValue(text)
                                            except Exception:
                                                # Фолбек через SendKeys к активному Edit
                                                auto.SendKeys("^a")
                                                time.sleep(0.02)
                                                auto.SendKeys(text)
                                        else:
                                            # Если ValuePattern нет, пробуем SendKeys
                                            auto.SendKeys("^a")
                                            time.sleep(0.02)
                                            auto.SendKeys(text)
                                        # Enter при необходимости
                                        try:
                                            if os.getenv('CURSOR_SEND_ENTER', '1') == '1':
                                                auto.SendKeys("{ENTER}")
                                        except Exception:
                                            pass
                                        return True
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                # Если не вышло — кликаем внутрь
                if not focused:
                    try:
                        if os.getenv('CURSOR_CLICK_FOCUS', '1') == '1':
                            if isinstance(hwnd, int) and hwnd != 0:
                                self._click_input_area(hwnd)
                    except Exception:
                        pass
                # Задержка перед вставкой уже выполнена выше; просто вставляем
                # Вставка через буфер обмена
                                # Задержка перед вставкой уже выполнена выше; просто вставляем
                # Вставка через буфер обмена
                try:
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.02)
                    if os.getenv('CURSOR_SEND_ENTER', '1') == '1':
                        pyautogui.press('enter')
                except Exception:
                    time.sleep(0.1)
                # Возвращаем курсор
                try:
                    if original_pos is not None:
                        pyautogui.moveTo(original_pos.x, original_pos.y, duration=0)
                except Exception:
                    pass
                return True
            except Exception:
                return False
        else:
            print("Автовставка промптов отключена из-за отсутствия pyautogui")
    
    def create_project_structure(self, domain, desktop_path=None, theme=None, progress_callback=None, generate_images=False, cancel_check=None):
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

                # Параллельная генерация (ускорение): число воркеров из env IDEOGRAM_CONCURRENCY (по умолчанию 3)
                try:
                    concurrency = max(1, int(os.getenv("IDEOGRAM_CONCURRENCY", "3")))
                except Exception:
                    concurrency = 3

                from concurrent.futures import ThreadPoolExecutor, as_completed

                def _gen_one(name: str, prompt_text: str):
                    if cancel_check and cancel_check():
                        return
                    return ideogram.generate_single_image(prompt_text, name, str(media_path), progress_callback)

                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    futures = [pool.submit(_gen_one, name, pr) for name, pr in tasks]
                    for _ in as_completed(futures):
                        pass
                
                # Подсчитываем успешные генерации
                try:
                    files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.png"))
                    successful_count = len(files)
                except Exception:
                    successful_count = 0
                
                if progress_callback:
                    progress_callback(f"✅ Генерация изображений завершена: {successful_count}/8")
                
                print(f"🎨 Сгенерировано {successful_count}/8 тематических изображений (Ideogram)")
                
            except Exception as e:
                error_msg = f"Ошибка генерации изображений: {str(e)}"
                print(f"⚠️ {error_msg}")
                if progress_callback:
                    progress_callback(f"⚠️ {error_msg}")
        
        elif theme and not IMAGE_GENERATION_AVAILABLE and generate_images:
            if progress_callback:
                progress_callback("⚠️ Модуль генерации изображений недоступен")
        elif theme and not generate_images:
            if progress_callback:
                progress_callback("📁 Создание проекта без изображений")
        
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
        # Копируем в буфер обмена (кросс-фреймворк)
        self.copy_to_clipboard(prompt, root_widget)
        
        # Пытаемся открыть Cursor
        if self.open_cursor_with_project(project_path):
            if auto_paste:
                # Автоматическая вставка с улучшенной надежностью для EXE
                try:
                    # Переводим окно Cursor на передний план
                    self._bring_cursor_window_to_front()
                    print(f"🔄 Ожидание загрузки курсора {paste_delay} секунд...")
                    time.sleep(max(5, paste_delay))  # Минимум 5 секунд ожидания
                    
                    # Создаем шаблон области чата если его нет (для будущих запусков)
                    self.create_chat_template_if_needed()
                    
                    if PYAUTOGUI_AVAILABLE:
                        # Специальные настройки для EXE режима
                        if self._is_exe:
                            print("🔧 Применяем специальные настройки для EXE")
                            pyautogui.PAUSE = 0.5  # Увеличиваем паузы между действиями
                            pyautogui.FAILSAFE = False  # Отключаем failsafe для надежности
                        
                        # Находим и кликаем по области чата для надежности
                        self._click_on_chat_area()
                        time.sleep(1.5 if self._is_exe else 1)
                        
                        # Несколько попыток вставки для надежности
                        max_attempts = 5 if self._is_exe else 3
                        for attempt in range(max_attempts):
                            try:
                                print(f"🔄 Попытка вставки #{attempt + 1}")
                                
                                # Дополнительная проверка фокуса для EXE
                                if self._is_exe and attempt > 0:
                                    self._click_on_chat_area()
                                    time.sleep(0.5)
                                
                                pyautogui.hotkey('ctrl', 'a')  # Выделяем все (если что-то есть)
                                time.sleep(0.3 if self._is_exe else 0.2)
                                pyautogui.hotkey('ctrl', 'v')  # Вставляем
                                time.sleep(0.8 if self._is_exe else 0.5)
                                pyautogui.press('enter')  # Отправляем
                                print("✅ Промпт вставлен успешно")
                                break
                            except Exception as e:
                                print(f"⚠️ Ошибка попытки {attempt + 1}: {e}")
                                if attempt < max_attempts - 1:  # Не последняя попытка
                                    time.sleep(2 if self._is_exe else 1)
                                else:
                                    # Последняя попытка - пробуем альтернативный метод
                                    if self._is_exe:
                                        print("🔄 Пробуем альтернативный метод вставки для EXE...")
                                        self._paste_using_alternative_method()
                                    else:
                                        raise e
                    else:
                        print("⚠️ pyautogui недоступен, автовставка невозможна")
                except Exception as e:
                    print(f"❌ Ошибка автовставки: {e}")
            
            return True, "Cursor AI запущен успешно"
        else:
            return False, "Cursor AI не найден. Промпт скопирован в буфер обмена"

    # ===== Windows helpers =====
    def _bring_cursor_window_to_front(self) -> int | bool:
        """Выводит окно Cursor на передний план (Windows). Возвращает hwnd при успехе или False."""
        try:
            if platform.system().lower() != 'windows':
                return False

            user32 = ctypes.windll.user32

            EnumWindows = user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            IsWindowVisible = user32.IsWindowVisible
            GetWindowTextLengthW = user32.GetWindowTextLengthW
            GetWindowTextW = user32.GetWindowTextW
            SetForegroundWindow = user32.SetForegroundWindow
            ShowWindow = user32.ShowWindow
            SetWindowPos = user32.SetWindowPos
            GetWindowRect = user32.GetWindowRect
            IsIconic = user32.IsIconic

            SW_SHOW = 5
            SW_RESTORE = 9
            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002

            target_hwnd = 0
            fallback_hwnd = 0
            preferred = (self._preferred_window_hint or "").lower()

            def enum_proc(hwnd, lParam):
                try:
                    if not IsWindowVisible(hwnd):
                        return True
                    length = GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return True
                    buf = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value or ""
                    tl = title.lower()
                    if 'cursor' in tl:
                        nonlocal target_hwnd
                        nonlocal fallback_hwnd
                        # Сохраняем первое встреченное как запасной вариант
                        if not fallback_hwnd:
                            fallback_hwnd = int(hwnd)
                        # Если есть подсказка и она содержится в заголовке — это наш кандидат
                        if preferred and preferred in tl:
                            target_hwnd = int(hwnd)
                            return False  # нашли лучший матч
                except Exception:
                    return True
                return True

            EnumWindows(EnumWindowsProc(enum_proc), 0)

            if not target_hwnd:
                target_hwnd = fallback_hwnd
            if not target_hwnd:
                return False

            # Восстановить из свернутого состояния, показать и поднять над всеми
            if IsIconic(target_hwnd):
                ShowWindow(target_hwnd, SW_RESTORE)
            else:
                ShowWindow(target_hwnd, SW_SHOW)
            SetWindowPos(target_hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            SetWindowPos(target_hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            SetForegroundWindow(target_hwnd)
            return target_hwnd
        except Exception as e:
            try:
                print(f"Ошибка активации окна Cursor: {e}")
            except Exception:
                pass
            return False

    def _paste_using_alternative_method(self) -> bool:
        """
        Альтернативный метод вставки текста для EXE режима.
        Использует посимвольный ввод и различные методы активации окна.
        """
        try:
            print("🔧 Альтернативный метод: посимвольная вставка")
            
            # Получаем текст из буфера обмена
            if self.os_type == 'windows':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    text = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                except ImportError:
                    # Используем tkinter если win32clipboard недоступен
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        root.withdraw()
                        text = root.clipboard_get()
                        root.destroy()
                    except Exception:
                        print("❌ Не удалось получить текст из буфера обмена")
                        return False
            else:
                return False  # Пока только для Windows
            
            if not text:
                print("❌ Буфер обмена пуст")
                return False
            
            # Дополнительное ожидание и активация
            time.sleep(2)
            self._bring_cursor_window_to_front()
            time.sleep(1)
            
            # Очищаем поле и вводим текст посимвольно
            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.press('delete')
                time.sleep(0.5)
                
                # Печатаем текст небольшими частями для надежности
                chunk_size = 50
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i+chunk_size]
                    pyautogui.write(chunk, interval=0.01)
                    time.sleep(0.1)
                
                time.sleep(1)
                pyautogui.press('enter')
                print("✅ Альтернативная вставка выполнена")
                return True
            
            return False
        except Exception as e:
            print(f"❌ Ошибка альтернативной вставки: {e}")
            return False

    def _click_on_chat_area(self) -> bool:
        """
        100% надежный поиск и клик по области чата Cursor.
        Использует множество методов для гарантированного попадания.
        """
        try:
            # Находим активное окно Cursor
            hwnd = self._bring_cursor_window_to_front()
            if not hwnd:
                print("⚠️ Не удалось найти окно Cursor для клика по чату")
                return False
            
            print("🎯 Начинаем поиск области чата...")
            
            # Метод 1: Поиск по тексту "Plan, search, build anything"
            chat_pos = self._find_chat_by_text(hwnd)
            if chat_pos:
                print("✅ Найдена область чата по тексту!")
                return self._click_at_position(hwnd, chat_pos[0], chat_pos[1])
            
            # Метод 2: OCR поиск текста в интерфейсе
            chat_pos = self._find_chat_by_ocr(hwnd)
            if chat_pos:
                print("✅ Найдена область чата через OCR!")
                return self._click_at_position(hwnd, chat_pos[0], chat_pos[1])
            
            # Метод 3: Поиск по изображению шаблона
            chat_pos = self._find_chat_by_template(hwnd)
            if chat_pos:
                print("✅ Найдена область чата по шаблону!")
                return self._click_at_position(hwnd, chat_pos[0], chat_pos[1])
            
            # Метод 4: Умный расчет координат (нижняя центральная область)
            chat_pos = self._calculate_chat_coordinates(hwnd)
            if chat_pos:
                print("✅ Используем расчетные координаты области чата!")
                return self._click_at_position(hwnd, chat_pos[0], chat_pos[1])
            
            # Метод 5: Запасной - используем старую функцию
            print("🔄 Используем запасной метод...")
            success = self._click_input_area(hwnd)
            if success:
                print("✅ Клик по области чата выполнен (запасной метод)")
            else:
                print("⚠️ Все методы поиска области чата не сработали")
            return success
            
        except Exception as e:
            print(f"❌ Ошибка при клике по области чата: {e}")
            return False

    def _find_chat_by_text(self, hwnd: int) -> tuple[int, int] | None:
        """
        Поиск области чата по тексту 'Plan, search, build anything' через UI Automation
        """
        try:
            if not UIA_AVAILABLE:
                return None
                
            import uiautomation as auto
            
            # Получаем окно Cursor
            window = auto.ControlFromHandle(hwnd)
            if not window:
                return None
            
            # Ищем текст-подсказки в области чата
            search_texts = [
                "Plan, search, build anything",
                "Plan, search",
                "build anything", 
                "Ask Cursor",
                "Type a message",
                "Message Cursor"
            ]
            
            for search_text in search_texts:
                # Ищем элементы с данным текстом
                text_controls = window.GetChildren()
                for control in text_controls:
                    try:
                        if hasattr(control, 'Name') and search_text.lower() in control.Name.lower():
                            rect = control.BoundingRectangle
                            if rect.width() > 0 and rect.height() > 0:
                                # Возвращаем центр найденного элемента
                                center_x = rect.left + rect.width() // 2
                                center_y = rect.top + rect.height() // 2
                                print(f"📍 Найден текст '{search_text}' в ({center_x}, {center_y})")
                                return (center_x, center_y)
                    except Exception:
                        continue
            
            return None
        except Exception as e:
            print(f"⚠️ Ошибка поиска по тексту: {e}")
            return None

    def _find_chat_by_ocr(self, hwnd: int) -> tuple[int, int] | None:
        """
        Поиск области чата через OCR (распознавание текста на скриншоте)
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return None
                
            # Делаем скриншот окна
            user32 = ctypes.windll.user32
            rect = ctypes.wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return None
                
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            
            # Скриншот области окна
            screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
            
            # Пытаемся использовать pytesseract если доступен
            try:
                import pytesseract
                text = pytesseract.image_to_string(screenshot)
                
                # Ищем ключевые фразы
                target_phrases = [
                    "plan, search, build anything",
                    "plan search build",
                    "ask cursor",
                    "message cursor"
                ]
                
                text_lower = text.lower()
                for phrase in target_phrases:
                    if phrase in text_lower:
                        # Грубая оценка - возвращаем нижнюю центральную область
                        chat_x = left + (right - left) // 2
                        chat_y = bottom - 100  # Примерно область ввода
                        print(f"📍 OCR нашел '{phrase}' -> ({chat_x}, {chat_y})")
                        return (chat_x, chat_y)
                        
            except ImportError:
                print("⚠️ pytesseract недоступен для OCR")
            
            return None
        except Exception as e:
            print(f"⚠️ Ошибка OCR поиска: {e}")
            return None

    def _find_chat_by_template(self, hwnd: int) -> tuple[int, int] | None:
        """
        Улучшенный поиск области чата по шаблону изображения
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return None
                
            user32 = ctypes.windll.user32
            rect = ctypes.wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return None
                
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            
            # Проверяем несколько возможных шаблонов
            template_paths = [
                os.getenv('CURSOR_CHAT_TEMPLATE'),
                'cursor_chat_template.png',
                'chat_area.png',
                'input_field.png'
            ]
            
            for template_path in template_paths:
                if not template_path or not os.path.exists(template_path):
                    continue
                    
                try:
                    # Ищем шаблон в области окна
                    region = (left, top, right - left, bottom - top)
                    found = pyautogui.locateOnScreen(
                        template_path, 
                        region=region, 
                        confidence=0.7
                    )
                    
                    if found:
                        center = pyautogui.center(found)
                        print(f"📍 Найден шаблон '{template_path}' -> ({center.x}, {center.y})")
                        return (center.x, center.y)
                        
                except Exception:
                    continue
            
            return None
        except Exception as e:
            print(f"⚠️ Ошибка поиска по шаблону: {e}")
            return None

    def _calculate_chat_coordinates(self, hwnd: int) -> tuple[int, int] | None:
        """
        Умный расчет координат области чата на основе размеров окна
        """
        try:
            user32 = ctypes.windll.user32
            rect = ctypes.wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return None
                
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            
            # Проверяем, что окно видимое и нормального размера
            if left <= -32000 or top <= -32000 or (right - left) < 100 or (bottom - top) < 100:
                return None
            
            width = right - left
            height = bottom - top
            
            # Умный расчет позиции области чата
            # Обычно чат находится в нижней части окна, по центру
            
            # Различные стратегии в зависимости от размера окна
            if width > 1200:  # Широкое окно
                chat_x = left + width // 2  # Центр по горизонтали
                chat_y = bottom - 80  # 80 пикселей от низа
            elif width > 800:  # Среднее окно
                chat_x = left + width // 2
                chat_y = bottom - 60
            else:  # Узкое окно
                chat_x = left + width // 2
                chat_y = bottom - 40
            
            # Дополнительные проверки и корректировки
            # Убеждаемся, что координаты в пределах окна
            if chat_x < left + 50:
                chat_x = left + 50
            elif chat_x > right - 50:
                chat_x = right - 50
                
            if chat_y < top + 100:
                chat_y = top + height // 2
            elif chat_y > bottom - 20:
                chat_y = bottom - 30
            
            print(f"📍 Расчетные координаты чата: ({chat_x}, {chat_y}) для окна {width}x{height}")
            return (chat_x, chat_y)
            
        except Exception as e:
            print(f"⚠️ Ошибка расчета координат: {e}")
            return None

    def _click_at_position(self, hwnd: int, x: int, y: int) -> bool:
        """
        Универсальная функция для клика в указанной позиции
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            # Дополнительная активация окна перед кликом
            self._bring_cursor_window_to_front()
            time.sleep(0.2)
            
            # Выполняем клик
            if self._is_exe:
                # Для EXE используем более надежный метод
                pyautogui.click(x, y)
                time.sleep(0.3)
                # Дублируем клик для надежности
                pyautogui.click(x, y)
            else:
                pyautogui.click(x, y)
            
            time.sleep(0.2)
            print(f"🎯 Клик выполнен в позиции ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка клика в позиции ({x}, {y}): {e}")
            return False

    def create_chat_template_if_needed(self) -> str | None:
        """
        Создает шаблон области чата для будущего поиска, если его еще нет.
        Возвращает путь к созданному шаблону или None.
        """
        try:
            template_path = 'cursor_chat_template.png'
            
            # Если шаблон уже существует, используем его
            if os.path.exists(template_path):
                return template_path
            
            print("📸 Создаем шаблон области чата...")
            
            # Находим окно Cursor
            hwnd = self._bring_cursor_window_to_front()
            if not hwnd:
                return None
            
            time.sleep(2)  # Ждем пока окно полностью загрузится
            
            if PYAUTOGUI_AVAILABLE:
                user32 = ctypes.windll.user32
                rect = ctypes.wintypes.RECT()
                if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    return None
                
                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
                
                # Создаем скриншот нижней части окна (где обычно чат)
                chat_height = min(150, (bottom - top) // 3)  # Нижние 150px или треть окна
                chat_region = (
                    left, 
                    bottom - chat_height, 
                    right - left, 
                    chat_height
                )
                
                screenshot = pyautogui.screenshot(region=chat_region)
                screenshot.save(template_path)
                
                print(f"✅ Шаблон области чата сохранен: {template_path}")
                return template_path
            
            return None
        except Exception as e:
            print(f"⚠️ Ошибка создания шаблона: {e}")
            return None

    def _click_input_area(self, hwnd: int) -> bool:
        """Делает клик по нижней части окна, чтобы сфокусировать поле ввода."""
        try:
            if platform.system().lower() != 'windows' or not hwnd:
                return False
            user32 = ctypes.windll.user32
            rect = ctypes.wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return False
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            # Если окно свернуто или вынесено за экран (типичный -32000), клики запрещаем
            if left <= -32000 or top <= -32000 or (right - left) < 100 or (bottom - top) < 100:
                return False
            # 1) Пытаемся найти область чата по шаблону, если указана картинка
            try:
                template_path = os.getenv('CURSOR_CHAT_TEMPLATE')
                if template_path:
                    # Сначала пробуем более устойчивый CV2 мульти-масштабный поиск внутри окна
                    pt = self._locate_in_window_by_template(hwnd, template_path, (left, top, right, bottom))
                    if pt is not None:
                        cx, cy = pt
                        if os.getenv('CURSOR_HWND_CLICK', '1') == '1':
                            self._send_click(hwnd, int(cx), int(cy))
                        elif PYAUTOGUI_AVAILABLE:
                            pyautogui.click(int(cx), int(cy))
                        time.sleep(0.05)
                        return True
                    # Фолбек: стандартный pyautogui.locateOnScreen по региону окна
                    if PYAUTOGUI_AVAILABLE:
                        region = (left, top, right - left, bottom - top)
                        found = pyautogui.locateOnScreen(template_path, region=region, confidence=float(os.getenv('CURSOR_CHAT_CONFIDENCE', '0.8')))
                        if found:
                            center = pyautogui.center(found)
                            if os.getenv('CURSOR_HWND_CLICK', '1') == '1':
                                self._send_click(hwnd, center.x, center.y)
                            else:
                                pyautogui.click(center.x, center.y)
                            time.sleep(0.05)
                            return True
            except Exception:
                pass
            try:
                # По умолчанию кликаем ближе к правой панели (чат справа)
                default_x = max(10, int(os.getenv('CURSOR_CLICK_OFFSET_X', '300')))
                # Если задан процент от ширины — используем его
                perc = os.getenv('CURSOR_CLICK_X_PERCENT')
                if perc is not None:
                    p = max(1, min(99, int(perc)))
                    off_x = int((right - left) * (p / 100.0))
                else:
                    off_x = (right - left) - default_x
            except Exception:
                off_x = (right - left) - 300
            try:
                off_y = max(10, int(os.getenv('CURSOR_CLICK_OFFSET_Y', '160')))
            except Exception:
                off_y = 160
            x = left + off_x
            y = bottom - off_y
            # Клик без перемещения курсора через WinAPI (по умолчанию)
            try:
                if os.getenv('CURSOR_HWND_CLICK', '1') == '1':
                    self._send_click(hwnd, x, y)
                    time.sleep(0.05)
                    return True
            except Exception:
                pass
            # Фолбек — обычный клик
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.click(x, y)
                    time.sleep(0.05)
                    return True
                except Exception:
                    return False
            return False
        except Exception:
            return False

    def _normalize_window_rect(self, hwnd: int) -> None:
        """Принудительно ставит окно Cursor в предсказуемое место/размер (по желанию)."""
        try:
            if platform.system().lower() != 'windows' or not hwnd:
                return
            # По умолчанию включено; можно отключить переменной окружения
            if os.getenv('CURSOR_FORCE_WINDOW_RECT', '1') == '0':
                return
            user32 = ctypes.windll.user32
            # Перед перемещением гарантируем разворачивание окна
            try:
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            except Exception:
                pass
            SM_CXSCREEN = 0
            SM_CYSCREEN = 1
            sw = user32.GetSystemMetrics(SM_CXSCREEN)
            sh = user32.GetSystemMetrics(SM_CYSCREEN)
            try:
                x = int(os.getenv('CURSOR_WIN_X', '80'))
                y = int(os.getenv('CURSOR_WIN_Y', '60'))
                w = int(os.getenv('CURSOR_WIN_W', str(int(sw * 0.6))))
                h = int(os.getenv('CURSOR_WIN_H', str(int(sh * 0.7))))
            except Exception:
                x, y, w, h = 80, 60, int(sw * 0.6), int(sh * 0.7)
            user32.MoveWindow(hwnd, x, y, w, h, True)
            time.sleep(0.05)
        except Exception:
            pass

    def _send_click(self, hwnd: int, screen_x: int, screen_y: int) -> None:
        """Отправляет WM_LBUTTONDOWN/UP по координатам окна без перемещения курсора."""
        user32 = ctypes.windll.user32
        pt_screen = ctypes.wintypes.POINT(screen_x, screen_y)
        # Определяем наиболее глубокое дочернее окно под точкой
        try:
            child_hwnd = user32.WindowFromPoint(pt_screen)
        except Exception:
            child_hwnd = 0
        target_hwnd = child_hwnd if child_hwnd else hwnd
        # Переводим координаты в клиентские координаты target_hwnd
        pt_client = ctypes.wintypes.POINT(screen_x, screen_y)
        try:
            user32.ScreenToClient(target_hwnd, ctypes.byref(pt_client))
        except Exception:
            # если не удалось — пробуем для главного окна
            try:
                user32.ScreenToClient(hwnd, ctypes.byref(pt_client))
                target_hwnd = hwnd
            except Exception:
                pt_client = ctypes.wintypes.POINT(0, 0)
                target_hwnd = hwnd
        x, y = pt_client.x, pt_client.y
        WM_LBUTTONDOWN = 0x0201
        WM_LBUTTONUP = 0x0202
        MK_LBUTTON = 0x0001
        lparam = (y << 16) | (x & 0xFFFF)
        try:
            user32.PostMessageW(target_hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
            time.sleep(0.02)
            user32.PostMessageW(target_hwnd, WM_LBUTTONUP, 0, lparam)
            return
        except Exception:
            pass
        # Фолбек: имитация клика через SendInput с возвратом курсора на место
        try:
            if os.getenv('CURSOR_FORCE_SENDINPUT', '1') == '1':
                self._send_click_via_sendinput(screen_x, screen_y)
        except Exception:
            pass

    def _send_click_via_sendinput(self, screen_x: int, screen_y: int) -> None:
        """Выполняет клик через SendInput по абсолютным координатам и возвращает курсор на место."""
        try:
            if platform.system().lower() != 'windows':
                return
            user32 = ctypes.windll.user32
            # Сохраняем позицию
            orig_pt = ctypes.wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(orig_pt))
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            # Преобразуем в абсолютные координаты (0..65535)
            abs_x = int(screen_x * 65535 / max(1, sw - 1))
            abs_y = int(screen_y * 65535 / max(1, sh - 1))

            class MOUSEINPUT(ctypes.Structure):
                _fields_ = (
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
                )

            class INPUT(ctypes.Structure):
                _fields_ = (("type", wintypes.DWORD), ("mi", MOUSEINPUT))

            MOUSEEVENTF_MOVE = 0x0001
            MOUSEEVENTF_ABSOLUTE = 0x8000
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004

            def send(mi: MOUSEINPUT):
                inp = INPUT(type=0, mi=mi)
                ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

            # Перемещаем, кликаем, возвращаем
            send(MOUSEINPUT(abs_x, abs_y, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, None))
            time.sleep(0.01)
            send(MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, None))
            time.sleep(0.01)
            send(MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, None))
            time.sleep(0.01)
            # Возврат курсора
            user32.SetCursorPos(orig_pt.x, orig_pt.y)
        except Exception:
            pass

    def _focus_chat_via_uia(self, hwnd: int) -> bool:
        """Пробует сфокусировать поле ввода чата через UI Automation (если доступно)."""
        try:
            if not UIA_AVAILABLE or platform.system().lower() != 'windows' or not hwnd:
                return False
            w = auto.ControlFromHandle(hwnd)
            if not w:
                return False
            # Ищем Edit в окне — предпочтительно в правой панели
            # Можно ограничить глубину; берём первый видимый активный Edit
            edits = w.GetDescendants(controlType=auto.ControlType.Edit)
            for ed in edits[::-1]:  # чаще нужный ниже по дереву
                try:
                    if ed.IsEnabled and ed.IsOffscreen is False:
                        # По имени можно фильтровать через env
                        name_hint = (os.getenv('CURSOR_EDIT_NAME_HINT', '') or '').strip().lower()
                        if name_hint and name_hint not in (ed.Name or '').lower():
                            continue
                        ed.SetFocus()
                        time.sleep(0.05)
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _focus_chat_by_placeholder(self, hwnd: int) -> bool:
        """Находит поле ввода по плейсхолдеру "Plan, search, build anything" и кликает по центру."""
        try:
            if not UIA_AVAILABLE or platform.system().lower() != 'windows' or not hwnd:
                return False
            w = auto.ControlFromHandle(hwnd)
            if not w:
                return False
            # Тексты-подсказки, по которым можно найти чат
            phints = [
                os.getenv('CURSOR_CHAT_PLACEHOLDER', 'Plan, search, build anything').strip(),
                'Plan, search, build anything',
            ]
            # Обход всех Text/Edit для поиска совпадений по Name/LegacyIAccessibleName/Value/HelpText
            candidates = w.GetDescendants()
            for c in candidates:
                try:
                    name = (c.Name or '').strip()
                    if not name and hasattr(c, 'LegacyIAccessiblePattern'):
                        try:
                            name = (c.LegacyIAccessiblePattern.Value or '').strip()
                        except Exception:
                            pass
                    if not name and hasattr(c, 'GetValuePattern'):
                        try:
                            vp = c.GetValuePattern()
                            if vp is not None:
                                name = (vp.Value or '').strip()
                        except Exception:
                            pass
                    if name:
                        for p in phints:
                            if p and p.lower() in name.lower():
                                try:
                                    rect = c.BoundingRectangle
                                    # BoundingRectangle: (l, t, r, b)
                                    l, t, r, b = int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)
                                    if r > l and b > t:
                                        cx = l + (r - l) // 2
                                        cy = t + (b - t) // 2
                                        if os.getenv('CURSOR_HWND_CLICK', '1') == '1':
                                            self._send_click(hwnd, cx, cy)
                                        elif PYAUTOGUI_AVAILABLE:
                                            pyautogui.click(cx, cy)
                                        time.sleep(0.05)
                                        return True
                                except Exception:
                                    continue
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _ensure_window_active(self, hwnd: int | bool, timeout_s: float = 2.0) -> bool:
        """Ждёт, пока окно будет развернуто и станет активным (Windows)."""
        try:
            if platform.system().lower() != 'windows' or not isinstance(hwnd, int) or hwnd == 0:
                return False
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            start = time.time()
            while time.time() - start < max(0.2, timeout_s):
                try:
                    # Если свернуто — разворачиваем
                    if user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                        time.sleep(0.05)
                    # Поднимаем с привязкой ввода потоков (повышает шанс сфокусировать)
                    try:
                        current_tid = kernel32.GetCurrentThreadId()
                        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
                        user32.AttachThreadInput(current_tid, target_tid, True)
                        user32.SetForegroundWindow(hwnd)
                        user32.AttachThreadInput(current_tid, target_tid, False)
                    except Exception:
                        user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                time.sleep(0.05)
                try:
                    fg = user32.GetForegroundWindow()
                    if int(fg) == int(hwnd):
                        return True
                except Exception:
                    pass
            return False
        except Exception:
            return False

    def _throttle_before_launch(self) -> None:
        """Обеспечивает паузу между запусками окон Cursor (по умолчанию 3 сек)."""
        try:
            with self._launch_lock:
                now = time.monotonic()
                elapsed = now - self._last_launch_monotonic
                wait_for = self._launch_interval_sec - elapsed
                if wait_for > 0:
                    time.sleep(wait_for)
                # фиксируем момент запуска, чтобы следующие ждали интервал
                self._last_launch_monotonic = time.monotonic()
                # Дополнительная пауза перед открытием следующего окна для стабильности загрузки UI
                try:
                    extra_gap = float(os.getenv('CURSOR_EXTRA_LAUNCH_GAP_SEC', '3.0'))
                except Exception:
                    extra_gap = 3.0
                if extra_gap > 0:
                    time.sleep(extra_gap)
        except Exception:
            pass

    def _locate_in_window_by_template(self, hwnd: int, template_path: str, rect_tuple: tuple[int, int, int, int]) -> tuple[int, int] | None:
        """Ищет шаблон внутри окна Cursor по скриншоту окна. Возвращает центр (screen_x, screen_y) или None.
        Использует OpenCV multi-scale matchTemplate при наличии, иначе None.
        """
        try:
            if not CV2_AVAILABLE:
                return None
            left, top, right, bottom = rect_tuple
            w = right - left
            h = bottom - top
            if w <= 0 or h <= 0:
                return None
            # Скриншот только области окна
            screen_img = self._screenshot_region(left, top, w, h)
            if screen_img is None:
                return None
            tpl = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if tpl is None:
                return None
            img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2RGB)
            conf = 0.8
            try:
                conf = float(os.getenv('CURSOR_CHAT_CONFIDENCE', '0.8'))
            except Exception:
                conf = 0.8
            # Масштабы можно задать через переменную окружения
            scales_env = os.getenv('CURSOR_CHAT_SCALES', '')
            scales = []
            if scales_env:
                try:
                    scales = [max(0.5, min(2.0, float(s.strip()))) for s in scales_env.split(',') if s.strip()]
                except Exception:
                    scales = []
            if not scales:
                scales = [0.75, 0.85, 1.0, 1.15, 1.25]
            best_val = -1.0
            best_pt = None
            th, tw = tpl.shape[:2]
            for s in scales:
                try:
                    tpl_s = cv2.resize(tpl, (max(1, int(tw * s)), max(1, int(th * s))), interpolation=cv2.INTER_AREA)
                    res = cv2.matchTemplate(img, tpl_s, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    if max_val > best_val:
                        best_val = max_val
                        best_pt = (max_loc[0] + tpl_s.shape[1] // 2, max_loc[1] + tpl_s.shape[0] // 2)
                except Exception:
                    continue
            if best_pt is not None and best_val >= conf:
                cx = left + int(best_pt[0])
                cy = top + int(best_pt[1])
                return cx, cy
            return None
        except Exception:
            return None

    def _screenshot_region(self, x: int, y: int, w: int, h: int):
        """Скриншот области экрана. Возвращает numpy array RGBA или None."""
        try:
            if PYAUTOGUI_AVAILABLE:
                im = pyautogui.screenshot(region=(x, y, w, h))
                return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2RGBA)
        except Exception:
            pass
        try:
            if PIL_AVAILABLE:
                from PIL import ImageGrab  # type: ignore
                im = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2RGBA)
        except Exception:
            pass
        return None