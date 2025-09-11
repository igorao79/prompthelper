# -*- coding: utf-8 -*-

"""
Автоматический процессор промптов из истории
"""

import time
from typing import List, Dict, Optional
from shared.settings_manager import SettingsManager


class AutoPromptProcessor:
    """Класс для автоматической обработки промптов из истории"""
    
    def __init__(self, window_manager, clipboard_manager, prompt_inserter):
        self.window_manager = window_manager
        self.clipboard_manager = clipboard_manager
        self.prompt_inserter = prompt_inserter
        self.settings = SettingsManager()
        
        # Настройки обработки
        self.batch_size = 10  # Размер пакета для обработки
        self.processing_delay = 15  # Пауза между вставками (секунды)
        self.last_processed_count = 0  # Количество обработанных элементов
        
        print("🤖 AutoPromptProcessor инициализирован")
    
    def should_start_processing(self) -> bool:
        """Проверяет, нужно ли начинать автоматическую обработку"""
        history = self.settings.get_landing_history()
        current_count = len(history)
        
        # Начинаем обработку, если:
        # 1. Накопилось достаточно элементов в истории
        # 2. Появились новые элементы с момента последней обработки
        should_process = (
            current_count >= self.batch_size and 
            current_count > self.last_processed_count
        )
        
        if should_process:
            print(f"🚀 Условия для автообработки выполнены: {current_count} элементов в истории")
        
        return should_process
    
    def start_auto_processing(self) -> Dict:
        """Запускает автоматическую обработку промптов из истории"""
        if not self.should_start_processing():
            return {"success": False, "message": "Условия для автообработки не выполнены"}
        
        print("🤖 НАЧИНАЕТСЯ АВТОМАТИЧЕСКАЯ ОБРАБОТКА ПРОМПТОВ")
        print("=" * 60)
        
        # Получаем историю и окна Cursor
        history = self.settings.get_landing_history()
        cursor_windows = self.window_manager.get_all_cursor_windows()
        
        if not cursor_windows:
            return {"success": False, "message": "Не найдено окон Cursor для обработки"}
        
        print(f"📊 Статистика:")
        print(f"   Элементов в истории: {len(history)}")
        print(f"   Окон Cursor: {len(cursor_windows)}")
        
        # Создаем план обработки
        processing_plan = self._create_processing_plan(history, cursor_windows)
        
        if not processing_plan:
            return {"success": False, "message": "Не найдено совпадений между историей и окнами"}
        
        print(f"📋 План обработки: {len(processing_plan)} совпадений")
        
        # Выполняем обработку
        results = self._execute_processing_plan(processing_plan)
        
        # Обновляем счетчик обработанных
        self.last_processed_count = len(history)
        
        print("\n🎉 АВТОМАТИЧЕСКАЯ ОБРАБОТКА ЗАВЕРШЕНА!")
        print("=" * 60)
        
        return results
    
    def _create_processing_plan(self, history: List[Dict], cursor_windows: List[Dict]) -> List[Dict]:
        """Создает план обработки на основе истории и доступных окон"""
        plan = []
        
        # Для каждого элемента истории ищем соответствующее окно
        for hist_entry in history:
            domain = hist_entry.get('domain', '').lower()
            prompt = hist_entry.get('prompt', '')
            
            if not domain or not prompt:
                continue
            
            # Ищем окно Cursor с этим доменом в заголовке
            matching_window = self._find_matching_window(domain, cursor_windows)
            
            if matching_window:
                plan.append({
                    'domain': domain,
                    'prompt': prompt,
                    'window': matching_window,
                    'timestamp': hist_entry.get('ts', 0)
                })
                print(f"✅ Найдено совпадение: {domain} → '{matching_window['title']}'")
            else:
                print(f"❌ Не найдено окно для: {domain}")
        
        # Сортируем по времени (новые первыми)
        plan.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return plan
    
    def _find_matching_window(self, domain: str, cursor_windows: List[Dict]) -> Optional[Dict]:
        """Находит окно Cursor, соответствующее домену"""
        domain_clean = domain.replace('.', '').replace('-', '').replace('_', '').lower()
        
        # Сначала ищем точное совпадение
        for window in cursor_windows:
            title = window['title'].lower()
            if domain in title:
                return window
        
        # Потом ищем по частям домена
        domain_parts = domain_clean.split('.')
        if len(domain_parts) > 1:
            main_part = domain_parts[0]  # Основная часть до первой точки
            
            for window in cursor_windows:
                title = window['title'].lower()
                if main_part in title and len(main_part) > 3:
                    return window
        
        return None
    
    def _execute_processing_plan(self, plan: List[Dict]) -> Dict:
        """Выполняет план обработки"""
        total_items = len(plan)
        processed_count = 0
        failed_count = 0
        
        print(f"\n🔄 ВЫПОЛНЕНИЕ ПЛАНА ОБРАБОТКИ ({total_items} элементов)")
        print("-" * 40)
        
        for i, item in enumerate(plan, 1):
            domain = item['domain']
            prompt = item['prompt']
            window = item['window']
            
            print(f"\n📝 [{i}/{total_items}] Обработка: {domain}")
            print(f"🎯 Окно: {window['title']}")
            print(f"📄 Промпт: {prompt[:100]}..." if len(prompt) > 100 else f"📄 Промпт: {prompt}")
            
            try:
                # Используем полный цикл вставки промпта как в основном коде
                success = self._insert_prompt_to_cursor_window(window, prompt, domain)
                
                if success:
                    print(f"✅ Промпт успешно вставлен для {domain}")
                    processed_count += 1
                else:
                    print(f"❌ Ошибка вставки промпта для {domain}")
                    failed_count += 1
                
                # Пауза между обработками
                if i < total_items:
                    print(f"⏳ Пауза {self.processing_delay} секунд до следующей обработки...")
                    time.sleep(self.processing_delay)
                
            except Exception as e:
                print(f"❌ Исключение при обработке {domain}: {e}")
                failed_count += 1
        
        return {
            "success": True,
            "processed": processed_count,
            "failed": failed_count,
            "total": total_items,
            "message": f"Обработано: {processed_count}/{total_items}, ошибок: {failed_count}"
        }
    
    def get_processing_status(self) -> Dict:
        """Возвращает статус системы автообработки"""
        history = self.settings.get_landing_history()
        cursor_windows = self.window_manager.get_all_cursor_windows()
        
        return {
            "history_count": len(history),
            "cursor_windows_count": len(cursor_windows),
            "last_processed_count": self.last_processed_count,
            "ready_for_processing": self.should_start_processing(),
            "batch_size": self.batch_size,
            "processing_delay": self.processing_delay
        }
    
    def print_status(self):
        """Выводит статус автообработки"""
        status = self.get_processing_status()
        
        print("\n" + "="*50)
        print("🤖 СТАТУС АВТООБРАБОТКИ ПРОМПТОВ")
        print("="*50)
        
        print(f"📚 Элементов в истории: {status['history_count']}")
        print(f"🖥️ Окон Cursor: {status['cursor_windows_count']}")
        print(f"📊 Последняя обработка: {status['last_processed_count']} элементов")
        print(f"🎯 Размер пакета: {status['batch_size']}")
        print(f"⏱️ Пауза между вставками: {status['processing_delay']} сек")
        print(f"🚀 Готов к обработке: {'✅' if status['ready_for_processing'] else '❌'}")
        
        print("="*50)
    
    def _insert_prompt_to_cursor_window(self, window: Dict, prompt: str, domain: str) -> bool:
        """Вставляет промпт в конкретное окно Cursor"""
        try:
            hwnd = window['hwnd']
            
            print(f"🎯 Активация окна: {window['title']}")
            
            # Активируем окно
            if not self.window_manager._ensure_window_active(hwnd, timeout_s=3.0):
                print(f"❌ Не удалось активировать окно для {domain}")
                return False
            
            # Даем время на активацию
            time.sleep(2.0)
            
            # Копируем промпт в буфер обмена
            if not self.clipboard_manager.copy_to_clipboard(prompt):
                print(f"❌ Не удалось скопировать промпт для {domain}")
                return False
            
            print(f"📋 Промпт скопирован в буфер обмена")
            
            # Ждем готовности приложения
            print(f"⏳ Ожидание готовности Cursor...")
            time.sleep(3.0)  # Дополнительное время для загрузки интерфейса
            
            # Пытаемся активировать чат в Cursor различными способами
            chat_activated = self._activate_cursor_chat(hwnd)
            if not chat_activated:
                print(f"⚠️ Не удалось активировать чат, пробуем вставить напрямую")
            
            # Вставляем промпт
            print(f"📝 Вставка промпта...")
            
            # Используем pyautogui для вставки
            try:
                import pyautogui
                
                # Очищаем поле ввода
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.2)
                pyautogui.press('delete')
                time.sleep(0.3)
                
                # Вставляем промпт
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.0)
                
                # Отправляем
                pyautogui.press('enter')
                
                print(f"✅ Промпт отправлен в {domain}")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка вставки через pyautogui: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обработки окна {domain}: {e}")
            return False
    
    def _activate_cursor_chat(self, hwnd: int) -> bool:
        """Пытается активировать чат в Cursor"""
        try:
            import pyautogui
            
            # Проверяем, что окно активно
            if not self.window_manager._ensure_window_active(hwnd):
                return False
            
            # Пробуем разные комбинации клавиш для активации чата
            key_combinations = [
                ['ctrl', 'j'],           # Обычная комбинация для терминала/чата
                ['ctrl', 'shift', 'grave'],  # Backtick для терминала
                ['ctrl', 'l'],           # Часто активирует чат
                ['f1'],                  # Помощь/чат
            ]
            
            for combo in key_combinations:
                try:
                    print(f"⌨️ Пробуем активировать чат: {'+'.join(combo)}")
                    pyautogui.hotkey(*combo)
                    time.sleep(0.8)
                    
                    # Если открылась командная палитра, закрываем её
                    if 'shift' in combo and 'p' in combo:
                        pyautogui.press('escape')
                        time.sleep(0.3)
                    
                except Exception as e:
                    print(f"⚠️ Ошибка комбинации {combo}: {e}")
                    continue
            
            # Дополнительно пытаемся навигацией найти чат
            try:
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('tab')
                time.sleep(0.3)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка активации чата: {e}")
            return False
    
    def reset_processing_counter(self):
        """Сбрасывает счетчик обработанных элементов"""
        self.last_processed_count = 0
        print("🔄 Счетчик обработки сброшен")
