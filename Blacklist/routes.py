"""
Phishing_Email_Detector_Server/Blacklist/routes.py
Flask blueprint for domain blacklist endpoints.
"""

from flask import Blueprint, jsonify, request
from .blacklist_service import BlacklistService

blacklist_bp = Blueprint("blacklist_bp", __name__, url_prefix="/api/blacklist")
blacklist_service = BlacklistService()


@blacklist_bp.route("", methods=["GET"])
def get_blacklist():
    """List all blacklisted domains."""
    domains = blacklist_service.get_all()
    return jsonify({
        "success": True,
        "count": len(domains),
        "data": domains
    }), 200


@blacklist_bp.route("", methods=["POST"])
def add_to_blacklist():
    """Add a domain or sender address to the blacklist."""
    data = request.get_json(silent=True) or {}
    domain = data.get("domain", "").strip()

    if not domain:
        return jsonify({"success": False, "error": "Missing 'domain' in request body"}), 400

    success, message = blacklist_service.add(domain)
    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "domain": blacklist_service.clean_domain(domain),
        "count": blacklist_service.count()
    }), 201


@blacklist_bp.route("/<path:domain>", methods=["DELETE"])
def remove_from_blacklist(domain: str):
    """Remove a domain from the blacklist."""
    if not domain:
        return jsonify({"success": False, "error": "Domain parameter required"}), 400

    success, message = blacklist_service.remove(domain)
    if not success:
        return jsonify({"success": False, "error": message}), 404

    return jsonify({
        "success": True,
        "message": message,
        "count": blacklist_service.count()
    }), 200

