"""
Phishing_Email_Detector_Server/Analysis/routes.py
Flask blueprint for statistical analytics endpoints.
"""

from flask import Blueprint, jsonify
from .analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/api/analytics")
analytics_service = AnalyticsService()


@analytics_bp.route("/summary", methods=["GET"])
def get_analytics_summary():
    """Return high-level summary of records, scans, and breakdown."""
    data = analytics_service.get_summary()
    return jsonify({
        "success": True,
        "data": data
    }), 200


@analytics_bp.route("/scores", methods=["GET"])
def get_scores_statistics():
    """Return statistical distribution of risk scores (NumPy computed)."""
    data = analytics_service.get_scores_statistics()
    return jsonify({
        "success": True,
        "data": data
    }), 200


@analytics_bp.route("/top-keywords", methods=["GET"])
def get_top_keywords():
    """Return most frequently identified phishing keywords."""
    keywords = analytics_service.get_top_keywords()
    return jsonify({
        "success": True,
        "count": len(keywords),
        "data": keywords
    }), 200


@analytics_bp.route("/domain-breakdown", methods=["GET"])
def get_domain_breakdown():
    """Return top phishing origin domains."""
    breakdown = analytics_service.get_domain_breakdown()
    return jsonify({
        "success": True,
        "count": len(breakdown),
        "data": breakdown
    }), 200

