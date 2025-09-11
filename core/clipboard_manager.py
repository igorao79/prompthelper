# -*- coding: utf-8 -*-

"""
Модуль для работы с буфером обмена
"""

import platform
import time
from typing import Optional


class ClipboardManager:
    """Класс для работы с буфером обмена на разных платформах"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self._detect_available_methods()
    
    def _detect_available_methods(self):
        """Определяет доступные методы работы с буфером обмена"""
        self.methods = []
        
        # pyperclip
        try:
            import pyperclip
            self.methods.append('pyperclip')
        except ImportError:
            pass
        
        # Windows COM
        if self.os_type == "windows":
            try:
                import win32clipboard
                self.methods.append('win32clipboard')
            except ImportError:
                pass
        
        # Qt (если доступен)
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QClipboard
            self.methods.append('qt')
        except ImportError:
            pass
        
        # tkinter
        try:
            import tkinter as tk
            self.methods.append('tkinter')
        except ImportError:
            pass
        
        print(f"📋 Доступные методы буфера обмена: {', '.join(self.methods)}")
    
    def copy_to_clipboard(self, text: str, root_widget=None) -> bool:
        """
        Копирует текст в буфер обмена
        
        Args:
            text: Текст для копирования
            root_widget: Корневой виджет (для Qt/tkinter методов)
            
        Returns:
            bool: Успешность операции
        """
        if not text:
            print("❌ Пустой текст для копирования")
            return False
        
        print(f"📋 Копирование в буфер обмена ({len(text)} символов)...")
        
        # Пробуем методы по порядку приоритета
        methods_to_try = self._get_preferred_methods()
        
        for method in methods_to_try:
            try:
                if method == 'pyperclip':
                    success = self._copy_pyperclip(text)
                elif method == 'win32clipboard':
                    success = self._copy_win32clipboard(text)
                elif method == 'qt':
                    success = self._copy_qt(text, root_widget)
                elif method == 'tkinter':
                    success = self._copy_tkinter(text)
                else:
                    continue
                
                if success:
                    print(f"✅ Текст скопирован методом: {method}")
                    return True
                
            except Exception as e:
                print(f"⚠️ Ошибка метода {method}: {e}")
                continue
        
        print("❌ Не удалось скопировать текст ни одним методом")
        return False
    
    def _get_preferred_methods(self) -> list:
        """Возвращает методы в порядке приоритета"""
        if self.os_type == "windows":
            # Для Windows предпочитаем win32clipboard и pyperclip
            preferred = ['win32clipboard', 'pyperclip', 'qt', 'tkinter']
        else:
            # Для других ОС предпочитаем pyperclip
            preferred = ['pyperclip', 'qt', 'tkinter']
        
        # Возвращаем только доступные методы в порядке приоритета
        return [method for method in preferred if method in self.methods]
    
    def _copy_pyperclip(self, text: str) -> bool:
        """Копирование через pyperclip"""
        try:
            import pyperclip
            pyperclip.copy(text)
            
            # Проверяем, что текст действительно скопирован
            time.sleep(0.1)
            clipboard_content = pyperclip.paste()
            return clipboard_content == text
            
        except Exception as e:
            print(f"⚠️ Ошибка pyperclip: {e}")
            return False
    
    def _copy_win32clipboard(self, text: str) -> bool:
        """Копирование через win32clipboard"""
        if self.os_type != "windows":
            return False
        
        try:
            import win32clipboard
            
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                
                # Проверяем результат
                time.sleep(0.1)
                clipboard_content = win32clipboard.GetClipboardData()
                return clipboard_content == text
                
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            print(f"⚠️ Ошибка win32clipboard: {e}")
            return False
    
    def _copy_qt(self, text: str, root_widget=None) -> bool:
        """Копирование через Qt"""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QClipboard
            
            app = QApplication.instance()
            if not app and root_widget:
                app = root_widget
            
            if app:
                clipboard = app.clipboard()
                clipboard.setText(text)
                
                # Проверяем результат
                time.sleep(0.1)
                clipboard_content = clipboard.text()
                return clipboard_content == text
            
            return False
            
        except Exception as e:
            print(f"⚠️ Ошибка Qt clipboard: {e}")
            return False
    
    def _copy_tkinter(self, text: str) -> bool:
        """Копирование через tkinter"""
        try:
            import tkinter as tk
            
            # Создаем временное окно
            root = tk.Tk()
            root.withdraw()  # Скрываем окно
            
            try:
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()  # Обновляем буфер обмена
                
                # Проверяем результат
                time.sleep(0.1)
                clipboard_content = root.clipboard_get()
                return clipboard_content == text
                
            finally:
                root.destroy()
                
        except Exception as e:
            print(f"⚠️ Ошибка tkinter clipboard: {e}")
            return False
    
    def _copy_to_clipboard_win32_com(self, text: str) -> bool:
        """Альтернативное копирование через COM (Windows)"""
        if self.os_type != "windows":
            return False
        
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            pythoncom.CoInitialize()
            try:
                # Создаем объект WScript.Shell для работы с буфером
                shell = Dispatch("WScript.Shell")
                
                # Используем метод SendKeys для копирования
                # Сначала "набираем" текст, затем Ctrl+A и Ctrl+C
                shell.SendKeys(text)
                time.sleep(0.1)
                shell.SendKeys("^a")  # Ctrl+A
                time.sleep(0.1)
                shell.SendKeys("^c")  # Ctrl+C
                
                return True
                
            finally:
                pythoncom.CoUninitialize()
                
        except Exception as e:
            print(f"⚠️ Ошибка COM метода: {e}")
            return False
    
    def _copy_to_clipboard_qt_with_com_init(self, text: str) -> bool:
        """Qt метод с инициализацией COM для EXE"""
        try:
            # Инициализация COM для совместимости с EXE
            if self.os_type == "windows":
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except ImportError:
                    pass
            
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QCoreApplication
            
            app = QCoreApplication.instance() or QApplication.instance()
            if app:
                clipboard = app.clipboard()
                clipboard.setText(text)
                app.processEvents()  # Обрабатываем события
                
                # Проверяем результат
                time.sleep(0.1)
                clipboard_content = clipboard.text()
                success = clipboard_content == text
                
                if success:
                    print(f"✅ Текст скопирован через Qt (длина: {len(text)})")
                else:
                    print(f"⚠️ Qt копирование: ожидали {len(text)} символов, получили {len(clipboard_content)}")
                
                return success
            
            print("❌ QApplication не найден")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка Qt метода: {e}")
            return False
        
        finally:
            if self.os_type == "windows":
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except ImportError:
                    pass
    
    def get_clipboard_content(self) -> Optional[str]:
        """Получает содержимое буфера обмена"""
        methods_to_try = self._get_preferred_methods()
        
        for method in methods_to_try:
            try:
                if method == 'pyperclip':
                    import pyperclip
                    return pyperclip.paste()
                elif method == 'win32clipboard':
                    if self.os_type == "windows":
                        import win32clipboard
                        win32clipboard.OpenClipboard()
                        try:
                            return win32clipboard.GetClipboardData()
                        finally:
                            win32clipboard.CloseClipboard()
                elif method == 'qt':
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        return app.clipboard().text()
                elif method == 'tkinter':
                    import tkinter as tk
                    root = tk.Tk()
                    root.withdraw()
                    try:
                        return root.clipboard_get()
                    finally:
                        root.destroy()
            except Exception:
                continue
        
        return None
    
    def clear_clipboard(self) -> bool:
        """Очищает буфер обмена"""
        return self.copy_to_clipboard("")



