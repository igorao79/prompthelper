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
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Отвязываем прокрутку при закрытии окна
        def _on_popup_destroy(event):
            canvas.unbind_all("<MouseWheel>")
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
        self.root.geometry("800x750")
        self.root.resizable(False, False)
        
        # Компоненты
        self.city_generator = CityGenerator()
        self.cursor_manager = CursorManager()
        self.settings_manager = SettingsManager()
        
        # Переменные
        self.selected_country = tk.StringVar()
        self.theme_var = tk.StringVar()
        self.domain_var = tk.StringVar()
        self.save_path_var = tk.StringVar(value=self.settings_manager.get_save_path())
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
            # Создаем основной фрейм с прокруткой
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
        """Создает основную область без прокрутки"""
        # Основной контейнер без отступов
        main_container = tk.Frame(self.root, bg="#f0f0f0")
        main_container.pack(fill="both", expand=True)
        
        # Содержимое напрямую без канваса и скролла
        self.scrollable_frame = tk.Frame(main_container, bg="#f0f0f0")
        self.scrollable_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
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
    
    def create_action_buttons(self):
        """Создает кнопки действий"""
        section = tk.Frame(self.scrollable_frame)
        section.pack(fill="x", pady=10)
        
        # Кнопка редактирования промпта
        edit_btn = tk.Button(
            section,
            text="✏️ Настроить промпт",
            command=self.edit_prompt,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            pady=5
        )
        edit_btn.pack(pady=(0, 8))
        
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
    
    def edit_prompt(self):
        """Редактирование промпта"""
        try:
            # Получаем данные (используем значения по умолчанию если не заполнены)
            theme = self.theme_var.get().strip() or "Продажа недвижимости"
            country = self.selected_country.get() or "Россия"
            domain = self.domain_var.get().strip() or "example"
            city = self.current_city or "Москва"
            
            # Генерируем промпт если нет сохраненного
            if not self.current_prompt:
                language = get_language_by_country(country)
                self.current_prompt = create_landing_prompt(country, city, language, domain, theme)
            
            # Открываем редактор
            edited_prompt = open_text_editor(self.current_prompt)
            if edited_prompt is not None:  # None означает отмену
                self.current_prompt = edited_prompt
                self.settings_manager.save_prompt(edited_prompt)
                messagebox.showinfo("Готово", "Промпт сохранен успешно!")
            
        except Exception as e:
            print(f"Ошибка редактирования промпта: {e}")
            messagebox.showerror("Ошибка", f"Не удалось отредактировать промпт: {e}")
    
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
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Создать лендинг:\n\n"
            f"Тематика: {theme}\n"
            f"Страна: {country}\n"
            f"Город: {self.current_city}\n"
            f"Домен: {domain}\n"
            f"Папка: {save_path}\n\n"
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
            
            # Создание структуры проекта
            project_path, media_path = self.cursor_manager.create_project_structure(
                domain, save_path
            )
            
            self.update_status("📄 Подготовка промпта...")
            
            # Используем отредактированный промпт если есть, иначе генерируем новый
            if self.current_prompt:
                full_prompt = self.current_prompt
            else:
                base_prompt = create_landing_prompt(country, city, language, domain, theme)
                full_prompt = base_prompt
            
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
                    f"Папка: {project_path}\n"
                    f"Cursor AI запущен с готовым промптом.\n\n"
                    f"Если промпт не вставился автоматически,\n"
                    f"нажмите Ctrl+V в Cursor AI"
                )
            else:
                self.update_status("⚠️ Cursor не найден, промпт скопирован")
                messagebox.showwarning(
                    "Предупреждение",
                    f"Папка проекта создана: {project_path}\n\n"
                    f"Cursor AI не найден, но промпт скопирован в буфер обмена.\n"
                    f"Откройте проект в Cursor вручную и вставьте промпт."
                )
                
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            print(error_msg)
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def update_status(self, text):
        """Обновляет статус"""
        self.status_label.config(text=text)
        self.root.update()
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.settings_manager.save_settings()
        self.root.destroy()
        
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()