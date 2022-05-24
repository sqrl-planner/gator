"""Flask extensions."""
from flask import Flask
from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_app(app: Flask) -> None:
    """Initialise extensions with a flask app context."""
    db.init_app(app)