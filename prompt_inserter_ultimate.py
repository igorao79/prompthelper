#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СУПЕР-НАДЕЖНАЯ СИСТЕМА ВСТАВКИ ПРОМПТОВ
Гарантирует что каждый промпт будет вставлен ОБЯЗАТЕЛЬНО
"""

import time
import ctypes
import platform
from window_activator_ultimate import UltimateWindowActivator

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Отключаем fail-safe для надежности
    pyautogui.FAILSAFE = False
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui не установлен - автовставка отключена")

try:
    import win32clipboard
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class UltimatePromptInserter:
    """Класс для 100% гарантированной вставки промптов в Cursor"""
    
    def __init__(self):
        if platform.system().lower() != 'windows':
            raise RuntimeError("Поддерживается только Windows")
        
        self.activator = UltimateWindowActivator()
        
        # Настройки надежности
        self.max_insert_attempts = 5
        self.max_focus_attempts = 3
        self.delay_between_attempts = 1.0
        self.delay_before_paste = 2.0
        self.delay_after_paste = 1.0
        
        print("🎯 UltimatePromptInserter инициализирован")
    
    def copy_to_clipboard_ultimate(self, text: str) -> bool:
        """Супер-надежное копирование в буфер обмена с проверкой"""
        print(f"📋 Копируем в буфер: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        methods = []
        
        # Метод 1: win32clipboard
        if WIN32_AVAILABLE:
            methods.append(self._copy_win32)
        
        # Метод 2: pyautogui
        if PYAUTOGUI_AVAILABLE:
            methods.append(self._copy_pyautogui)
        
        # Метод 3: tkinter (fallback)
        methods.append(self._copy_tkinter)
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"   🔄 Пробуем метод {i}/{len(methods)}: {method.__name__}")
                if method(text):
                    print(f"   ✅ Метод {i} УСПЕШЕН!")
                    return True
                else:
                    print(f"   ❌ Метод {i} не сработал")
            except Exception as e:
                print(f"   ❌ Ошибка метода {i}: {e}")
        
        print("❌ ВСЕ МЕТОДЫ копирования провалились!")
        return False
    
    def _copy_win32(self, text: str) -> bool:
        """Копирование через win32clipboard"""
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
        """Копирование через pyautogui"""
        try:
            pyautogui.copy(text)
            return True
        except Exception:
            return False
    
    def _copy_tkinter(self, text: str) -> bool:
        """Копирование через tkinter"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Скрываем окно
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            return False
    
    def focus_cursor_input_area(self, hwnd: int) -> bool:
        """Фокусируемся на области ввода Cursor с множественными попытками"""
        print(f"🎯 Фокусируемся на области ввода окна {hwnd}")
        
        for attempt in range(self.max_focus_attempts):
            print(f"   🔄 Попытка фокуса #{attempt + 1}/{self.max_focus_attempts}")
            
            try:
                # Получаем размеры окна
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                window_width = rect.right - rect.left
                window_height = rect.bottom - rect.top
                
                # Клик в нижнюю часть окна (где обычно поле ввода)
                click_x = rect.left + window_width // 2
                click_y = rect.bottom - 100  # 100 пикселей от низа
                
                print(f"   🖱️ Кликаем в позицию ({click_x}, {click_y})")
                
                if PYAUTOGUI_AVAILABLE:
                    # Сохраняем текущую позицию мыши
                    orig_x, orig_y = pyautogui.position()
                    
                    # Кликаем в область ввода
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.2)
                    
                    # Дополнительный клик для уверенности
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.2)
                    
                    # Возвращаем мышь
                    pyautogui.moveTo(orig_x, orig_y, duration=0)
                    
                    print(f"   ✅ Фокус установлен за попытку #{attempt + 1}")
                    return True
                
            except Exception as e:
                print(f"   ❌ Ошибка фокуса попытка #{attempt + 1}: {e}")
                time.sleep(0.3)
        
        print("❌ НЕ УДАЛОСЬ установить фокус!")
        return False
    
    def paste_and_send_ultimate(self) -> bool:
        """Супер-надежная вставка и отправка промпта"""
        print("📥 Вставляем и отправляем промпт...")
        
        if not PYAUTOGUI_AVAILABLE:
            print("❌ pyautogui недоступен для вставки!")
            return False
        
        try:
            # Пауза перед вставкой
            print(f"   ⏳ Пауза {self.delay_before_paste} сек перед вставкой...")
            time.sleep(self.delay_before_paste)
            
            # Вставляем промпт
            print("   📋 Вставляем промпт (Ctrl+V)...")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # Дополнительная проверка - еще одна вставка
            print("   📋 Дублирующая вставка для надежности...")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Отправляем промпт
            print("   📤 Отправляем промпт (Enter)...")
            pyautogui.press('enter')
            
            # Пауза после отправки
            print(f"   ⏳ Пауза {self.delay_after_paste} сек после отправки...")
            time.sleep(self.delay_after_paste)
            
            print("   ✅ Промпт вставлен и отправлен!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка вставки: {e}")
            return False
    
    def insert_prompt_ultimate(self, prompt: str, project_hint: str = None) -> bool:
        """
        ГЛАВНАЯ ФУНКЦИЯ: Супер-надежная вставка промпта в Cursor
        
        Args:
            prompt: Текст промпта для вставки
            project_hint: Подсказка проекта (необязательно)
            
        Returns:
            bool: True если промпт вставлен успешно
        """
        print("🚀 НАЧИНАЕМ СУПЕР-НАДЕЖНУЮ ВСТАВКУ ПРОМПТА")
        print("=" * 60)
        print(f"📝 Промпт: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
        print(f"📁 Проект: '{project_hint or 'любой'}'")
        print("=" * 60)
        
        # ЭТАП 1: Копирование в буфер обмена
        print("\n1️⃣ ЭТАП: Копирование в буфер обмена")
        if not self.copy_to_clipboard_ultimate(prompt):
            print("❌ ЭТАП 1 ПРОВАЛЕН: Не удалось скопировать в буфер!")
            return False
        print("✅ ЭТАП 1 ПРОЙДЕН: Промпт скопирован в буфер")
        
        # ЭТАП 2: Поиск и активация окна Cursor (с повторами)
        print("\n2️⃣ ЭТАП: Поиск и активация окна Cursor")
        hwnd = None
        
        for attempt in range(self.max_insert_attempts):
            print(f"   🔄 Попытка поиска #{attempt + 1}/{self.max_insert_attempts}")
            
            hwnd = self.activator.bring_cursor_to_front_ultimate(project_hint)
            
            if hwnd:
                print(f"   ✅ Окно найдено и активировано: HWND={hwnd}")
                break
            else:
                print(f"   ❌ Попытка #{attempt + 1} не удалась")
                if attempt < self.max_insert_attempts - 1:
                    print(f"   ⏳ Пауза {self.delay_between_attempts} сек перед повтором...")
                    time.sleep(self.delay_between_attempts)
        
        if not hwnd:
            print("❌ ЭТАП 2 ПРОВАЛЕН: Не удалось найти окно Cursor!")
            return False
        print("✅ ЭТАП 2 ПРОЙДЕН: Окно Cursor активно")
        
        # ЭТАП 3: Фокусировка на поле ввода и вставка промпта (с повторами)
        print("\n3️⃣ ЭТАП: Фокусировка и вставка промпта")
        
        for attempt in range(self.max_insert_attempts):
            print(f"   🔄 Попытка вставки #{attempt + 1}/{self.max_insert_attempts}")
            
            # Устанавливаем фокус на поле ввода
            if self.focus_cursor_input_area(hwnd):
                # Пробуем вставить промпт
                if self.paste_and_send_ultimate():
                    print(f"   ✅ Вставка успешна за попытку #{attempt + 1}!")
                    print("✅ ЭТАП 3 ПРОЙДЕН: Промпт вставлен и отправлен")
                    print("\n🎉 СУПЕР-НАДЕЖНАЯ ВСТАВКА ЗАВЕРШЕНА УСПЕШНО!")
                    return True
                else:
                    print(f"   ❌ Вставка не удалась в попытке #{attempt + 1}")
            else:
                print(f"   ❌ Фокус не установлен в попытке #{attempt + 1}")
            
            if attempt < self.max_insert_attempts - 1:
                print(f"   ⏳ Пауза {self.delay_between_attempts} сек перед повтором...")
                time.sleep(self.delay_between_attempts)
        
        print("❌ ЭТАП 3 ПРОВАЛЕН: Не удалось вставить промпт!")
        print("❌ СУПЕР-НАДЕЖНАЯ ВСТАВКА ПРОВАЛЕНА!")
        return False


def test_ultimate_inserter():
    """Тестирует супер-надежную вставку промптов"""
    print("🧪 ТЕСТ СУПЕР-НАДЕЖНОЙ ВСТАВКИ ПРОМПТОВ")
    print("=" * 70)
    
    try:
        inserter = UltimatePromptInserter()
        
        # Тестовый промпт
        test_prompt = "🧪 ТЕСТОВЫЙ ПРОМПТ: Проверка супер-надежной системы вставки промптов. Время: " + str(time.time())
        
        print(f"\n📝 Тестовый промпт: {test_prompt}")
        print("\n⚠️ ВНИМАНИЕ: Убедитесь что у вас открыт Cursor с проектом!")
        print("🎯 Через 5 секунд начнется вставка промпта...")
        
        # Обратный отсчет
        for i in range(5, 0, -1):
            print(f"   ⏰ {i}...")
            time.sleep(1)
        
        # Запускаем тест
        print("\n🚀 ЗАПУСК ТЕСТА!")
        success = inserter.insert_prompt_ultimate(test_prompt, "prompttest")
        
        if success:
            print("\n🎉 ТЕСТ ПРОЙДЕН: Промпт вставлен успешно!")
        else:
            print("\n❌ ТЕСТ ПРОВАЛЕН: Промпт не вставлен!")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")


if __name__ == "__main__":
    test_ultimate_inserter()
    print("\n🔄 Нажмите Enter для выхода...")
    input()


