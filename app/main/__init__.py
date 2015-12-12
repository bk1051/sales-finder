from flask import Blueprint

main = Blueprint('main', __name__)

# Import views and errors here to avoid circular dependencies (need main object to exist)
from . import views, errors
