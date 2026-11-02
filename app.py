import sys
import os

# Environment Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify
from flask_cors import CORS

from Dataset.routes import dataset_bp
from Blacklist.routes import blacklist_bp
from History.routes import history_bp
from Analysis.routes import analytics_bp


# Flask Application Factory
def create_app():
    app = Flask(__name__)

    # CORS Configuration
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprint Registration
    app.register_blueprint(dataset_bp)
    app.register_blueprint(blacklist_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(analytics_bp)

    # Root & Error Handlers
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "status": "online",
            "service": "PhishGuard API Server",
            "version": "1.0.0",
            "endpoints": [
                "GET /api/dataset",
                "GET /api/dataset/search",
                "POST /api/dataset",
                "PUT /api/dataset/<id>",
                "DELETE /api/dataset/<id>",
                "GET /api/dataset/export",
                "GET /api/blacklist",
                "POST /api/blacklist",
                "DELETE /api/blacklist/<domain>",
                "GET /api/history",
                "DELETE /api/history/<id>",
                "DELETE /api/history",
                "GET /api/analytics/summary",
                "GET /api/analytics/scores",
                "GET /api/analytics/top-keywords",
                "GET /api/analytics/domain-breakdown",
            ]
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


# Server Startup
app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("  PhishGuard API Server running at http://127.0.0.1:5000")
    print("  Dataset API:   http://127.0.0.1:5000/api/dataset")
    print("  Blacklist API: http://127.0.0.1:5000/api/blacklist")
    print("  History API:   http://127.0.0.1:5000/api/history")
    print("  Analytics API: http://127.0.0.1:5000/api/analytics/summary")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
