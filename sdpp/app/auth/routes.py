from flask import Blueprint, request, jsonify, session
import mysql
from werkzeug.security import generate_password_hash

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

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
import mysql.connector

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-up', methods=['POST'])
def sign_up():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibió JSON válido'}), 400

        nombre = data.get('nombre')
        correo = data.get('correo')
        contraseña = data.get('contraseña')
        rol = data.get('rol')

        if not all([nombre, correo, contraseña, rol]):
            return jsonify({'success': False, 'message': 'Faltan datos'}), 400

        hashed_pw = generate_password_hash(contraseña)

        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='******',
            database='********'  # Reemplaza con tu base de datos
        )
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Correo ya registrado'}), 409

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contraseña, rol)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, hashed_pw, rol))
        conn.commit()

        session['user_id'] = cursor.lastrowid
        session['rol'] = rol
        session['nombre'] = nombre

        return jsonify({'success': True, 'message': 'Usuario registrado correctamente'})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
