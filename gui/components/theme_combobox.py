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
        """Создает современный интерфейс"""
        # Импортируем тему локально, чтобы избежать циклических импортов
        from ..styles.modern_theme import ModernTheme
        self.theme = ModernTheme()
        
        # Современное поле ввода
        self.entry = self.theme.create_modern_entry(
            self, 
            textvariable=self.textvariable,
            font=self.theme.typography.body_lg(),
            width=70
        )
        self.entry.pack(fill="x", ipady=8)
        
        # Современная кнопка истории
        self.history_btn = self.theme.create_modern_button(
            self,
            text="📋",
            command=self.show_history,
            style="secondary",
            font=self.theme.typography.button_sm(),
            padx=12,
            pady=6
        )
        self.history_btn.pack(side="right", padx=(8, 0))
    
    def set_history(self, history):
        """Устанавливает историю тематик"""
        self.history = history
    
    def show_history(self):
        """Показывает историю тематик"""
        if not self.history:
            messagebox.showinfo("История", "История тематик пуста")
            return
        
        # Создаем современное окно выбора
        history_window = tk.Toplevel(self)
        history_window.title("📋 История тематик")
        history_window.geometry("450x350")
        history_window.transient(self)
        history_window.grab_set()
        history_window.configure(bg=self.theme.colors.BACKGROUND)
        
        # Заголовок
        title_label = self.theme.create_modern_label(
            history_window,
            text="📋 Выберите тематику из истории",
            style="heading_md",
            bg=self.theme.colors.BACKGROUND
        )
        title_label.pack(pady=(15, 10))
        
        # Современный список истории
        listbox_frame = self.theme.create_modern_frame(history_window)
        listbox_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        listbox = tk.Listbox(
            listbox_frame, 
            font=self.theme.typography.body_md(),
            bg=self.theme.colors.CARD,
            fg=self.theme.colors.TEXT_PRIMARY,
            selectbackground=self.theme.colors.PRIMARY,
            selectforeground=self.theme.colors.TEXT_PRIMARY,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.theme.colors.PRIMARY
        )
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for theme in self.history:
            listbox.insert(tk.END, theme)
        
        # Современные кнопки
        btn_frame = self.theme.create_modern_frame(
            history_window,
            bg=self.theme.colors.BACKGROUND,
            highlightthickness=0
        )
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        def select_theme():
            selection = listbox.curselection()
            if selection:
                selected_theme = listbox.get(selection[0])
                self.textvariable.set(selected_theme)
                history_window.destroy()
        
        select_btn = self.theme.create_modern_button(
            btn_frame,
            text="✅ Выбрать",
            command=select_theme,
            style="success"
        )
        select_btn.pack(side="right", padx=(8, 0))
        
        close_btn = self.theme.create_modern_button(
            btn_frame,
            text="❌ Закрыть",
            command=history_window.destroy,
            style="danger"
        )
        close_btn.pack(side="right")
        
        # Двойной клик для выбора
        listbox.bind("<Double-Button-1>", lambda e: select_theme()) 