from flask import Blueprint

bp = Blueprint(
    'main',
    __name__,
    static_folder='static'
)

from app.main import routes
