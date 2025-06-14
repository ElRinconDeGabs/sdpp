from flask import Blueprint, send_from_directory
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # La carpeta 'static' está dentro de app/, así que la ruta base es app/static
    return send_from_directory('static', 'index.html')

@main_bp.route('/sign-up.html')
def sign_up_page():
    return send_from_directory('static', 'sign-up.html')

@main_bp.route('/estudiante/dashboard')
def estudiante_dashboard():
    return send_from_directory('static', 'e_dashboard.html')
