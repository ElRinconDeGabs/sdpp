from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint('auth', __name__)

usuarios_fake = [
    {'correo': 'test@test.com', 'contraseña': '123', 'nombre': 'Test'}
]

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')
    user = next((u for u in usuarios_fake if u['correo'] == correo and u['contraseña'] == contraseña), None)
    if user:
        session['user'] = user['nombre']
        return jsonify({'success': True, 'nombre': user['nombre']})
    return jsonify({'success': False, 'message': 'Credenciales inválidas'})
