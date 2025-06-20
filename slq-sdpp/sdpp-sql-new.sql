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
    cedula VARCHAR(20) UNIQUE
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

-- Tabla de asignaciones (ahora incluye tutor académico)
CREATE TABLE asignaciones (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_tutor_academico INT NOT NULL,
    id_tutor_empresarial INT NOT NULL,
    id_estudiante INT NOT NULL,
    fecha_asignacion DATE NOT NULL,
    FOREIGN KEY (id_tutor_academico) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_tutor_empresarial) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_estudiante) REFERENCES usuarios(id_usuario),
    UNIQUE KEY unique_asignacion (id_tutor_academico, id_tutor_empresarial, id_estudiante)
);

-- PROCEDIMIENTOS ALMACENADOS

DELIMITER $$

CREATE PROCEDURE sp_registrar_usuario(
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(100),
    IN p_contraseña VARCHAR(255),
    IN p_rol ENUM('estudiante','tutor_academico','tutor_empresarial'),
    IN p_cedula VARCHAR(20)
)
BEGIN
    -- Validar si ya existe correo
    IF EXISTS (SELECT 1 FROM usuarios WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Correo ya registrado';
    END IF;

    -- Validar si ya existe cedula
    IF EXISTS (SELECT 1 FROM usuarios WHERE cedula = p_cedula) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cédula ya registrada';
    END IF;

    -- Insertar usuario
    INSERT INTO usuarios (nombre, correo, contraseña, rol, cedula)
    VALUES (p_nombre, p_correo, p_contraseña, p_rol, p_cedula);
END $$

CREATE PROCEDURE sp_login_usuario(IN p_correo VARCHAR(100))
BEGIN
    SELECT id_usuario, nombre, contraseña, rol, cedula
    FROM usuarios
    WHERE correo = p_correo;
END $$

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

CREATE PROCEDURE sp_resumen_actividades(IN p_id_estudiante INT, IN p_inicio_semana DATE)
BEGIN
    SELECT
        (SELECT IFNULL(SUM(horas), 0) FROM actividades WHERE id_estudiante = p_id_estudiante) AS total_horas,
        (SELECT IFNULL(SUM(horas), 0) FROM actividades WHERE id_estudiante = p_id_estudiante AND fecha >= p_inicio_semana) AS horas_semana;
END $$

CREATE PROCEDURE sp_asignar_tutores_por_cedula(
    IN p_cedula_academico VARCHAR(20),
    IN p_cedula_empresarial VARCHAR(20),
    IN p_cedula_estudiante VARCHAR(20),
    IN p_fecha_asignacion DATE
)
BEGIN
    DECLARE id_academico INT;
    DECLARE id_empresarial INT;
    DECLARE id_estudiante INT;

    SELECT id_usuario INTO id_academico FROM usuarios WHERE cedula = p_cedula_academico AND rol = 'tutor_academico';
    SELECT id_usuario INTO id_empresarial FROM usuarios WHERE cedula = p_cedula_empresarial AND rol = 'tutor_empresarial';
    SELECT id_usuario INTO id_estudiante FROM usuarios WHERE cedula = p_cedula_estudiante AND rol = 'estudiante';

    IF id_academico IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tutor académico no válido';
    ELSEIF id_empresarial IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tutor empresarial no válido';
    ELSEIF id_estudiante IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estudiante no válido';
    ELSE
        INSERT IGNORE INTO asignaciones (id_tutor_academico, id_tutor_empresarial, id_estudiante, fecha_asignacion)
        VALUES (id_academico, id_empresarial, id_estudiante, p_fecha_asignacion);
    END IF;
END $$

CREATE PROCEDURE sp_listar_estudiantes_asignados(IN p_id_tutor INT)
BEGIN
    SELECT DISTINCT u.id_usuario, u.nombre, u.correo
    FROM usuarios u
    INNER JOIN asignaciones a ON a.id_estudiante = u.id_usuario
    WHERE a.id_tutor_academico = p_id_tutor;
END $$

CREATE PROCEDURE sp_listar_estudiantes_con_tutores()
BEGIN
    SELECT 
        e.id_usuario AS id_estudiante,
        e.nombre AS nombre_estudiante,
        ta.nombre AS tutor_academico,
        te.nombre AS tutor_empresarial
    FROM usuarios e
    LEFT JOIN asignaciones a ON a.id_estudiante = e.id_usuario
    LEFT JOIN usuarios ta ON ta.id_usuario = a.id_tutor_academico
    LEFT JOIN usuarios te ON te.id_usuario = a.id_tutor_empresarial
    WHERE e.rol = 'estudiante';
END $$

CREATE PROCEDURE sp_listar_actividades_estudiantes_asignados(IN p_id_tutor_academico INT)
BEGIN

    SELECT 
        u_est.nombre AS nombre_estudiante,
        u_tutor_emp.nombre AS tutor_empresarial,
        a.fecha,
        a.descripcion,
        a.horas,
        a.estado,
        a.comentarios
    FROM actividades a
    INNER JOIN usuarios u_est ON a.id_estudiante = u_est.id_usuario
    INNER JOIN asignaciones asign ON asign.id_estudiante = a.id_estudiante AND asign.id_tutor_academico = p_id_tutor_academico
    LEFT JOIN usuarios u_tutor_emp ON asign.id_tutor_empresarial = u_tutor_emp.id_usuario
    ORDER BY a.fecha DESC;

END$$

CREATE PROCEDURE sp_listar_actividades_con_tutor()
BEGIN
    SELECT 
        u.nombre AS estudiante,
        te.nombre AS tutor_empresarial,
        a.fecha,
        a.descripcion,
        a.horas,
        a.estado_validacion,
        COALESCE(
          (SELECT texto FROM comentarios c WHERE c.id_actividad = a.id_actividad ORDER BY fecha_comentario DESC LIMIT 1),
          ''
        ) AS comentario
    FROM actividades a
    INNER JOIN usuarios u ON a.id_estudiante = u.id_usuario
    LEFT JOIN asignaciones asg ON asg.id_estudiante = u.id_usuario
    LEFT JOIN usuarios te ON te.id_usuario = asg.id_tutor_empresarial
    ORDER BY a.fecha DESC;
END$$

CREATE PROCEDURE sp_listar_actividades_por_validar(IN p_id_tutor_empresarial INT)
BEGIN
  SELECT 
    a.id_actividad,
    u.nombre AS nombre_estudiante,
    a.fecha,
    a.descripcion,
    a.horas,
    a.archivo_adjunto
  FROM actividades a
  INNER JOIN usuarios u ON a.id_estudiante = u.id_usuario
  INNER JOIN asignaciones asg ON asg.id_estudiante = a.id_estudiante
  WHERE a.estado_validacion = 'pendiente'
    AND asg.id_tutor_empresarial = p_id_tutor_empresarial
  ORDER BY a.fecha DESC;
END$$


CREATE PROCEDURE sp_validar_actividad(
    IN p_id_actividad INT,
    IN p_id_tutor_empresarial INT,
    IN p_estado ENUM('aprobada', 'rechazada'),
    IN p_comentario TEXT
)
BEGIN
    DECLARE fecha_actual DATE;
    SET fecha_actual = CURDATE();

    -- Insertar comentario
    INSERT INTO comentarios (id_actividad, texto)
    VALUES (p_id_actividad, p_comentario);

    -- Insertar registro de validación
    INSERT INTO validaciones (id_actividad, id_tutor_empresarial, estado, motivo_rechazo, fecha_validacion)
    VALUES (p_id_actividad, p_id_tutor_empresarial, p_estado,
      IF(p_estado = 'rechazada', p_comentario, NULL), fecha_actual);

    -- Actualizar estado de la actividad
    UPDATE actividades
    SET estado_validacion = p_estado
    WHERE id_actividad = p_id_actividad;
END$$

DELIMITER ;

select * from actividades;
select * from comentarios;
select * from usuarios;

INSERT INTO tutor_estudiante (id_tutor_empresarial, id_estudiante)
VALUES (1, 2, CURDATE());

SHOW COLUMNS FROM actividades;

call sp_listar_actividades_estudiantes_asignados(5);
call sp_listar_actividades_estudiante();
CALL sp_listar_actividades_por_validar(1);
