# -*- coding: utf-8 -*-

"""
GUI модуль для генератора лендингов
Разбит на подкомпоненты для лучшей организации
"""

# Оставляем только Qt-версию
from .qt_main import QtMainWindow, run_qt

__all__ = [
    'QtMainWindow',
    'run_qt'
]