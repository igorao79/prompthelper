# -*- coding: utf-8 -*-

"""
Компонент комбобокса для выбора стран с поиском и избранным
"""

import tkinter as tk
from tkinter import ttk
from shared.data import COUNTRIES_DATA


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
        self.last_selected = self.settings_manager.get_last_selected_country()
        
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
            font=("Arial", 11),
            width=40
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
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
                # Обработка скролла для разных ОС
                if event.delta:
                    # Windows и macOS
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                else:
                    # Linux - используем event.num
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")
        
        # Привязываем прокрутку к нескольким элементам для лучшей работы
        # Windows и macOS
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.items_frame.bind("<MouseWheel>", _on_mousewheel)
        self.popup_window.bind("<MouseWheel>", _on_mousewheel)
        # Linux
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
        self.items_frame.bind("<Button-4>", _on_mousewheel)
        self.items_frame.bind("<Button-5>", _on_mousewheel)
        self.popup_window.bind("<Button-4>", _on_mousewheel)
        self.popup_window.bind("<Button-5>", _on_mousewheel)
        
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
                    canvas.unbind("<Button-4>")
                    canvas.unbind("<Button-5>")
                if self.items_frame.winfo_exists():
                    self.items_frame.unbind("<MouseWheel>")
                    self.items_frame.unbind("<Button-4>")
                    self.items_frame.unbind("<Button-5>")
                if self.popup_window.winfo_exists():
                    self.popup_window.unbind("<MouseWheel>")
                    self.popup_window.unbind("<Button-4>")
                    self.popup_window.unbind("<Button-5>")
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
        """Обновляет список стран с приоритетом для последней выбранной"""
        # Очищаем старые элементы
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        items_added = []
        
        # ПРИОРИТЕТ 1: Последняя выбранная страна (ЖЕЛТОЕ выделение)
        if (self.last_selected and 
            self._matches_search(self.last_selected) and 
            self.last_selected in self.all_countries):
            self.create_country_item(self.last_selected, False, is_last_selected=True)
            items_added.append(self.last_selected)
            
            # Разделитель после последней выбранной
            if (self.favorites or 
                any(self._matches_search(c) for c in self.filtered_countries if c != self.last_selected)):
                separator = ttk.Separator(self.items_frame)
                separator.pack(fill="x", pady=3)
        
        # ПРИОРИТЕТ 2: Избранные страны
        if self.favorites:
            for country in self.favorites:
                if self._matches_search(country) and country not in items_added:
                    self.create_country_item(country, True)
                    items_added.append(country)
            
            # Разделитель после избранных
            if any(self._matches_search(c) for c in self.filtered_countries if c not in items_added):
                separator = ttk.Separator(self.items_frame)
                separator.pack(fill="x", pady=2)
        
        # ПРИОРИТЕТ 3: Остальные страны
        for country in self.filtered_countries:
            if country not in items_added and self._matches_search(country):
                self.create_country_item(country, False)
    
    def create_country_item(self, country, is_favorite, is_last_selected=False):
        """Создает элемент страны с возможностью выделения последней выбранной"""
        frame = ttk.Frame(self.items_frame)
        frame.pack(fill="x")
        
        # Определяем стиль и цвета
        if is_last_selected:
            # ЖЕЛТОЕ выделение для последней выбранной страны
            style = "LastSelected.TLabel"
            bg_color = "#FFE135"  # Ярко-желтый
            fg_color = "#000000"  # Черный текст
            prefix = "🕒 "  # Иконка часов для последней выбранной
        elif is_favorite:
            style = "Favorite.TLabel"
            bg_color = None
            fg_color = None
            prefix = ""
        else:
            style = "Country.TLabel"
            bg_color = None
            fg_color = None
            prefix = ""
        
        # Настраиваем стиль для последней выбранной
        if is_last_selected:
            ttk.Style().configure("LastSelected.TLabel", 
                                background=bg_color, 
                                foreground=fg_color,
                                padding=6,
                                font=("Arial", 9, "bold"))
        
        # Метка страны
        label = ttk.Label(
            frame, 
            text=f"{prefix}{country}",
            style=style
        )
        label.pack(side="left", fill="x", expand=True)
        
        # Звездочка и дополнительные иконки
        icon_text = ""
        if is_last_selected:
            icon_text = "🕒"  # Часы для последней выбранной
        elif is_favorite:
            icon_text = "★"  # Звезда для избранных
        else:
            icon_text = "☆"  # Пустая звезда для обычных
        
        star = ttk.Label(
            frame,
            text=icon_text,
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
                        # Обработка скролла для разных ОС
                        if event.delta:
                            # Windows и macOS
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                        else:
                            # Linux - используем event.num
                            if event.num == 4:
                                canvas.yview_scroll(-1, "units")
                            elif event.num == 5:
                                canvas.yview_scroll(1, "units")
            
            # Windows и macOS
            frame.bind("<MouseWheel>", _item_mousewheel)
            label.bind("<MouseWheel>", _item_mousewheel)
            star.bind("<MouseWheel>", _item_mousewheel)
            # Linux
            frame.bind("<Button-4>", _item_mousewheel)
            frame.bind("<Button-5>", _item_mousewheel)
            label.bind("<Button-4>", _item_mousewheel)
            label.bind("<Button-5>", _item_mousewheel)
            star.bind("<Button-4>", _item_mousewheel)
            star.bind("<Button-5>", _item_mousewheel)
        
        # Подсветка при наведении
        for widget in (label, star):
            widget.bind('<Enter>', lambda e, w=widget: w.configure(foreground="#2980b9"))
            widget.bind('<Leave>', lambda e, w=widget: w.configure(foreground="black"))
    
    def _matches_search(self, country):
        """Проверяет соответствие поисковому запросу"""
        search = self.search_var.get().lower()
        return not search or search in country.lower()
    
    def _select_country(self, country):
        """Выбирает страну и сохраняет её как последнюю выбранную"""
        self.textvariable.set(country)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, country)
        
        # Сохраняем как последнюю выбранную страну
        self.settings_manager.set_last_selected_country(country)
        self.last_selected = country
        
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
        
        # Обновляем последнюю выбранную страну
        self.last_selected = self.settings_manager.get_last_selected_country()
        
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