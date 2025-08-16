# -*- coding: utf-8 -*-

"""
GUI интерфейс для генератора лендингов
Обновлено для использования модульной структуры
"""

# Импортируем основной класс из новой структуры
from gui.main_window import LandingPageGeneratorGUI

# Также импортируем компоненты для обратной совместимости
from gui.components.country_combobox import CountrySearchCombobox
from gui.components.theme_combobox import ThemeHistoryCombobox

# Для обратной совместимости оставляем основные классы доступными
__all__ = [
    'LandingPageGeneratorGUI',
    'CountrySearchCombobox', 
    'ThemeHistoryCombobox'
]