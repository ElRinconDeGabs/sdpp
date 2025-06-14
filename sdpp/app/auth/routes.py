from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- REGISTRO ----------
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
            password='root123',
            database='seguimientos_practicas'
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

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123',
            database='seguimientos_practicas'
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario, nombre, contraseña, rol FROM usuarios WHERE correo = %s", (correo,))
        user = cursor.fetchone()

        if user and check_password_hash(user['contraseña'], contraseña):
            session['user_id'] = user['id_usuario']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol']
            return jsonify({'success': True, 'nombre': user['nombre'], 'rol': user['rol']})
        else:
            return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------- DASHBOARD DEL ESTUDIANTE (HTML) ----------
@auth_bp.route('/estudiante/dashboard')
def estudiante_dashboard():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    return send_from_directory('static', 'e_dashboard.html')

# ---------- REGISTRO DE ACTIVIDADES ----------
@auth_bp.route('/api/actividades/registrar', methods=['POST'])
def registrar_actividad():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_estudiante = session['user_id']
    fecha = request.form.get('fecha')
    descripcion = request.form.get('descripcion')
    horas = request.form.get('horas')
    archivo = request.files.get('archivo_adjunto')
    archivo_nombre = None

    if archivo:
        archivo_nombre = secure_filename(archivo.filename)
        archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123',
            database='seguimientos_practicas'
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO actividades (id_estudiante, fecha, descripcion, horas, archivo_adjunto)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_estudiante, fecha, descripcion, horas, archivo_nombre))
        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'success': False, 'message': 'Error al registrar actividad'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------- CONSULTA DE ACTIVIDADES DEL ESTUDIANTE ----------
@auth_bp.route('/api/actividades/mias', methods=['GET'])
def mis_actividades():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_estudiante = session['user_id']

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123',
            database='seguimientos_practicas'
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                a.fecha, a.descripcion, a.horas, a.estado_validacion,
                COALESCE(c.texto, '') AS comentarios
            FROM actividades a
            LEFT JOIN comentarios c ON a.id_actividad = c.id_actividad
            WHERE a.id_estudiante = %s
            ORDER BY a.fecha DESC
        """, (id_estudiante,))

        actividades = cursor.fetchall()
        return jsonify({'success': True, 'actividades': actividades})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'success': False, 'message': 'Error al obtener actividades'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
