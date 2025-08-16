# -*- coding: utf-8 -*-

"""
Современная цветовая палитра для GUI
"""

class ColorPalette:
    """Современная цветовая схема в стиле 2024"""
    
    # Основные цвета (более мягкие)
    PRIMARY = "#2563eb"
    SECONDARY = "#64748b"
    ACCENT = "#f59e0b"
    DANGER = "#ef4444"
    WARNING = "#f59e0b"
    SUCCESS = "#10b981"
    
    # Фоновые цвета (менее "ядрёные")
    BACKGROUND = "#0b1220"
    SURFACE = "#121a2a"
    CARD = "#0b1526"
    
    # Текстовые цвета
    TEXT_PRIMARY = "#f8fafc"    # Основной текст
    TEXT_SECONDARY = "#cbd5e1"  # Вторичный текст
    TEXT_MUTED = "#94a3b8"      # Приглушенный текст
    
    # Границы
    BORDER = "#233047"
    BORDER_LIGHT = "#2e405d"
    
    # Кнопки
    BUTTON_PRIMARY = "#2563eb"
    BUTTON_PRIMARY_HOVER = "#1d4ed8"
    BUTTON_SECONDARY = "#475569"
    BUTTON_SECONDARY_HOVER = "#334155"
    BUTTON_SUCCESS = "#059669"
    BUTTON_SUCCESS_HOVER = "#047857"
    BUTTON_DANGER = "#dc2626"
    BUTTON_DANGER_HOVER = "#b91c1c"
    
    # Состояния
    HOVER = "#60a5fa"
    ACTIVE = "#93c5fd"
    DISABLED = "#1e3a8a"
    
    # Светлая тема (опционально)
    class Light:
        BACKGROUND = "#ffffff"
        SURFACE = "#f8fafc"
        CARD = "#ffffff"
        TEXT_PRIMARY = "#1e293b"
        TEXT_SECONDARY = "#475569"
        TEXT_MUTED = "#64748b"
        BORDER = "#e2e8f0" 