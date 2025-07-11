# -*- coding: utf-8 -*-

"""
Компонент комбобокса для выбора тематик с историей
"""

import tkinter as tk
from tkinter import ttk, messagebox


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
            font=("Arial", 13),
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