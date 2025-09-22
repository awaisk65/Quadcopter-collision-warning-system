from flask import Flask, redirect
from flask_cors import CORS
import logging


def create_app(config: dict | None = None):
    app = Flask(__name__)
    app.config.update(config or {})
    logging.basicConfig(level=logging.INFO)
    CORS(app)

    from resources.monitor_resource import register_routes
    register_routes(app)

    # 👇 Add redirect route here
    @app.route("/")
    def home():
        return redirect("/api/v1/monitor?conn1=udp:0.0.0.0:14550&conn2=udp:0.0.0.0:14551&hthresh=7&vthresh=5")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)
