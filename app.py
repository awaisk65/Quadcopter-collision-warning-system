from flask import Flask
from flask_cors import CORS
import logging


def create_app(config: dict | None = None):
    app = Flask(__name__)
    app.config.update(config or {})
    logging.basicConfig(level=logging.INFO)
    CORS(app)

    from resources.monitor_resource import register_routes
    register_routes(app)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)
