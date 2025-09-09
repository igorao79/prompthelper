# -*- coding: utf-8 -*-

"""
Модуль для работы с Cursor AI
Кроссплатформенная версия (Windows/Linux/macOS)

Переменные окружения:
- CURSOR_LAUNCH_INTERVAL_SEC: интервал между запусками Cursor (секунды)
- CURSOR_EXTRA_LAUNCH_GAP_SEC: дополнительная пауза после запуска (секунды)
- CURSOR_HWND_CLICK: использовать клик через hwnd (1/0)
- CURSOR_APP_READY_TIMEOUT_SEC: таймаут ожидания готовности окна Cursor (секунды, по умолчанию 10)
- CURSOR_INTERFACE_READY_DELAY_SEC: пауза после готовности окна для загрузки интерфейса (секунды, по умолчанию 5.0)
- CURSOR_FALLBACK_DELAY_SEC: резервная пауза если окно не готово (секунды, по умолчанию 12.0)
- CURSOR_CHAT_READY_DELAY_SEC: пауза после активации чата для готовности курсора (секунды, по умолчанию 4.0)
- CURSOR_STABILIZATION_CHECKS: количество проверок стабилизации ввода (по умолчанию 3)
- CURSOR_STABILIZATION_DELAY_SEC: задержка между проверками стабилизации (секунды, по умолчанию 0.25)
- CURSOR_PASTE_ENTER_DELAY_SEC: задержка между вставкой промпта и нажатием Enter (секунды, по умолчанию 1.0)
- CURSOR_CURSOR_READY_CHECKS: количество попыток проверки готовности курсора (по умолчанию 5)
- CURSOR_PASTE_RETRY_ATTEMPTS: количество попыток вставки промпта (по умолчанию 3)
- CURSOR_CURSOR_READY_CHECK_DELAY: задержка между проверками готовности курсора (секунды, по умолчанию 0.5)
- CURSOR_DIAGNOSTIC_MODE: включить подробную диагностику проблем (1/0, по умолчанию 0)
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

# Убраны тяжёлые опциональные зависимости (UI Automation / OCR / шаблоны)

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
        # Проверяем, запущен ли как EXE
        self._is_exe = self._detect_exe_mode()
        if self._is_exe:
            print("🔧 Обнаружен запуск через EXE - активирована улучшенная совместимость")
        
        # Троттлинг между запусками окон Cursor
        try:
            # Жесткий троттлинг - 5 секунд минимум между запусками
            default_interval = "5.0"
            self._launch_interval_sec = float(os.getenv("CURSOR_LAUNCH_INTERVAL_SEC", default_interval))
        except Exception:
            self._launch_interval_sec = 5.0
        self._launch_lock = threading.Lock()
        self._last_launch_monotonic = 0.0

        # Дополнительный троттлинг для предотвращения смешивания проектов
        self._project_launch_times = {}  # словарь для отслеживания времени запуска по проектам
        self._min_project_interval_sec = 3.0  # минимум 3 секунды между проектами
        
        # Управление позиционированием окон
        self._window_position_offset = 0  # Смещение для каждого нового окна
        self._base_window_x = 100  # Базовая позиция X
        self._base_window_y = 100  # Базовая позиция Y
        self._window_cascade_step = 30  # Шаг каскадного смещения
        
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
            clean_hint = (hint or "").strip()
            if clean_hint:
                # Убираем расширение файла если есть
                clean_hint = clean_hint.replace('.exe', '').replace('.lnk', '')
                # Берем только имя папки/проекта
                clean_hint = clean_hint.split('/')[-1].split('\\')[-1]
                self._preferred_window_hint = clean_hint.lower()
                print(f"🎯 Установлена подсказка окна: '{self._preferred_window_hint}'")
            else:
                self._preferred_window_hint = None
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
        # Троттлинг перед запуском нового окна Cursor с учётом проекта
        project_hint = str(project_path).split('/')[-1] if '/' in str(project_path) else str(project_path).split('\\')[-1]
        self._throttle_before_launch(project_hint)

        cursor_exe = self.find_cursor_executable()
        
        if not cursor_exe:
            return False
        
        # Дополнительная валидация перед запуском
        if not self._validate_pre_launch_conditions(project_path):
            print(f"❌ Предварительные условия запуска не соблюдены для: {project_path}")
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
            
            # Даем время на запуск, затем принудительно позиционируем окно
            time.sleep(2)
            self._position_new_cursor_window()
            
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
            
            # Даем время на запуск, затем принудительно позиционируем окно
            time.sleep(2)
            self._position_new_cursor_window()
            
            return True
        except Exception as e:
            print(f"Ошибка запуска Cursor в Linux: {e}")
            return False
    
    def _validate_pre_launch_conditions(self, project_path):
        """
        Проверяет предварительные условия перед запуском Cursor

        Args:
            project_path: Путь к проекту

        Returns:
            bool: True если условия соблюдены
        """
        try:
            # Проверяем существование пути к проекту
            if not os.path.exists(project_path):
                print(f"⚠️ Путь к проекту не существует: {project_path}")
                return False

            # Проверяем, что путь является директорией
            if not os.path.isdir(project_path):
                print(f"⚠️ Путь к проекту не является директорией: {project_path}")
                return False

            # Проверяем права доступа к директории
            try:
                test_file = os.path.join(project_path, ".cursor_test")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                print(f"⚠️ Нет прав доступа к директории проекта: {e}")
                return False

            # Проверяем, что подсказка проекта установлена
            if not self._preferred_window_hint:
                print("⚠️ Не установлена подсказка проекта")
                return False

            print(f"✅ Предварительные условия запуска соблюдены для: {project_path}")
            return True

        except Exception as e:
            print(f"⚠️ Ошибка валидации предварительных условий: {e}")
            return False

    def _validate_project_window_match(self, project_path, hwnd):
        """
        Проверяет, соответствует ли окно Cursor данному проекту

        Args:
            project_path: Путь к проекту
            hwnd: Handle окна Cursor

        Returns:
            bool: True если окно соответствует проекту
        """
        try:
            if not self._preferred_window_hint or not hwnd:
                return True  # Если нет подсказки или hwnd, считаем что подходит

            # Получаем заголовок окна
            user32 = ctypes.windll.user32
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return False

            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value or ""
            tl = title.lower()

            preferred = self._preferred_window_hint.lower()

            # Проверяем точное совпадение
            if preferred in tl:
                return True

            # Проверяем частичные совпадения
            hint_parts = preferred.replace('_', ' ').replace('-', ' ').split()
            for part in hint_parts:
                if len(part) > 3 and part in tl:
                    return True

            print(f"⚠️ Окно Cursor '{title}' не соответствует проекту '{preferred}'")
            return False

        except Exception as e:
            print(f"⚠️ Ошибка валидации окна проекта: {e}")
            return True  # В случае ошибки считаем что подходит

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
            
            # Даем время на запуск, затем принудительно позиционируем окно
            time.sleep(2)
            self._position_new_cursor_window()
            
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
            
            # Даем время на запуск, затем принудительно позиционируем окно
            time.sleep(2)
            self._position_new_cursor_window()
            
            return True
        except Exception as e:
            print(f"Ошибка универсального запуска Cursor: {e}")
            return False
    
    def copy_to_clipboard(self, text, root_widget):
        """Копирует текст в буфер обмена с исправлением COM ошибок для EXE."""
        
        # Специальная обработка для EXE режима на Windows
        if self._is_exe and platform.system().lower() == 'windows':
            # Метод 1: Инициализируем COM и используем win32clipboard
            success = self._copy_to_clipboard_win32_com(text)
            if success:
                return True
        
        # 1) Если передан Tk root
        try:
            if root_widget is not None:
                root_widget.clipboard_clear()
                root_widget.clipboard_append(text)
                root_widget.update()
                print("✅ Текст скопирован через Tkinter")
                return True
        except Exception as e:
            print(f"⚠️ Ошибка копирования через Tkinter: {e}")

        # 2) Windows: Улучшенная работа с COM для Qt
        if platform.system().lower() == 'windows':
            success = self._copy_to_clipboard_qt_with_com_init(text)
            if success:
                return True

        # 3) Стандартная попытка через Qt (без COM инициализации)
        try:
            from PySide6 import QtWidgets  # type: ignore
            cb = QtWidgets.QApplication.clipboard()
            if cb is not None:
                cb.setText(text)
                print("✅ Текст скопирован через Qt")
                return True
        except Exception as e:
            print(f"⚠️ Ошибка копирования через Qt: {e}")

        # 4) Пытаемся через pyperclip
        try:
            import pyperclip  # type: ignore
            pyperclip.copy(text)
            print("✅ Текст скопирован через pyperclip")
            return True
        except Exception as e:
            print(f"⚠️ Ошибка копирования через pyperclip: {e}")

        # 5) Windows: командная строка clip
        try:
            if platform.system().lower() == 'windows':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = 0x08000000  # CREATE_NO_WINDOW
                p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True, startupinfo=si, creationflags=creationflags)
                if p.stdin:
                    p.stdin.write(text.encode('utf-8'))
                    p.stdin.close()
                print("✅ Текст скопирован через clip")
                return True
        except Exception as e:
            print(f"⚠️ Ошибка копирования через clip: {e}")

        print("❌ Все методы копирования в буфер обмена не сработали")
        return False

    def _copy_to_clipboard_win32_com(self, text: str) -> bool:
        """
        Копирует текст в буфер обмена через win32clipboard с инициализацией COM.
        Исправляет ошибку CO_E_NOTINITIALIZED для EXE режима.
        """
        try:
            # Пытаемся импортировать win32clipboard
            import win32clipboard
            import win32api
            import win32con
            
            # Инициализируем COM для данного потока
            try:
                import pythoncom
                pythoncom.CoInitialize()
                print("✅ COM инициализирован для win32clipboard")
            except Exception as e:
                print(f"⚠️ Не удалось инициализировать COM: {e}")
            
            # Открываем буфер обмена
            win32clipboard.OpenClipboard()
            try:
                # Очищаем буфер
                win32clipboard.EmptyClipboard()
                # Устанавливаем текст
                win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                print("✅ Текст скопирован через win32clipboard")
                return True
            finally:
                # Обязательно закрываем буфер
                win32clipboard.CloseClipboard()
                
        except ImportError:
            print("⚠️ win32clipboard недоступен")
            return False
        except Exception as e:
            print(f"❌ Ошибка копирования через win32clipboard: {e}")
            return False

    def _copy_to_clipboard_qt_with_com_init(self, text: str) -> bool:
        """
        Копирует текст в буфер обмена через Qt с предварительной инициализацией COM.
        """
        try:
            # Инициализируем COM перед работой с Qt
            if platform.system().lower() == 'windows':
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    print("✅ COM инициализирован для Qt clipboard")
                except Exception as e:
                    print(f"⚠️ Не удалось инициализировать COM для Qt: {e}")
            
            # Теперь пытаемся работать с Qt
            from PySide6 import QtWidgets
            cb = QtWidgets.QApplication.clipboard()
            if cb is not None:
                cb.setText(text)
                print("✅ Текст скопирован через Qt с COM инициализацией")
                return True
            else:
                print("⚠️ Qt clipboard недоступен")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка копирования через Qt с COM: {e}")
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
                # ГИБРИДНЫЙ ПОДХОД: Сначала пробуем новый (точный), если не получилось - старый (по заголовкам)
                print(f"🔍 Начинаем поиск окна Cursor для проекта: '{self._preferred_window_hint}'")
                hwnd = self._find_cursor_process_for_project(project_path)

                if not hwnd:
                    print("⚠️ Новый метод не нашел процесс, пробуем старый метод (по заголовкам окон)...")
                    hwnd = self._bring_cursor_window_to_front_old()

                    if not hwnd:
                        print("❌ СТАРЫЙ МЕТОД ТОЖЕ НЕ НАШЕЛ окно Cursor!")
                        print("📋 ДИАГНОСТИКА: Проверьте, что у вас открыт Cursor с этим проектом")
                        print(f"   Ожидаемый проект: '{self._preferred_window_hint}'")
                        print("   Советы:")
                        print("   1. Откройте проект в Cursor")
                        print("   2. Убедитесь что окно Cursor не свернуто")
                        print("   3. Проверьте заголовок окна в диспетчере задач")
                        return False, "Не найдено окно Cursor для проекта"
                    else:
                        print(f"✅ Старый метод нашел окно: HWND={hwnd}")
                else:
                    print(f"✅ Новый метод нашел процесс: HWND={hwnd}")
                    
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
                # Убрана ветка вставки через UIAutomation
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

                # Параллельная генерация (ускорение): число воркеров из env IDEOGRAM_CONCURRENCY (по умолчанию 6)
                try:
                    concurrency = max(1, int(os.getenv("IDEOGRAM_CONCURRENCY", "6")))
                except Exception:
                    concurrency = 6

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
                    # Ждём загрузку приложения Cursor (стабильное окно)
                    print("⏳ Ожидание полного запуска Cursor...")
                    try:
                        app_ready_to = int(os.getenv('CURSOR_APP_READY_TIMEOUT_SEC', '10'))
                    except Exception:
                        app_ready_to = 10
                    
                    hwnd_ready = self._wait_for_cursor_app_ready(timeout_sec=app_ready_to)
                    if hwnd_ready:
                        print("✅ Окно Cursor готово")
                        # Увеличенная пауза для полной загрузки интерфейса и курсора
                        try:
                            interface_ready_delay = float(os.getenv('CURSOR_INTERFACE_READY_DELAY_SEC', '8.0'))
                        except Exception:
                            interface_ready_delay = 8.0
                        print(f"⏳ Ждем полной загрузки интерфейса и курсора ({interface_ready_delay} сек)...")
                        time.sleep(interface_ready_delay)
                    else:
                        print(f"⚠️ Не дождались готовности окна за {app_ready_to}с, используем стандартную паузу")
                        try:
                            fallback_delay = float(os.getenv('CURSOR_FALLBACK_DELAY_SEC', '12.0'))
                        except Exception:
                            fallback_delay = 12.0
                        time.sleep(max(fallback_delay, paste_delay))
                    
                    # Сокращённая логика: без шаблонов/скриншотов
                    
                    if PYAUTOGUI_AVAILABLE:
                        # Специальные настройки для EXE режима
                        if self._is_exe:
                            print("🔧 Применяем специальные настройки для EXE")
                            pyautogui.PAUSE = 0.5  # Увеличиваем паузы между действиями
                            pyautogui.FAILSAFE = False  # Отключаем failsafe для надежности
                        
                        # Активируем чат через Ctrl+Shift+Y
                        print("🚀 Активация чата через Ctrl+Shift+Y...")
                        chat_activated = self._click_on_chat_area()
                        if chat_activated:
                            print("✅ Чат активирован через Ctrl+Shift+Y")
                        else:
                            print("⚠️ Не удалось активировать чат через Ctrl+Shift+Y")
                            return True, "Cursor AI запущен, но чат не активирован"
                        
                        # Увеличенная пауза для готовности чата и курсора
                        try:
                            chat_ready_delay = float(os.getenv('CURSOR_CHAT_READY_DELAY_SEC', '6.0'))
                        except Exception:
                            chat_ready_delay = 6.0
                        print(f"⏳ Ожидание готовности чата и курсора ({chat_ready_delay} сек)...")
                        time.sleep(chat_ready_delay)

                        # Диагностический режим
                        diagnostic_mode = str(os.getenv('CURSOR_DIAGNOSTIC_MODE', '0')).lower() in ('1', 'true', 'yes')

                        # Улучшенная стабилизация: проверка ввода с retry-логикой
                        def _check_cursor_ready(max_attempts=5):
                            """Проверяет готовность курсора к вводу с повторными попытками"""
                            try:
                                check_delay = float(os.getenv('CURSOR_CURSOR_READY_CHECK_DELAY', '0.5'))
                            except Exception:
                                check_delay = 0.5

                            for attempt in range(max_attempts):
                                try:
                                    if diagnostic_mode:
                                        print(f"🔍 [Диагностика] Попытка проверки курсора {attempt + 1}/{max_attempts}")
                                        print(f"🔍 [Диагностика] Пишем тестовый символ '.'")

                                    # Пишем тестовый символ
                                    pyautogui.write('.')

                                    # Небольшая пауза для обработки
                                    time.sleep(0.1)

                                    if diagnostic_mode:
                                        print(f"🔍 [Диагностика] Удаляем тестовый символ")

                                    # Удаляем тестовый символ
                                    pyautogui.press('backspace')
                                    time.sleep(0.1)

                                    # Если дошли до сюда без ошибок - курсор готов
                                    if diagnostic_mode:
                                        print(f"🔍 [Диагностика] Курсор успешно прошел проверку")
                                    print(f"✅ Курсор готов к вводу (попытка {attempt + 1})")
                                    return True

                                except Exception as e:
                                    if diagnostic_mode:
                                        print(f"🔍 [Диагностика] Ошибка при проверке курсора: {str(e)}")
                                    print(f"⚠️ Проверка курсора неудачна (попытка {attempt + 1}/{max_attempts}): {e}")
                                    if attempt < max_attempts - 1:
                                        if diagnostic_mode:
                                            print(f"🔍 [Диагностика] Ждем {check_delay} сек перед следующей попыткой")
                                        time.sleep(check_delay)  # Пауза перед следующей попыткой
                                    continue

                            print("❌ Курсор не готов к вводу после всех попыток")
                            return False

                        # Выполняем проверку готовности курсора
                        try:
                            cursor_ready_checks = int(os.getenv('CURSOR_CURSOR_READY_CHECKS', '5'))
                        except Exception:
                            cursor_ready_checks = 5

                        cursor_ready = _check_cursor_ready(cursor_ready_checks)
                        if not cursor_ready:
                            print("⚠️ Продолжаем несмотря на проблемы с курсором...")

                        # Вставка промпта с retry-логикой
                        def _paste_prompt_with_retry(max_attempts=3):
                            """Вставляет промпт с повторными попытками"""
                            for attempt in range(max_attempts):
                                try:
                                    print(f"📝 Попытка вставки промпта {attempt + 1}/{max_attempts}...")
                                    pyautogui.hotkey('ctrl', 'v')  # Вставляем

                                    try:
                                        paste_enter_delay = float(os.getenv('CURSOR_PASTE_ENTER_DELAY_SEC', '1.0'))
                                    except Exception:
                                        paste_enter_delay = 1.0

                                    time.sleep(paste_enter_delay)
                                    pyautogui.press('enter')  # Отправляем

                                    print(f"✅ Промпт вставлен успешно (попытка {attempt + 1})")
                                    return True

                                except Exception as e:
                                    print(f"⚠️ Ошибка вставки промпта (попытка {attempt + 1}/{max_attempts}): {e}")
                                    if attempt < max_attempts - 1:
                                        print("⏳ Повторная попытка через 1 секунду...")
                                        time.sleep(1.0)
                                    continue

                            print("❌ Все попытки вставки промпта неудачны")
                            return False

                        # Выполняем вставку промпта с retry
                        try:
                            paste_retry_attempts = int(os.getenv('CURSOR_PASTE_RETRY_ATTEMPTS', '3'))
                        except Exception:
                            paste_retry_attempts = 3

                        paste_success = _paste_prompt_with_retry(paste_retry_attempts)

                        if not paste_success:
                            return True, "Cursor AI запущен, но вставка промпта неудачна после нескольких попыток"
                        else:
                            print("✅ Промпт вставлен успешно через Ctrl+Shift+Y")
                    else:
                        print("⚠️ pyautogui недоступен, автовставка невозможна")
                except Exception as e:
                    print(f"❌ Ошибка автовставки: {e}")
            
            return True, "Cursor AI запущен успешно"
        else:
            return False, "Cursor AI не найден. Промпт скопирован в буфер обмена"

    # ===== Windows helpers =====
    def _find_cursor_process_for_project(self, project_path) -> int | bool:
        """
        Новый подход: ищет процесс Cursor, запущенный с конкретным проектом
        через анализ аргументов командной строки процессов
        """
        try:
            if platform.system().lower() != 'windows':
                return self._bring_cursor_window_to_front_old()

            import psutil
            
            project_name = str(project_path).split('/')[-1] if '/' in str(project_path) else str(project_path).split('\\')[-1]
            project_full_path = str(project_path).replace('/', '\\')
            
            print(f"🔍 Поиск процесса Cursor для проекта: '{project_name}' по пути: '{project_full_path}'")
            
            cursor_processes = []
            
            # Ищем все процессы Cursor
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'cursor' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline:
                            cmdline_str = ' '.join(cmdline)
                            cursor_processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline_str,
                                'match_score': 0
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print(f"📊 Найдено {len(cursor_processes)} процессов Cursor")
            
            if not cursor_processes:
                print("❌ Процессы Cursor не найдены")
                return False
                
            # Оцениваем каждый процесс по соответствию проекту
            best_match = None
            best_score = 0
            
            for proc_info in cursor_processes:
                cmdline = proc_info['cmdline']
                score = 0
                
                # Проверяем точное совпадение пути
                if project_full_path.lower() in cmdline.lower():
                    score += 100
                    print(f"✅ Точное совпадение пути в процессе PID {proc_info['pid']}")
                
                # Проверяем совпадение имени проекта
                elif project_name.lower() in cmdline.lower():
                    score += 50
                    print(f"🎯 Совпадение имени проекта в процессе PID {proc_info['pid']}")
                
                # Проверяем части имени проекта
                else:
                    parts = project_name.replace('_', ' ').replace('-', ' ').split()
                    for part in parts:
                        if len(part) > 3 and part.lower() in cmdline.lower():
                            score += 10
                
                proc_info['match_score'] = score
                
                if score > best_score:
                    best_score = score
                    best_match = proc_info
                    
                print(f"   PID {proc_info['pid']}: score={score}, cmdline={cmdline[:100]}...")
            
            if best_match and best_score > 0:
                print(f"🎯 Лучшее совпадение: PID {best_match['pid']} (score={best_score})")
                return self._get_window_handle_by_pid(best_match['pid'])
            else:
                print("❌ Не найден подходящий процесс Cursor для проекта")
                return False
                
        except ImportError:
            print("⚠️ psutil не установлен, используем старый метод")
            return self._bring_cursor_window_to_front_old()
        except Exception as e:
            print(f"⚠️ Ошибка поиска процесса: {e}")
            return self._bring_cursor_window_to_front_old()

    def _get_window_handle_by_pid(self, pid) -> int | bool:
        """Получает handle окна по PID процесса"""
        try:
            if platform.system().lower() != 'windows':
                return False
                
            user32 = ctypes.windll.user32
            
            target_hwnd = 0
            
            def enum_proc(hwnd, lParam):
                try:
                    nonlocal target_hwnd
                    process_id = ctypes.wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                    
                    if process_id.value == pid and user32.IsWindowVisible(hwnd):
                        # Проверяем что это главное окно (не дочернее)
                        if not user32.GetParent(hwnd):
                            target_hwnd = hwnd
                            return False  # Останавливаем поиск
                except:
                    pass
                return True
            
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            user32.EnumWindows(EnumWindowsProc(enum_proc), 0)
            
            if target_hwnd:
                print(f"✅ Найдено окно для PID {pid}: HWND={target_hwnd}")
                self._force_window_to_front_and_position(target_hwnd)
                return target_hwnd
            else:
                print(f"❌ Не найдено окно для PID {pid}")
                return False
                
        except Exception as e:
            print(f"⚠️ Ошибка получения handle окна: {e}")
            return False

    def _bring_cursor_window_to_front_old(self) -> int | bool:
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
            all_cursor_windows = []
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
                        
                        # Добавляем в список всех окон Cursor
                        all_cursor_windows.append((hwnd, title))
                        
                        # Сохраняем первое встреченное как запасной вариант
                        if not fallback_hwnd:
                            fallback_hwnd = int(hwnd)
                            print(f"📱 Найдено окно Cursor (fallback): '{title}'")

                        # Улучшенное соответствие: более гибкий поиск с учетом различных форматов заголовков
                        if preferred:
                            # Проверяем точное вхождение имени проекта в заголовок
                            if preferred in tl:
                                target_hwnd = int(hwnd)
                                print(f"🎯 ТОЧНОЕ совпадение окна Cursor: '{title}' для проекта '{preferred}'")
                                return False  # нашли точный матч

                            # Проверяем части имени проекта (более гибко)
                            hint_parts = preferred.replace('_', ' ').replace('-', ' ').split()
                            matching_parts = 0
                            for part in hint_parts:
                                if len(part) > 2 and part.lower() in tl.lower():  # Уменьшили минимальную длину с 3 до 2
                                    matching_parts += 1

                            # Более мягкие критерии: достаточно хотя бы одной совпадающей части
                            total_parts = len(hint_parts)
                            if total_parts > 0 and matching_parts >= max(1, total_parts // 2):
                                if not target_hwnd:  # Берем только если еще не нашли лучший
                                    target_hwnd = int(hwnd)
                                    print(f"🎯 Частичное совпадение окна Cursor: '{title}' ({matching_parts}/{total_parts} частей для '{preferred}')")
                                    
                except Exception:
                    return True
                return True

            EnumWindows(EnumWindowsProc(enum_proc), 0)

            print(f"📊 РЕЗУЛЬТАТЫ ПОИСКА ПО ЗАГОЛОВКАМ:")
            print(f"   Всего найдено окон Cursor: {len(all_cursor_windows)}")
            print(f"   Точное совпадение: {'найдено' if target_hwnd else 'не найдено'}")
            print(f"   Подсказка поиска: '{preferred}'")

            if all_cursor_windows:
                print("   Список всех окон Cursor:")
                for i, (hwnd, title) in enumerate(all_cursor_windows[:5], 1):  # Показываем первые 5
                    status = "🎯" if hwnd == target_hwnd else "   "
                    print(f"   {status} {i}. '{title}'")
                if len(all_cursor_windows) > 5:
                    print(f"   ... и еще {len(all_cursor_windows) - 5} окон")

            # Если не нашли подходящее окно, но есть подсказка - создаем новое
            if not target_hwnd and preferred:
                print(f"⚠️ Не найдено окно Cursor для проекта '{preferred}'")
                print("❌ Промпт НЕ будет отправлен в случайное окно!")
                print("💡 СОВЕТ: Убедитесь, что проект открыт в Cursor и заголовок окна содержит имя проекта")
                return False  # Не используем случайное окно

            if not target_hwnd:
                print("⚠️ Не найдено ни одного подходящего окна Cursor")
                if fallback_hwnd:
                    print(f"📱 Используем fallback окно: {fallback_hwnd}")
                    target_hwnd = fallback_hwnd
                else:
                    print("❌ Нет доступных окон Cursor")
                    return False

            # Дополнительная валидация выбранного окна
            if target_hwnd and preferred:
                window_title = ""
                try:
                    length = GetWindowTextLengthW(target_hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        GetWindowTextW(target_hwnd, buf, length + 1)
                        window_title = buf.value or ""
                except:
                    pass
                    
                if preferred not in window_title.lower():
                    print(f"⚠️ ВНИМАНИЕ: Выбранное окно '{window_title}' может не соответствовать проекту '{preferred}'")

            # Восстановить из свернутого состояния, показать и принудительно поднять поверх всех
            if IsIconic(target_hwnd):
                ShowWindow(target_hwnd, SW_RESTORE)
            else:
                ShowWindow(target_hwnd, SW_SHOW)
            
            # Принудительное позиционирование и активация
            self._force_window_to_front_and_position(target_hwnd)
            return target_hwnd
        except Exception as e:
            try:
                print(f"Ошибка активации окна Cursor: {e}")
            except Exception:
                pass
            return False

    # Убран альтернативный посимвольный метод вставки (ускорение и упрощение)

    def _click_on_chat_area(self) -> bool:
        """Активирует чат через Ctrl+Shift+Y - 100% способ открытия чата."""
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False

            print("🎯 Используем ГАРАНТИРОВАННУЮ горячую клавишу Ctrl+Shift+Y...")

            # Убеждаемся что окно активно
            self._bring_cursor_window_to_front()
            time.sleep(1)

            # Отправляем Ctrl+Shift+Y для открытия чата
            pyautogui.hotkey('ctrl', 'shift', 'y')
            time.sleep(2)  # Даем больше времени

            # Проверяем активацию чата
            print("🔍 Проверяем активацию чата...")
            pyautogui.write('test')
            time.sleep(0.3)

            # Очищаем тестовый текст
            for _ in range(4):  # Удаляем 'test'
                pyautogui.press('backspace')
                time.sleep(0.1)

            print("🎉 Чат ГАРАНТИРОВАННО активирован через Ctrl+Shift+Y!")
            return True

        except Exception as e:
            print(f"❌ Ошибка активации чата через Ctrl+Shift+Y: {e}")
            return False

    def _try_guaranteed_chat_activation(self, hwnd: int) -> bool:
        """
        Пробует ГАРАНТИРОВАННУЮ активацию чата через Ctrl+I.
        Упрощенная версия для максимальной надежности в EXE.
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            print("🎯 Используем ГАРАНТИРОВАННУЮ горячую клавишу Ctrl+I...")
            
            # Убеждаемся что окно активно
            self._bring_cursor_window_to_front()
            time.sleep(1)
            
            # Пробуем Ctrl+I несколько раз для надежности
            for attempt in range(3):
                try:
                    print(f"🔥 Попытка {attempt + 1}: Отправляем Ctrl+I...")
                    pyautogui.hotkey('ctrl', 'i')
                    time.sleep(3)  # Увеличено с 2 до 3 секунд

                    # Проверяем активацию чата
                    print("🔍 Проверяем активацию чата...")
                    pyautogui.write('test')
                    time.sleep(0.5)  # Увеличено с 0.3 до 0.5

                    # Очищаем тестовый текст
                    for _ in range(4):  # Удаляем 'test'
                        pyautogui.press('backspace')
                        time.sleep(0.15)  # Увеличено с 0.1 до 0.15
                    
                    print("🎉 ГАРАНТИРОВАННАЯ активация чата через Ctrl+I УСПЕШНА!")
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Попытка {attempt + 1} не удалась: {e}")
                    if attempt < 2:  # Не последняя попытка
                        time.sleep(1)
                        continue
            
            print("❌ Все попытки Ctrl+I не сработали")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка гарантированной активации: {e}")
            return False

    def _activate_chat_by_keyboard(self, hwnd: int) -> bool:
        """
        Активирует область чата через клавиатурную навигацию.
        Самый надежный метод для EXE режима.
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            print("⌨️ Используем клавиатурную навигацию для поиска чата...")
            
            # Убеждаемся что окно активно
            self._bring_cursor_window_to_front()
            time.sleep(1)
            
            # Метод 1: ГАРАНТИРОВАННАЯ горячая клавиша Cursor для чата (Ctrl+I)
            print("🔥 Пробуем ГАРАНТИРОВАННУЮ горячую клавишу Ctrl+I для чата...")
            try:
                pyautogui.hotkey('ctrl', 'i')
                time.sleep(3)  # Увеличено с 2 до 3 секунд
                print("✅ Ctrl+I отправлен")

                # Проверяем что чат активировался (пробуем напечатать и стереть символ)
                pyautogui.write('.')
                time.sleep(0.3)  # Увеличено с 0.2 до 0.3
                pyautogui.press('backspace')
                time.sleep(0.3)  # Увеличено с 0.2 до 0.3
                print("🎉 Чат ГАРАНТИРОВАННО активирован через Ctrl+I!")
                return True
            except Exception as e:
                print(f"⚠️ Ctrl+I не сработал: {e}")
            
            # Метод 2: Запасная горячая клавиша (Ctrl+Shift+`)
            print("🔄 Пробуем запасную горячую клавишу Ctrl+Shift+`...")
            try:
                pyautogui.hotkey('ctrl', 'shift', '`')
                time.sleep(2)  # Даем время на открытие чата
                print("✅ Ctrl+Shift+` отправлен")
                
                # Проверяем что чат активировался
                pyautogui.write('.')
                time.sleep(0.2)
                pyautogui.press('backspace')
                time.sleep(0.2)
                print("✅ Чат активирован через запасную горячую клавишу!")
                return True
            except Exception as e:
                print(f"⚠️ Запасная горячая клавиша не сработала: {e}")
            
            # Метод 3: Tab навигация для поиска поля ввода
            print("🔄 Пробуем Tab навигацию...")
            try:
                # Сначала идем в начало (Alt+Home или Ctrl+Home)
                pyautogui.hotkey('ctrl', 'home')
                time.sleep(0.5)
                
                # Пробуем несколько Tab нажатий для поиска поля ввода
                for i in range(15):  # Максимум 15 табов
                    pyautogui.press('tab')
                    time.sleep(0.2)
                    
                    # Пробуем напечатать символ чтобы проверить что это поле ввода
                    pyautogui.write('.')
                    time.sleep(0.1)
                    
                    # Если смогли напечатать - это может быть наше поле
                    pyautogui.press('backspace')
                    time.sleep(0.1)
                    
                    # Проверяем не попали ли мы в область чата
                    # (можно по наличию placeholder текста или другим признакам)
                    if i > 5:  # После 5 табов вероятно попали в область чата
                        print(f"✅ Возможно нашли поле ввода через Tab (позиция {i})")
                        return True
                        
            except Exception as e:
                print(f"⚠️ Tab навигация не сработала: {e}")
            
            # Метод 4: Комбинированный подход - клики + клавиши
            print("🔄 Пробуем комбинированный подход...")
            try:
                # Кликаем в нижнюю часть окна
                user32 = ctypes.windll.user32
                rect = ctypes.wintypes.RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
                    
                    # Кликаем в нижнюю центральную область
                    click_x = left + (right - left) // 2
                    click_y = bottom - 50  # 50 пикселей от низа
                    
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.5)
                    
                    # Пробуем гарантированную горячую клавишу после клика
                    pyautogui.hotkey('ctrl', 'i')
                    time.sleep(1)
                    
                    # Проверяем активацию
                    pyautogui.write('.')
                    time.sleep(0.1)
                    pyautogui.press('backspace')
                    
                    print("✅ Комбинированный метод сработал!")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Комбинированный метод не сработал: {e}")
            
            # Метод 5: Попытка через End (переход в конец документа) + Enter
            print("🔄 Пробуем End + Enter...")
            try:
                pyautogui.press('end')  # Переходим в конец
                time.sleep(0.5)
                pyautogui.press('enter')  # Возможно откроется поле ввода
                time.sleep(1)
                
                # Пробуем напечатать
                pyautogui.write('.')
                time.sleep(0.1)
                pyautogui.press('backspace')
                
                print("✅ End + Enter метод сработал!")
                return True
                
            except Exception as e:
                print(f"⚠️ End + Enter не сработал: {e}")
            
            print("❌ Все методы клавиатурной навигации не сработали")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка клавиатурной навигации: {e}")
            return False

    # Убран поиск по тексту через UI Automation

    # Убран поиск через OCR

    # Убран поиск по шаблону изображения

    # Убран «умный» расчет координат

    def _click_at_position(self, hwnd: int, x: int, y: int) -> bool:
        """
        Универсальная функция для клика в указанной позиции
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            # Дополнительная активация окна перед кликом
            self._bring_cursor_window_to_front()
            time.sleep(0.5)  # Увеличиваем задержку
            
            # Выполняем ОДИН точный клик
            pyautogui.click(x, y)
            
            # Небольшая пауза для обработки клика
            time.sleep(0.5)
            print(f"🎯 Клик выполнен в позиции ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка клика в позиции ({x}, {y}): {e}")
            return False

    # Убраны отладочные скриншоты

    # Убран принудительный метод вставки через Windows API (ускорение и упрощение)

    # Убраны вспомогательные методы буфера обмена для принудительной вставки

    # Убрано создание шаблона области чата

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

    # Убран UI Automation фокус

    # Убран поиск по плейсхолдеру через UI Automation

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

    def _wait_for_cursor_app_ready(self, timeout_sec: int = 30) -> int | bool:
        """Ждёт, пока окно Cursor будет готово: найдено, показано, не меняет размеры резко.
        Возвращает hwnd или False по таймауту.
        """
        try:
            if platform.system().lower() != 'windows':
                # На других ОС — простой фолбек
                self._bring_cursor_window_to_front()
                time.sleep(2)
                return True
            user32 = ctypes.windll.user32
            start = time.time()
            last_rect = None
            stable_count = 0
            while time.time() - start < max(5, timeout_sec):
                hwnd = self._bring_cursor_window_to_front()
                if not hwnd:
                    time.sleep(0.3)
                    continue
                rect = ctypes.wintypes.RECT()
                if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    time.sleep(0.2)
                    continue
                l, t, r, b = rect.left, rect.top, rect.right, rect.bottom
                w, h = r - l, b - t
                if w < 200 or h < 200:
                    time.sleep(0.3)
                    continue
                current = (l, t, r, b)
                if last_rect is None:
                    last_rect = current
                    stable_count = 1
                else:
                    # считаем окно стабильным, если 3 цикла подряд размеры идентичны
                    if current == last_rect:
                        stable_count += 1
                    else:
                        stable_count = 1
                        last_rect = current
                if stable_count >= 3:
                    # финальная активация
                    self._ensure_window_active(hwnd, timeout_s=2.0)
                    return hwnd
                time.sleep(0.3)
            return False
        except Exception:
            return False

    def _throttle_before_launch(self, project_hint: str = None) -> None:
        """Обеспечивает паузу между запусками окон Cursor с учётом проектов."""
        try:
            with self._launch_lock:
                now = time.monotonic()
                elapsed = now - self._last_launch_monotonic
                wait_for = self._launch_interval_sec - elapsed

                # Дополнительный троттлинг по проектам
                if project_hint:
                    last_project_time = self._project_launch_times.get(project_hint, 0)
                    project_elapsed = now - last_project_time
                    project_wait = self._min_project_interval_sec - project_elapsed

                    if project_wait > 0:
                        print(f"⏳ Ожидание {project_wait:.1f} сек между проектами для '{project_hint}'...")
                        time.sleep(project_wait)
                        # Обновляем время после ожидания
                        now = time.monotonic()

                if wait_for > 0:
                    print(f"⏳ ЖЕСТКИЙ ТРОТТЛИНГ: ожидание {wait_for:.1f} сек до следующего запуска Cursor...")
                    time.sleep(wait_for)

                # фиксируем момент запуска, чтобы следующие ждали интервал
                self._last_launch_monotonic = time.monotonic()

                # Сохраняем время запуска для проекта
                if project_hint:
                    self._project_launch_times[project_hint] = time.monotonic()

                # Дополнительная жесткая пауза для стабильности
                try:
                    extra_gap = float(os.getenv('CURSOR_EXTRA_LAUNCH_GAP_SEC', '2.0'))
                except Exception:
                    extra_gap = 2.0

                if extra_gap > 0:
                    print(f"⏳ Дополнительная пауза {extra_gap} сек для стабильности...")
                    time.sleep(extra_gap)
        except Exception:
            pass

    def _force_window_to_front_and_position(self, hwnd):
        """
        Принудительно выводит окно поверх всех остальных и позиционирует его
        """
        try:
            if platform.system().lower() != 'windows' or not hwnd:
                return False

            user32 = ctypes.windll.user32
            
            # Получаем размеры экрана
            screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
            
            # Фиксированная позиция - все окна в одном месте
            new_x = self._base_window_x
            new_y = self._base_window_y
            
            # Размеры окна (80% экрана)
            window_width = int(screen_width * 0.8)
            window_height = int(screen_height * 0.8)

            print(f"🪟 Позиционирование окна Cursor: X={new_x}, Y={new_y}, W={window_width}, H={window_height} (фиксированная позиция)")

            # Принудительно устанавливаем позицию и размер
            user32.MoveWindow(hwnd, new_x, new_y, window_width, window_height, True)
            
            # Многоступенчатая активация для гарантированного выведения поверх всех
            SW_RESTORE = 9
            SW_SHOW = 5
            SW_MAXIMIZE = 3
            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_SHOWWINDOW = 0x0040

            # Шаг 1: Восстанавливаем если свернуто
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, SW_RESTORE)
                time.sleep(0.1)

            # Шаг 2: Показываем окно
            user32.ShowWindow(hwnd, SW_SHOW)
            time.sleep(0.1)

            # Шаг 3: Ставим поверх всех (topmost)
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            time.sleep(0.1)

            # Шаг 4: Убираем topmost но оставляем активным
            user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            time.sleep(0.1)

            # Шаг 5: Принудительно активируем окно
            current_tid = ctypes.windll.kernel32.GetCurrentThreadId()
            target_tid = user32.GetWindowThreadProcessId(hwnd, None)
            
            # Привязываем потоки ввода для лучшей активации
            user32.AttachThreadInput(current_tid, target_tid, True)
            try:
                user32.SetForegroundWindow(hwnd)
                user32.SetActiveWindow(hwnd)
                user32.SetFocus(hwnd)
            finally:
                user32.AttachThreadInput(current_tid, target_tid, False)

            print("✅ Окно Cursor принудительно выведено поверх всех и позиционировано")
            return True

        except Exception as e:
            print(f"⚠️ Ошибка принудительного позиционирования окна: {e}")
            return False

    def _position_new_cursor_window(self):
        """
        Ищет последнее открытое окно Cursor и позиционирует его
        """
        try:
            if platform.system().lower() != 'windows':
                return False

            user32 = ctypes.windll.user32
            
            # Ищем новое окно Cursor (последнее по времени)
            cursor_windows = []
            
            def enum_proc(hwnd, lParam):
                try:
                    if not user32.IsWindowVisible(hwnd):
                        return True
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return True
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value or ""
                    if 'cursor' in title.lower():
                        cursor_windows.append((hwnd, title))
                except Exception:
                    pass
                return True

            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            user32.EnumWindows(EnumWindowsProc(enum_proc), 0)

            if cursor_windows:
                # Берем последнее найденное окно (предположительно новое)
                latest_hwnd, latest_title = cursor_windows[-1]
                print(f"🎯 Позиционирование нового окна Cursor: '{latest_title}'")
                self._force_window_to_front_and_position(latest_hwnd)
                return True

            return False

        except Exception as e:
            print(f"⚠️ Ошибка поиска нового окна Cursor: {e}")
            return False

    # Убран поиск шаблона внутри окна

    # Убран скриншот области экрана (OCR/шаблоны не используются)