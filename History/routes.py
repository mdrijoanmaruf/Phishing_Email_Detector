"""
Phishing_Email_Detector_Server/History/routes.py
Flask blueprint for scan history endpoints.
"""

from flask import Blueprint, jsonify, request
from .history_service import HistoryService

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")
history_service = HistoryService()


@history_bp.route("", methods=["GET"])
def get_history():
    """Retrieve past email scans with optional verdict filter and limit."""
    verdict = request.args.get("verdict")
    limit = request.args.get("limit", default=100, type=int)

    scans = history_service.get_all(verdict=verdict, limit=limit)
    return jsonify({
        "success": True,
        "count": len(scans),
        "total": history_service.count(),
        "data": scans
    }), 200


@history_bp.route("/<string:scan_id>", methods=["DELETE"])
def delete_history_item(scan_id: str):
    """Delete a single scan history record."""
    deleted = history_service.delete(scan_id)
    if not deleted:
        return jsonify({"success": False, "error": f"Scan with ID '{scan_id}' not found"}), 404

    return jsonify({
        "success": True,
        "message": f"Scan '{scan_id}' deleted successfully",
        "count": history_service.count()
    }), 200


@history_bp.route("", methods=["DELETE"])
def clear_all_history():
    """Clear all scan history."""
    history_service.clear_all()
    return jsonify({
        "success": True,
        "message": "All scan history cleared successfully",
        "count": 0
    }), 200

