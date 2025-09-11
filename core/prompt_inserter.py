# -*- coding: utf-8 -*-

"""
Модуль для автоматической вставки промптов в Cursor
"""

import os
import time
import platform
import ctypes
from ctypes import wintypes
from typing import Optional, Union

# Проверяем доступность pyautogui
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class PromptInserter:
    """Класс для автоматической вставки промптов в Cursor"""
    
    def __init__(self, clipboard_manager, window_manager):
        self.clipboard_manager = clipboard_manager
        self.window_manager = window_manager
        self.os_type = platform.system().lower()
        
        # Настройки из переменных окружения
        self.chat_ready_delay = float(os.getenv("CURSOR_CHAT_READY_DELAY_SEC", "4.0"))
        self.stabilization_checks = int(os.getenv("CURSOR_STABILIZATION_CHECKS", "3"))
        self.stabilization_delay = float(os.getenv("CURSOR_STABILIZATION_DELAY_SEC", "0.25"))
        self.paste_enter_delay = float(os.getenv("CURSOR_PASTE_ENTER_DELAY_SEC", "1.0"))
        self.cursor_ready_checks = int(os.getenv("CURSOR_CURSOR_READY_CHECKS", "5"))
        self.paste_retry_attempts = int(os.getenv("CURSOR_PASTE_RETRY_ATTEMPTS", "3"))
        self.cursor_ready_check_delay = float(os.getenv("CURSOR_CURSOR_READY_CHECK_DELAY", "0.5"))
        self.diagnostic_mode = bool(int(os.getenv("CURSOR_DIAGNOSTIC_MODE", "0")))
        
        # Инициализация Windows API для кликов
        if self.os_type == "windows":
            self._init_windows_click_api()
    
    def _init_windows_click_api(self):
        """Инициализация Windows API для кликов"""
        try:
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
            # Структуры для ввода
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [("dx", ctypes.c_long),
                           ("dy", ctypes.c_long),
                           ("mouseData", wintypes.DWORD),
                           ("dwFlags", wintypes.DWORD),
                           ("time", wintypes.DWORD),
                           ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
            
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [("wVk", wintypes.WORD),
                           ("wScan", wintypes.WORD),
                           ("dwFlags", wintypes.DWORD),
                           ("time", wintypes.DWORD),
                           ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
            
            class HARDWAREINPUT(ctypes.Structure):
                _fields_ = [("uMsg", wintypes.DWORD),
                           ("wParamL", wintypes.WORD),
                           ("wParamH", wintypes.WORD)]
            
            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    _fields_ = [("ki", KEYBDINPUT),
                               ("mi", MOUSEINPUT),
                               ("hi", HARDWAREINPUT)]
                _fields_ = [("type", wintypes.DWORD),
                           ("ii", _INPUT)]
            
            self.POINT = POINT
            self.MOUSEINPUT = MOUSEINPUT
            self.INPUT = INPUT
            
            # Константы
            self.INPUT_MOUSE = 0
            self.MOUSEEVENTF_LEFTDOWN = 0x0002
            self.MOUSEEVENTF_LEFTUP = 0x0004
            self.MOUSEEVENTF_ABSOLUTE = 0x8000
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации Windows API для кликов: {e}")
    
    def auto_paste_prompt(self, delay_seconds: int = 5) -> bool:
        """
        Автоматически вставляет промпт в активное окно Cursor
        
        Args:
            delay_seconds: Задержка перед вставкой
            
        Returns:
            bool: Успешность вставки
        """
        if not PYAUTOGUI_AVAILABLE:
            print("❌ pyautogui недоступен для автовставки")
            return False
        
        print(f"⏳ Автовставка промпта через {delay_seconds} секунд...")
        print("💡 Убедитесь, что Cursor активен и курсор находится в поле ввода")
        
        # Обратный отсчет
        for i in range(delay_seconds, 0, -1):
            print(f"⏰ {i}...")
            time.sleep(1)
        
        try:
            print("📝 Вставка промпта...")
            
            # Вставляем текст через Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # Нажимаем Enter
            pyautogui.press('enter')
            
            print("✅ Промпт отправлен!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка автовставки: {e}")
            return False
    
    def open_project_and_paste_prompt(self, project_path: str, prompt: str, 
                                    root_widget, cursor_exe: str = None,
                                    paste_delay: int = 5, max_retries: int = 3) -> bool:
        """
        Открывает проект в Cursor и вставляет промпт
        
        Args:
            project_path: Путь к проекту
            prompt: Промпт для вставки
            root_widget: Корневой виджет для буфера обмена
            cursor_exe: Путь к исполняемому файлу Cursor
            paste_delay: Задержка перед вставкой
            max_retries: Количество попыток
            
        Returns:
            bool: Успешность операции
        """
        if not cursor_exe:
            print("❌ Путь к Cursor не указан")
            return False
        
        print(f"🚀 Запуск процесса для проекта: {os.path.basename(project_path)}")
        
        # Копируем промпт в буфер обмена
        if not self.clipboard_manager.copy_to_clipboard(prompt, root_widget):
            print("❌ Не удалось скопировать промпт в буфер обмена")
            return False
        
        # Устанавливаем подсказку для поиска окна
        project_hint = os.path.basename(project_path)
        self.window_manager.set_window_hint(project_hint)
        
        # Проверяем, есть ли уже запущенный Cursor для этого проекта
        existing_pid = self.window_manager._find_cursor_process_for_project(project_path)
        
        if existing_pid:
            print(f"🔍 Найден существующий процесс Cursor: PID {existing_pid}")
            
            # Получаем дескриптор окна по PID
            hwnd = self.window_manager._get_window_handle_by_pid(existing_pid)
            if hwnd:
                print(f"✅ Активация существующего окна: {hwnd}")
                
                if self.window_manager._ensure_window_active(hwnd):
                    # Даем время на активацию и готовность чата
                    time.sleep(self.chat_ready_delay)
                    
                    # Пытаемся вставить промпт
                    return self._paste_prompt_with_retry(hwnd)
                else:
                    print("⚠️ Не удалось активировать существующее окно")
        
        # Если существующего окна нет, запускаем новый Cursor
        from core.cursor_launcher import CursorLauncher
        launcher = CursorLauncher()
        
        if not launcher.open_cursor_with_project(project_path, cursor_exe):
            print("❌ Не удалось запустить Cursor")
            return False
        
        # Ждем готовности приложения
        app_ready_timeout = int(os.getenv("CURSOR_APP_READY_TIMEOUT_SEC", "10"))
        hwnd = self.window_manager._wait_for_cursor_app_ready(app_ready_timeout)
        
        if not hwnd:
            print("❌ Cursor не готов к работе")
            return False
        
        # Активируем чат и вставляем промпт
        if self._activate_chat_in_cursor(hwnd):
            return self._paste_prompt_with_retry(hwnd)
        else:
            print("❌ Не удалось активировать чат в Cursor")
            return False
    
    def _activate_chat_in_cursor(self, hwnd: int) -> bool:
        """Активирует чат в Cursor"""
        print("💬 Активация чата в Cursor...")
        
        # Проверяем, что окно активно
        if not self.window_manager._ensure_window_active(hwnd):
            print("❌ Не удалось активировать окно")
            return False
        
        # Пробуем разные методы активации чата
        methods = []
        
        # Метод 1: Клик в область чата
        if self.os_type == "windows":
            methods.append(lambda: self._click_on_chat_area())
        
        # Метод 2: Гарантированная активация чата
        methods.append(lambda: self._try_guaranteed_chat_activation(hwnd))
        
        # Метод 3: Активация через клавиатуру
        methods.append(lambda: self._activate_chat_by_keyboard(hwnd))
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Попытка активации чата (метод {i})...")
                if method():
                    print(f"✅ Чат активирован методом {i}")
                    time.sleep(self.chat_ready_delay)
                    return True
            except Exception as e:
                print(f"⚠️ Ошибка метода {i}: {e}")
                continue
        
        print("❌ Не удалось активировать чат ни одним методом")
        return False
    
    def _click_on_chat_area(self) -> bool:
        """Кликает в область чата"""
        if not PYAUTOGUI_AVAILABLE or self.os_type != "windows":
            return False
        
        try:
            # Получаем размеры экрана
            screen_width, screen_height = pyautogui.size()
            
            # Кликаем в предполагаемую область чата (правая часть экрана)
            chat_x = int(screen_width * 0.75)
            chat_y = int(screen_height * 0.8)
            
            print(f"🖱️ Клик в область чата: ({chat_x}, {chat_y})")
            pyautogui.click(chat_x, chat_y)
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка клика в область чата: {e}")
            return False
    
    def _try_guaranteed_chat_activation(self, hwnd: int) -> bool:
        """Гарантированная активация чата"""
        try:
            # Используем комбинацию клавиш для активации чата
            if PYAUTOGUI_AVAILABLE:
                # Ctrl+L часто активирует чат в редакторах кода
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.3)
                
                # Альтернативно: Ctrl+Shift+P для командной палитры
                pyautogui.hotkey('ctrl', 'shift', 'p')
                time.sleep(0.3)
                pyautogui.press('escape')  # Закрываем палитру
                time.sleep(0.3)
                
                # Tab для навигации к чату
                pyautogui.press('tab')
                time.sleep(0.2)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Ошибка гарантированной активации: {e}")
            return False
    
    def _activate_chat_by_keyboard(self, hwnd: int) -> bool:
        """Активирует чат через клавиатуру"""
        try:
            if not PYAUTOGUI_AVAILABLE:
                return False
            
            # Фокусируемся на окне
            if self.os_type == "windows":
                self.user32.SetForegroundWindow(hwnd)
                time.sleep(0.2)
            
            # Пробуем разные комбинации клавиш
            key_combinations = [
                ['ctrl', 'j'],           # Обычная комбинация для терминала/чата
                ['ctrl', 'shift', 'grave'],  # Backtick для терминала
                ['ctrl', 'shift', '`'],      # Альтернативный backtick
                ['f1'],                      # Помощь/чат
                ['ctrl', 'shift', 'p'],      # Командная палитра
            ]
            
            for combo in key_combinations:
                try:
                    print(f"⌨️ Пробуем комбинацию: {'+'.join(combo)}")
                    pyautogui.hotkey(*combo)
                    time.sleep(0.5)
                    
                    # Если открылась командная палитра, закрываем её
                    if combo == ['ctrl', 'shift', 'p']:
                        pyautogui.press('escape')
                        time.sleep(0.3)
                    
                    # Пробуем активировать чат
                    pyautogui.press('tab')
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"⚠️ Ошибка комбинации {combo}: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка активации через клавиатуру: {e}")
            return False
    
    def _paste_prompt_with_retry(self, hwnd: int) -> bool:
        """Вставляет промпт с повторными попытками"""
        print("📝 Вставка промпта в чат...")
        
        for attempt in range(1, self.paste_retry_attempts + 1):
            print(f"🔄 Попытка вставки {attempt}/{self.paste_retry_attempts}")
            
            try:
                # Проверяем готовность курсора
                if not self._check_cursor_ready():
                    print("⚠️ Курсор не готов к вводу")
                    continue
                
                # Выполняем вставку
                if self._perform_paste():
                    print("✅ Промпт успешно вставлен!")
                    return True
                
            except Exception as e:
                print(f"⚠️ Ошибка попытки {attempt}: {e}")
            
            # Пауза между попытками
            if attempt < self.paste_retry_attempts:
                time.sleep(1.0)
        
        print("❌ Не удалось вставить промпт после всех попыток")
        return False
    
    def _check_cursor_ready(self) -> bool:
        """Проверяет готовность курсора к вводу"""
        for check in range(self.cursor_ready_checks):
            try:
                if PYAUTOGUI_AVAILABLE:
                    # Проверяем стабильность позиции курсора
                    pos1 = pyautogui.position()
                    time.sleep(self.cursor_ready_check_delay)
                    pos2 = pyautogui.position()
                    
                    # Если курсор стабилен, считаем готовым
                    if pos1 == pos2:
                        print(f"✅ Курсор готов (позиция: {pos1})")
                        return True
                
                time.sleep(self.stabilization_delay)
                
            except Exception as e:
                if self.diagnostic_mode:
                    print(f"⚠️ Ошибка проверки курсора: {e}")
                continue
        
        print("⚠️ Курсор нестабилен или не готов")
        return False
    
    def _perform_paste(self) -> bool:
        """Выполняет фактическую вставку промпта"""
        try:
            if not PYAUTOGUI_AVAILABLE:
                print("❌ pyautogui недоступен для вставки")
                return False
            
            # Очищаем поле ввода
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            # Вставляем текст из буфера обмена
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(self.paste_enter_delay)
            
            # Нажимаем Enter для отправки
            pyautogui.press('enter')
            
            print("✅ Промпт отправлен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка вставки промпта: {e}")
            return False



