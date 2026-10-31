"""
Blacklist module for PhishGuard.
"""
from .blacklist_service import BlacklistService
from .routes import blacklist_bp

__all__ = ["BlacklistService", "blacklist_bp"]

