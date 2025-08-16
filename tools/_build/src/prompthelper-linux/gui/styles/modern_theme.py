# -*- coding: utf-8 -*-

"""
Современная тема для tkinter GUI
"""

import tkinter as tk
from tkinter import ttk
from .color_palette import ColorPalette
from .typography import Typography

class ModernTheme:
    """Современная тема в стиле 2024"""
    
    def __init__(self):
        self.colors = ColorPalette
        self.typography = Typography
        self._style = None
    
    def apply_to_root(self, root):
        """Применяет современную тему к корневому окну"""
        # Настройка основного окна
        root.configure(bg=self.colors.BACKGROUND)
        
        # Настройка ttk стилей
        self._setup_ttk_styles(root)
        
        # Применение современных настроек
        self._configure_modern_appearance(root)
    
    def _setup_ttk_styles(self, root):
        """Настраивает стили ttk виджетов"""
        self._style = ttk.Style(root)
        
        # Современная тема на основе clam
        self._style.theme_use('clam')
        
        # Настройка LabelFrame
        self._style.configure(
            "Modern.TLabelframe",
            background=self.colors.SURFACE,
            borderwidth=1,
            relief="flat",
            bordercolor=self.colors.BORDER
        )
        
        self._style.configure(
            "Modern.TLabelframe.Label",
            background=self.colors.SURFACE,
            foreground=self.colors.TEXT_PRIMARY,
            font=self.typography.heading_md()
        )
        
        # Настройка Entry
        self._style.configure(
            "Modern.TEntry",
            fieldbackground=self.colors.CARD,
            background=self.colors.CARD,
            foreground=self.colors.TEXT_PRIMARY,
            bordercolor=self.colors.BORDER,
            borderwidth=1,
            relief="flat",
            insertcolor=self.colors.PRIMARY
        )
        
        # Настройка Button
        self._style.configure(
            "Modern.TButton",
            background=self.colors.BUTTON_PRIMARY,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=0,
            relief="flat",
            font=self.typography.button_md()
        )
        
        self._style.map(
            "Modern.TButton",
            background=[
                ('active', self.colors.BUTTON_PRIMARY_HOVER),
                ('pressed', self.colors.ACTIVE)
            ]
        )
        
        # Настройка Scrollbar
        self._style.configure(
            "Modern.Vertical.TScrollbar",
            background=self.colors.SURFACE,
            bordercolor=self.colors.BORDER,
            arrowcolor=self.colors.TEXT_SECONDARY,
            darkcolor=self.colors.CARD,
            lightcolor=self.colors.CARD
        )
    
    def _configure_modern_appearance(self, root):
        """Настраивает современный внешний вид"""
        # Попытка включить DPI awareness (Windows)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    def create_modern_button(self, parent, text, command=None, style="primary", **kwargs):
        """Создает современную кнопку"""
        button_styles = {
            "primary": {
                "bg": self.colors.BUTTON_PRIMARY,
                "fg": self.colors.TEXT_PRIMARY,
                "activebackground": self.colors.BUTTON_PRIMARY_HOVER
            },
            "secondary": {
                "bg": self.colors.BUTTON_SECONDARY,
                "fg": self.colors.TEXT_PRIMARY,
                "activebackground": self.colors.BUTTON_SECONDARY_HOVER
            },
            "success": {
                "bg": self.colors.BUTTON_SUCCESS,
                "fg": self.colors.TEXT_PRIMARY,
                "activebackground": self.colors.BUTTON_SUCCESS_HOVER
            },
            "danger": {
                "bg": self.colors.BUTTON_DANGER,
                "fg": self.colors.TEXT_PRIMARY,
                "activebackground": self.colors.BUTTON_DANGER_HOVER
            }
        }
        
        style_config = button_styles.get(style, button_styles["primary"])
        
        default_config = {
            "font": self.typography.button_md(),
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": 20,
            "pady": 10
        }
        
        # Объединяем стили
        final_config = {**default_config, **style_config, **kwargs}
        
        button = tk.Button(parent, text=text, command=command, **final_config)
        
        # Добавляем hover эффект
        self._add_hover_effect(button, style_config)
        
        return button
    
    def create_modern_label(self, parent, text, style="body", **kwargs):
        """Создает современную метку"""
        label_styles = {
            "heading_xl": {
                "font": self.typography.heading_xl(),
                "fg": self.colors.TEXT_PRIMARY
            },
            "heading_lg": {
                "font": self.typography.heading_lg(),
                "fg": self.colors.TEXT_PRIMARY
            },
            "heading_md": {
                "font": self.typography.heading_md(),
                "fg": self.colors.TEXT_PRIMARY
            },
            "body": {
                "font": self.typography.body_md(),
                "fg": self.colors.TEXT_SECONDARY
            },
            "caption": {
                "font": self.typography.body_sm(),
                "fg": self.colors.TEXT_MUTED
            }
        }
        
        style_config = label_styles.get(style, label_styles["body"])
        
        default_config = {
            "bg": self.colors.BACKGROUND,
            "anchor": "w"
        }
        
        final_config = {**default_config, **style_config, **kwargs}
        
        return tk.Label(parent, text=text, **final_config)
    
    def create_modern_frame(self, parent, **kwargs):
        """Создает современный фрейм"""
        default_config = {
            "bg": self.colors.SURFACE,
            "relief": "flat",
            "borderwidth": 0,
            "highlightbackground": self.colors.SURFACE,
            "highlightthickness": 0,
            "highlightcolor": self.colors.SURFACE
        }
        
        final_config = {**default_config, **kwargs}
        
        return tk.Frame(parent, **final_config)
    
    def create_modern_labelframe(self, parent, text, **kwargs):
        """Создает современный LabelFrame"""
        default_config = {
            "bg": self.colors.SURFACE,
            "fg": self.colors.TEXT_PRIMARY,
            "font": self.typography.heading_md(),
            "relief": "flat",
            "borderwidth": 0,
            "highlightbackground": self.colors.SURFACE,
            "highlightthickness": 0
        }
        
        final_config = {**default_config, **kwargs}
        
        return tk.LabelFrame(parent, text=text, **final_config)
    
    def create_modern_entry(self, parent, **kwargs):
        """Создает современное поле ввода"""
        default_config = {
            "bg": self.colors.CARD,
            "fg": self.colors.TEXT_PRIMARY,
            "font": self.typography.body_md(),
            "relief": "flat",
            "borderwidth": 0,
            "highlightbackground": self.colors.CARD,
            "highlightthickness": 0,
            "highlightcolor": self.colors.CARD,
            "insertbackground": self.colors.TEXT_PRIMARY
        }
        
        final_config = {**default_config, **kwargs}
        
        return tk.Entry(parent, **final_config)
    
    def _add_hover_effect(self, widget, style_config):
        """Добавляет hover эффект к виджету"""
        original_bg = style_config["bg"]
        hover_bg = style_config["activebackground"]
        
        def on_enter(event):
            widget.configure(bg=hover_bg)
        
        def on_leave(event):
            widget.configure(bg=original_bg)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def get_icon(self, name):
        """Получает современную иконку (Unicode символы)"""
        icons = {
            "folder": "📁",
            "save": "💾", 
            "settings": "⚙️",
            "search": "🔍",
            "star": "⭐",
            "star_empty": "☆",
            "home": "🏠",
            "rocket": "🚀",
            "image": "🖼️",
            "edit": "✏️",
            "reset": "🔄",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "target": "🎯",
            "globe": "🌍",
            "heart": "❤️",
            "fire": "🔥",
            "magic": "✨"
        }
        return icons.get(name, "")
    
    def add_shadow_effect(self, widget):
        """Добавляет эффект тени (имитация через границы)"""
        widget.configure(
            relief="flat",
            borderwidth=2,
            highlightbackground="#000000",
            highlightthickness=1
        ) 