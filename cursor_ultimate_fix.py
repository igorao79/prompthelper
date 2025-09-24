#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ФИНАЛЬНАЯ СУПЕР-НАДЕЖНАЯ СИСТЕМА CURSOR
Интегрируется в основной CursorManager и гарантирует 100% работу
"""

import time
import ctypes
import platform
from typing import Optional

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = False
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import win32clipboard
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class CursorUltimateFix:
    """Финальная супер-надежная система для Cursor"""
    
    def __init__(self):
        if platform.system().lower() != 'windows':
            print("⚠️ Ультимейт система работает только на Windows")
            return
        
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Константы Windows API
        self.SW_RESTORE = 9
        self.SW_SHOW = 5
        self.HWND_TOPMOST = -1
        self.HWND_NOTOPMOST = -2
        self.SWP_NOSIZE = 0x0001
        self.SWP_NOMOVE = 0x0002
        self.SWP_SHOWWINDOW = 0x0040
        self.SWP_FRAMECHANGED = 0x0020
        
        print("🚀 CursorUltimateFix инициализирован")
    
    def copy_to_clipboard_ultimate(self, text: str) -> bool:
        """Супер-надежное копирование в буфер обмена"""
        methods = []
        
        if WIN32_AVAILABLE:
            methods.append(self._copy_win32)
        
        if PYAUTOGUI_AVAILABLE:
            methods.append(self._copy_pyautogui)
        
        methods.append(self._copy_tkinter)
        
        for method in methods:
            try:
                if method(text):
                    return True
            except Exception:
                continue
        
        return False
    
    def _copy_win32(self, text: str) -> bool:
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return False
    
    def _copy_pyautogui(self, text: str) -> bool:
        try:
            pyautogui.copy(text)
            return True
        except Exception:
            return False
    
    def _copy_tkinter(self, text: str) -> bool:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            return False
    
    def activate_window_ultimate(self, hwnd: int) -> bool:
        """СУПЕР-АГРЕССИВНАЯ активация окна"""
        try:
            # Восстанавливаем если свернуто
            if self.user32.IsIconic(hwnd):
                self.user32.ShowWindow(hwnd, self.SW_RESTORE)
                time.sleep(0.1)
            
            # Делаем видимым
            self.user32.ShowWindow(hwnd, self.SW_SHOW)
            time.sleep(0.1)
            
            # Присоединяем потоки для прав
            current_thread = self.kernel32.GetCurrentThreadId()
            window_thread = self.user32.GetWindowThreadProcessId(hwnd, None)
            
            if window_thread != current_thread:
                self.user32.AttachThreadInput(current_thread, window_thread, True)
            
            # ТОПМОСТ режим
            self.user32.SetWindowPos(
                hwnd, self.HWND_TOPMOST, 0, 0, 0, 0,
                self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW | self.SWP_FRAMECHANGED
            )
            time.sleep(0.1)
            
            # Активируем
            self.user32.SetForegroundWindow(hwnd)
            self.user32.SetActiveWindow(hwnd)
            self.user32.SetFocus(hwnd)
            time.sleep(0.1)
            
            # Отключаем ТОПМОСТ
            self.user32.SetWindowPos(
                hwnd, self.HWND_NOTOPMOST, 0, 0, 0, 0,
                self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW | self.SWP_FRAMECHANGED
            )
            
            # Финальная активация
            self.user32.SetForegroundWindow(hwnd)
            
            # Отсоединяем потоки
            if window_thread != current_thread:
                self.user32.AttachThreadInput(current_thread, window_thread, False)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка активации: {e}")
            return False
    
    def find_cursor_window(self, project_hint: str = None) -> Optional[int]:
        """Находит окно Cursor с учетом проекта"""
        found_windows = []
        
        def enum_proc(hwnd, lParam):
            try:
                buffer = ctypes.create_unicode_buffer(512)
                length = self.user32.GetWindowTextW(hwnd, buffer, 512)
                
                if length == 0:
                    return True
                
                title = buffer.value
                
                if 'cursor' not in title.lower():
                    return True
                
                # Сохраняем все окна Cursor
                found_windows.append((hwnd, title))
                return True
                
            except Exception:
                return True
        
        # Ищем все окна
        self.user32.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(enum_proc),
            0
        )
        
        if not found_windows:
            print("❌ Не найдено окон Cursor")
            return None
        
        # Если проект указан, ищем точное совпадение
        if project_hint:
            project_lower = project_hint.lower()
            for hwnd, title in found_windows:
                if project_lower in title.lower():
                    print(f"✅ Найдено окно проекта: '{title}'")
                    return hwnd
        
        # Берем первое найденное
        hwnd, title = found_windows[0]
        print(f"✅ Найдено окно Cursor: '{title}'")
        return hwnd
    
    def paste_prompt_ultimate(self) -> bool:
        """Супер-надежная вставка промпта"""
        if not PYAUTOGUI_AVAILABLE:
            print("❌ pyautogui недоступен")
            return False
        
        try:
            # Пауза для стабильности
            time.sleep(1.0)
            
            # Вставляем промпт
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # Дублирующая вставка
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Отправляем
            pyautogui.press('enter')
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка вставки: {e}")
            return False
    
    def generate_and_paste_prompt_ultimate(self, prompt: str, project_hint: str = None) -> tuple:
        """
        ГЛАВНАЯ ФУНКЦИЯ: Супер-надежная генерация и вставка промпта
        
        Args:
            prompt: Текст промпта
            project_hint: Подсказка проекта
            
        Returns:
            tuple: (success: bool, message: str)
        """
        print("🚀 НАЧИНАЕМ СУПЕР-НАДЕЖНУЮ ОБРАБОТКУ ПРОМПТА")
        print("=" * 60)
        
        # ЭТАП 1: Копирование
        print("1️⃣ Копируем в буфер обмена...")
        if not self.copy_to_clipboard_ultimate(prompt):
            return False, "Не удалось скопировать в буфер обмена"
        print("✅ Промпт скопирован")
        
        # ЭТАП 2: Поиск окна
        print("2️⃣ Ищем окно Cursor...")
        hwnd = self.find_cursor_window(project_hint)
        if not hwnd:
            return False, "Не найдено окно Cursor"
        
        # ЭТАП 3: Активация
        print("3️⃣ Активируем окно...")
        if not self.activate_window_ultimate(hwnd):
            return False, "Не удалось активировать окно"
        print("✅ Окно активировано")
        
        # ЭТАП 4: Вставка
        print("4️⃣ Вставляем промпт...")
        if not self.paste_prompt_ultimate():
            return False, "Не удалось вставить промпт"
        print("✅ Промпт вставлен и отправлен")
        
        print("🎉 СУПЕР-НАДЕЖНАЯ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
        return True, "Промпт успешно вставлен"


# Патч для интеграции в существующий CursorManager
def patch_cursor_manager():
    """Применяет супер-надежные исправления к CursorManager"""
    
    # Создаем экземпляр ультимейт системы
    ultimate_fix = CursorUltimateFix()
    
    def ultimate_generate_and_paste_prompt(self, prompt: str, project_path = None, auto_paste: bool = True, root_widget = None):
        """Замена generate_and_paste_prompt на супер-надежную версию"""
        
        if not auto_paste:
            # Если автовставка отключена, просто копируем
            return ultimate_fix.copy_to_clipboard_ultimate(prompt), "Промпт скопирован в буфер"
        
        # Получаем подсказку проекта
        project_hint = None
        if project_path:
            import os
            project_hint = os.path.basename(str(project_path))
        elif hasattr(self, '_preferred_window_hint'):
            project_hint = self._preferred_window_hint
        
        # Используем супер-надежную систему
        success, message = ultimate_fix.generate_and_paste_prompt_ultimate(prompt, project_hint)
        return success, message
    
    return ultimate_generate_and_paste_prompt


def test_ultimate_fix():
    """Тестирует финальную супер-надежную систему"""
    print("🧪 ТЕСТ ФИНАЛЬНОЙ СУПЕР-НАДЕЖНОЙ СИСТЕМЫ CURSOR")
    print("=" * 70)
    
    try:
        ultimate = CursorUltimateFix()
        
        test_prompt = f"🧪 ТЕСТОВЫЙ ПРОМПТ финальной системы. Время: {time.time()}"
        
        print(f"\n📝 Тестовый промпт: {test_prompt}")
        print("\n⚠️ Убедитесь что у вас открыт Cursor!")
        print("🎯 Через 3 секунды начнется обработка...")
        
        for i in range(3, 0, -1):
            print(f"   ⏰ {i}...")
            time.sleep(1)
        
        print("\n🚀 ЗАПУСК ТЕСТА!")
        success, message = ultimate.generate_and_paste_prompt_ultimate(test_prompt, "prompttest")
        
        if success:
            print(f"\n🎉 ТЕСТ ПРОЙДЕН: {message}")
        else:
            print(f"\n❌ ТЕСТ ПРОВАЛЕН: {message}")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ultimate_fix()
    print("\n🔄 Нажмите Enter для выхода...")
    input()


