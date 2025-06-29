# -*- coding: utf-8 -*-

"""
GUI интерфейс для генератора лендингов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from data import COUNTRIES_DATA, THEME_COLORS
from utils import CityGenerator, validate_domain, format_status_message, get_language_by_country
from cursor_manager import CursorManager
from prompt_generator import create_landing_prompt, get_theme_specific_instructions


class LandingPageGeneratorGUI:
    """Основной класс GUI приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Генератор Лендингов")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Компоненты
        self.city_generator = CityGenerator()
        self.cursor_manager = CursorManager()
        
        # Переменные
        self.selected_country = tk.StringVar()
        self.theme_var = tk.StringVar()
        self.domain_var = tk.StringVar()
        self.current_city = ""
        
        # Настройка интерфейса
        self.setup_ui()
        
    def setup_ui(self):
        """Создает интерфейс приложения"""
        # Заголовок
        header = tk.Label(
            self.root, 
            text="🚀 Генератор Лендингов 🚀", 
            font=("Arial", 16, "bold"), 
            bg="#2c3e50", 
            fg="white",
            pady=15
        )
        header.pack(fill="x")
        
        # Основная область с прокруткой
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Тематика
        tk.Label(main_frame, text="Тематика лендинга:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        theme_entry = tk.Entry(
            main_frame, 
            textvariable=self.theme_var,
            font=("Arial", 11),
            width=60
        )
        theme_entry.pack(fill="x", pady=(0,5))
        
        # Подсказки для тематики
        theme_hint = tk.Label(
            main_frame,
            text="Примеры: Продажа недвижимости, Строительство домов, Ремонт квартир, Коммерческая недвижимость, Загородная недвижимость",
            font=("Arial", 9),
            fg="#666",
            wraplength=700
        )
        theme_hint.pack(anchor="w", pady=(0,15))
        
        # Страна
        tk.Label(main_frame, text="Страна:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        country_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.selected_country,
            values=list(COUNTRIES_DATA.keys()),
            state="readonly", 
            font=("Arial", 11),
            width=30
        )
        country_combo.pack(anchor="w", pady=(0,15))
        country_combo.bind("<<ComboboxSelected>>", self.on_country_select)
        
        # Информация
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0,15))
        
        self.language_label = tk.Label(info_frame, text="Язык: не выбран", font=("Arial", 11), fg="#666")
        self.language_label.pack(anchor="w")
        
        self.city_label = tk.Label(info_frame, text="Город: не выбран", font=("Arial", 11), fg="#666")
        self.city_label.pack(anchor="w")
        
        # Кнопка генерации города
        city_btn = tk.Button(
            info_frame, 
            text="🎲 Сгенерировать город", 
            command=self.generate_new_city,
            bg="#f39c12", 
            fg="white",
            font=("Arial", 10, "bold")
        )
        city_btn.pack(anchor="w", pady=(5,0))
        
        # Домен
        tk.Label(main_frame, text="Домен:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15,5))
        domain_entry = tk.Entry(
            main_frame, 
            textvariable=self.domain_var, 
            font=("Arial", 12),
            width=40
        )
        domain_entry.pack(anchor="w", pady=(0,20))
        
        # ГЛАВНАЯ КНОПКА - САМАЯ БОЛЬШАЯ И ЗАМЕТНАЯ
        create_button = tk.Button(
            main_frame,
            text="🚀 СОЗДАТЬ ЛЕНДИНГ",
            command=self.create_landing,
            bg="#e74c3c",
            fg="white", 
            font=("Arial", 18, "bold"),
            padx=50,
            pady=20,
            relief="raised",
            bd=5,
            cursor="hand2"
        )
        create_button.pack(pady=30)
        
        # Статус
        self.status_label = tk.Label(
            main_frame, 
            text="✅ Готов к работе", 
            font=("Arial", 10), 
            fg="#27ae60"
        )
        self.status_label.pack(pady=(20,0))
        
    def on_country_select(self, event=None):
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
            
        return True, ""
        
    def create_landing(self):
        """Основная функция создания лендинга"""
        print("КНОПКА НАЖАТА!")  # Отладка
        
        # Валидация
        is_valid, error_msg = self.validate_form()
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg)
            return
            
        # Подтверждение
        theme = self.theme_var.get().strip()
        country = self.selected_country.get()
        domain = self.domain_var.get().strip()
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Создать лендинг:\n\n"
            f"Тематика: {theme}\n"
            f"Страна: {country}\n"
            f"Город: {self.current_city}\n"
            f"Домен: {domain}\n\n"
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
            
            # Обновление статуса
            self.update_status("🔄 Создание папок...")
            
            # Создание структуры проекта
            project_path, media_path = self.cursor_manager.create_project_structure(domain)
            
            self.update_status("📄 Подготовка промпта...")
            
            # Генерация промпта
            base_prompt = create_landing_prompt(country, city, language, domain, theme)
            theme_instructions = get_theme_specific_instructions(theme)
            full_prompt = base_prompt + theme_instructions
            
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
                    f"используйте Ctrl+V для вставки."
                )
            else:
                self.update_status(f"⚠️ {message}")
                messagebox.showinfo("Информация", message)
                
        except Exception as e:
            error_msg = f"Произошла ошибка: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
            
    def update_status(self, text):
        """Обновляет статусную строку"""
        self.root.after(0, lambda: self.status_label.config(text=text))
        
    def run(self):
        """Запускает приложение"""
        print("Запуск GUI...")
        self.root.mainloop()
        print("GUI завершен")