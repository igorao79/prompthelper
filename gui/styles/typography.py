# -*- coding: utf-8 -*-

"""
Современная типографика для GUI
"""

class Typography:
    """Современные шрифты и размеры текста"""
    
    # Семейства шрифтов (приоритетные)
    FONT_FAMILY_PRIMARY = ("Segoe UI", "SF Pro Display", "Roboto", "Arial", "sans-serif")
    FONT_FAMILY_MONO = ("Cascadia Code", "SF Mono", "Consolas", "Monaco", "monospace")
    
    # Размеры шрифтов
    class Size:
        XS = 10      # Очень мелкий
        SM = 11      # Мелкий  
        BASE = 12    # Базовый
        MD = 13      # Средний
        LG = 14      # Большой
        XL = 16      # Очень большой
        XXL = 18     # Заголовки
        XXXL = 24    # Главные заголовки
    
    # Веса шрифтов
    class Weight:
        LIGHT = "normal"
        NORMAL = "normal" 
        MEDIUM = "normal"
        SEMIBOLD = "bold"
        BOLD = "bold"
        EXTRABOLD = "bold"
    
    # Готовые стили
    @classmethod
    def get_font(cls, size=None, weight=None, family=None):
        """Получить шрифт с заданными параметрами"""
        size = size or cls.Size.BASE
        weight = weight or cls.Weight.NORMAL
        family = family or cls.FONT_FAMILY_PRIMARY[0]
        
        return (family, size, weight)
    
    @classmethod 
    def heading_xl(cls):
        """Очень большой заголовок"""
        return cls.get_font(cls.Size.XXXL, cls.Weight.BOLD)
    
    @classmethod
    def heading_lg(cls):
        """Большой заголовок"""
        return cls.get_font(cls.Size.XXL, cls.Weight.SEMIBOLD)
    
    @classmethod
    def heading_md(cls):
        """Средний заголовок"""
        return cls.get_font(cls.Size.XL, cls.Weight.SEMIBOLD)
    
    @classmethod
    def body_lg(cls):
        """Большой текст"""
        return cls.get_font(cls.Size.LG, cls.Weight.NORMAL)
    
    @classmethod
    def body_md(cls):
        """Средний текст"""
        return cls.get_font(cls.Size.MD, cls.Weight.NORMAL)
    
    @classmethod
    def body_sm(cls):
        """Мелкий текст"""
        return cls.get_font(cls.Size.SM, cls.Weight.NORMAL)
    
    @classmethod
    def button_lg(cls):
        """Большая кнопка"""
        return cls.get_font(cls.Size.LG, cls.Weight.SEMIBOLD)
    
    @classmethod
    def button_md(cls):
        """Средняя кнопка"""
        return cls.get_font(cls.Size.MD, cls.Weight.MEDIUM)
    
    @classmethod
    def button_sm(cls):
        """Маленькая кнопка"""
        return cls.get_font(cls.Size.SM, cls.Weight.MEDIUM) 