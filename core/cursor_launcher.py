# -*- coding: utf-8 -*-

"""
Модуль для запуска Cursor с проектами
"""

import os
import subprocess
import platform
import threading
import time
from pathlib import Path
from typing import Optional


class CursorLauncher:
    """Класс для запуска Cursor с проектами на разных платформах"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self._launch_lock = threading.Lock()
        self._last_launch_monotonic = 0.0
        
        # Настройки троттлинга из переменных окружения
        try:
            default_interval = "5.0"
            self._launch_interval_sec = float(os.getenv("CURSOR_LAUNCH_INTERVAL_SEC", default_interval))
        except Exception:
            self._launch_interval_sec = 5.0
    
    def open_cursor_with_project(self, project_path: str, cursor_exe: str) -> bool:
        """
        Открывает Cursor с указанным проектом
        
        Args:
            project_path: Путь к проекту
            cursor_exe: Путь к исполняемому файлу Cursor
            
        Returns:
            bool: Успешность запуска
        """
        if not cursor_exe:
            print("❌ Путь к Cursor не указан")
            return False
        
        if not os.path.isfile(cursor_exe):
            print(f"❌ Файл Cursor не найден: {cursor_exe}")
            return False
        
        if not self._validate_pre_launch_conditions(project_path):
            return False
        
        # Применяем троттлинг
        self._throttle_before_launch(os.path.basename(project_path))
        
        print(f"🚀 Запуск Cursor для проекта: {project_path}")
        
        try:
            if self.os_type == "windows":
                return self._launch_cursor_windows(cursor_exe, project_path)
            elif self.os_type == "linux":
                return self._launch_cursor_linux(cursor_exe, project_path)
            elif self.os_type == "darwin":
                return self._launch_cursor_macos(cursor_exe, project_path)
            else:
                return self._launch_cursor_generic(cursor_exe, project_path)
                
        except Exception as e:
            print(f"❌ Ошибка запуска Cursor: {e}")
            return False
    
    def _launch_cursor_windows(self, cursor_exe: str, project_path: str) -> bool:
        """Запуск Cursor на Windows"""
        try:
            # Используем cmd для запуска, чтобы избежать проблем с путями
            cmd = f'"{cursor_exe}" "{project_path}"'
            
            # Используем subprocess с shell=True для корректной обработки путей
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(project_path)
            )
            
            print(f"✅ Cursor запущен (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска Cursor на Windows: {e}")
            return False
    
    def _launch_cursor_linux(self, cursor_exe: str, project_path: str) -> bool:
        """Запуск Cursor на Linux"""
        try:
            # Пытаемся запустить Cursor
            process = subprocess.Popen(
                [cursor_exe, project_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid  # Создаем новую группу процессов
            )
            
            print(f"✅ Cursor запущен на Linux (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска Cursor на Linux: {e}")
            
            # Попытка запуска через nohup
            try:
                subprocess.Popen(
                    ["nohup", cursor_exe, project_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("✅ Cursor запущен через nohup")
                return True
            except Exception as e2:
                print(f"❌ Ошибка запуска через nohup: {e2}")
                return False
    
    def _launch_cursor_macos(self, cursor_exe: str, project_path: str) -> bool:
        """Запуск Cursor на macOS"""
        try:
            # На macOS используем 'open' для запуска приложений
            if cursor_exe.endswith('.app'):
                # Если это .app bundle, используем open
                process = subprocess.Popen(
                    ["open", "-a", cursor_exe, project_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Если это обычный исполняемый файл
                process = subprocess.Popen(
                    [cursor_exe, project_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            print(f"✅ Cursor запущен на macOS (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска Cursor на macOS: {e}")
            return False
    
    def _launch_cursor_generic(self, cursor_exe: str, project_path: str) -> bool:
        """Универсальный запуск Cursor для неизвестных платформ"""
        try:
            process = subprocess.Popen(
                [cursor_exe, project_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print(f"✅ Cursor запущен (универсальный метод, PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка универсального запуска Cursor: {e}")
            return False
    
    def _validate_pre_launch_conditions(self, project_path: str) -> bool:
        """Проверяет условия перед запуском"""
        if not project_path:
            print("❌ Путь к проекту не указан")
            return False
        
        if not os.path.exists(project_path):
            print(f"❌ Путь к проекту не существует: {project_path}")
            return False
        
        if not os.path.isdir(project_path):
            print(f"❌ Указанный путь не является директорией: {project_path}")
            return False
        
        return True
    
    def _validate_project_window_match(self, project_path: str, hwnd: int) -> bool:
        """Проверяет соответствие окна проекту"""
        try:
            # Получаем имя проекта из пути
            project_name = os.path.basename(project_path).lower()
            
            # Получаем заголовок окна (это требует импорта Windows API)
            if self.os_type == "windows":
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Получаем заголовок окна
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return False
                    
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    window_title = buff.value.lower()
                    
                    # Проверяем, содержит ли заголовок имя проекта
                    return project_name in window_title
                    
                except Exception:
                    return False
            
            # Для других платформ пока просто возвращаем True
            return True
            
        except Exception:
            return False
    
    def _is_cursor_already_running_with_project(self, project_path: str) -> bool:
        """Проверяет, запущен ли уже Cursor с данным проектом"""
        try:
            project_name = os.path.basename(project_path).lower()
            
            if self.os_type == "windows":
                return self._check_windows_cursor_processes(project_name)
            elif self.os_type == "linux":
                return self._check_linux_cursor_processes(project_name)
            elif self.os_type == "darwin":
                return self._check_macos_cursor_processes(project_name)
            
            return False
            
        except Exception:
            return False
    
    def _check_windows_cursor_processes(self, project_name: str) -> bool:
        """Проверяет процессы Cursor на Windows"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'cursor' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any(project_name in arg.lower() for arg in cmdline):
                            print(f"🔍 Найден запущенный Cursor для проекта: {project_name}")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            pass
        
        return False
    
    def _check_linux_cursor_processes(self, project_name: str) -> bool:
        """Проверяет процессы Cursor на Linux"""
        try:
            result = subprocess.run(
                ["pgrep", "-af", "cursor"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if project_name in line.lower():
                        print(f"🔍 Найден запущенный Cursor для проекта: {project_name}")
                        return True
                        
        except Exception:
            pass
        
        return False
    
    def _check_macos_cursor_processes(self, project_name: str) -> bool:
        """Проверяет процессы Cursor на macOS"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'cursor' in line.lower() and project_name in line.lower():
                        print(f"🔍 Найден запущенный Cursor для проекта: {project_name}")
                        return True
                        
        except Exception:
            pass
        
        return False
    
    def _throttle_before_launch(self, project_hint: str = None) -> None:
        """Применяет троттлинг между запусками Cursor"""
        with self._launch_lock:
            current_time = time.monotonic()
            time_since_last = current_time - self._last_launch_monotonic
            
            if time_since_last < self._launch_interval_sec:
                sleep_time = self._launch_interval_sec - time_since_last
                print(f"⏳ Троттлинг: ожидание {sleep_time:.1f} сек перед запуском...")
                time.sleep(sleep_time)
            
            self._last_launch_monotonic = time.monotonic()
            
            # Дополнительная пауза после запуска
            extra_gap = float(os.getenv("CURSOR_EXTRA_LAUNCH_GAP_SEC", "2.0"))
            if extra_gap > 0:
                print(f"⏳ Дополнительная пауза: {extra_gap} сек...")
                time.sleep(extra_gap)



