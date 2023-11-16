from flask import Blueprint

bp = Blueprint('certs', __name__, template_folder='templates')
bp.cli.short_help = 'Perform certificate operations.'

from app.main import cli, routes
