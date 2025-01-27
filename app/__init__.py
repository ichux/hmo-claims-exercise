import os

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config

CONFIG = os.getenv("CONFIG", "config")

application = Flask(
    import_name="app",
    template_folder="templates",
    static_folder="static",
    instance_relative_config=True,
)
application.config.from_object(app_config[CONFIG])
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database = SQLAlchemy(application)

Migrate(
    app=application,
    db=database,
    directory="intron_health_migrations",
    render_as_batch=True,
)

from .home import home as home_blueprint

application.register_blueprint(home_blueprint, url_prefix="/home")


@application.errorhandler(404)
# Custom error handler for 404 Not Found
def not_found_error(error):
    return render_template("errors/404.html"), 404


# Custom error handler for 500 Internal Server Error
@application.errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500
