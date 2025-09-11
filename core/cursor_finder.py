# -*- coding: utf-8 -*-

"""
Модуль для поиска исполняемого файла Cursor
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional


class CursorFinder:
    """Класс для поиска исполняемого файла Cursor на разных платформах"""
    
    def __init__(self):
        self.cursor_paths = ["cursor", "code"]
        self.cached_cursor_path = None
        self.os_type = platform.system().lower()
    
    def _get_platform_search_paths(self) -> List[str]:
        """Получает пути поиска для текущей платформы"""
        if self.os_type == "windows":
            return self._get_windows_search_paths()
        elif self.os_type == "linux":
            return self._get_linux_search_paths()
        elif self.os_type == "darwin":
            return self._get_macos_search_paths()
        else:
            return []
    
    def _get_windows_search_paths(self) -> List[str]:
        """Возвращает пути поиска для Windows"""
        paths = []
        
        # Основные пути установки
        base_paths = [
            os.path.expanduser("~\\AppData\\Local\\Programs\\cursor"),
            "C:\\Program Files\\Cursor",
            "C:\\Program Files (x86)\\Cursor",
            os.path.expanduser("~\\AppData\\Local\\cursor"),
            "C:\\Users\\Public\\Desktop\\cursor"
        ]
        
        # Добавляем пути из переменных окружения
        if "PROGRAMFILES" in os.environ:
            paths.append(os.path.join(os.environ["PROGRAMFILES"], "Cursor"))
        if "PROGRAMFILES(X86)" in os.environ:
            paths.append(os.path.join(os.environ["PROGRAMFILES(X86)"], "Cursor"))
        if "LOCALAPPDATA" in os.environ:
            paths.append(os.path.join(os.environ["LOCALAPPDATA"], "Programs", "cursor"))
        
        paths.extend(base_paths)
        return paths
    
    def _get_linux_search_paths(self) -> List[str]:
        """Возвращает пути поиска для Linux"""
        home = os.path.expanduser("~")
        return [
            "/usr/bin",
            "/usr/local/bin", 
            "/opt/cursor/bin",
            "/snap/bin",
            "/var/lib/snapd/snap/bin",
            f"{home}/.local/bin",
            f"{home}/.cursor",
            f"{home}/Applications",
            "/usr/share/applications",
            "/opt",
            "/usr/local/share/applications"
        ]
    
    def _get_macos_search_paths(self) -> List[str]:
        """Возвращает пути поиска для macOS"""
        home = os.path.expanduser("~")
        return [
            "/Applications",
            f"{home}/Applications",
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "/usr/bin"
        ]
    
    def find_cursor_in_directories(self) -> Optional[str]:
        """Ищет Cursor в стандартных директориях"""
        search_paths = self._get_platform_search_paths()
        
        for directory in search_paths:
            if not os.path.isdir(directory):
                continue
                
            try:
                for item in os.listdir(directory):
                    full_path = os.path.join(directory, item)
                    
                    if self._is_cursor_file(item) and self._test_cursor_executable(full_path):
                        print(f"✅ Найден Cursor: {full_path}")
                        return full_path
                        
            except (PermissionError, OSError):
                continue
        
        return None
    
    def _get_search_directories(self) -> List[str]:
        """Получает расширенный список директорий для поиска"""
        directories = self._get_platform_search_paths()
        
        # Добавляем PATH
        path_env = os.environ.get("PATH", "")
        if path_env:
            directories.extend(path_env.split(os.pathsep))
        
        return directories
    
    def _is_cursor_file(self, filename: str) -> bool:
        """Проверяет, является ли файл исполняемым Cursor"""
        filename_lower = filename.lower()
        
        # Список возможных имен исполняемого файла
        cursor_names = [
            "cursor.exe", "cursor", "cursor.app",
            "code.exe", "code", "code.app"
        ]
        
        return filename_lower in cursor_names or filename_lower.startswith("cursor")
    
    def _test_cursor_executable(self, path: str) -> bool:
        """Тестирует, является ли файл рабочим исполняемым Cursor"""
        if not os.path.isfile(path):
            return False
        
        # Проверяем права на выполнение
        if not os.access(path, os.X_OK):
            return False
        
        try:
            # Пытаемся получить версию
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout.lower() + result.stderr.lower()
            return "cursor" in output or "code" in output
            
        except Exception:
            return False
    
    def find_cursor_executable(self) -> Optional[str]:
        """Основной метод поиска исполняемого файла Cursor"""
        if self.cached_cursor_path and os.path.isfile(self.cached_cursor_path):
            return self.cached_cursor_path
        
        print("🔍 Поиск исполняемого файла Cursor...")
        
        # 1. Поиск в стандартных директориях
        cursor_path = self.find_cursor_in_directories()
        if cursor_path:
            self.cached_cursor_path = cursor_path
            return cursor_path
        
        # 2. Поиск в реестре (Windows)
        if self.os_type == "windows":
            cursor_path = self.find_cursor_in_registry()
            if cursor_path:
                self.cached_cursor_path = cursor_path
                return cursor_path
        
        # 3. Поиск в меню Пуск (Windows)
        if self.os_type == "windows":
            cursor_path = self.find_cursor_in_start_menu()
            if cursor_path:
                self.cached_cursor_path = cursor_path
                return cursor_path
        
        # 4. Поиск через which/whereis (Linux)
        if self.os_type == "linux":
            cursor_path = self.find_cursor_linux_commands()
            if cursor_path:
                self.cached_cursor_path = cursor_path
                return cursor_path
        
        print("❌ Cursor не найден автоматически")
        return None
    
    def find_cursor_in_registry(self) -> Optional[str]:
        """Поиск Cursor в реестре Windows"""
        if self.os_type != "windows":
            return None
            
        try:
            import winreg
            
            # Пути в реестре для поиска
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
            ]
            
            for hkey, subkey_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        if "cursor" in display_name.lower():
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                            cursor_exe = os.path.join(install_location, "Cursor.exe")
                                            if os.path.isfile(cursor_exe):
                                                return cursor_exe
                                    except FileNotFoundError:
                                        pass
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue
                    
        except ImportError:
            pass
        
        return None
    
    def find_cursor_in_start_menu(self) -> Optional[str]:
        """Поиск Cursor в меню Пуск Windows"""
        if self.os_type != "windows":
            return None
            
        start_menu_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"),
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"
        ]
        
        for start_path in start_menu_paths:
            if not os.path.exists(start_path):
                continue
                
            try:
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if file.lower() == "cursor.lnk":
                            # Попытка извлечь путь из ярлыка
                            return self._extract_path_from_shortcut(os.path.join(root, file))
            except Exception:
                continue
        
        return None
    
    def _extract_path_from_shortcut(self, shortcut_path: str) -> Optional[str]:
        """Извлекает путь к исполняемому файлу из ярлыка Windows"""
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            pythoncom.CoInitialize()
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            target_path = shortcut.Targetpath
            pythoncom.CoUninitialize()
            
            if os.path.isfile(target_path) and "cursor" in target_path.lower():
                return target_path
                
        except ImportError:
            pass
        except Exception:
            pass
        
        return None
    
    def find_cursor_linux_commands(self) -> Optional[str]:
        """Поиск Cursor через системные команды Linux"""
        if self.os_type != "linux":
            return None
            
        commands_to_try = ["which cursor", "whereis cursor", "which code", "whereis code"]
        
        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip().split()[0]
                    if os.path.isfile(path):
                        return path
                        
            except Exception:
                continue
        
        return None
    
    def ask_for_cursor_path(self) -> Optional[str]:
        """Запрашивает путь к Cursor у пользователя"""
        print("🤔 Не удалось найти Cursor автоматически.")
        print("Пожалуйста, укажите путь к исполняемому файлу Cursor:")
        
        user_path = input("Путь к Cursor: ").strip().strip('"')
        
        if user_path and os.path.isfile(user_path):
            if self._test_cursor_executable(user_path):
                self.cached_cursor_path = user_path
                return user_path
            else:
                print("❌ Указанный файл не является рабочим исполняемым Cursor")
        else:
            print("❌ Указанный файл не существует")
        
        return None



