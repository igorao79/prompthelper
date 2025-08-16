"""
Основные компоненты приложения
""" 

from .cursor_manager import CursorManager

try:
    from .update_checker import UpdateChecker  # optional
except Exception:
    UpdateChecker = None  # type: ignore