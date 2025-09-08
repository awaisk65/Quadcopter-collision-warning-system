"""Flask resource for monitoring drones (GET-based)."""

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from services.monitor_service import MonitorService

bp = Blueprint("monitor", __name__, url_prefix="/api/v1")


class MonitorAPI(MethodView):
    """GET endpoint to check drone proximity once."""

    def get(self):
        # Extract query parameters
        conn1 = request.args.get("conn1")
        conn2 = request.args.get("conn2")
        hthresh = request.args.get("hthresh", type=float, default=15.0)
        vthresh = request.args.get("vthresh", type=float, default=5.0)

        # Validate required params
        if not conn1 or not conn2:
            return jsonify({
                "error": "Missing required query params: conn1 and conn2"
            }), 400

        # Run one-time proximity check
        service = MonitorService(conn1, conn2, hthresh, vthresh)
        result = service.run_check()
        return jsonify(result), 200


def register_routes(app):
    """Register routes with Flask app."""
    view = MonitorAPI.as_view("monitor_api")
    bp.add_url_rule("/monitor", view_func=view, methods=["GET"])
    app.register_blueprint(bp)
