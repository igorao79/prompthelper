# -*- coding: utf-8 -*-

"""
Главное окно приложения генератора лендингов
Обновлено с современным дизайном 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

from shared.data import COUNTRIES_DATA, THEME_COLORS
from shared.city_generator import CityGenerator
from shared.settings_manager import SettingsManager, get_desktop_path
from shared.helpers import (validate_domain, format_status_message, 
                           get_language_by_country, get_language_display_name,
                  open_text_editor, check_directory_exists, ensure_empty_zip_for_landing)
from core.cursor_manager import CursorManager
from generators.prompt_generator import create_landing_prompt

from .components.country_combobox import CountrySearchCombobox
from .components.theme_combobox import ThemeHistoryCombobox
from .styles.modern_theme import ModernTheme


class LandingPageGeneratorGUI:
    """Основной класс GUI приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✨ Генератор Лендингов v2.0 — Современный")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Современная тема
        self.theme = ModernTheme()
        self.theme.apply_to_root(self.root)
        
        # Улучшенные настройки окна
        self.root.minsize(900, 720)
        
        # Попытка установить иконку окна
        try:
            # Можно добавить ico файл позже
            pass
        except:
            pass
        
        # Компоненты
        self.city_generator = CityGenerator()
        self.cursor_manager = CursorManager()
        self.settings_manager = SettingsManager()
        
        # Переменные с ограничениями длины
        self.selected_country = tk.StringVar()
        
        # Тематика с ограничением 50 символов
        self.theme_var = tk.StringVar()
        def limit_theme_length(*args):
            value = self.theme_var.get()
            if len(value) > 50:
                self.theme_var.set(value[:50])
        self.theme_var.trace_add("write", limit_theme_length)
        
        # Домен с ограничением 50 символов  
        self.domain_var = tk.StringVar()
        def limit_domain_length(*args):
            value = self.domain_var.get()
            if len(value) > 50:
                self.domain_var.set(value[:50])
        self.domain_var.trace_add("write", limit_domain_length)
        self.save_path_var = tk.StringVar(value=self.settings_manager.get_save_path())
        self.last_created_project_path = None
        
        # Источник изображений удален — всегда AI-генерация
        
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
        """Создает современный интерфейс приложения"""
        try:
            # Современный заголовок с градиентом (имитация)
            header_frame = self.theme.create_modern_frame(self.root, bg=self.theme.colors.PRIMARY)
            header_frame.pack(fill="x", padx=0, pady=0)
            
            header = self.theme.create_modern_label(
                header_frame,
                text="✨ Генератор Лендингов v2.0 — Современный",
                style="heading_xl",
                bg=self.theme.colors.PRIMARY,
                fg=self.theme.colors.TEXT_PRIMARY,
                pady=15
            )
            header.pack()
            
            # Подзаголовок
            subtitle = self.theme.create_modern_label(
                header_frame,
                text="Создавайте профессиональные лендинги с искусственным интеллектом",
                style="body",
                bg=self.theme.colors.PRIMARY,
                fg=self.theme.colors.TEXT_SECONDARY
            )
            subtitle.pack()

            # ВЕРХНЯЯ ПАНЕЛЬ ДЕЙСТВИЙ
            toolbar = self.theme.create_modern_frame(header_frame, bg=self.theme.colors.PRIMARY, highlightthickness=0)
            toolbar.pack(fill="x", pady=(8, 12))

            inner = self.theme.create_modern_frame(toolbar, bg=self.theme.colors.PRIMARY, highlightthickness=0)
            inner.pack(fill="x", padx=10)

            # Кнопки слева: редактировать/сбросить промпт
            left = self.theme.create_modern_frame(inner, bg=self.theme.colors.PRIMARY, highlightthickness=0)
            left.pack(side="left")
            edit_btn = self.theme.create_modern_button(
                left,
                text=f"{self.theme.get_icon('edit')} Настроить промпт",
                command=self.edit_prompt,
                style="secondary",
                padx=16,
                pady=8
            )
            edit_btn.pack(side="left", padx=(0, 8))
            reset_btn = self.theme.create_modern_button(
                left,
                text=f"{self.theme.get_icon('reset')} Сбросить",
                command=self.reset_prompt,
                style="secondary",
                padx=16,
                pady=8
            )
            reset_btn.pack(side="left")

            # Главная кнопка справа
            right = self.theme.create_modern_frame(inner, bg=self.theme.colors.PRIMARY, highlightthickness=0)
            right.pack(side="right")
            create_button = self.theme.create_modern_button(
                right,
                text=f"{self.theme.get_icon('rocket')} СОЗДАТЬ ЛЕНДИНГ {self.theme.get_icon('magic')}",
                command=self.create_landing,
                style="primary",
                padx=28,
                pady=12
            )
            create_button.pack(side="right")
            self.theme.add_shadow_effect(create_button)

            # Верхняя панель уже добавлена выше
            
            # Создаем прокручиваемую область с канвасом и скроллбаром
            self.create_scrollable_frame()

            # Компактная одноколоночная раскладка для стабильности
            self.create_save_path_section()
            self.create_theme_section()
            self.create_country_section()
            self.create_info_section()
            self.create_domain_section()
            self.create_image_management_section()
            
            # Статус
            self.create_status_section(parent=self.scrollable_frame)
            
        except Exception as e:
            print(f"❌ Ошибка создания интерфейса: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def create_scrollable_frame(self):
        """Создает современную прокручиваемую область с канвасом и скроллбаром"""
        # Основной контейнер с современными стилями
        main_container = self.theme.create_modern_frame(
            self.root,
            bg=self.theme.colors.BACKGROUND,
            highlightthickness=0
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        
        # Создаем канвас и современный скроллбар
        self.canvas = tk.Canvas(
            main_container, 
            bg=self.theme.colors.BACKGROUND, 
            highlightthickness=0,
            borderwidth=0
        )
        
        scrollbar = ttk.Scrollbar(
            main_container, 
            orient="vertical", 
            command=self.canvas.yview,
            style="Modern.Vertical.TScrollbar"
        )
        
        # Фрейм для содержимого с современным стилем
        self.scrollable_frame = self.theme.create_modern_frame(
            self.canvas,
            bg=self.theme.colors.BACKGROUND,
            highlightthickness=0
        )
        
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
            # Обработка скролла для разных ОС
            if event.delta:
                # Windows и macOS
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                # Linux - используем event.num
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
        
        # Привязываем обработчики
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", configure_canvas_width)
        
        # Привязываем скролл мыши к канвасу и всем дочерним элементам
        # Windows и macOS
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)
        
        # Добавляем современные отступы для содержимого
        self.scrollable_frame.configure(padx=20, pady=15)
    
    def create_save_path_section(self, parent=None):
        """Создает современную секцию выбора папки для сохранения"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container, 
            text=f"{self.theme.get_icon('folder')} Папка для создания проектов",
            padx=15, 
            pady=12
        )
        section.pack(fill="x", pady=(0, 15), ipady=8)
        
        path_frame = self.theme.create_modern_frame(
            section,
            bg=self.theme.colors.SURFACE,
            highlightthickness=0
        )
        path_frame.pack(fill="x", pady=(5, 0))
        
        # Современное поле пути
        path_entry = self.theme.create_modern_entry(
            path_frame,
            textvariable=self.save_path_var,
            state="readonly",
            font=self.theme.typography.body_lg()
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
        
        # Современная кнопка выбора папки
        browse_btn = self.theme.create_modern_button(
            path_frame,
            text=f"{self.theme.get_icon('folder')} Выбрать",
            command=self.browse_save_path,
            style="primary",
            font=self.theme.typography.button_md()
        )
        browse_btn.pack(side="right", padx=(0, 8))
        
        # Современная кнопка сброса на рабочий стол
        reset_btn = self.theme.create_modern_button(
            path_frame,
            text=f"{self.theme.get_icon('home')} Рабочий стол",
            command=self.reset_to_desktop,
            style="secondary",
            font=self.theme.typography.button_md()
        )
        reset_btn.pack(side="right")
    
    def create_theme_section(self, parent=None):
        """Создает современную секцию тематики"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container, 
            text=f"{self.theme.get_icon('target')} Тематика лендинга",
            padx=15, 
            pady=12
        )
        section.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Комбобокс с историей (обновляем стили)
        self.theme_combo = ThemeHistoryCombobox(section, self.theme_var)
        self.theme_combo.pack(fill="x", pady=(5, 0))
        self.theme_combo.set_history(self.settings_manager.get_theme_history())
        
        # Современные подсказки
        theme_hint = self.theme.create_modern_label(
            section,
            text="💡 Примеры: Продажа недвижимости, Строительство домов, Ремонт квартир",
            style="caption",
            bg=self.theme.colors.SURFACE,
            wraplength=650
        )
        theme_hint.pack(anchor="w", pady=(8, 0))
    
    def create_country_section(self, parent=None):
        """Создает современную секцию выбора страны"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container, 
            text=f"{self.theme.get_icon('globe')} Страна и город",
            padx=15, 
            pady=12
        )
        section.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Комбобокс с поиском стран (обновляем стили)
        self.country_combo = CountrySearchCombobox(
            section,
            settings_manager=self.settings_manager,
            textvariable=self.selected_country,
            on_select=self.on_country_select
        )
        self.country_combo.pack(fill="x", pady=(5, 0))
        
        # Современная инструкция
        instruction = self.theme.create_modern_label(
            section,
            text=f"💡 Начните печатать для поиска. {self.theme.get_icon('star')} для избранного.",
            style="caption",
            bg=self.theme.colors.SURFACE
        )
        instruction.pack(anchor="w", pady=(8, 0))
    
    def create_info_section(self, parent=None):
        """Создает современную информационную секцию"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container, 
            text=f"{self.theme.get_icon('info')} Информация",
            padx=15, 
            pady=12
        )
        section.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Контейнер для информации
        info_container = self.theme.create_modern_frame(
            section,
            bg=self.theme.colors.SURFACE,
            highlightthickness=0
        )
        info_container.pack(fill="x", pady=(5, 0))
        
        self.language_label = self.theme.create_modern_label(
            info_container, 
            text="🌐 Язык: не выбран", 
            style="body",
            bg=self.theme.colors.SURFACE
        )
        self.language_label.pack(anchor="w", pady=2)
        
        self.city_label = self.theme.create_modern_label(
            info_container, 
            text="🏙️ Город: не выбран", 
            style="body",
            bg=self.theme.colors.SURFACE
        )
        self.city_label.pack(anchor="w", pady=2)
        
        # Современная кнопка генерации города
        city_btn = self.theme.create_modern_button(
            info_container, 
            text="🎲 Сгенерировать город", 
            command=self.generate_new_city,
            style="secondary",
            font=self.theme.typography.button_sm()
        )
        city_btn.pack(anchor="w", pady=(8, 0))
    
    def create_domain_section(self, parent=None):
        """Создает современную секцию домена"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container, 
            text="🌐 Домен сайта",
            padx=15, 
            pady=12
        )
        section.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Современное поле домена
        domain_entry = self.theme.create_modern_entry(
            section, 
            textvariable=self.domain_var,
            font=self.theme.typography.body_lg(),
            width=60
        )
        domain_entry.pack(anchor="w", fill="x", pady=(5, 0), ipady=8)
        
        # Подсказка
        domain_hint = self.theme.create_modern_label(
            section,
            text="💡 Введите название домена для вашего проекта (например: my-business)",
            style="caption",
            bg=self.theme.colors.SURFACE
        )
        domain_hint.pack(anchor="w", pady=(8, 0))
    
    def create_action_buttons(self):
        """Создает современные кнопки действий"""
        section = self.theme.create_modern_frame(self.scrollable_frame, bg=self.theme.colors.BACKGROUND, highlightthickness=0)
        # В компактной раскладке панель действий вынесена наверх — скрываем секцию
        section.pack_forget()
        
        # Современный фрейм для кнопок промпта
        prompt_buttons_frame = self.theme.create_modern_frame(
            section,
            bg=self.theme.colors.BACKGROUND,
            highlightthickness=0
        )
        prompt_buttons_frame.pack(pady=(0, 15))
        
        # Современная кнопка редактирования промпта
        edit_btn = self.theme.create_modern_button(
            prompt_buttons_frame,
            text=f"{self.theme.get_icon('edit')} Настроить промпт",
            command=self.edit_prompt,
            style="secondary",
            font=self.theme.typography.button_md()
        )
        edit_btn.pack(side="left", padx=(0, 10))
        
        # Современная кнопка сброса промпта  
        reset_btn = self.theme.create_modern_button(
            prompt_buttons_frame,
            text=f"{self.theme.get_icon('reset')} Сбросить",
            command=self.reset_prompt,
            style="secondary",
            font=self.theme.typography.button_md()
        )
        reset_btn.pack(side="left")
        
        # Кнопка генерации изображений удалена
        
        # Кнопка "Создать" перенесена в верхнюю панель
    
    def create_image_management_section(self, parent=None):
        """Компактная плашка перегенерации изображений"""
        container = parent if parent is not None else self.scrollable_frame
        section = self.theme.create_modern_labelframe(
            container,
            text=f"{self.theme.get_icon('image')} Перегенерация изображений",
            padx=12,
            pady=10
        )
        section.pack(fill="x", pady=(0, 15), ipady=6)

        # Путь проекта
        path_frame = self.theme.create_modern_frame(section, bg=self.theme.colors.SURFACE)
        path_frame.pack(fill="x", pady=(5, 8))

        self.project_path_var = tk.StringVar()
        entry = self.theme.create_modern_entry(path_frame, textvariable=self.project_path_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=6)

        browse_btn = self.theme.create_modern_button(
            path_frame,
            text=f"{self.theme.get_icon('folder')} Выбрать",
            command=self.browse_project_path,
            style="secondary",
        )
        browse_btn.pack(side="right")

        # Кнопки действий (компактно)
        buttons = self.theme.create_modern_frame(section, bg=self.theme.colors.SURFACE)
        buttons.pack(fill="x")

        regen_all_btn = self.theme.create_modern_button(
            buttons,
            text=f"{self.theme.get_icon('reset')} Пересоздать все",
            command=self.regenerate_all_images,
            style="primary"
        )
        regen_all_btn.pack(side="left", padx=(0, 8))

        # Кнопки отдельных изображений короткими чипами
        names = [
            ("Главное", "main"), ("О нас 1", "about1"), ("О нас 2", "about2"), ("О нас 3", "about3"),
            ("Отзыв 1", "review1"), ("Отзыв 2", "review2"), ("Отзыв 3", "review3"), ("Favicon", "favicon")
        ]
        chips = self.theme.create_modern_frame(section, bg=self.theme.colors.SURFACE)
        chips.pack(fill="x", pady=(10, 0))
        for label, key in names:
            btn = self.theme.create_modern_button(
                chips,
                text=label,
                command=lambda k=key: self.regenerate_single_image(k),
                style="secondary",
                padx=10,
                pady=6
            )
            btn.pack(side="left", padx=4, pady=2)
    
    def create_status_section(self, parent=None):
        """Создает современную секцию статуса"""
        # Современный статусный контейнер
        container = parent if parent is not None else self.scrollable_frame
        status_container = self.theme.create_modern_frame(
            container,
            bg=self.theme.colors.CARD,
            highlightthickness=1,
            highlightbackground=self.theme.colors.BORDER
        )
        status_container.pack(fill="x", pady=(15, 0), ipady=10)
        
        self.status_label = self.theme.create_modern_label(
            status_container, 
            text=f"{self.theme.get_icon('success')} Готов к работе", 
            style="body",
            bg=self.theme.colors.CARD,
            fg=self.theme.colors.SUCCESS
        )
        self.status_label.pack(pady=5)
    
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
            language_display = get_language_display_name(country)
            self.language_label.config(
                text=f"🌐 Язык: {language_display}", 
                fg=self.theme.colors.SUCCESS
            )
            self.generate_new_city()
            
    def generate_new_city(self):
        """Генерирует новый город"""
        country = self.selected_country.get()
        if not country:
            messagebox.showwarning("Предупреждение", "Сначала выберите страну!")
            return
            
        new_city = self.city_generator.get_random_city(country)
        self.current_city = new_city
        self.city_label.config(
            text=f"🏙️ Город: {new_city}", 
            fg=self.theme.colors.SUCCESS
        )
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
        is_valid, error_msg, corrected_domain = validate_domain(domain)
        if not is_valid:
            return False, error_msg
        
        # Обновляем поле домена исправленным значением
        if corrected_domain != domain:
            self.domain_var.set(corrected_domain)
            print(f"🔧 Домен исправлен: {domain} → {corrected_domain}")
            
        if not self.current_city:
            return False, "Сгенерируйте город!"
        
        # Проверяем существование папки
        save_path = self.save_path_var.get()
        if not Path(save_path).exists():
            return False, f"Выбранная папка не существует: {save_path}"
            
        return True, ""
        
    def generate_images_only(self):
            return
    
    def _generate_images_only_process(self, media_path, theme):
                return

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
        
        # Получаем человеко-читаемое название языка для диалога
        language_display = get_language_display_name(country)
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Создать лендинг:\n\n"
            f"Тематика: {theme}\n"
            f"Страна: {country}\n"
            f"Город: {self.current_city}\n"
            f"Язык: {language_display}\n"
            f"Домен: {domain}\n"
            f"Папка: {save_path}\n"
            f"Промпт: {prompt_type}\n\n"
            f"Будет создан проект с папкой media. Изображения будут сгенерированы автоматически.\n\n"
            f"Продолжить?"
        )
        if not result:
            return
            
        # Запуск в отдельном потоке
        threading.Thread(target=self._create_landing_process, daemon=True).start()
    
    def _create_landing_process(self):
        """Процесс создания лендинга в отдельном потоке"""
        try:
            print("🚀 ЗАПУСК ПРОЦЕССА СОЗДАНИЯ ЛЕНДИНГА")
            print("=" * 50)
            
            # Получение данных
            theme = self.theme_var.get().strip()
            country = self.selected_country.get()
            language = get_language_by_country(country)
            domain = self.domain_var.get().strip()
            city = self.current_city
            save_path = self.save_path_var.get()
            
            print(f"📋 ПАРАМЕТРЫ СОЗДАНИЯ:")
            print(f"  • Тематика: {theme}")
            print(f"  • Страна: {country}")
            print(f"  • Язык: {language}")
            print(f"  • Домен: {domain}")
            print(f"  • Город: {city}")
            print(f"  • Папка: {save_path}")
            
            # Пустой ZIP по правилу: <КодСтраны>_<Тематика>_<ДД.ММ.ГГГГ>.zip
            try:
                zip_path = ensure_empty_zip_for_landing(save_path, country, theme)
                if zip_path:
                    print(f"📦 Создан пустой ZIP: {zip_path}")
                else:
                    print("ℹ️ ZIP не создан (уже существует для этой страны и тематики)")
            except Exception as _e:
                print(f"⚠️ Не удалось создать ZIP: {_e}")
            
            # Обновление статуса
            self.update_status("🔄 Создание папок...")
            print("🔄 Шаг 1: Создание папок...")
            
            # Создание структуры проекта, опциональная генерация изображений
            print("🔄 Шаг 2: Создание структуры проекта...")
            should_generate_images = True
            project_path, media_path = self.cursor_manager.create_project_structure(
                domain, save_path, theme, self.update_status, generate_images=should_generate_images
            )
            print(f"✅ Структура проекта создана: {project_path}")
            print(f"✅ Папка media создана: {media_path}")
            
            # Сохраняем путь проекта для автоматического выбора при перегенерации
            self.last_created_project_path = project_path
            
            self.update_status("📄 Подготовка промпта...")
            print("🔄 Шаг 3: Подготовка промпта...")
            
            # Используем отредактированный промпт если есть, иначе генерируем новый с актуальными данными
            if self.current_prompt:
                full_prompt = self.current_prompt
                print("📝 Используется отредактированный промпт")
            else:
                full_prompt = create_landing_prompt(country, city, language, domain, theme)
                print("📝 Сгенерирован новый промпт")
            
            print(f"📏 Длина промпта: {len(full_prompt)} символов")
            
            self.update_status("🚀 Запуск Cursor AI...")
            print("🔄 Шаг 4: Запуск Cursor AI...")
            
            # Запуск Cursor AI
            success, message = self.cursor_manager.open_project_and_paste_prompt(
                project_path, full_prompt, self.root, auto_paste=True, paste_delay=5
            )
            print(f"🎯 Результат запуска Cursor: success={success}, message='{message}'")
            
            if success:
                self.update_status("✅ Готово! Cursor AI запущен")
                messagebox.showinfo(
                    "Успех!", 
                    f"Проект создан успешно!\n\n"
                    f"📁 Папка: {project_path}\n"
                    f"🎨 Папка media: {media_path}\n"
                    f"🚀 Cursor AI запущен с готовым промптом\n\n"
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
            error_msg = f"Ошибка создания лендинга: {str(e)}"
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {error_msg}")
            print("🐛 ПОЛНАЯ ТРАССИРОВКА:")
            import traceback
            traceback.print_exc()
            
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Критическая ошибка", 
                               f"{error_msg}\n\n"
                               f"Проверьте консоль для подробной информации.\n\n"
                               f"💡 Попробуйте:\n"
                               f"• Перезапустить приложение\n"
                               f"• Проверить заполнение всех полей\n"
                               f"• Выбрать другую папку для сохранения")
    
    def update_status(self, text):
        """Обновляет статус с современными цветами"""
        # Определяем цвет по типу сообщения
        color = self.theme.colors.TEXT_SECONDARY
        if "✅" in text or "Готов" in text:
            color = self.theme.colors.SUCCESS
        elif "⚠️" in text or "Предупреждение" in text:
            color = self.theme.colors.WARNING
        elif "❌" in text or "Ошибка" in text:
            color = self.theme.colors.DANGER
        elif "🔄" in text or "Создание" in text or "Генерация" in text:
            color = self.theme.colors.PRIMARY
        
        self.status_label.config(text=text, fg=color)
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
            self.update_status(f"🎨 Пересоздание AI-ИЗОБРАЖЕНИЯ {image_name}...")
            
            # Импортируем генератор
            from generators.image_generator import ImageGenerator
            image_generator = ImageGenerator(
                silent_mode=True,
                fast_mode=True
            )
            
            # Получаем промпты (через основной генератор)
            from generators.prompt_generator import create_complete_prompts_dict
            prompts = create_complete_prompts_dict(theme)
            
            # Только AI-генерация
            
            # ОРИГИНАЛЬНАЯ ЛОГИКА AI-генерации: разные промпты для разных типов
            if image_name in ["review1", "review2", "review3"]:
                # ДЛЯ ОТЗЫВОВ - СЛОЖНАЯ СИСТЕМА РАЗНООБРАЗИЯ ЛИЦ! 
                self.update_status(f"🔥 {image_name}: Активируем ЭКСТРЕМАЛЬНУЮ систему разнообразия лиц!")
                
                try:
                    from generators.prompt_generator import create_human_focused_review_prompts
                    human_reviews = create_human_focused_review_prompts()
                    
                    # Выбираем соответствующий промпт
                    review_index = int(image_name[-1]) - 1  # review1 -> 0, review2 -> 1, review3 -> 2
                    prompt = human_reviews[review_index]
                    
                    self.update_status(f"✅ {image_name}: Получен сложный промпт ({len(prompt)} символов)")
                    print(f"🎭 Тип лица: {['Западный/Европейский', 'Азиатский/Восточный', 'Африканский/Латиноамериканский'][review_index]}")
                except Exception as e:
                    self.update_status(f"⚠️ {image_name}: Ошибка сложной системы ({e}), используем fallback")
                    prompt = "happy customer portrait"  # Fallback
                    
            elif image_name == "favicon":
                # ДЛЯ ФАВИКОНКИ - ТЕМАТИЧЕСКАЯ ПРОСТАЯ ИКОНКА!  
                prompt = f"{theme} simple icon logo, minimalist business symbol"
                self.update_status(f"🏷️ {image_name}: Используем тематический промпт для иконки: {theme}")
            else:
                # Для остальных используем тематические промпты
                if isinstance(prompts, list):
                    prompt_dict = {
                        'main': prompts[0] if len(prompts) > 0 else f"professional {theme} service",
                        'about1': prompts[1] if len(prompts) > 1 else f"modern {theme} business",
                        'about2': prompts[2] if len(prompts) > 2 else f"quality {theme} company",
                        'about3': prompts[3] if len(prompts) > 3 else f"expert {theme} team"
                    }
                    prompt = prompt_dict.get(image_name, f"professional {theme} service")
                else:
                    # Если промпты уже в виде словаря
                    prompt = prompts.get(image_name, f"professional {theme} service")
            
            # Применяем рандомизацию через основной генератор
            prompt = image_generator._add_randomization(prompt, image_name)
            
            # Специальная обработка для фавиконки
            if image_name == "favicon":
                filename = Path(media_path) / f"{image_name}.jpg"
                
                # Генерируем изображение через Pollinations
                image = self._generate_single_image_pollinations(prompt, image_generator)
                if image:
                    from PIL import Image
                    image = image.resize((512, 512), Image.Resampling.LANCZOS)
                    image = image_generator._make_favicon_transparent(image)
                    
                    # Используем сжатие для AI фавиконки (50кб)
                    if image_generator._save_compressed_image(image, str(filename), target_size_kb=50):
                        self.update_status(f"✅ AI фавиконка пересоздана!")
                        messagebox.showinfo("Готово", f"Фавиконка '{image_name}' пересоздана!")
                    else:
                        self.update_status(f"❌ Не удалось создать фавиконку")
                        messagebox.showerror("Ошибка", f"Не удалось создать фавиконку '{image_name}'")
                else:
                    self.update_status(f"❌ Не удалось создать фавиконку")
                    messagebox.showerror("Ошибка", f"Не удалось создать фавиконку '{image_name}'")
            else:
                # Обычная генерация для остальных изображений
                # Генерируем изображение через Pollinations
                image = self._generate_single_image_pollinations(prompt, image_generator)
                
                if image:
                    # Унифицируем формат - все изображения в .jpg
                    filename = Path(media_path) / f"{image_name}.jpg"
                    
                    # Для обычных изображений используем сжатие до 150кб
                    if image_generator._save_compressed_image(image, str(filename), target_size_kb=150):
                        self.update_status(f"✅ AI-изображение {image_name} пересоздано с сжатием!")
                        messagebox.showinfo("Готово", f"AI-изображение '{image_name}' успешно пересоздано!")
                    else:
                        self.update_status(f"❌ Не удалось сохранить AI-изображение {image_name}")
                        messagebox.showerror("Ошибка", f"Не удалось сохранить AI-изображение '{image_name}'")
                else:
                    self.update_status(f"❌ Не удалось создать AI-изображение {image_name}")
                    messagebox.showerror("Ошибка", f"Не удалось создать AI-изображение '{image_name}'")
                
        except Exception as e:
            error_msg = f"Ошибка пересоздания {image_name}: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def _regenerate_all_images_process(self, media_path, theme):
        """Процесс пересоздания всех изображений"""
        try:
            self.update_status(f"🎨 Пересоздание всех AI-ИЗОБРАЖЕНИЙ...")
            
            # Импортируем генератор
            from generators.image_generator import ImageGenerator
            
            image_generator = ImageGenerator(
                silent_mode=True,
                fast_mode=True
            )
            
            # Генерируем полный набор с выбранным источником
            results = image_generator.generate_thematic_set(
                theme_input=theme,
                media_dir=media_path,
                progress_callback=self.update_status
            )
            
            # Подсчитываем результаты
            successful_count = results if isinstance(results, int) else 0
            
            # 🆕 УЧИТЫВАЕМ ТИП ИСТОЧНИКА В СООБЩЕНИЯХ
            action_past = "пересоздано"
            source_desc = "AI-изображений"
            
            self.update_status(f"✅ {action_past.capitalize()} {successful_count}/8 {source_desc}")
            
            messagebox.showinfo(
                "Готово",
                f"Пересоздание завершено!\n\n"
                f"Успешно {action_past}: {successful_count}/8 {source_desc}\n"
                f"Источник: 🤖 AI-генерация\n"
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
            # Сохраняем данные для автоматического заполнения перегенерации
            last_theme = self.theme_var.get().strip()
            
            # Автоматически устанавливаем папку последнего проекта для перегенерации
            if hasattr(self, 'last_created_project_path') and self.last_created_project_path:
                self.project_path_var.set(self.last_created_project_path)
            else:
                # Очищаем тематику только если нет сохраненного проекта
                self.theme_var.set("")
            
            # Очищаем остальные поля формы  
            self.domain_var.set("")
            self.selected_country.set("")
            self.current_city = ""
            
            # Обновляем отображение с современными цветами
            self.language_label.config(
                text="🌐 Язык: не выбран", 
                fg=self.theme.colors.TEXT_MUTED
            )
            self.city_label.config(
                text="🏙️ Город: не выбран", 
                fg=self.theme.colors.TEXT_MUTED
            )
            
            # Очищаем поисковые поля в комбобоксах БЕЗОПАСНО через textvariable
            if hasattr(self.country_combo, 'search_var'):
                self.country_combo.search_var.set("")
            
            # Очищаем текущий промпт
            self.current_prompt = None
            self.settings_manager.save_prompt("")
            
            # Обновляем статус с подсказкой
            if hasattr(self, 'last_created_project_path') and self.last_created_project_path:
                self.update_status("✅ Проект создан! Папка автоматически выбрана для перегенерации")
            else:
                self.update_status("✅ Готов к созданию нового лендинга")
            
        except Exception as e:
            print(f"Ошибка сброса формы: {e}")
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.settings_manager.save_settings()
        self.root.destroy()
        
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()

    def _generate_single_image_pollinations(self, prompt, image_generator):
        """Генерирует одно изображение через Pollinations API"""
        try:
            import requests
            from urllib.parse import quote
            from PIL import Image
            from io import BytesIO
            import time
            
            # Создаем временный файл для результата
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Генерируем изображение через метод генератора
            result = image_generator._generate_image_pollinations_aggressive(
                prompt, 'temp', tempfile.gettempdir()
            )
            
            if result:
                # Загружаем изображение
                image = Image.open(result)
                return image
            else:
                return None
                
        except Exception as e:
            print(f"❌ Ошибка генерации изображения: {e}")
            return None 