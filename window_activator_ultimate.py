#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СУПЕР-НАДЕЖНЫЙ АКТИВАТОР ОКОН CURSOR
Гарантирует 100% активацию окна поверх всех остальных
"""

import ctypes
import time
import platform
from ctypes import wintypes

class UltimateWindowActivator:
    """Класс для 100% гарантированной активации окон Cursor"""
    
    def __init__(self):
        if platform.system().lower() != 'windows':
            raise RuntimeError("Поддерживается только Windows")
            
        # Константы Windows API
        self.SW_RESTORE = 9
        self.SW_SHOW = 5
        self.SW_MAXIMIZE = 3
        self.HWND_TOPMOST = -1
        self.HWND_NOTOPMOST = -2
        self.SWP_NOSIZE = 0x0001
        self.SWP_NOMOVE = 0x0002
        self.SWP_SHOWWINDOW = 0x0040
        self.SWP_FRAMECHANGED = 0x0020
        
        # API функции
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
    def force_window_to_absolute_top(self, hwnd: int, max_attempts: int = 10) -> bool:
        """
        СУПЕР-АГРЕССИВНАЯ активация окна - использует ВСЕ возможные методы
        """
        print(f"🚀 НАЧИНАЕМ СУПЕР-АГРЕССИВНУЮ АКТИВАЦИЮ ОКНА HWND={hwnd}")
        
        for attempt in range(max_attempts):
            print(f"   🔄 Попытка #{attempt + 1}/{max_attempts}")
            
            try:
                # ШАГ 1: Восстанавливаем окно если свернуто
                if self.user32.IsIconic(hwnd):
                    print("   📤 Восстанавливаем свернутое окно...")
                    self.user32.ShowWindow(hwnd, self.SW_RESTORE)
                    time.sleep(0.1)
                
                # ШАГ 2: Делаем окно видимым
                print("   👁️ Делаем окно видимым...")
                self.user32.ShowWindow(hwnd, self.SW_SHOW)
                time.sleep(0.1)
                
                # ШАГ 3: Получаем PID процесса окна
                process_id = wintypes.DWORD()
                self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                
                # ШАГ 4: Получаем текущий активный поток
                current_thread = self.kernel32.GetCurrentThreadId()
                window_thread = self.user32.GetWindowThreadProcessId(hwnd, None)
                
                # ШАГ 5: Присоединяем потоки для прав на активацию
                if window_thread != current_thread:
                    print("   🔗 Присоединяем потоки...")
                    self.user32.AttachThreadInput(current_thread, window_thread, True)
                
                # ШАГ 6: ТОПМОСТ РЕЖИМ (сначала включаем)
                print("   ⬆️ Включаем TOPMOST режим...")
                self.user32.SetWindowPos(
                    hwnd, self.HWND_TOPMOST, 0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW | self.SWP_FRAMECHANGED
                )
                time.sleep(0.1)
                
                # ШАГ 7: Активируем окно
                print("   🎯 Активируем окно...")
                success1 = self.user32.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                
                # ШАГ 8: Устанавливаем активное окно
                print("   ⚡ Устанавливаем как активное...")
                success2 = self.user32.SetActiveWindow(hwnd)
                time.sleep(0.05)
                
                # ШАГ 9: Устанавливаем фокус
                print("   🔍 Устанавливаем фокус...")
                success3 = self.user32.SetFocus(hwnd)
                time.sleep(0.05)
                
                # ШАГ 10: Отключаем TOPMOST (чтобы не мешал другим окнам)
                print("   ⬇️ Отключаем TOPMOST режим...")
                self.user32.SetWindowPos(
                    hwnd, self.HWND_NOTOPMOST, 0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW | self.SWP_FRAMECHANGED
                )
                time.sleep(0.05)
                
                # ШАГ 11: Финальная активация
                print("   🏁 Финальная активация...")
                final_success = self.user32.SetForegroundWindow(hwnd)
                
                # ШАГ 12: Отсоединяем потоки
                if window_thread != current_thread:
                    print("   🔌 Отсоединяем потоки...")
                    self.user32.AttachThreadInput(current_thread, window_thread, False)
                
                # Проверяем результат
                current_foreground = self.user32.GetForegroundWindow()
                if current_foreground == hwnd:
                    print(f"   ✅ УСПЕХ! Окно активировано за {attempt + 1} попыток")
                    return True
                else:
                    print(f"   ⚠️ Попытка {attempt + 1} не удалась. Активное окно: {current_foreground}")
                
                # Пауза между попытками
                time.sleep(0.2)
                
            except Exception as e:
                print(f"   ❌ Ошибка в попытке {attempt + 1}: {e}")
                time.sleep(0.3)
        
        print(f"❌ НЕ УДАЛОСЬ активировать окно за {max_attempts} попыток!")
        return False
    
    def bring_cursor_to_front_ultimate(self, project_hint: str = None) -> int:
        """
        Находит окно Cursor и ГАРАНТИРОВАННО выводит его на передний план
        """
        print(f"🔍 ПОИСК И СУПЕР-АКТИВАЦИЯ окна Cursor для проекта: '{project_hint}'")
        
        def enum_windows_proc(hwnd, lParam):
            try:
                # Получаем заголовок окна
                buffer = ctypes.create_unicode_buffer(512)
                length = self.user32.GetWindowTextW(hwnd, buffer, 512)
                
                if length == 0:
                    return True  # Продолжаем поиск
                    
                title = buffer.value.lower()
                
                # Проверяем что это Cursor
                if 'cursor' not in title:
                    return True
                
                print(f"🎯 Найдено окно Cursor: '{buffer.value}'")
                
                # Если указан проект, проверяем соответствие
                if project_hint:
                    project_lower = project_hint.lower()
                    if project_lower not in title:
                        print(f"   ⚠️ Проект не совпадает: ожидался '{project_hint}', найден '{buffer.value}'")
                        return True  # Продолжаем поиск
                
                print(f"   ✅ Найдено подходящее окно Cursor!")
                
                # СУПЕР-АКТИВАЦИЯ!
                if self.force_window_to_absolute_top(hwnd):
                    # Сохраняем найденный hwnd
                    ctypes.cast(lParam, ctypes.POINTER(ctypes.c_int)).contents = ctypes.c_int(hwnd)
                    return False  # Останавливаем поиск
                else:
                    print("   ❌ Не удалось активировать - продолжаем поиск...")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Ошибка при обработке окна {hwnd}: {e}")
                return True
        
        # Переменная для хранения результата
        result_hwnd = ctypes.c_int(0)
        
        # Запускаем поиск окон
        self.user32.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))(enum_windows_proc),
            ctypes.byref(result_hwnd)
        )
        
        final_hwnd = result_hwnd.value
        if final_hwnd:
            print(f"🎉 СУПЕР-АКТИВАЦИЯ ЗАВЕРШЕНА! HWND={final_hwnd}")
            return final_hwnd
        else:
            print("❌ НЕ НАЙДЕНО подходящих окон Cursor!")
            return 0


def test_ultimate_activator():
    """Тестирует супер-активатор окон"""
    print("🧪 ТЕСТ СУПЕР-АКТИВАТОРА ОКОН CURSOR")
    print("=" * 60)
    
    try:
        activator = UltimateWindowActivator()
        
        # Тест 1: Поиск любого окна Cursor
        print("\n1️⃣ ТЕСТ: Поиск и активация любого окна Cursor")
        hwnd = activator.bring_cursor_to_front_ultimate()
        
        if hwnd:
            print(f"✅ Тест 1 ПРОЙДЕН: Найдено и активировано окно {hwnd}")
        else:
            print("❌ Тест 1 ПРОВАЛЕН: Окно Cursor не найдено")
        
        time.sleep(2)
        
        # Тест 2: Поиск окна с конкретным проектом
        print("\n2️⃣ ТЕСТ: Поиск окна с проектом 'prompttest'")
        hwnd2 = activator.bring_cursor_to_front_ultimate("prompttest")
        
        if hwnd2:
            print(f"✅ Тест 2 ПРОЙДЕН: Найдено окно проекта {hwnd2}")
        else:
            print("❌ Тест 2 ПРОВАЛЕН: Окно проекта не найдено")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")


if __name__ == "__main__":
    test_ultimate_activator()
    print("\n🔄 Нажмите Enter для выхода...")
    input()


