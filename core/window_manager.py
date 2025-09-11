# -*- coding: utf-8 -*-

"""
Модуль для работы с окнами Cursor
"""

import os
import time
import platform
import ctypes
from ctypes import wintypes
from typing import Optional, List, Dict, Any


class WindowManager:
    """Класс для работы с окнами Cursor"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self._preferred_window_hint = None
        
        # Инициализация Windows API, если доступно
        if self.os_type == "windows":
            self._init_windows_api()
    
    def _init_windows_api(self):
        """Инициализация Windows API"""
        try:
            # Основные функции Windows API
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
            # Типы данных
            self.HWND = ctypes.c_void_p
            self.DWORD = wintypes.DWORD
            self.BOOL = wintypes.BOOL
            
            # Константы
            self.SW_RESTORE = 9
            self.SW_SHOW = 5
            self.SW_MAXIMIZE = 3
            self.HWND_TOP = 0
            self.HWND_TOPMOST = ctypes.c_void_p(-1).value if hasattr(ctypes.c_void_p, 'value') else -1
            self.HWND_NOTOPMOST = ctypes.c_void_p(-2).value if hasattr(ctypes.c_void_p, 'value') else -2
            self.SWP_NOMOVE = 0x0002
            self.SWP_NOSIZE = 0x0001
            self.SWP_SHOWWINDOW = 0x0040
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации Windows API: {e}")
    
    def set_window_hint(self, hint: str | None):
        """Устанавливает подсказку для выбора окна Cursor"""
        self._preferred_window_hint = hint
        if hint:
            print(f"🎯 Установлена подсказка для окна: {hint}")
    
    def _find_cursor_process_for_project(self, project_path: str) -> int | bool:
        """Находит процесс Cursor для конкретного проекта"""
        if self.os_type != "windows":
            return False
        
        try:
            import psutil
            
            project_name = os.path.basename(project_path).lower()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if not proc_info['name'] or 'cursor' not in proc_info['name'].lower():
                        continue
                    
                    cmdline = proc_info['cmdline']
                    if not cmdline:
                        continue
                    
                    # Проверяем аргументы командной строки
                    for arg in cmdline:
                        if project_name in arg.lower() or project_path.lower() in arg.lower():
                            print(f"🎯 Найден процесс Cursor для проекта {project_name}: PID {proc_info['pid']}")
                            return proc_info['pid']
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print(f"❌ Не найден процесс Cursor для проекта: {project_name}")
            return False
            
        except ImportError:
            print("⚠️ psutil не доступен для поиска процессов")
            return False
        except Exception as e:
            print(f"⚠️ Ошибка поиска процесса: {e}")
            return False
    
    def _get_window_handle_by_pid(self, pid: int) -> int | bool:
        """Получает дескриптор окна по PID процесса"""
        if self.os_type != "windows":
            return False
        
        try:
            EnumWindows = self.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(self.BOOL, self.HWND, ctypes.POINTER(ctypes.c_int))
            GetWindowThreadProcessId = self.user32.GetWindowThreadProcessId
            IsWindowVisible = self.user32.IsWindowVisible
            
            found_hwnd = None
            
            def enum_proc(hwnd, lParam):
                nonlocal found_hwnd
                try:
                    if not IsWindowVisible(hwnd):
                        return True
                    
                    window_pid = self.DWORD()
                    GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                    
                    if window_pid.value == pid:
                        found_hwnd = int(hwnd)
                        return False  # Останавливаем перебор
                    
                except Exception:
                    pass
                
                return True
            
            EnumWindows(EnumWindowsProc(enum_proc), 0)
            
            if found_hwnd:
                print(f"✅ Найдено окно для PID {pid}: {found_hwnd}")
                return found_hwnd
            else:
                print(f"❌ Не найдено окно для PID {pid}")
                return False
                
        except Exception as e:
            print(f"⚠️ Ошибка получения окна по PID: {e}")
            return False
    
    def _bring_cursor_window_to_front_old(self) -> int | bool:
        """Старый метод поиска и активации окна Cursor"""
        if self.os_type != "windows":
            return False
        
        try:
            EnumWindows = self.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(self.BOOL, self.HWND, ctypes.POINTER(ctypes.c_int))
            GetWindowTextW = self.user32.GetWindowTextW
            GetWindowTextLengthW = self.user32.GetWindowTextLengthW
            IsWindowVisible = self.user32.IsWindowVisible
            
            target_hwnd = 0
            fallback_hwnd = 0
            all_cursor_windows = []
            preferred = (self._preferred_window_hint or "").lower()
            
            def enum_proc(hwnd, lParam):
                nonlocal target_hwnd
                nonlocal fallback_hwnd
                
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
                        all_cursor_windows.append((hwnd, title))
                        
                        if not fallback_hwnd:
                            fallback_hwnd = int(hwnd)
                            print(f"📱 Найдено окно Cursor (fallback): '{title}'")
                        
                        if preferred:
                            if preferred in tl:
                                target_hwnd = int(hwnd)
                                print(f"🎯 ТОЧНОЕ совпадение окна Cursor: '{title}' для проекта '{preferred}'")
                                return False  # нашли точный матч
                            
                            # Проверяем части имени проекта (более гибко)
                            hint_parts = preferred.replace('_', ' ').replace('-', ' ').split()
                            matching_parts = 0
                            for part in hint_parts:
                                if len(part) > 2 and part.lower() in tl.lower():
                                    matching_parts += 1
                            
                            total_parts = len(hint_parts)
                            if total_parts > 0 and matching_parts >= max(1, total_parts // 2):
                                if not target_hwnd:
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
            
            # Логика выбора окна
            if preferred and not target_hwnd:
                print(f"⚠️ Не найдено окно Cursor для проекта '{preferred}'")
                print("❌ Промпт НЕ будет отправлен в случайное окно!")
                print("💡 СОВЕТ: Убедитесь, что проект открыт в Cursor и заголовок окна содержит имя проекта")
                return False
            
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
                        GetWindowTextW(hwnd, buf, length + 1)
                        window_title = buf.value or ""
                except Exception:
                    pass
                
                print(f"🎯 ВЫБРАНО окно: '{window_title}' (HWND: {target_hwnd})")
            
            # Активируем выбранное окно
            return self._ensure_window_active(target_hwnd)
            
        except Exception as e:
            print(f"❌ Ошибка поиска окна Cursor: {e}")
            return False
    
    def _ensure_window_active(self, hwnd: int | bool, timeout_s: float = 2.0) -> bool:
        """Обеспечивает активность указанного окна"""
        if not hwnd or self.os_type != "windows":
            return False
        
        try:
            hwnd = int(hwnd)
            
            # Проверяем, что окно существует
            if not self.user32.IsWindow(hwnd):
                print(f"❌ Окно {hwnd} не существует")
                return False
            
            print(f"🎯 Активация окна {hwnd}...")
            
            # Восстанавливаем окно, если оно свернуто
            if self.user32.IsIconic(hwnd):
                self.user32.ShowWindow(hwnd, self.SW_RESTORE)
                time.sleep(0.3)
            
            # Выводим окно на передний план
            self.user32.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            
            # Дополнительные попытки активации
            self.user32.BringWindowToTop(hwnd)
            self.user32.SetActiveWindow(hwnd)
            self.user32.SetFocus(hwnd)
            
            # Проверяем результат
            start_time = time.time()
            while time.time() - start_time < timeout_s:
                if self.user32.GetForegroundWindow() == hwnd:
                    # Делаем окно всегда поверх
                    try:
                        self.user32.SetWindowPos(
                            hwnd,
                            self.HWND_TOPMOST,
                            0, 0, 0, 0,
                            self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW
                        )
                    except Exception:
                        pass
                    print(f"✅ Окно {hwnd} успешно активировано")
                    return hwnd
                time.sleep(0.1)
            
            print(f"⚠️ Окно {hwnd} могло не активироваться полностью")
            # В любом случае поднимаем окно наверх как TOPMOST
            try:
                self.user32.SetWindowPos(
                    hwnd,
                    self.HWND_TOPMOST,
                    0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW
                )
            except Exception:
                pass
            return hwnd  # Возвращаем hwnd даже если не уверены в активации
            
        except Exception as e:
            print(f"❌ Ошибка активации окна: {e}")
            return False
    
    def _wait_for_cursor_app_ready(self, timeout_sec: int = 30) -> int | bool:
        """Ожидает готовности приложения Cursor"""
        print(f"⏳ Ожидание готовности Cursor (таймаут: {timeout_sec} сек)...")
        
        start_time = time.time()
        check_interval = 1.0
        
        while time.time() - start_time < timeout_sec:
            # Ищем окно Cursor
            hwnd = self._bring_cursor_window_to_front_old()
            if hwnd:
                # Дополнительная пауза для загрузки интерфейса
                interface_delay = float(os.getenv("CURSOR_INTERFACE_READY_DELAY_SEC", "5.0"))
                print(f"⏳ Пауза для загрузки интерфейса: {interface_delay} сек...")
                time.sleep(interface_delay)
                
                print(f"✅ Cursor готов к работе (окно: {hwnd})")
                return hwnd
            
            print(f"🔄 Курсор пока не готов, повтор через {check_interval} сек...")
            time.sleep(check_interval)
        
        print(f"❌ Таймаут ожидания готовности Cursor ({timeout_sec} сек)")
        
        # Fallback: резервная пауза
        fallback_delay = float(os.getenv("CURSOR_FALLBACK_DELAY_SEC", "12.0"))
        print(f"⏳ Резервная пауза: {fallback_delay} сек...")
        time.sleep(fallback_delay)
        
        # Последняя попытка найти окно
        hwnd = self._bring_cursor_window_to_front_old()
        if hwnd:
            print(f"✅ Cursor найден после fallback паузы (окно: {hwnd})")
            return hwnd
        
        return False
    
    def _force_window_to_front_and_position(self, hwnd: int):
        """Принудительно выводит окно на передний план и позиционирует"""
        if self.os_type != "windows" or not hwnd:
            return
        
        try:
            # Получаем информацию о дисплее
            user32 = self.user32
            
            # Восстанавливаем окно
            user32.ShowWindow(hwnd, self.SW_RESTORE)
            time.sleep(0.2)
            
            # Получаем размеры экрана
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # Позиционируем окно в центре
            window_width = int(screen_width * 0.8)
            window_height = int(screen_height * 0.8)
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Перемещаем и изменяем размер окна
            user32.SetWindowPos(
                hwnd, self.HWND_TOP, x, y, window_width, window_height,
                0  # SWP_SHOWWINDOW
            )
            
            # Принудительно активируем
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
            user32.SetActiveWindow(hwnd)
            # Всегда поверх всех окон
            try:
                user32.SetWindowPos(
                    hwnd,
                    self.HWND_TOPMOST,
                    0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW
                )
            except Exception:
                pass
            
            print(f"✅ Окно {hwnd} принудительно активировано и позиционировано")
            
        except Exception as e:
            print(f"⚠️ Ошибка принудительного позиционирования: {e}")
    
    def _position_new_cursor_window(self):
        """Позиционирует новое окно Cursor"""
        if self.os_type != "windows":
            return
        
        try:
            time.sleep(1.0)  # Ждем появления окна
            
            EnumWindows = self.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(self.BOOL, self.HWND, ctypes.POINTER(ctypes.c_int))
            GetWindowTextW = self.user32.GetWindowTextW
            GetWindowTextLengthW = self.user32.GetWindowTextLengthW
            IsWindowVisible = self.user32.IsWindowVisible
            
            latest_hwnd = None
            latest_time = 0
            
            def enum_proc(hwnd, lParam):
                nonlocal latest_hwnd, latest_time
                
                try:
                    if not IsWindowVisible(hwnd):
                        return True
                    
                    length = GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return True
                    
                    buf = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value or ""
                    
                    if 'cursor' in title.lower():
                        # Простая эвристика: последнее найденное окно
                        latest_hwnd = int(hwnd)
                        latest_time = time.time()
                
                except Exception:
                    pass
                
                return True
            
            EnumWindows(EnumWindowsProc(enum_proc), 0)
            
            if latest_hwnd:
                self._force_window_to_front_and_position(latest_hwnd)
                
        except Exception as e:
            print(f"⚠️ Ошибка позиционирования нового окна: {e}")
    
    def _validate_cursor_window(self, hwnd: int, expected_project_hint: str) -> bool:
        """Проверяет, что окно Cursor соответствует ожидаемому проекту"""
        if self.os_type != "windows" or not hwnd:
            return False
        
        try:
            length = self.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return False
            
            buf = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buf, length + 1)
            window_title = buf.value or ""
            
            if not expected_project_hint:
                return 'cursor' in window_title.lower()
            
            return expected_project_hint.lower() in window_title.lower()
            
        except Exception:
            return False
    
    def get_all_cursor_windows(self) -> List[Dict[str, Any]]:
        """Получает список всех окон Cursor"""
        if self.os_type != "windows":
            return []
        
        windows = []
        
        try:
            EnumWindows = self.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(self.BOOL, self.HWND, ctypes.POINTER(ctypes.c_int))
            GetWindowTextW = self.user32.GetWindowTextW
            GetWindowTextLengthW = self.user32.GetWindowTextLengthW
            IsWindowVisible = self.user32.IsWindowVisible
            
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
                    
                    if 'cursor' in title.lower():
                        windows.append({
                            'hwnd': int(hwnd),
                            'title': title,
                            'visible': True
                        })
                
                except Exception:
                    pass
                
                return True
            
            EnumWindows(EnumWindowsProc(enum_proc), 0)
            
        except Exception as e:
            print(f"⚠️ Ошибка получения списка окон: {e}")
        
        return windows
