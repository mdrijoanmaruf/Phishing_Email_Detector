from flask import Blueprint, request, jsonify, Response
from Dataset.dataset_service import dataset_service

dataset_bp = Blueprint("dataset_bp", __name__)


# Read & Search Routes
@dataset_bp.route("/api/dataset", methods=["GET"])
def get_dataset():
    try:
        all_param = request.args.get("all", "false").lower()
        return_all = all_param in ("true", "1", "yes")

        try:
            page = int(request.args.get("page", 1))
        except (ValueError, TypeError):
            page = 1

        try:
            per_page = int(request.args.get("per_page", 20))
        except (ValueError, TypeError):
            per_page = 20

        result = dataset_service.get_paginated(
            page=page,
            per_page=per_page,
            return_all=return_all,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve dataset records",
            "details": str(e)
        }), 500


@dataset_bp.route("/api/dataset/search", methods=["GET"])
def search_dataset():
    try:
        query = request.args.get("q", "").strip() or None
        domain = request.args.get("domain", "").strip() or None

        label_raw = request.args.get("label", "").strip()
        label = None
        if label_raw in ("0", "1"):
            label = int(label_raw)

        try:
            page = int(request.args.get("page", 1))
        except (ValueError, TypeError):
            page = 1

        try:
            per_page = int(request.args.get("per_page", 20))
        except (ValueError, TypeError):
            per_page = 20

        result = dataset_service.search_records(
            query=query,
            label=label,
            domain=domain,
            page=page,
            per_page=per_page,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to search dataset records",
            "details": str(e)
        }), 500


# Mutation Routes (CRUD)
@dataset_bp.route("/api/dataset", methods=["POST"])
def add_dataset_record():
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid JSON body provided"
            }), 400

        success, message, new_record = dataset_service.add_record(data)

        if not success:
            status_code = 409 if "already exists" in message else 400
            return jsonify({
                "success": False,
                "error": message
            }), status_code

        return jsonify({
            "success": True,
            "message": message,
            "data": new_record.to_dict() if new_record else None
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to create email record",
            "details": str(e)
        }), 500


@dataset_bp.route("/api/dataset/<record_id>", methods=["PUT"])
def update_dataset_record(record_id):
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid JSON body provided"
            }), 400

        success, message, updated_record = dataset_service.update_record(record_id, data)

        if not success:
            return jsonify({
                "success": False,
                "error": message
            }), 404

        return jsonify({
            "success": True,
            "message": message,
            "data": updated_record.to_dict() if updated_record else None
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to update email record",
            "details": str(e)
        }), 500


@dataset_bp.route("/api/dataset/<record_id>", methods=["DELETE"])
def delete_dataset_record(record_id):
    try:
        success, message = dataset_service.delete_record(record_id)

        if not success:
            return jsonify({
                "success": False,
                "error": message
            }), 404

        return jsonify({
            "success": True,
            "message": message,
            "id": str(record_id)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to delete email record",
            "details": str(e)
        }), 500


# Export Route
@dataset_bp.route("/api/dataset/export", methods=["GET"])
def export_dataset_csv():
    try:
        query = request.args.get("q", "").strip() or None
        domain = request.args.get("domain", "").strip() or None

        label_raw = request.args.get("label", "").strip()
        label = None
        if label_raw in ("0", "1"):
            label = int(label_raw)

        csv_content = dataset_service.export_csv(
            query=query,
            label=label,
            domain=domain,
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=emails_export.csv",
                "Content-Type": "text/csv; charset=utf-8",
            }
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to export dataset CSV",
            "details": str(e)
        }), 500
