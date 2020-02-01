from flask import Flask

from .commands import create_tables
from .extensions import login_manager, db
from .routes.user_routes import user_routes
from .routes.role_routes import role_routes
from .routes.platform_currency_routes import platform_currency_routes
from .routes.profile_membership_routes import profile_membership_routes
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
    app.register_blueprint(role_routes)
    app.register_blueprint(platform_currency_routes)
    app.register_blueprint(profile_membership_routes)
    app.cli.add_command(create_tables)

    return app