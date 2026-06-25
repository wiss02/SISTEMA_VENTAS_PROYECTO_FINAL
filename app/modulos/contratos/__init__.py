from flask import Blueprint

bp = Blueprint('contratos', __name__)

from app.modulos.contratos import routes
