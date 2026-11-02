from flask import Blueprint, jsonify
from Analysis.analytics_service import AnalyticsService

# Blueprint Definition
analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/api/analytics")
analytics_service = AnalyticsService()


# Analytics Routes
@analytics_bp.route("/summary", methods=["GET"])
def get_analytics_summary():
    data = analytics_service.get_summary()
    return jsonify({
        "success": True,
        "data": data
    }), 200


@analytics_bp.route("/scores", methods=["GET"])
def get_scores_statistics():
    data = analytics_service.get_scores_statistics()
    return jsonify({
        "success": True,
        "data": data
    }), 200


@analytics_bp.route("/top-keywords", methods=["GET"])
def get_top_keywords():
    keywords = analytics_service.get_top_keywords()
    return jsonify({
        "success": True,
        "count": len(keywords),
        "data": keywords
    }), 200


@analytics_bp.route("/domain-breakdown", methods=["GET"])
def get_domain_breakdown():
    breakdown = analytics_service.get_domain_breakdown()
    return jsonify({
        "success": True,
        "count": len(breakdown),
        "data": breakdown
    }), 200
