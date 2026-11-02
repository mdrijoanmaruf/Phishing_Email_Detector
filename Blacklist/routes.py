from flask import Blueprint, jsonify, request
from Blacklist.blacklist_service import blacklist_service

blacklist_bp = Blueprint("blacklist_bp", __name__, url_prefix="/api/blacklist")


@blacklist_bp.route("", methods=["GET"])
def get_blacklist():
    try:
        domains = blacklist_service.get_all()
        return jsonify({
            "success": True,
            "count": len(domains),
            "data": domains
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to fetch blacklist", "details": str(e)}), 500


@blacklist_bp.route("", methods=["POST"])
def add_to_blacklist():
    try:
        data = request.get_json(silent=True) or {}
        domain = str(data.get("domain", "")).strip()

        if not domain:
            return jsonify({"success": False, "error": "Validation error: Missing 'domain' in request body"}), 400

        success, message = blacklist_service.add(domain)
        if not success:
            status_code = 409 if "Duplicate identifier" in message else 400
            return jsonify({"success": False, "error": message}), status_code

        return jsonify({
            "success": True,
            "message": message,
            "domain": blacklist_service.clean_domain(domain),
            "count": blacklist_service.count()
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": "Failed to add domain", "details": str(e)}), 500


@blacklist_bp.route("/<path:domain>", methods=["DELETE"])
def remove_from_blacklist(domain):
    try:
        domain_str = str(domain).strip()
        if not domain_str:
            return jsonify({"success": False, "error": "Validation error: Domain parameter is required"}), 400

        success, message = blacklist_service.remove(domain_str)
        if not success:
            return jsonify({"success": False, "error": message}), 404

        return jsonify({
            "success": True,
            "message": message,
            "count": blacklist_service.count()
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": "Failed to remove domain", "details": str(e)}), 500
