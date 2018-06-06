from flask import Blueprint

bp = Blueprint('problem', __name__)

from app.problem import routes
