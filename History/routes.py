from flask import Blueprint, jsonify, request
from History.history_service import history_service

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
def get_history():
    try:
        action = request.args.get("action")
        entity_type = request.args.get("entity_type")

        # Exception handling: Non-numeric and out-of-range limit
        try:
            limit = int(request.args.get("limit", 200))
        except (ValueError, TypeError):
            limit = 200

        logs = history_service.get_all(action=action, entity_type=entity_type, limit=limit)
        return jsonify({
            "success": True,
            "count": len(logs),
            "total": history_service.count(),
            "data": logs
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to retrieve history", "details": str(e)}), 500


@history_bp.route("/log", methods=["POST"])
def create_history_log():
    try:
        data = request.get_json(silent=True) or {}
        action = str(data.get("action", "VIEW")).upper()
        entity_type = str(data.get("entity_type", "EMAIL")).upper()
        entity_id = str(data.get("entity_id", "")).strip()
        summary = str(data.get("summary") or f"{action} action on {entity_type} #{entity_id}")
        details = data.get("details", {})
        actor = str(data.get("actor", "Administrator")).strip()

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

    except Exception as e:
        return jsonify({"success": False, "error": "Failed to log activity", "details": str(e)}), 500


@history_bp.route("/<string:log_id>", methods=["DELETE"])
def delete_history_item(log_id):
    try:
        success, message = history_service.delete(log_id)
        if not success:
            return jsonify({"success": False, "error": message}), 404

        return jsonify({
            "success": True,
            "message": message,
            "count": history_service.count()
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": "Failed to delete history record", "details": str(e)}), 500


@history_bp.route("", methods=["DELETE"])
def clear_all_history():
    try:
        success, message = history_service.clear()
        return jsonify({
            "success": True,
            "message": message,
            "count": 0
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to clear history", "details": str(e)}), 500
