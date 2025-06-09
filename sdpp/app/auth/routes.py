from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint('auth', __name__)

# Base de datos falsa
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


@auth_bp.route('/sign-up', methods=['GET'])
def sign_up():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')
    nombre = data.get('nombre')

    # Verificar si el correo ya existe
    if any(u['correo'] == correo for u in usuarios_fake):
        return jsonify({'success': False, 'message': 'El correo ya está registrado'})

    # Agregar nuevo usuario
    usuarios_fake.append({'correo': correo, 'contraseña': contraseña, 'nombre': nombre})
    session['user'] = nombre
    return jsonify({'success': True, 'message': 'Usuario registrado correctamente'})

