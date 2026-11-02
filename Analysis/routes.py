from flask import Blueprint, jsonify, request
from Analysis.analytics_service import analytics_service

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/summary", methods=["GET"])
def get_analytics_summary():
    try:
        data = analytics_service.get_summary()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to compute summary analytics", "details": str(e)}), 500


@analytics_bp.route("/scores", methods=["GET"])
def get_scores_statistics():
    try:
        sample_size = request.args.get("sample_size", default=1000, type=int)
        data = analytics_service.get_scores_statistics(sample_size=sample_size)
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to compute score statistics", "details": str(e)}), 500


@analytics_bp.route("/top-keywords", methods=["GET"])
def get_top_keywords():
    try:
        top_n = request.args.get("limit", default=8, type=int)
        keywords = analytics_service.get_top_keywords(top_n=top_n)
        return jsonify({
            "success": True,
            "count": len(keywords),
            "data": keywords
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to extract top keywords", "details": str(e)}), 500


@analytics_bp.route("/domain-breakdown", methods=["GET"])
def get_domain_breakdown():
    try:
        limit = request.args.get("limit", default=10, type=int)
        breakdown = analytics_service.get_domain_breakdown(limit=limit)
        return jsonify({
            "success": True,
            "count": len(breakdown),
            "data": breakdown
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to compute domain breakdown", "details": str(e)}), 500
