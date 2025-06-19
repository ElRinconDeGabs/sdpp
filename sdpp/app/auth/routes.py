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


@auth_bp.route('/sign-up', methods=['POST'])
def sign_up():
    conn = None
    cursor = None
    try:
        data = request.get_json(force=True)
        nombre = data.get('nombre')
        correo = data.get('correo')
        contraseña = data.get('contraseña')
        rol = data.get('rol')
        cedula = data.get('cedula')

        # Validar datos obligatorios
        if not all([nombre, correo, contraseña, rol, cedula]):
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400

        hashed_pw = generate_password_hash(contraseña)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Llamar al procedimiento almacenado
        cursor.callproc('sp_registrar_usuario', (nombre, correo, hashed_pw, rol, cedula))
        conn.commit()

        # Asignar sesión
        session['user_id'] = cursor.lastrowid
        session['rol'] = rol
        session['nombre'] = nombre

        return jsonify({'success': True, 'message': 'Usuario registrado correctamente'})

    except mysql.connector.Error as err:
        # Manejar error de llave duplicada (correo o cédula)
        if err.errno == 1644:  # SQLSTATE '45000' usado en SIGNAL
            return jsonify({'success': False, 'message': str(err.msg)}), 409
        print("❌ ERROR en sign_up:", err)
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    except Exception as e:
        print("❌ ERROR en sign_up:", e)
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

        # ✅ Usa sp_resumen_actividades en vez de los dos SP inexistentes
        cursor.callproc('sp_resumen_actividades', [id_estudiante, inicio_semana])

        total_horas = 0
        horas_semana = 0
        for result in cursor.stored_results():
            fila = result.fetchone()
            if fila:
                total_horas, horas_semana = fila

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

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nombre, rol, cedula FROM usuarios WHERE id_usuario = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({'success': False}), 404

    return jsonify({
        'success': True,
        'nombre': user['nombre'],
        'rol': user['rol'],
        'cedula': user['cedula']  # 👈 asegúrate de incluir esto
    })

# Middleware básico para verificar tutor académico
def es_tutor_academico():
    return 'user_id' in session and session.get('rol') == 'tutor_academico'


# 5. Listar tutores empresariales disponibles (AHORA incluye cédula)
@auth_bp.route('/tutores-empresariales', methods=['GET'])
def listar_tutores_empresariales():
    if not es_tutor_academico():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        # Agregamos cedula a la selección
        cursor.execute("SELECT id_usuario, nombre, cedula FROM usuarios WHERE rol = 'tutor_empresarial'")
        tutores = cursor.fetchall()
        return jsonify({'success': True, 'tutores': tutores})
    except Exception as e:
        print("❌ ERROR listar_tutores_empresariales:", e)
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500
    finally:
        cursor.close()
        conn.close()


# 2. Listar todos los estudiantes con sus tutores (sp_listar_estudiantes_con_tutores)
@auth_bp.route('/estudiantes-con-tutores', methods=['GET'])
def listar_estudiantes_con_tutores():
    if not es_tutor_academico():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_listar_estudiantes_con_tutores')
        estudiantes = []
        for result in cursor.stored_results():
            estudiantes = result.fetchall()
            
        ids_estudiantes = [e['id_estudiante'] for e in estudiantes]
        if ids_estudiantes:
            format_strings = ','.join(['%s'] * len(ids_estudiantes))
            cursor.execute(f"SELECT id_usuario, cedula FROM usuarios WHERE id_usuario IN ({format_strings})", tuple(ids_estudiantes))
            cedulas = {row['id_usuario']: row['cedula'] for row in cursor.fetchall()}
            for e in estudiantes:
                e['cedula'] = cedulas.get(e['id_estudiante'], None)
        else:
            for e in estudiantes:
                e['cedula'] = None

        return jsonify({'success': True, 'estudiantes': estudiantes})
    except Exception as e:
        print("❌ ERROR listar_estudiantes_con_tutores:", e)
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500
    finally:
        cursor.close()
        conn.close()


# 4. Asignar o actualizar tutor empresarial a estudiante (sp_asignar_tutor)
@auth_bp.route('/asignar-tutor', methods=['POST'])
def asignar_o_actualizar_tutor():
    if not es_tutor_academico():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.json
    cedula_empresarial = data.get('cedula_empresarial')
    cedula_estudiante = data.get('cedula_estudiante')
    fecha_asignacion = data.get('fecha_asignacion', datetime.now().date().isoformat())

    if not all([cedula_empresarial, cedula_estudiante]):
        return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400

    id_acad = session['user_id']

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Validar existencia de tutor empresarial
        cursor.execute("SELECT id_usuario FROM usuarios WHERE cedula=%s AND rol='tutor_empresarial'", (cedula_empresarial,))
        res_emp = cursor.fetchone()

        # Validar existencia de estudiante
        cursor.execute("SELECT id_usuario FROM usuarios WHERE cedula=%s AND rol='estudiante'", (cedula_estudiante,))
        res_est = cursor.fetchone()

        if not res_emp or not res_est:
            return jsonify({'success': False, 'message': 'Algún usuario no válido'}), 400

        id_emp = res_emp[0]
        id_est = res_est[0]

        # Verificar si ya existe asignación para ese estudiante y tutor académico
        cursor.execute(
            "SELECT id_asignacion FROM asignaciones WHERE id_estudiante=%s AND id_tutor_academico=%s",
            (id_est, id_acad)
        )
        asignacion_existente = cursor.fetchone()

        if asignacion_existente:
            cursor.execute(
                "UPDATE asignaciones SET id_tutor_empresarial=%s, fecha_asignacion=%s WHERE id_asignacion=%s",
                (id_emp, fecha_asignacion, asignacion_existente[0])
            )
        else:
            cursor.execute(
                "INSERT INTO asignaciones (id_tutor_academico, id_tutor_empresarial, id_estudiante, fecha_asignacion) VALUES (%s, %s, %s, %s)",
                (id_acad, id_emp, id_est, fecha_asignacion)
            )

        conn.commit()
        return jsonify({'success': True, 'message': 'Asignación realizada correctamente'})

    except Exception as e:
        print("❌ ERROR asignar_o_actualizar_tutor:", e)
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500
    finally:
        cursor.close()
        conn.close()

        
# 3. Listar actividades de estudiantes con tutor académico (sp_listar_actividades_con_tutor)
@auth_bp.route('/actividades-estudiantes', methods=['GET'])
def actividades_estudiantes():
    if 'user_id' not in session or session.get('rol') != 'tutor_academico':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.callproc('sp_listar_actividades_con_tutor')

        actividades = []
        for result in cursor.stored_results():
            actividades = result.fetchall()

        print("Datos actividades:", actividades)  # <-- Agrega este print para debug

        return jsonify({'success': True, 'actividades': actividades})

    except Exception as e:
        print("❌ ERROR en actividades_estudiantes:", e)
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

