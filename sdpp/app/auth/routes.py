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

# ---------- DASHBOARD DEL ESTUDIANTE (HTML) ----------
@auth_bp.route('/estudiante/dashboard')
def estudiante_dashboard():
    if 'user_id' not in session or session.get('rol') != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    return send_from_directory(os.path.join(BASE_DIR, '..', 'static'), 'e_dashboard.html')

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
        cursor.execute("""
            INSERT INTO actividades (id_estudiante, fecha, descripcion, horas, archivo_adjunto)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_estudiante, fecha, descripcion, horas, archivo_nombre))
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
        print("❌ ERROR en mis_actividades:", str(e))
        return jsonify({'success': False, 'message': 'Error al obtener actividades'}), 500

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

        cursor.execute("SELECT SUM(horas) FROM actividades WHERE id_estudiante = %s", (id_estudiante,))
        total_horas = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(horas) FROM actividades WHERE id_estudiante = %s AND fecha >= %s", (id_estudiante, inicio_semana))
        horas_semana = cursor.fetchone()[0] or 0

        porcentaje = min(100, int((total_horas / 80) * 100)) if total_horas else 0

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

# ---------- FUNCIONES AUXILIARES ----------
def es_tutor_empresarial():
    return session.get('rol') == 'tutor_empresarial'

def tiene_permiso_tutor(conn, id_actividad, id_tutor):
    cursor = conn.cursor()
    query = """
        SELECT 1
        FROM actividades a
        JOIN tutor_estudiante te ON te.id_estudiante = a.id_estudiante
        WHERE a.id_actividad = %s AND te.id_tutor_empresarial = %s
        LIMIT 1
    """
    cursor.execute(query, (id_actividad, id_tutor))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None

# ---------- RUTAS PARA TUTOR EMPRESARIAL CON PREFIJO /tutor ----------

# Obtener datos del tutor
@auth_bp.route('/tutor/usuario')
def tutor_usuario():
    if 'user_id' not in session or not es_tutor_empresarial():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    return jsonify({
        'success': True,
        'nombre': session.get('nombre'),
        'rol': session.get('rol')
    })

# Listar actividades pendientes de validar para tutor
@auth_bp.route('/tutor/actividades/por-validar', methods=['GET'])
def tutor_actividades_por_validar():
    if 'user_id' not in session or not es_tutor_empresarial():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_tutor = session['user_id']
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        consulta = """
            SELECT a.id_actividad, a.fecha, a.descripcion, a.horas, a.archivo_adjunto,
                   u.nombre AS nombre_estudiante
            FROM actividades a
            JOIN usuarios u ON u.id_usuario = a.id_estudiante
            JOIN tutor_estudiante te ON te.id_estudiante = a.id_estudiante
            WHERE te.id_tutor_empresarial = %s
              AND (a.estado_validacion IS NULL OR a.estado_validacion = 'pendiente')
            ORDER BY a.fecha DESC
        """
        cursor.execute(consulta, (id_tutor,))
        actividades = cursor.fetchall()

        return jsonify({'success': True, 'data': actividades})

    except Exception as e:
        print("❌ ERROR en tutor_actividades_por_validar:", e)
        return jsonify({'success': False, 'message': 'Error al obtener actividades'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Validar actividad (aprobar/rechazar)
@auth_bp.route('/tutor/actividades/validar', methods=['POST'])
def tutor_validar_actividad():
    if 'user_id' not in session or not es_tutor_empresarial():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'No se recibió JSON válido'}), 400

    id_actividad = data.get('id_actividad')
    estado_validacion = data.get('estado_validacion')
    comentario = data.get('comentario', '')

    if not id_actividad or estado_validacion not in ['aprobada', 'rechazada']:
        return jsonify({'success': False, 'message': 'Datos inválidos'}), 400

    id_tutor = session['user_id']

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        if not tiene_permiso_tutor(conn, id_actividad, id_tutor):
            return jsonify({'success': False, 'message': 'No tiene permiso para validar esta actividad'}), 403

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE actividades SET estado_validacion = %s WHERE id_actividad = %s",
            (estado_validacion, id_actividad)
        )

        fecha_validacion = datetime.now()
        cursor.execute("""
            INSERT INTO validaciones (id_actividad, id_tutor_empresarial, estado_validacion, comentarios, fecha_validacion)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_actividad, id_tutor, estado_validacion, comentario, fecha_validacion))

        conn.commit()
        return jsonify({'success': True, 'message': 'Actividad validada correctamente'})

    except Exception as e:
        print("❌ ERROR en tutor_validar_actividad:", e)
        return jsonify({'success': False, 'message': 'Error al validar actividad'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Descargar evidencia de actividad
@auth_bp.route('/tutor/actividad/<int:id_actividad>/evidencia', methods=['GET'])
def tutor_descargar_evidencia(id_actividad):
    if 'user_id' not in session or not es_tutor_empresarial():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    id_tutor = session['user_id']
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        if not tiene_permiso_tutor(conn, id_actividad, id_tutor):
            return jsonify({'success': False, 'message': 'No tiene permiso para ver esta evidencia'}), 403

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT archivo_adjunto FROM actividades WHERE id_actividad = %s", (id_actividad,))
        fila = cursor.fetchone()

        if not fila or not fila['archivo_adjunto']:
            return jsonify({'success': False, 'message': 'No hay archivo adjunto para esta actividad'}), 404

        nombre_archivo = fila['archivo_adjunto']
        return send_from_directory(UPLOAD_FOLDER, nombre_archivo)

    except Exception as e:
        print("❌ ERROR en tutor_descargar_evidencia:", e)
        return jsonify({'success': False, 'message': 'Error al obtener evidencia'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()