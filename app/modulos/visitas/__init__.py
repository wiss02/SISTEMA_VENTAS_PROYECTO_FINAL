from flask import Blueprint

bp = Blueprint('visitas', __name__)

from app.modulos.visitas import routes
