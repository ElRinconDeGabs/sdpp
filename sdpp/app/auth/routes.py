from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os
from datetime import datetime, timedelta

# Blueprint con prefijo para API de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Ruta absoluta para uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'seguimiento_practicas'
}

# ---------- REGISTRO ----------
@auth_bp.route('/sign-up', methods=['POST'])
def sign_up():
    conn = None
    cursor = None
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No se recibió JSON válido'}), 400

        nombre = data.get('nombre')
        correo = data.get('correo')
        contraseña = data.get('contraseña')
        rol = data.get('rol')

        if not all([nombre, correo, contraseña, rol]):
            return jsonify({'success': False, 'message': 'Faltan datos'}), 400

        hashed_pw = generate_password_hash(contraseña)

        conn = mysql.connector.connect(**DB_CONFIG)
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
        print("❌ ERROR en sign_up:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    conn = None
    cursor = None
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No se recibió JSON válido'}), 400

        correo = data.get('correo')
        contraseña = data.get('contraseña')

        if not correo or not contraseña:
            return jsonify({'success': False, 'message': 'Faltan datos'}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
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
        print("❌ ERROR en login:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------- REGISTRO DE ACTIVIDADES ----------
@auth_bp.route('/actividades/registrar', methods=['POST'])
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

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Llamada al SP para insertar actividad:
        cursor.callproc('sp_registrar_actividad', [id_estudiante, fecha, descripcion, horas, archivo_nombre])

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("❌ ERROR en registrar_actividad:", str(e))
        return jsonify({'success': False, 'message': 'Error al registrar actividad'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ---------- CONSULTA DE ACTIVIDADES DEL ESTUDIANTE ----------
@auth_bp.route('/actividades/mias', methods=['GET'])
def mis_actividades():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_estudiante = session['user_id']
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Llamar procedimiento almacenado para obtener actividades
        cursor.callproc('sp_listar_actividades_estudiante', [id_estudiante])

        actividades = []
        # Obtener resultados del SP (MySQL Connector devuelve resultados en stored_results())
        for result in cursor.stored_results():
            actividades = result.fetchall()

        return jsonify({'success': True, 'actividades': actividades})

    except Exception as e:
        print("❌ ERROR en mis_actividades:", str(e))
        return jsonify({'success': False, 'message': 'Error al obtener actividades'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ---------- RESUMEN DE ACTIVIDADES ----------
@auth_bp.route('/actividades/resumen')
def resumen_actividades():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False}), 401

    id_estudiante = session['user_id']
    hoy = datetime.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Llamada SP para total horas
        cursor.callproc('sp_total_horas', [id_estudiante])
        total_horas = 0
        for result in cursor.stored_results():
            fila = result.fetchone()
            if fila and fila[0]:
                total_horas = fila[0]

        # Llamada SP para horas semana
        cursor.callproc('sp_horas_semana', [id_estudiante, inicio_semana])
        horas_semana = 0
        for result in cursor.stored_results():
            fila = result.fetchone()
            if fila and fila[0]:
                horas_semana = fila[0]

        porcentaje = min(100, int((total_horas / 80) * 100))

        return jsonify({
            'success': True,
            'total_horas': total_horas,
            'horas_semana': horas_semana,
            'porcentaje': porcentaje
        })

    except Exception as e:
        print("❌ ERROR en resumen_actividades:", str(e))
        return jsonify({'success': False}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------- OBTENER DATOS DEL USUARIO ----------
@auth_bp.route('/usuario')
def obtener_usuario():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    return jsonify({
        'success': True,
        'nombre': session.get('nombre'),
        'rol': session.get('rol')
    })
    
    # ------------------- VER ESTUDIANTES ASIGNADOS -------------------
@auth_bp.route('/estudiantes', methods=['GET'])
def listar_estudiantes():
    if 'user_id' not in session or session.get('rol') != 'tutor_academico':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_tutor = session['user_id']
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_listar_estudiantes_asignados', [id_tutor])

        for result in cursor.stored_results():
            estudiantes = result.fetchall()

        return jsonify({'success': True, 'estudiantes': estudiantes})

    except Exception as e:
        print("❌ ERROR al listar estudiantes:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ------------------- VER ACTIVIDADES DE UN ESTUDIANTE -------------------
@auth_bp.route('/actividades/<int:id_estudiante>', methods=['GET'])
def listar_actividades_estudiante(id_estudiante):
    if 'user_id' not in session or session.get('rol') != 'tutor_academico':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_listar_actividades_estudiante', [id_estudiante])

        for result in cursor.stored_results():
            actividades = result.fetchall()

        return jsonify({'success': True, 'actividades': actividades})

    except Exception as e:
        print("❌ ERROR al listar actividades:", str(e))
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ------------------- DESCARGAR ARCHIVO ADJUNTO -------------------
@auth_bp.route('/archivo/<filename>')
def descargar_archivo(filename):
    if 'user_id' not in session or session.get('rol') != 'tutor_academico':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    return send_from_directory(UPLOAD_FOLDER, filename)