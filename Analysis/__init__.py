"""
Analysis module for PhishGuard.
"""
from .analytics_service import AnalyticsService
from .routes import analytics_bp

__all__ = ["AnalyticsService", "analytics_bp"]

