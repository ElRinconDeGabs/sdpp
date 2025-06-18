CREATE DATABASE IF NOT EXISTS seguimiento_practicas;
USE seguimiento_practicas;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('estudiante', 'tutor_academico', 'tutor_empresarial') NOT NULL
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

-- Tabla de validaciones
CREATE TABLE validaciones (
    id_validacion INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL UNIQUE,
    tutor_empresarial_id INT NOT NULL,
    estado ENUM('aprobada', 'rechazada') NOT NULL,
    motivo_rechazo TEXT,
    fecha_validacion DATE NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad),
    FOREIGN KEY (tutor_empresarial_id) REFERENCES usuarios(id_usuario)
);

-- Tabla de comentarios
CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT NOT NULL,
    tutor_academico_id INT NOT NULL,
    texto TEXT NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id_actividad),
    FOREIGN KEY (tutor_academico_id) REFERENCES usuarios(id_usuario)
);

-- Tabla de reportes
CREATE TABLE reportes (
    id_reporte INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    archivo_pdf VARCHAR(255),
    FOREIGN KEY (id_estudiante) REFERENCES usuarios(id_usuario)
);

select * from usuarios

INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES
('Ana Martínez', 'ana@correo.com', 'clave123', 'estudiante'),
('Luis Gómez', 'luis@correo.com', 'clave123', 'estudiante'),
('Carla Ríos', 'carla@correo.com', 'clave123', 'estudiante'),
('Dra. Elena Ruiz', 'elena@correo.com', 'clave123', 'tutor_academico'),
('Dr. Pedro Díaz', 'pedro@correo.com', 'clave123', 'tutor_academico'),
('Dra. María León', 'maria@correo.com', 'clave123', 'tutor_academico'),
('Ing. Jorge Pérez', 'jorge@empresa.com', 'clave123', 'tutor_empresarial'),
('Ing. Marta Sánchez', 'marta@empresa.com', 'clave123', 'tutor_empresarial'),
('Ing. Omar Ramírez', 'omar@empresa.com', 'clave123', 'tutor_empresarial'),
('Ing. Luisa Herrera', 'luisa@empresa.com', 'clave123', 'tutor_empresarial');

-- Inserción de actividades (una por estudiante)
INSERT INTO actividades (id_estudiante, fecha, descripcion, horas, archivo_adjunto, estado_validacion) VALUES
(1, '2025-05-01', 'Configuración de red en la empresa', 4, 'adjunto1.pdf', 'pendiente'),
(2, '2025-05-02', 'Desarrollo de módulo de inventario', 5, 'adjunto2.pdf', 'pendiente'),
(3, '2025-05-03', 'Revisión de tickets de soporte', 3, 'adjunto3.pdf', 'pendiente');

-- Inserción de validaciones (una por actividad, cada una con un tutor empresarial diferente)
INSERT INTO validaciones (id_actividad, tutor_empresarial_id, estado, motivo_rechazo, fecha_validacion) VALUES
(1, 7, 'aprobada', NULL, '2025-05-05'),
(2, 8, 'rechazada', 'No se adjuntó evidencia suficiente', '2025-05-06'),
(3, 9, 'aprobada', NULL, '2025-05-07');

-- Inserción de comentarios (una por actividad, cada uno con un tutor académico diferente)
INSERT INTO comentarios (id_actividad, tutor_academico_id, texto, fecha) VALUES
(1, 4, 'Buen trabajo, continúa así.', '2025-05-05'),
(2, 5, 'Debes ser más específico en la descripción.', '2025-05-06'),
(3, 6, 'Revisar el número de horas reportadas.', '2025-05-07');

-- Inserción de reportes (uno por estudiante)
INSERT INTO reportes (id_estudiante, fecha_inicio, fecha_fin, archivo_pdf) VALUES
(1, '2025-04-01', '2025-04-30', 'reporte1.pdf'),
(2, '2025-04-01', '2025-04-30', 'reporte2.pdf'),
(3, '2025-04-01', '2025-04-30', 'reporte3.pdf');
