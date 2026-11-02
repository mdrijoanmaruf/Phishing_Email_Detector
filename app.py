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


# Flask Application 
def create_app():
    app = Flask(__name__)

    # Allowed Origins (Production & Localhost)
    allowed_origins = [
        "https://phish.rijoan.com",
        "http://phish.rijoan.com",
        "https://phish.rijoan.com/",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # CORS Configuration
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    app.register_blueprint(dataset_bp)
    app.register_blueprint(blacklist_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(analytics_bp)

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
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print(f"  PhishGuard API Server running at http://127.0.0.1:{port}")
    print(f"  Dataset API:   http://127.0.0.1:{port}/api/dataset")
    print(f"  Blacklist API: http://127.0.0.1:{port}/api/blacklist")
    print(f"  History API:   http://127.0.0.1:{port}/api/history")
    print(f"  Analytics API: http://127.0.0.1:{port}/api/analytics/summary")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
