DROP DATABASE IF EXISTS seguimiento_practicas;
CREATE DATABASE seguimiento_practicas;
USE seguimiento_practicas;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('estudiante', 'tutor_academico', 'tutor_empresarial') NOT NULL,
    cedula VARCHAR(20) UNIQUE -- agregada columna cedula
);

-- Tabla de actividades
CREATE TABLE actividades (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT NOT NULL,
    horas INT NOT NULL,
    archivo_adjunto VARCHAR(255),
    estado_validacion ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    FOREIGN KEY (id_estudiante) REFERENCES usuarios(id_usuario)
);

-- Tabla de comentarios
CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL,
    texto TEXT,
    fecha_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad) ON DELETE CASCADE
);

-- Tabla de validaciones
CREATE TABLE validaciones (
    id_validacion INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL UNIQUE,
    id_tutor_empresarial INT NOT NULL,
    estado ENUM('aprobada', 'rechazada') NOT NULL,
    motivo_rechazo TEXT,
    fecha_validacion DATE NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad),
    FOREIGN KEY (id_tutor_empresarial) REFERENCES usuarios(id_usuario)
);

-- Tabla de asignaciones
CREATE TABLE asignaciones (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_tutor_empresarial INT NOT NULL,
    id_estudiante INT NOT NULL,
    fecha_asignacion DATE NOT NULL,
    FOREIGN KEY (id_tutor_empresarial) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_estudiante) REFERENCES usuarios(id_usuario),
    UNIQUE (id_tutor_empresarial, id_estudiante)
);

-- PROCEDIMIENTOS ALMACENADOS

DELIMITER $$

-- Registrar usuario
CREATE PROCEDURE sp_registrar_usuario(
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(100),
    IN p_contraseña VARCHAR(255),
    IN p_rol ENUM('estudiante','tutor_academico','tutor_empresarial'),
    IN p_cedula VARCHAR(20)
)
BEGIN
    INSERT INTO usuarios (nombre, correo, contraseña, rol, cedula)
    VALUES (p_nombre, p_correo, p_contraseña, p_rol, p_cedula);
END $$

-- Login
CREATE PROCEDURE sp_login_usuario(IN p_correo VARCHAR(100))
BEGIN
    SELECT id_usuario, nombre, contraseña, rol, cedula
    FROM usuarios
    WHERE correo = p_correo;
END $$

-- Registrar actividad
CREATE PROCEDURE sp_registrar_actividad(
    IN p_id_estudiante INT,
    IN p_fecha DATE,
    IN p_descripcion TEXT,
    IN p_horas INT,
    IN p_archivo_adjunto VARCHAR(255)
)
BEGIN
    INSERT INTO actividades (id_estudiante, fecha, descripcion, horas, archivo_adjunto)
    VALUES (p_id_estudiante, p_fecha, p_descripcion, p_horas, p_archivo_adjunto);
END $$

-- Listar actividades del estudiante
CREATE PROCEDURE sp_listar_actividades_estudiante(IN p_id_estudiante INT)
BEGIN
    SELECT 
        a.fecha, a.descripcion, a.horas, a.estado_validacion,
        COALESCE(c.texto, '') AS comentarios
    FROM actividades a
    LEFT JOIN comentarios c ON a.id_actividad = c.id_actividad
    WHERE a.id_estudiante = p_id_estudiante
    ORDER BY a.fecha DESC;
END $$

-- Obtener resumen
CREATE PROCEDURE sp_resumen_actividades(IN p_id_estudiante INT, IN p_inicio_semana DATE)
BEGIN
    SELECT
        (SELECT IFNULL(SUM(horas), 0) FROM actividades WHERE id_estudiante = p_id_estudiante) AS total_horas,
        (SELECT IFNULL(SUM(horas), 0) FROM actividades WHERE id_estudiante = p_id_estudiante AND fecha >= p_inicio_semana) AS horas_semana;
END $$

-- Asignar tutor a estudiante por cédulas
CREATE PROCEDURE sp_asignar_tutor_por_cedula(
    IN p_cedula_tutor VARCHAR(20),
    IN p_cedula_estudiante VARCHAR(20),
    IN p_fecha_asignacion DATE
)
BEGIN
    DECLARE tutor_id INT;
    DECLARE estudiante_id INT;

    SELECT id_usuario INTO tutor_id FROM usuarios WHERE cedula = p_cedula_tutor AND rol = 'tutor_empresarial' LIMIT 1;
    SELECT id_usuario INTO estudiante_id FROM usuarios WHERE cedula = p_cedula_estudiante AND rol = 'estudiante' LIMIT 1;

    IF tutor_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tutor no encontrado o no es tutor empresarial';
    ELSEIF estudiante_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estudiante no encontrado o no es estudiante';
    ELSE
        INSERT IGNORE INTO asignaciones (id_tutor_empresarial, id_estudiante, fecha_asignacion)
        VALUES (tutor_id, estudiante_id, p_fecha_asignacion);
    END IF;
END $$

DELIMITER $$

CREATE PROCEDURE sp_listar_estudiantes_asignados(IN p_id_tutor INT)
BEGIN
    SELECT DISTINCT u.id_usuario, u.nombre, u.correo
    FROM usuarios u
    INNER JOIN asignaciones a ON a.id_estudiante = u.id_usuario
    WHERE a.id_tutor_empresarial IN (
        SELECT id_usuario
        FROM usuarios
        WHERE rol = 'tutor_empresarial'
    ) AND EXISTS (
        SELECT 1
        FROM usuarios ua
        WHERE ua.id_usuario = p_id_tutor AND ua.rol = 'tutor_academico'
    );
END $$

DELIMITER $$

CREATE PROCEDURE sp_listar_estudiantes_asignados(IN p_id_tutor INT)
BEGIN
    SELECT DISTINCT u.id_usuario, u.nombre, u.correo
    FROM usuarios u
    INNER JOIN asignaciones a ON a.id_estudiante = u.id_usuario
    WHERE a.id_tutor_empresarial IN (
        SELECT id_usuario
        FROM usuarios
        WHERE rol = 'tutor_empresarial'
    ) AND EXISTS (
        SELECT 1
        FROM usuarios ua
        WHERE ua.id_usuario = p_id_tutor AND ua.rol = 'tutor_academico'
    );
END $$

DELIMITER ;


select * from usuarios;

INSERT INTO tutor_estudiante (id_tutor_empresarial, id_estudiante)
VALUES (1, 2, CURDATE());
