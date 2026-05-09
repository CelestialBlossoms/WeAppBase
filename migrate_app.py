from flask import Flask

from backend.app import configure_app
from backend.extensions import db, migrate
from backend.migration_models import load_project_models


def create_app() -> Flask:
    app = Flask(__name__)
    configure_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        load_project_models()

    return app


app = create_app()
