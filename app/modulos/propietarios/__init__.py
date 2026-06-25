from flask import Blueprint

bp = Blueprint('propietarios', __name__)

from app.modulos.propietarios import routes
