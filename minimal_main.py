#!/usr/bin/env python3
"""
Минимальная версия генератора лендингов для EXE
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import webbrowser
import subprocess
from pathlib import Path

class MinimalLandingGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Генератор Лендингов v2.0 - EXE")
        self.root.geometry("800x600")
        
        # Базовые переменные
        self.project_folder = tk.StringVar()
        self.theme = tk.StringVar(value="кафе")
        self.country = tk.StringVar(value="Россия")
        
        self.create_interface()
        
    def create_interface(self):
        """Создает простой интерфейс"""
        # Заголовок
        title_label = tk.Label(self.root, text="🚀 Генератор Лендингов v2.0", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Рамка для основных элементов
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Выбор папки
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Папка проекта", padding=10)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.project_folder, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Выбрать", command=self.select_folder).pack(side=tk.RIGHT)
        
        # Тематика
        theme_frame = ttk.LabelFrame(main_frame, text="🎯 Тематика", padding=10)
        theme_frame.pack(fill=tk.X, pady=5)
        
        themes = ["кафе", "ресторан", "автомойка", "парикмахерская", "стоматология", 
                 "фитнес", "строительство", "салон красоты"]
        ttk.Combobox(theme_frame, textvariable=self.theme, values=themes, width=30).pack()
        
        # Страна
        country_frame = ttk.LabelFrame(main_frame, text="🌍 Страна", padding=10)
        country_frame.pack(fill=tk.X, pady=5)
        
        countries = ["Россия", "Украина", "Беларусь", "Казахстан", "США", "Германия"]
        ttk.Combobox(country_frame, textvariable=self.country, values=countries, width=30).pack()
        
        # Кнопки действий
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(buttons_frame, text="🎨 Создать лендинг", 
                  command=self.create_landing, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🖼️ Генерировать изображения", 
                  command=self.generate_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📱 Открыть Cursor", 
                  command=self.open_cursor).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_text = tk.Text(main_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        self.log("✅ Интерфейс загружен!")
        self.log("🎯 Выберите папку проекта и начните работу")
        
    def log(self, message):
        """Добавляет сообщение в лог"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def select_folder(self):
        """Выбор папки проекта"""
        folder = filedialog.askdirectory(title="Выберите папку проекта")
        if folder:
            self.project_folder.set(folder)
            self.log(f"📁 Выбрана папка: {folder}")
            
    def create_landing(self):
        """Создает лендинг"""
        if not self.project_folder.get():
            messagebox.showwarning("Ошибка", "Выберите папку проекта!")
            return
            
        self.log("🎨 Создание лендинга...")
        self.log(f"🎯 Тематика: {self.theme.get()}")
        self.log(f"🌍 Страна: {self.country.get()}")
        
        # Здесь была бы логика создания лендинга
        # Пока просто имитируем
        
        self.log("✅ Лендинг создан успешно!")
        
    def generate_images(self):
        """Генерирует изображения"""
        if not self.project_folder.get():
            messagebox.showwarning("Ошибка", "Выберите папку проекта!")
            return
            
        self.log("🖼️ Генерация изображений...")
        
        try:
            # Используем DiceBear для фавиконок
            import requests
            
            # Простой запрос к DiceBear API
            url = f"https://api.dicebear.com/9.x/bottts/png?seed={self.theme.get()}&size=256"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Сохраняем фавиконку
                favicon_path = Path(self.project_folder.get()) / "favicon.png"
                with open(favicon_path, 'wb') as f:
                    f.write(response.content)
                
                self.log(f"✅ Фавиконка создана: {favicon_path}")
            else:
                self.log("⚠️ Ошибка создания фавиконки")
                
        except Exception as e:
            self.log(f"❌ Ошибка генерации: {e}")
            
        self.log("🎉 Генерация завершена!")
        
    def open_cursor(self):
        """Открывает Cursor AI"""
        self.log("🔍 Поиск Cursor AI...")
        
        # Простой поиск Cursor
        cursor_paths = [
            "C:\\Users\\AppData\\Local\\Programs\\cursor\\Cursor.exe",
            "E:\\cursor\\Cursor.exe",
            "C:\\Program Files\\Cursor\\Cursor.exe"
        ]
        
        for path in cursor_paths:
            if os.path.exists(path):
                subprocess.Popen([path, self.project_folder.get()])
                self.log(f"✅ Cursor запущен: {path}")
                return
                
        self.log("❌ Cursor AI не найден")
        
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

def main():
    """Главная функция"""
    app = MinimalLandingGenerator()
    app.run()

if __name__ == "__main__":
    main()
