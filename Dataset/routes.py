"""
Dataset/routes.py
Flask Blueprint defining the Dataset API endpoints.
"""

from flask import Blueprint, request, jsonify
from Dataset.dataset_service import dataset_service

dataset_bp = Blueprint("dataset_bp", __name__)


@dataset_bp.route("/api/dataset", methods=["GET"])
def get_dataset():
    """
    GET /api/dataset
    Return all email records (or paginated).
    Query Parameters:
      - page (int, optional): Page number, default 1
      - per_page (int, optional): Items per page, default 20 (max 200)
      - all (str, optional): If 'true', returns all records without pagination
    """
    try:
        # Check if caller requested all records
        all_param = request.args.get("all", "false").lower()
        return_all = all_param in ("true", "1", "yes")

        # Parse pagination parameters
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
