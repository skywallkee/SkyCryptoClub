from flask import Flask

from .commands import create_tables
from .extensions import login_manager, db
from .routes.user_routes import user_routes

def create_app(config_file="settings.py"):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)

    login_manager.init_app(app)

    # login_manager.login_view = ''

    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(user_id)

    app.register_blueprint(user_routes)

    app.cli.add_command(create_tables)

    return app