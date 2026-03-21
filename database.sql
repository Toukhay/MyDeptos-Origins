-- MyDeptos - Database Schema
-- Versión 1.0

CREATE DATABASE IF NOT EXISTS bdmydeptos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bdmydeptos;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    telefono VARCHAR(30),
    rol ENUM('user', 'admin') DEFAULT 'user',
    fecha_registro DATETIME DEFAULT NOW(),
    fecha_ultima_modificacion DATETIME,
    ediciones_ultimos_dos_dias INT DEFAULT 0
);

-- Tabla de localidades
CREATE TABLE IF NOT EXISTS localidad (
    id_localidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla de departamentos
CREATE TABLE IF NOT EXISTS departamento (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_localidad INT,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo_publicacion ENUM('venta', 'alquiler') NOT NULL,
    precio DECIMAL(12,2) NOT NULL,
    moneda ENUM('ARS', 'USD') DEFAULT 'ARS',
    ambientes INT NOT NULL,
    dormitorios INT NOT NULL,
    banos INT NOT NULL,
    superficie DECIMAL(8,2),
    direccion VARCHAR(200) NOT NULL,
    rol_inmo_dir ENUM('Dueño directo', 'Inmobiliaria') NOT NULL,
    estado ENUM('disponible', 'reservado', 'vendido', 'alquilado') DEFAULT 'disponible',
    fecha_publicacion DATETIME DEFAULT NOW(),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    FOREIGN KEY (id_localidad) REFERENCES localidad(id_localidad)
);

-- Tabla de fotos
CREATE TABLE IF NOT EXISTS foto (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,
    id_departamento INT NOT NULL,
    url_foto VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento)
);

-- Tabla de coordenadas
CREATE TABLE IF NOT EXISTS coordenadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_departamento INT NOT NULL UNIQUE,
    latitud DECIMAL(10,7),
    longitud DECIMAL(10,7),
    FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento)
);

-- Tabla de favoritos
CREATE TABLE IF NOT EXISTS favorito (
    id_favorito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_departamento INT NOT NULL,
    fecha_agregado DATETIME DEFAULT NOW(),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento)
);

-- Tabla de reseñas
CREATE TABLE IF NOT EXISTS resena (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,
    id_departamento INT NOT NULL,
    id_usuario_calificador INT NOT NULL,
    puntaje INT NOT NULL CHECK (puntaje BETWEEN 1 AND 5),
    comentario TEXT NOT NULL,
    fecha_calificacion DATETIME DEFAULT NOW(),
    FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento),
    FOREIGN KEY (id_usuario_calificador) REFERENCES usuario(id)
);

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_receptor INT NOT NULL,
    tipo_notificacion VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    id_departamento_ref INT,
    id_resena_ref INT,
    fecha_envio DATETIME DEFAULT NOW(),
    leida TINYINT(1) DEFAULT 0,
    FOREIGN KEY (id_usuario_receptor) REFERENCES usuario(id),
    FOREIGN KEY (id_departamento_ref) REFERENCES departamento(id_departamento),
    FOREIGN KEY (id_resena_ref) REFERENCES resena(id_resena)
);

-- Tabla de configuración de usuario
CREATE TABLE IF NOT EXISTS configuracion_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);

-- Localidades de ejemplo (Misiones, Argentina)
INSERT IGNORE INTO localidad (nombre) VALUES
('Posadas'),
('Oberá'),
('Eldorado'),
('Puerto Iguazú'),
('Apóstoles'),
('Leandro N. Alem'),
('San Vicente'),
('Jardín América'),
('Aristóbulo del Valle'),
('Montecarlo');

-- Usuario admin por defecto (password: admin1234)
INSERT IGNORE INTO usuario (name, email, password, telefono, rol)
VALUES (
    'admin',
    'admin@mydeptos.com',
    'pbkdf2:sha256:600000$x8K2pQ4mN1nV3$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
    '0000000000',
    'admin'
);