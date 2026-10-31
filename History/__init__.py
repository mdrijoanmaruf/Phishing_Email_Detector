"""
History module for PhishGuard.
"""
from .history_service import HistoryService
from .routes import history_bp

__all__ = ["HistoryService", "history_bp"]

