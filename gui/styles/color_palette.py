# -*- coding: utf-8 -*-

"""
Современная цветовая палитра для GUI
"""

class ColorPalette:
    """Современная цветовая схема в стиле 2024"""
    
    # Основные цвета (Dark Theme)
    PRIMARY = "#2563eb"      # Синий
    SECONDARY = "#10b981"    # Зеленый
    ACCENT = "#f59e0b"       # Оранжевый
    DANGER = "#ef4444"       # Красный
    WARNING = "#f59e0b"      # Желтый
    SUCCESS = "#10b981"      # Зеленый успеха
    
    # Фоновые цвета
    BACKGROUND = "#1e40af"   # Синий фон
    SURFACE = "#2563eb"      # Поверхности
    CARD = "#1e3a8a"         # Карточки (темнее для читаемости)
    
    # Текстовые цвета
    TEXT_PRIMARY = "#f8fafc"    # Основной текст
    TEXT_SECONDARY = "#cbd5e1"  # Вторичный текст
    TEXT_MUTED = "#94a3b8"      # Приглушенный текст
    
    # Границы
    BORDER = "#60a5fa"
    BORDER_LIGHT = "#93c5fd"
    
    # Кнопки
    BUTTON_PRIMARY = "#3b82f6"
    BUTTON_PRIMARY_HOVER = "#2563eb"
    BUTTON_SECONDARY = "#6366f1"
    BUTTON_SECONDARY_HOVER = "#5b21b6"
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