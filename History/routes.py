"""
Phishing_Email_Detector_Server/History/routes.py
Flask blueprint for activity history and audit logs.
"""

from flask import Blueprint, jsonify, request
from .history_service import history_service

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
def get_history():
    """Retrieve activity history with optional action and entity_type filters."""
    action = request.args.get("action")
    entity_type = request.args.get("entity_type")
    limit = request.args.get("limit", default=200, type=int)

    logs = history_service.get_all(action=action, entity_type=entity_type, limit=limit)
    return jsonify({
        "success": True,
        "count": len(logs),
        "total": history_service.count(),
        "data": logs
    }), 200


@history_bp.route("/log", methods=["POST"])
def create_history_log():
    """
    Log an activity event (e.g., VIEW, ADD, EDIT, DELETE).
    Payload: { action, entity_type, entity_id, summary, details, actor }
    """
    data = request.get_json(silent=True) or {}
    action = data.get("action", "VIEW").upper()
    entity_type = data.get("entity_type", "EMAIL").upper()
    entity_id = str(data.get("entity_id", ""))
    summary = data.get("summary") or f"{action} action on {entity_type} {entity_id}"
    details = data.get("details", {})
    actor = data.get("actor", "Administrator")

    entry = history_service.log_action(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        details=details,
        actor=actor
    )

    return jsonify({
        "success": True,
        "message": "Activity logged successfully",
        "data": entry
    }), 201


@history_bp.route("/<string:log_id>", methods=["DELETE"])
def delete_history_item(log_id: str):
    """Delete a single history record."""
    deleted = history_service.delete(log_id)
    if not deleted:
        return jsonify({"success": False, "error": f"History record with ID '{log_id}' not found"}), 404

    return jsonify({
        "success": True,
        "message": f"History record '{log_id}' deleted successfully",
        "count": history_service.count()
    }), 200


@history_bp.route("", methods=["DELETE"])
def clear_all_history():
    """Clear all history records."""
    history_service.clear_all()
    return jsonify({
        "success": True,
        "message": "All activity history cleared successfully",
        "count": 0
    }), 200
