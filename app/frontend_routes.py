from flask import Blueprint, render_template, send_from_directory
from flask_wtf.csrf import generate_csrf
import os

bp = Blueprint('frontend', __name__, static_folder='static')

@bp.route('/')
def index():
    return render_template('index.html', csrf_token=generate_csrf())

@bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(bp.static_folder), filename)