# -*- coding: utf-8 -*-

"""
GUI модуль для генератора лендингов
Разбит на подкомпоненты для лучшей организации
"""

# Импортируем основные классы
from .main_window import LandingPageGeneratorGUI
from .components.country_combobox import CountrySearchCombobox
from .components.theme_combobox import ThemeHistoryCombobox

# Главный класс для обратной совместимости
__all__ = [
    'LandingPageGeneratorGUI',
    'CountrySearchCombobox', 
    'ThemeHistoryCombobox'
] 