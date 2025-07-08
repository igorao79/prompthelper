# -*- coding: utf-8 -*-

"""
GUI интерфейс для генератора лендингов
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

from data import COUNTRIES_DATA, THEME_COLORS
from utils import (CityGenerator, validate_domain, format_status_message, 
                  get_language_by_country, SettingsManager, get_desktop_path, 
                  open_text_editor, check_directory_exists)
from cursor_manager import CursorManager
from prompt_generator import create_landing_prompt


def enable_clipboard_operations_with_var(entry_widget, text_variable):
    """
    Добавляет поддержку операций буфера обмена к Entry виджету с textvariable
    
    Args:
        entry_widget: tk.Entry или ttk.Entry виджет
        text_variable: tk.StringVar связанная с полем
    """
    def select_all(event=None):
        try:
            entry_widget.select_range(0, tk.END)
            return 'break'
        except:
            return None
    
    def paste_text_with_var(event=None):
        try:
            clipboard_text = entry_widget.clipboard_get()
            # Очищаем поле полностью если есть выделение или заменяем весь текст
            if entry_widget.selection_present():
                entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                # Если ничего не выделено, заменяем весь текст
                entry_widget.delete(0, tk.END)
            entry_widget.insert(0, clipboard_text)
            # Обновляем переменную
            text_variable.set(entry_widget.get())
            return 'break'
        except:
            return None
    
    # Добавляем только Ctrl+A и переопределенный Ctrl+V
    entry_widget.bind('<Control-a>', select_all)
    entry_widget.bind('<Control-A>', select_all)
    entry_widget.bind('<Control-v>', paste_text_with_var)
    entry_widget.bind('<Control-V>', paste_text_with_var)
    
    # Добавляем контекстное меню
    def show_context_menu(event):
        context_menu = tk.Menu(entry_widget, tearoff=0)
        try:
            # Используем стандартные команды для копирования/вырезания
            context_menu.add_command(label="Копировать", command=lambda: entry_widget.event_generate('<<Copy>>'))
            context_menu.add_command(label="Вырезать", command=lambda: entry_widget.event_generate('<<Cut>>'))
            context_menu.add_command(label="Вставить", command=paste_text_with_var)
            context_menu.add_separator()
            context_menu.add_command(label="Выделить всё", command=select_all)
            
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception:
            pass
        finally:
            try:
                context_menu.grab_release()
            except:
                pass
    
    entry_widget.bind('<Button-3>', show_context_menu)  # Правая кнопка мыши


def enable_clipboard_operations(entry_widget):
    """
    Добавляет поддержку операций буфера обмена к Entry виджету
    
    Args:
        entry_widget: tk.Entry или ttk.Entry виджет
    """
    def select_all(event=None):
        try:
            entry_widget.select_range(0, tk.END)
            return 'break'
        except:
            return None
    
    # Добавляем только Ctrl+A (выделить всё) - остальные операции оставляем стандартными
    entry_widget.bind('<Control-a>', select_all)
    entry_widget.bind('<Control-A>', select_all)
    
    # Добавляем контекстное меню
    def show_context_menu(event):
        context_menu = tk.Menu(entry_widget, tearoff=0)
        try:
            # Используем стандартные команды Tkinter
            context_menu.add_command(label="Копировать", command=lambda: entry_widget.event_generate('<<Copy>>'))
            context_menu.add_command(label="Вырезать", command=lambda: entry_widget.event_generate('<<Cut>>'))
            context_menu.add_command(label="Вставить", command=lambda: entry_widget.event_generate('<<Paste>>'))
            context_menu.add_separator()
            context_menu.add_command(label="Выделить всё", command=select_all)
            
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception:
            pass
        finally:
            try:
                context_menu.grab_release()
            except:
                pass
    
    entry_widget.bind('<Button-3>', show_context_menu)  # Правая кнопка мыши


class CountrySearchCombobox(ttk.Frame):
    """Компактный комбобокс с поиском для стран"""
    
    def __init__(self, parent, settings_manager, textvariable=None, on_select=None):
        super().__init__(parent)
        
        self.textvariable = textvariable or tk.StringVar()
        self.on_select = on_select
        self.settings_manager = settings_manager
        self.all_countries = list(COUNTRIES_DATA.keys())
        self.filtered_countries = self.all_countries.copy()
        self.favorites = self.settings_manager.get_favorite_countries()
        
        # Переменные
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.popup_window = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Создает интерфейс"""
        # Основной фрейм
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="x")
        
        # Поле поиска
        self.entry = ttk.Entry(
            main_frame, 
            textvariable=self.search_var,
            font=("Arial", 9)
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Добавляем поддержку операций буфера обмена
        enable_clipboard_operations(self.entry)
        
        # Кнопка выбора
        select_btn = ttk.Button(
            main_frame,
            text="▼",
            width=3,
            command=self.show_dropdown
        )
        select_btn.pack(side="left", padx=(2, 0))
        
        # Бинды
        self.entry.bind('<Return>', lambda e: self.show_dropdown())
        self.entry.bind('<Down>', lambda e: self.show_dropdown())
        
    def show_dropdown(self):
        """Показывает выпадающий список"""
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
            return
            
        # Создаем окно
        self.popup_window = tk.Toplevel(self)
        self.popup_window.overrideredirect(True)
        self.popup_window.transient()
        
        # Позиционируем под полем ввода
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.popup_window.geometry(f"{self.entry.winfo_width() + 30}x200+{x}+{y}")
        
        # Создаем фрейм со скроллом
        container = ttk.Frame(self.popup_window)
        container.pack(fill="both", expand=True)
        
        # Канвас для скролла
        canvas = tk.Canvas(container, height=200)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Фрейм для элементов
        self.items_frame = ttk.Frame(canvas)
        self.items_frame.bind("<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Настраиваем канвас
        canvas.create_window((0, 0), window=self.items_frame, anchor="nw", width=self.entry.winfo_width() + 13)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем элементы
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Добавляем прокрутку колесиком мыши
        def _on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Привязываем прокрутку к нескольким элементам для лучшей работы
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.items_frame.bind("<MouseWheel>", _on_mousewheel)
        self.popup_window.bind("<MouseWheel>", _on_mousewheel)
        
        # Также привязываем к элементам внутри popup
        def _bind_mousewheel_to_children(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_mousewheel_to_children(child)
        
        # Отвязываем прокрутку при закрытии окна
        def _on_popup_destroy(event):
            try:
                if canvas.winfo_exists():
                    canvas.unbind("<MouseWheel>")
                if self.items_frame.winfo_exists():
                    self.items_frame.unbind("<MouseWheel>")
                if self.popup_window.winfo_exists():
                    self.popup_window.unbind("<MouseWheel>")
            except:
                pass
        self.popup_window.bind("<Destroy>", _on_popup_destroy)
        
        # Добавляем страны
        self.update_dropdown_items()
        
        # Бинды для закрытия
        self.popup_window.bind('<Escape>', lambda e: self.popup_window.destroy())
        self.popup_window.bind('<FocusOut>', self._on_focus_out)
        
        # Стили для элементов списка
        style = ttk.Style()
        style.configure("Country.TLabel", padding=4, font=("Arial", 9))
        style.configure("Favorite.TLabel", padding=4, font=("Arial", 9, "bold"))
        
    def update_dropdown_items(self):
        """Обновляет список стран"""
        # Очищаем старые элементы
        for widget in self.items_frame.winfo_children():
            widget.destroy()
            
        # Сначала избранные
        if self.favorites:
            for country in self.favorites:
                if self._matches_search(country):
                    self.create_country_item(country, True)
            
            # Разделитель
            if any(self._matches_search(c) for c in self.filtered_countries if c not in self.favorites):
                ttk.Separator(self.items_frame).pack(fill="x", pady=2)
        
        # Остальные страны
        for country in self.filtered_countries:
            if country not in self.favorites and self._matches_search(country):
                self.create_country_item(country, False)
    
    def create_country_item(self, country, is_favorite):
        """Создает элемент страны"""
        frame = ttk.Frame(self.items_frame)
        frame.pack(fill="x")
        
        # Стиль метки
        style = "Favorite.TLabel" if is_favorite else "Country.TLabel"
        
        # Метка страны
        label = ttk.Label(
            frame, 
            text=country,
            style=style
        )
        label.pack(side="left", fill="x", expand=True)
        
        # Звездочка
        star = ttk.Label(
            frame,
            text="★" if is_favorite else "☆",
            style=style,
            cursor="hand2"
        )
        star.pack(side="right", padx=5)
        
        # Бинды
        label.bind('<Button-1>', lambda e, c=country: self._select_country(c))
        star.bind('<Button-1>', lambda e, c=country: self._toggle_favorite(c))
        
        # Добавляем прокрутку колесиком к элементам стран
        if hasattr(self, 'popup_window') and self.popup_window:
            def _item_mousewheel(event):
                if self.popup_window and self.popup_window.winfo_exists():
                    # Находим canvas через иерархию виджетов
                    canvas = None
                    parent = event.widget
                    while parent and not isinstance(parent, tk.Canvas):
                        parent = parent.master
                        if hasattr(parent, 'winfo_class') and parent.winfo_class() == 'Canvas':
                            canvas = parent
                            break
                    if canvas:
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            frame.bind("<MouseWheel>", _item_mousewheel)
            label.bind("<MouseWheel>", _item_mousewheel)
            star.bind("<MouseWheel>", _item_mousewheel)
        
        # Подсветка при наведении
        for widget in (label, star):
            widget.bind('<Enter>', lambda e, w=widget: w.configure(foreground="#2980b9"))
            widget.bind('<Leave>', lambda e, w=widget: w.configure(foreground="black"))
    
    def _matches_search(self, country):
        """Проверяет соответствие поисковому запросу"""
        search = self.search_var.get().lower()
        return not search or search in country.lower()
    
    def _select_country(self, country):
        """Выбирает страну"""
        self.textvariable.set(country)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, country)
        if self.popup_window:
            self.popup_window.destroy()
        if self.on_select:
            self.on_select()
    
    def _toggle_favorite(self, country):
        """Переключает избранное"""
        current_favorites = self.settings_manager.get_favorite_countries()
        
        if country in current_favorites:
            self.settings_manager.remove_favorite_country(country)
            self.favorites = self.settings_manager.get_favorite_countries()
        else:
            self.settings_manager.add_favorite_country(country)
            self.favorites = self.settings_manager.get_favorite_countries()
        
        self.update_dropdown_items()
    
    def _on_focus_out(self, event):
        """Обработчик потери фокуса"""
        if self.popup_window:
            # Проверяем, не на наших ли элементах фокус
            focused = self.popup_window.focus_get()
            if not focused or not (focused.winfo_toplevel() == self.popup_window):
                self.popup_window.destroy()
    
    def on_search_change(self, *args):
        """Обработчик изменения поиска"""
        if self.popup_window and self.popup_window.winfo_exists():
            self.update_dropdown_items()
            
    def set_value(self, value):
        """Устанавливает значение"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.textvariable.set(value)


class ThemeHistoryCombobox(ttk.Frame):
    """Комбобокс с историей для тематик"""
    
    def __init__(self, parent, textvariable=None):
        super().__init__(parent)
        
        self.textvariable = textvariable or tk.StringVar()
        self.history = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Создает интерфейс"""
        # Основное поле ввода
        self.entry = tk.Entry(
            self, 
            textvariable=self.textvariable,
            font=("Arial", 12),
            width=70
        )
        self.entry.pack(fill="x", ipady=3)
        
        # Добавляем поддержку операций буфера обмена
        enable_clipboard_operations(self.entry)
        
        # Кнопка истории
        self.history_btn = tk.Button(
            self,
            text="📋",
            command=self.show_history,
            width=3,
            font=("Arial", 10)
        )
        self.history_btn.pack(side="right", padx=(5, 0))
    
    def set_history(self, history):
        """Устанавливает историю тематик"""
        self.history = history
    
    def show_history(self):
        """Показывает историю тематик"""
        if not self.history:
            messagebox.showinfo("История", "История тематик пуста")
            return
        
        # Создаем окно выбора
        history_window = tk.Toplevel(self)
        history_window.title("История тематик")
        history_window.geometry("400x300")
        history_window.transient(self)
        history_window.grab_set()
        
        # Список истории
        listbox = tk.Listbox(history_window, font=("Arial", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for theme in self.history:
            listbox.insert(tk.END, theme)
        
        # Кнопки
        btn_frame = tk.Frame(history_window)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def select_theme():
            selection = listbox.curselection()
            if selection:
                selected_theme = listbox.get(selection[0])
                self.textvariable.set(selected_theme)
                history_window.destroy()
        
        select_btn = tk.Button(
            btn_frame,
            text="Выбрать",
            command=select_theme,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_btn.pack(side="right", padx=(5, 0))
        
        close_btn = tk.Button(
            btn_frame,
            text="Закрыть",
            command=history_window.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold")
        )
        close_btn.pack(side="right")
        
        # Двойной клик для выбора
        listbox.bind("<Double-Button-1>", lambda e: select_theme())


class LandingPageGeneratorGUI:
    """Основной класс GUI приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Генератор Лендингов v2.0")
        self.root.geometry("850x900")  # Увеличил размер окна
        self.root.resizable(True, True)  # Разрешил изменение размеров
        
        # Компоненты
        self.city_generator = CityGenerator()
        self.cursor_manager = CursorManager()
        self.settings_manager = SettingsManager()
        
        # Переменные
        self.selected_country = tk.StringVar()
        self.theme_var = tk.StringVar()
        self.domain_var = tk.StringVar()
        self.save_path_var = tk.StringVar(value=self.settings_manager.get_save_path())
        self.project_path_var = tk.StringVar()  # Для управления изображениями
        
        # Привязываем обработчики изменений для автосброса промпта
        self.theme_var.trace('w', self._on_data_change)
        self.selected_country.trace('w', self._on_data_change)
        self.domain_var.trace('w', self._on_data_change)
        self.current_city = ""
        self.current_prompt = self.settings_manager.get_prompt()
        
        # Окна
        self.prompt_window = None
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Создает интерфейс приложения"""
        try:
            print("🎨 Создание заголовка...")
            # Заголовок
            header = tk.Label(
                self.root, 
                text="🚀 Генератор Лендингов v2.0 🚀", 
                font=("Arial", 12, "bold"), 
                bg="#2c3e50", 
                fg="white",
                pady=8
            )
            header.pack(fill="x")
            
            print("🖼️ Создание прокручиваемой области...")
            # Создаем прокручиваемую область с канвасом и скроллбаром
            self.create_scrollable_frame()
            
            print("📁 Создание секции папки...")
            # Блок выбора папки для сохранения
            self.create_save_path_section()
            
            print("🎯 Создание секции тематики...")
            # Блок тематики
            self.create_theme_section()
            
            print("🌍 Создание секции страны...")
            # Блок выбора страны
            self.create_country_section()
            
            print("ℹ️ Создание информационной секции...")
            # Информационный блок
            self.create_info_section()
            
            print("🌐 Создание секции домена...")
            # Блок домена
            self.create_domain_section()
            
            print("⚡ Создание кнопок действий...")
            # Кнопки действий
            self.create_action_buttons()
            
            print("🎨 Создание секции управления изображениями...")
            # Секция управления изображениями
            self.create_image_management_section()
            
            print("📊 Создание секции статуса...")
            # Статус
            self.create_status_section()
            
            print("✅ Интерфейс создан успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка создания интерфейса: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def create_scrollable_frame(self):
        """Создает прокручиваемую область с канвасом и скроллбаром"""
        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#f0f0f0")
        main_container.pack(fill="both", expand=True)
        
        # Создаем канвас и скроллбар
        self.canvas = tk.Canvas(main_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        
        # Фрейм для содержимого
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        # Привязываем скроллбар к канвасу
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем элементы
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Добавляем фрейм в канвас
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Обработчики событий
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Привязываем обработчики
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", configure_canvas_width)
        
        # Привязываем скролл мыши к канвасу и всем дочерним элементам
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Добавляем отступы для содержимого
        self.scrollable_frame.configure(padx=15, pady=10)
    
    def create_save_path_section(self):
        """Создает секцию выбора папки для сохранения"""
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="📁 Папка для создания проектов", 
            font=("Arial", 9, "bold"),
            padx=8, 
            pady=5
        )
        section.pack(fill="x", pady=(0, 8), ipady=2)
        
        path_frame = tk.Frame(section)
        path_frame.pack(fill="x")
        
        # Поле пути
        path_entry = tk.Entry(
            path_frame,
            textvariable=self.save_path_var,
            font=("Arial", 12),
            state="readonly"
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)
        
        # Добавляем поддержку операций буфера обмена (только копирование для readonly поля)
        enable_clipboard_operations(path_entry)
        
        # Кнопка выбора папки
        browse_btn = tk.Button(
            path_frame,
            text="📂 Выбрать",
            command=self.browse_save_path,
            bg="#3498db",
            fg="white",
            font=("Arial", 8, "bold"),
            padx=8,
            pady=3
        )
        browse_btn.pack(side="right", padx=(0, 3))
        
        # Кнопка сброса на рабочий стол
        reset_btn = tk.Button(
            path_frame,
            text="🏠 Рабочий стол",
            command=self.reset_to_desktop,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12),
            padx=5,
            pady=3
        )
        reset_btn.pack(side="right")
    
    def create_theme_section(self):
        """Создает секцию тематики"""
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="🎯 Тематика лендинга", 
            font=("Arial", 9, "bold"),
            padx=8, 
            pady=5
        )
        section.pack(fill="x", pady=(0, 8), ipady=2)
        
        # Комбобокс с историей
        self.theme_combo = ThemeHistoryCombobox(section, self.theme_var)
        self.theme_combo.pack(fill="x")
        self.theme_combo.set_history(self.settings_manager.get_theme_history())
        
        # Подсказки
        theme_hint = tk.Label(
            section,
            text="Примеры: Продажа недвижимости, Строительство домов, Ремонт квартир",
            font=("Arial", 12),
            fg="#666",
            wraplength=600
        )
        theme_hint.pack(anchor="w", pady=(2, 0))
    
    def create_country_section(self):
        """Создает секцию выбора страны"""
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="🌍 Страна и город", 
            font=("Arial", 9, "bold"),
            padx=8, 
            pady=5
        )
        section.pack(fill="x", pady=(0, 8), ipady=2)
        
        # Комбобокс с поиском стран
        self.country_combo = CountrySearchCombobox(
            section,
            settings_manager=self.settings_manager,  # Передаем settings_manager
            textvariable=self.selected_country,
            on_select=self.on_country_select
        )
        self.country_combo.pack(fill="x")
        
        # Инструкция
        instruction = tk.Label(
            section,
            text="💡 Начните печатать для поиска. ⭐ для избранного.",
            font=("Arial", 12),
            fg="#666"
        )
        instruction.pack(anchor="w", pady=(2, 0))
    
    def create_info_section(self):
        """Создает информационную секцию"""
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="ℹ️ Информация", 
            font=("Arial", 9, "bold"),
            padx=8, 
            pady=5
        )
        section.pack(fill="x", pady=(0, 8), ipady=2)
        
        self.language_label = tk.Label(
            section, 
            text="Язык: не выбран", 
            font=("Arial", 12), 
            fg="#666"
        )
        self.language_label.pack(anchor="w")
        
        self.city_label = tk.Label(
            section, 
            text="Город: не выбран", 
            font=("Arial", 12), 
            fg="#666"
        )
        self.city_label.pack(anchor="w")
        
        # Кнопка генерации города
        city_btn = tk.Button(
            section, 
            text="🎲 Сгенерировать город", 
            command=self.generate_new_city,
            bg="#f39c12", 
            fg="white",
            font=("Arial", 8, "bold"),
            padx=5,
            pady=2
        )
        city_btn.pack(anchor="w", pady=(3, 0))
    
    def create_domain_section(self):
        """Создает секцию домена"""
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="🌐 Домен", 
            font=("Arial", 9, "bold"),
            padx=8, 
            pady=5
        )
        section.pack(fill="x", pady=(0, 8), ipady=2)
        
        domain_entry = tk.Entry(
            section, 
            textvariable=self.domain_var, 
            font=("Arial", 12),
            width=60
        )
        domain_entry.pack(anchor="w", ipady=3)
        
        # Добавляем поддержку операций буфера обмена с textvariable
        enable_clipboard_operations_with_var(domain_entry, self.domain_var)
    
    def create_action_buttons(self):
        """Создает кнопки действий"""
        section = tk.Frame(self.scrollable_frame)
        section.pack(fill="x", pady=10)
        
        # Фрейм для кнопок промпта
        prompt_buttons_frame = tk.Frame(section)
        prompt_buttons_frame.pack(pady=(0, 8))
        
        # Кнопка редактирования промпта
        edit_btn = tk.Button(
            prompt_buttons_frame,
            text="✏️ Настроить промпт",
            command=self.edit_prompt,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            pady=5
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        # Кнопка сброса промпта  
        reset_btn = tk.Button(
            prompt_buttons_frame,
            text="🔄 Сбросить",
            command=self.reset_prompt,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            pady=5
        )
        reset_btn.pack(side="left")
        
        # ГЛАВНАЯ КНОПКА - СОЗДАТЬ ЛЕНДИНГ
        create_button = tk.Button(
            section,
            text="🚀 СОЗДАТЬ ЛЕНДИНГ",
            command=self.create_landing,
            bg="#e74c3c",
            fg="white", 
            font=("Arial", 12, "bold"),
            padx=25,
            pady=10,
            relief="raised",
            bd=3,
            cursor="hand2"
        )
        create_button.pack()
    
    def create_image_management_section(self):
        """Создает секцию управления изображениями"""
        # Основной фрейм секции
        section = tk.LabelFrame(
            self.scrollable_frame, 
            text="🎨 Управление изображениями", 
            font=("Arial", 10, "bold"),
            padx=10,
            pady=8
        )
        section.pack(fill="x", pady=10)
        
        # Описание
        description = tk.Label(
            section,
            text="Пересоздать отдельные изображения для существующего проекта",
            font=("Arial", 9),
            fg="#555555"
        )
        description.pack(pady=(0, 8))
        
        # Поле для выбора папки проекта
        project_frame = tk.Frame(section)
        project_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(project_frame, text="Папка проекта:", font=("Arial", 9)).pack(anchor="w")
        
        path_frame = tk.Frame(project_frame)
        path_frame.pack(fill="x", pady=(2, 0))
        
        project_entry = tk.Entry(
            path_frame, 
            textvariable=self.project_path_var,
            font=("Arial", 9)
        )
        project_entry.pack(side="left", fill="x", expand=True)
        enable_clipboard_operations_with_var(project_entry, self.project_path_var)
        
        browse_project_btn = tk.Button(
            path_frame,
            text="📁",
            command=self.browse_project_path,
            font=("Arial", 8),
            padx=8
        )
        browse_project_btn.pack(side="right", padx=(5, 0))
        
        # Фрейм с кнопками для отдельных изображений
        buttons_frame = tk.Frame(section)
        buttons_frame.pack(fill="x", pady=(8, 0))
        
        # Создаем кнопки в две строки
        row1 = tk.Frame(buttons_frame)
        row1.pack(fill="x", pady=(0, 4))
        
        row2 = tk.Frame(buttons_frame)
        row2.pack(fill="x")
        
        # Первая строка кнопок
        image_buttons_row1 = [
            ("🖼️ Main", "main", "#e74c3c"),
            ("📖 About1", "about1", "#3498db"),
            ("📘 About2", "about2", "#3498db"),
            ("📙 About3", "about3", "#3498db")
        ]
        
        for text, image_name, color in image_buttons_row1:
            btn = tk.Button(
                row1,
                text=text,
                command=lambda name=image_name: self.regenerate_single_image(name),
                bg=color,
                fg="white",
                font=("Arial", 8, "bold"),
                padx=10,
                pady=3
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)
        
        # Вторая строка кнопок
        image_buttons_row2 = [
            ("⭐ Review1", "review1", "#f39c12"),
            ("⭐ Review2", "review2", "#f39c12"),
            ("⭐ Review3", "review3", "#f39c12"),
            ("🎯 Favicon", "favicon", "#9b59b6")
        ]
        
        for text, image_name, color in image_buttons_row2:
            btn = tk.Button(
                row2,
                text=text,
                command=lambda name=image_name: self.regenerate_single_image(name),
                bg=color,
                fg="white",
                font=("Arial", 8, "bold"),
                padx=10,
                pady=3
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)
        
        # Кнопка для пересоздания всех изображений
        regenerate_all_btn = tk.Button(
            section,
            text="🔄 Пересоздать ВСЕ изображения",
            command=self.regenerate_all_images,
            bg="#34495e",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            pady=5
        )
        regenerate_all_btn.pack(pady=(8, 0))
    
    def create_status_section(self):
        """Создает секцию статуса"""
        self.status_label = tk.Label(
            self.scrollable_frame, 
            text="✅ Готов к работе", 
            font=("Arial", 12), 
            fg="#27ae60"
        )
        self.status_label.pack(pady=(8, 0))
    
    def browse_save_path(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(
            title="Выберите папку для создания проектов",
            initialdir=self.save_path_var.get()
        )
        if folder:
            self.save_path_var.set(folder)
            self.settings_manager.set_save_path(folder)
    
    def reset_to_desktop(self):
        """Сброс на рабочий стол"""
        desktop = str(get_desktop_path())
        self.save_path_var.set(desktop)
        self.settings_manager.set_save_path(desktop)
    
    def on_country_select(self):
        """Обработчик выбора страны"""
        country = self.selected_country.get()
        if country:
            language = get_language_by_country(country)
            self.language_label.config(text=f"Язык: {language}", fg="#27ae60")
            self.generate_new_city()
            
    def generate_new_city(self):
        """Генерирует новый город"""
        country = self.selected_country.get()
        if not country:
            messagebox.showwarning("Предупреждение", "Сначала выберите страну!")
            return
            
        new_city = self.city_generator.get_random_city(country)
        self.current_city = new_city
        self.city_label.config(text=f"Город: {new_city}", fg="#27ae60")
        # Сбрасываем промпт при изменении города
        self._reset_prompt_on_change()
    
    def _on_data_change(self, *args):
        """Обработчик изменения основных данных"""
        self._reset_prompt_on_change()
    
    def _reset_prompt_on_change(self):
        """Сбрасывает сохраненный промпт при изменении данных"""
        if self.current_prompt:
            self.current_prompt = None
            self.settings_manager.save_prompt("")
            print("🔄 Промпт сброшен из-за изменения данных")
    
    def edit_prompt(self):
        """Редактирование промпта"""
        try:
            # Получаем данные - проверяем заполненность
            theme = self.theme_var.get().strip()
            country = self.selected_country.get()
            domain = self.domain_var.get().strip()
            city = self.current_city
            
            # Проверяем заполненность обязательных полей
            if not theme:
                messagebox.showwarning("Предупреждение", "Введите тематику лендинга!")
                return
            if not country:
                messagebox.showwarning("Предупреждение", "Выберите страну!")
                return
            if not domain:
                messagebox.showwarning("Предупреждение", "Введите домен!")
                return
            if not city:
                messagebox.showwarning("Предупреждение", "Сгенерируйте город!")
                return
            
            # Всегда генерируем актуальный промпт с текущими значениями
            language = get_language_by_country(country)
            current_prompt = create_landing_prompt(country, city, language, domain, theme)
            
            # Открываем редактор
            edited_prompt = open_text_editor(current_prompt)
            if edited_prompt is not None:  # None означает отмену
                self.current_prompt = edited_prompt
                self.settings_manager.save_prompt(edited_prompt)
                messagebox.showinfo("Готово", "Промпт сохранен успешно!")
            
        except Exception as e:
            print(f"Ошибка редактирования промпта: {e}")
            messagebox.showerror("Ошибка", f"Не удалось отредактировать промпт: {e}")
    
    def reset_prompt(self):
        """Сбрасывает сохраненный промпт"""
        try:
            if self.current_prompt:
                result = messagebox.askyesno(
                    "Подтверждение",
                    "Сбросить отредактированный промпт?\n\n"
                    "При создании лендинга будет использован\n"
                    "стандартный промпт с актуальными данными."
                )
                if result:
                    self.current_prompt = None
                    self.settings_manager.save_prompt("")
                    messagebox.showinfo("Готово", "Промпт сброшен! Теперь будет использован стандартный промпт.")
            else:
                messagebox.showinfo("Информация", "Промпт уже использует стандартные настройки.")
        except Exception as e:
            print(f"Ошибка сброса промпта: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сбросить промпт: {e}")
    
    def validate_form(self):
        """Проверяет заполненность формы"""
        theme = self.theme_var.get().strip()
        if not theme:
            return False, "Введите тематику лендинга!"
            
        if not self.selected_country.get():
            return False, "Выберите страну!"
            
        domain = self.domain_var.get().strip()
        is_valid, error_msg = validate_domain(domain)
        if not is_valid:
            return False, error_msg
            
        if not self.current_city:
            return False, "Сгенерируйте город!"
        
        # Проверяем существование папки
        save_path = self.save_path_var.get()
        if not Path(save_path).exists():
            return False, f"Выбранная папка не существует: {save_path}"
            
        return True, ""
        
    def create_landing(self):
        """Основная функция создания лендинга"""
        # Валидация
        is_valid, error_msg = self.validate_form()
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg)
            return
        
        # Сохраняем тематику в историю
        theme = self.theme_var.get().strip()
        self.settings_manager.add_theme_to_history(theme)
        self.theme_combo.set_history(self.settings_manager.get_theme_history())
        
        # Подтверждение
        country = self.selected_country.get()
        domain = self.domain_var.get().strip()
        save_path = self.save_path_var.get()
        
        # Проверяем существование папки проекта
        exists, full_path = check_directory_exists(save_path, domain)
        if exists:
            result = messagebox.askyesno(
                "Папка существует",
                f"Папка '{domain}' уже существует в:\n{save_path}\n\n"
                f"Хотите перезаписать содержимое?"
            )
            if not result:
                return
        
        # Определяем тип промпта
        prompt_type = "✏️ Отредактированный промпт" if self.current_prompt else "📋 Стандартный промпт"
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Создать лендинг:\n\n"
            f"Тематика: {theme}\n"
            f"Страна: {country}\n"
            f"Город: {self.current_city}\n"
            f"Домен: {domain}\n"
            f"Папка: {save_path}\n"
            f"Промпт: {prompt_type}\n\n"
            f"🎨 Дополнительно будет создано 8 тематических изображений:\n"
            f"   • main, about1-3, review1-3, favicon\n"
            f"   • Изображения будут соответствовать тематике '{theme}'\n\n"
            f"Продолжить?"
        )
        if not result:
            return
            
        # Запуск в отдельном потоке
        threading.Thread(target=self._create_landing_process, daemon=True).start()
    
    def _create_landing_process(self):
        """Процесс создания лендинга в отдельном потоке"""
        try:
            # Получение данных
            theme = self.theme_var.get().strip()
            country = self.selected_country.get()
            language = get_language_by_country(country)
            domain = self.domain_var.get().strip()
            city = self.current_city
            save_path = self.save_path_var.get()
            
            # Обновление статуса
            self.update_status("🔄 Создание папок...")
            
            # Создание структуры проекта с генерацией изображений
            project_path, media_path = self.cursor_manager.create_project_structure(
                domain, save_path, theme, self.update_status
            )
            
            self.update_status("📄 Подготовка промпта...")
            
            # Используем отредактированный промпт если есть, иначе генерируем новый с актуальными данными
            if self.current_prompt:
                full_prompt = self.current_prompt
            else:
                full_prompt = create_landing_prompt(country, city, language, domain, theme)
            
            self.update_status("🚀 Запуск Cursor AI...")
            
            # Запуск Cursor AI
            success, message = self.cursor_manager.open_project_and_paste_prompt(
                project_path, full_prompt, self.root, auto_paste=True, paste_delay=5
            )
            
            if success:
                self.update_status("✅ Готово! Cursor AI запущен")
                messagebox.showinfo(
                    "Успех!", 
                    f"Проект создан успешно!\n\n"
                    f"📁 Папка: {project_path}\n"
                    f"🎨 Папка media: {media_path}\n"
                    f"🚀 Cursor AI запущен с готовым промптом\n\n"
                    f"🖼️ Тематические изображения созданы автоматически!\n"
                    f"   Проверьте папку media в вашем проекте.\n\n"
                    f"💡 Если промпт не вставился автоматически,\n"
                    f"   нажмите Ctrl+V в Cursor AI"
                )
                # Сбрасываем форму для возможности создания нового лендинга
                self.reset_form_after_creation()
            else:
                self.update_status("⚠️ Cursor не найден, промпт скопирован")
                messagebox.showwarning(
                    "Предупреждение",
                    f"📁 Папка проекта создана: {project_path}\n"
                    f"🎨 Папка media: {media_path}\n\n"
                    f"🖼️ Тематические изображения созданы автоматически!\n"
                    f"   Проверьте папку media в вашем проекте.\n\n"
                    f"⚠️ Cursor AI не найден, но промпт скопирован в буфер обмена.\n"
                    f"   Откройте проект в Cursor вручную и вставьте промпт."
                )
                # Сбрасываем форму для возможности создания нового лендинга
                self.reset_form_after_creation()
                
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            print(error_msg)
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def update_status(self, text):
        """Обновляет статус"""
        self.status_label.config(text=text)
        self.root.update()
    
    def browse_project_path(self):
        """Выбор папки существующего проекта"""
        try:
            current_path = self.project_path_var.get()
            initial_dir = current_path if current_path and Path(current_path).exists() else self.save_path_var.get()
            
            project_path = filedialog.askdirectory(
                title="Выберите папку проекта с изображениями",
                initialdir=initial_dir
            )
            
            if project_path:
                # Проверяем есть ли папка media
                media_path = Path(project_path) / "media"
                if not media_path.exists():
                    result = messagebox.askyesno(
                        "Папка media не найдена",
                        f"В выбранной папке нет подпапки 'media'.\n\n"
                        f"Создать папку media в:\n{project_path}?"
                    )
                    if result:
                        media_path.mkdir(exist_ok=True)
                        self.project_path_var.set(project_path)
                    # Если пользователь сказал "Нет", не устанавливаем путь
                else:
                    self.project_path_var.set(project_path)
                    # Проверяем сколько изображений уже есть
                    existing_images = list(media_path.glob("*.png"))
                    messagebox.showinfo("Проект выбран", f"Папка проекта:\n{project_path}\n\nПапка media найдена!\nИзображений в папке: {len(existing_images)}")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выбрать папку: {e}")
    
    def regenerate_single_image(self, image_name):
        """Пересоздает одно конкретное изображение"""
        if not self._validate_image_regeneration():
            return
            
        try:
            project_path = self.project_path_var.get()
            media_path = Path(project_path) / "media"
            theme = self.theme_var.get().strip()
            
            if not theme:
                messagebox.showwarning("Предупреждение", "Введите тематику для генерации изображения!")
                return
            
            # Подтверждение
            result = messagebox.askyesno(
                "Подтверждение пересоздания",
                f"Пересоздать изображение '{image_name}'?\n\n"
                f"Тематика: {theme}\n"
                f"Папка: {media_path}\n\n"
                f"Существующий файл будет заменен."
            )
            if not result:
                return
            
            # Запуск в отдельном потоке
            threading.Thread(
                target=self._regenerate_image_process,
                args=(image_name, str(media_path), theme),
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось пересоздать изображение: {e}")
    
    def regenerate_all_images(self):
        """Пересоздает все изображения"""
        if not self._validate_image_regeneration():
            return
            
        try:
            project_path = self.project_path_var.get()
            media_path = Path(project_path) / "media"
            theme = self.theme_var.get().strip()
            
            if not theme:
                messagebox.showwarning("Предупреждение", "Введите тематику для генерации изображений!")
                return
            
            # Подтверждение
            result = messagebox.askyesno(
                "Подтверждение пересоздания всех изображений",
                f"Пересоздать ВСЕ изображения?\n\n"
                f"Тематика: {theme}\n"
                f"Папка: {media_path}\n\n"
                f"Все существующие файлы будут заменены!\n"
                f"Это займет несколько минут."
            )
            if not result:
                return
            
            # Запуск в отдельном потоке
            threading.Thread(
                target=self._regenerate_all_images_process,
                args=(str(media_path), theme),
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось пересоздать изображения: {e}")
    
    def _validate_image_regeneration(self):
        """Проверяет возможность пересоздания изображений"""
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showwarning("Предупреждение", "Выберите папку проекта!")
            return False
            
        if not Path(project_path).exists():
            messagebox.showerror("Ошибка", f"Папка проекта не существует:\n{project_path}")
            return False
            
        media_path = Path(project_path) / "media"
        if not media_path.exists():
            messagebox.showerror("Ошибка", f"Папка media не найдена:\n{media_path}")
            return False
            
        return True
    
    def _regenerate_image_process(self, image_name, media_path, theme):
        """Процесс пересоздания одного изображения"""
        try:
            self.update_status(f"🎨 Пересоздание изображения {image_name}...")
            
            # Импортируем генератор
            from img_gen import ThematicImageGenerator, ImageGenerator
            
            # Создаем генераторы с поддержкой Icons8
            image_generator = ImageGenerator(silent_mode=True, use_icons8_for_favicons=True)
            thematic_gen = ThematicImageGenerator(silent_mode=True)
            
            # Получаем промпты
            prompts, detected_theme = thematic_gen.get_theme_prompts(theme)
            prompt = prompts[image_name]
            
            # Применяем рандомизацию
            if image_name == "favicon":
                prompt = thematic_gen.add_favicon_randomization(prompt)
                prompt += ", TRANSPARENT BACKGROUND, icon design, vector style, flat design, simple logo, no background, white cutout, isolated on transparent, PNG with alpha channel, clear background, cutout style, logo without background"
            else:
                prompt = thematic_gen.add_randomization(prompt)
            
            # Специальная обработка для фавиконки
            if image_name == "favicon" and hasattr(image_generator, 'use_icons8_for_favicons') and image_generator.use_icons8_for_favicons and image_generator.icons8_manager:
                # Используем Icons8 для фавиконки
                filename = Path(media_path) / f"{image_name}.png"
                favicon_success = image_generator.icons8_manager.create_favicon_from_theme(theme, str(filename), 512)
                
                if favicon_success:
                    self.update_status(f"✅ Фавиконка Icons8 пересоздана!")
                    messagebox.showinfo("Готово", f"Фавиконка '{image_name}' успешно пересоздана с Icons8!")
                else:
                    # Fallback на AI генерацию
                    image = image_generator.generate_via_pollinations_clean(prompt)
                    if image:
                        from PIL import Image
                        image = image.resize((512, 512), Image.Resampling.LANCZOS)
                        image = image_generator.make_favicon_transparent(image)
                        
                        # Используем сжатие для AI фавиконки (50кб)
                        if image_generator.save_compressed_image(image, str(filename), target_size_kb=50):
                            self.update_status(f"✅ AI фавиконка пересоздана с сжатием!")
                            messagebox.showinfo("Готово", f"Фавиконка '{image_name}' пересоздана через AI (Icons8 недоступен)")
                        else:
                            self.update_status(f"❌ Не удалось сохранить {image_name}")
                            messagebox.showerror("Ошибка", f"Не удалось сохранить фавиконку '{image_name}'")
                    else:
                        self.update_status(f"❌ Не удалось создать {image_name}")
                        messagebox.showerror("Ошибка", f"Не удалось создать фавиконку '{image_name}'")
            else:
                # Обычная генерация для остальных изображений
                image = image_generator.generate_via_pollinations_clean(prompt)
                
                if image:
                    filename = Path(media_path) / f"{image_name}.png"
                    
                    # Специальная обработка для AI фавиконки
                    if image_name == "favicon":
                        from PIL import Image
                        image = image.resize((512, 512), Image.Resampling.LANCZOS)
                        image = image_generator.make_favicon_transparent(image)
                        
                        # Используем сжатие для AI фавиконки (50кб)
                        if image_generator.save_compressed_image(image, str(filename), target_size_kb=50):
                            self.update_status(f"✅ AI фавиконка пересоздана с сжатием!")
                            messagebox.showinfo("Готово", f"Фавиконка '{image_name}' успешно пересоздана!")
                        else:
                            self.update_status(f"❌ Не удалось сохранить {image_name}")
                            messagebox.showerror("Ошибка", f"Не удалось сохранить фавиконку '{image_name}'")
                    else:
                        # Для обычных изображений используем сжатие до 150кб
                        if image_generator.save_compressed_image(image, str(filename), target_size_kb=150):
                            self.update_status(f"✅ Изображение {image_name} пересоздано с сжатием!")
                            messagebox.showinfo("Готово", f"Изображение '{image_name}' успешно пересоздано!")
                        else:
                            self.update_status(f"❌ Не удалось сохранить {image_name}")
                            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение '{image_name}'")
                else:
                    self.update_status(f"❌ Не удалось создать {image_name}")
                    messagebox.showerror("Ошибка", f"Не удалось создать изображение '{image_name}'")
                
        except Exception as e:
            error_msg = f"Ошибка пересоздания {image_name}: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def _regenerate_all_images_process(self, media_path, theme):
        """Процесс пересоздания всех изображений"""
        try:
            self.update_status("🎨 Пересоздание всех изображений...")
            
            # Импортируем генератор
            from img_gen import ImageGenerator
            
            # Создаем генератор с поддержкой Icons8
            image_generator = ImageGenerator(silent_mode=True, use_icons8_for_favicons=True)
            
            # Генерируем полный набор
            results = image_generator.generate_thematic_set(
                theme_input=theme,
                media_dir=media_path,
                method="1",
                progress_callback=self.update_status
            )
            
            # Подсчитываем результаты
            successful_count = len([f for f in results.values() if f is not None])
            
            self.update_status(f"✅ Пересоздано {successful_count}/8 изображений")
            
            messagebox.showinfo(
                "Готово",
                f"Пересоздание завершено!\n\n"
                f"Успешно: {successful_count}/8 изображений\n"
                f"Папка: {media_path}\n\n"
                f"Проверьте результат в папке media."
            )
            
        except Exception as e:
            error_msg = f"Ошибка пересоздания изображений: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def reset_form_after_creation(self):
        """Сбрасывает форму после создания лендинга для возможности создания нового"""
        try:
            # Очищаем все поля формы
            self.theme_var.set("")  # Очищаем тематику
            self.domain_var.set("") # Очищаем домен
            self.selected_country.set("")  # Очищаем страну
            self.current_city = ""  # Очищаем город
            
            # Обновляем отображение
            self.language_label.config(text="Язык: Не выбран", fg="#7f8c8d")
            self.city_label.config(text="Город: Не сгенерирован", fg="#7f8c8d")
            
            # Очищаем поисковые поля в комбобоксах
            if hasattr(self.country_combo, 'entry'):
                self.country_combo.entry.delete(0, tk.END)
            if hasattr(self.theme_combo, 'entry'):
                self.theme_combo.entry.delete(0, tk.END)
            
            # Очищаем текущий промпт
            self.current_prompt = None
            self.settings_manager.save_prompt("")
            
            # Обновляем статус
            self.update_status("✅ Готов к созданию нового лендинга")
            
            print("🔄 Форма полностью сброшена, готова для нового лендинга")
            
        except Exception as e:
            print(f"Ошибка сброса формы: {e}")
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.settings_manager.save_settings()
        self.root.destroy()
        
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()