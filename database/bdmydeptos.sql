-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 24-07-2025 a las 01:14:58
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bdmydeptos`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion_usuario`
--

CREATE TABLE `configuracion_usuario` (
  `id_configuracion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `email` varchar(200) NOT NULL,
  `telefono` int(11) NOT NULL,
  `fecha_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `coordenadas`
--

CREATE TABLE `coordenadas` (
  `id_coordenadas` int(11) NOT NULL,
  `id_departamento` int(11) NOT NULL,
  `latitud` float NOT NULL,
  `longitud` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `coordenadas`
--

INSERT INTO `coordenadas` (`id_coordenadas`, `id_departamento`, `latitud`, `longitud`) VALUES
(49, 120, -27.4879, -55.1145),
(58, 129, -27.4883, -55.1141),
(61, 132, -27.4861, -55.1197);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamento`
--

CREATE TABLE `departamento` (
  `id_departamento` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_localidad` int(11) NOT NULL,
  `id_coordenadas` int(11) NOT NULL,
  `rol_inmo_dir` varchar(255) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `descripcion` varchar(500) NOT NULL,
  `tipo_publicacion` varchar(200) NOT NULL,
  `precio` float NOT NULL,
  `moneda` varchar(200) NOT NULL,
  `ambientes` int(11) NOT NULL,
  `dormitorios` int(11) NOT NULL,
  `banos` int(11) NOT NULL,
  `superficie` float NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `fecha_publicacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `telefono_opcional` varchar(30) NOT NULL,
  `visitas` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `departamento`
--

INSERT INTO `departamento` (`id_departamento`, `id_usuario`, `id_localidad`, `id_coordenadas`, `rol_inmo_dir`, `titulo`, `descripcion`, `tipo_publicacion`, `precio`, `moneda`, `ambientes`, `dormitorios`, `banos`, `superficie`, `direccion`, `fecha_publicacion`, `telefono_opcional`, `visitas`) VALUES
(120, 13, 1, 0, 'Inmobiliaria', 'Departamento para estudiantes o trabajadores', 'Este departamento esta ubicado en el microcentro de Obera, fecha 2025', 'alquiler', 170000, 'ARS', 1, 1, 1, 50, 'Maipu 100', '2025-05-17 15:47:46', '0', 0),
(129, 25, 1, 0, 'Dueño directo', 'departamento de hanne2', 'departamento para estudiantes y/o trabajadores\r\n', 'alquiler', 180000, 'ARS', 1, 1, 1, 500, 'Brasil 535, Oberá, Municipio de Oberá, Provincia de Misiones, Argentina', '2025-06-11 14:53:56', '', 0),
(132, 27, 1, 0, 'Dueño directo', 'Departamento de Orlando', 'Departamento del profe orlando, publicado el dia de hoy 23/06 tiene 1 baño en mal estado', 'alquiler', 650000, 'ARS', 2, 1, 1, 2000, '9 de Julio 796, Oberá, Municipio de Oberá, Provincia de Misiones, Argentina', '2025-06-23 16:35:38', '', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `favorito`
--

CREATE TABLE `favorito` (
  `id_favorito` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_departamento` int(11) NOT NULL,
  `fecha_agregado` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `favorito`
--

INSERT INTO `favorito` (`id_favorito`, `id_usuario`, `id_departamento`, `fecha_agregado`) VALUES
(47, 13, 18, '2025-02-27 22:25:55'),
(48, 13, 14, '2025-02-27 22:36:59'),
(69, 12, 30, '2025-02-28 19:44:37'),
(70, 13, 31, '2025-03-13 13:42:13'),
(71, 13, 30, '2025-03-13 13:46:19'),
(92, 12, 49, '2025-03-19 14:38:21'),
(96, 13, 50, '2025-03-19 22:14:23'),
(98, 13, 57, '2025-03-23 21:10:16'),
(99, 13, 58, '2025-03-23 21:18:09'),
(122, 12, 70, '2025-03-24 17:33:00'),
(125, 12, 65, '2025-03-24 17:43:03'),
(134, 12, 80, '2025-03-28 02:04:16'),
(135, 12, 80, '2025-04-12 13:36:16'),
(136, 12, 80, '2025-04-12 14:55:07'),
(140, 12, 90, '2025-04-17 19:43:46'),
(146, 13, 98, '2025-04-27 21:01:54'),
(148, 13, 95, '2025-04-27 21:02:13'),
(184, 13, 116, '2025-05-13 00:28:06'),
(209, 13, 131, '2025-06-21 15:48:10'),
(212, 27, 132, '2025-06-23 16:41:27'),
(214, 27, 117, '2025-06-23 16:41:40'),
(217, 13, 120, '2025-07-05 21:54:52'),
(220, 13, 133, '2025-07-06 22:30:29'),
(221, 13, 134, '2025-07-06 22:30:30'),
(223, 13, 117, '2025-07-06 22:30:34'),
(231, 12, 120, '2025-07-09 17:36:08'),
(233, 25, 129, '2025-07-12 22:12:44'),
(234, 25, 120, '2025-07-12 22:12:45');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `foto`
--

CREATE TABLE `foto` (
  `id_foto` int(11) NOT NULL,
  `id_departamento` int(11) NOT NULL,
  `url_foto` varchar(535) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `foto`
--

INSERT INTO `foto` (`id_foto`, `id_departamento`, `url_foto`) VALUES
(172, 120, 'b4adf95cf26149b780a337feab842692_489372094_1190603509279635_5779781098789826881_n.jpg'),
(173, 120, 'a6bd891418ef4a28a61aec40fac295c2_489374759_687727687335352_8190738063981778176_n.jpg'),
(174, 120, 'b6ddfe5f334a496e9d212fc6e3061553_496063745_3621494658156466_1751569581737620015_n.jpg'),
(193, 132, 'c1257296671d4e20abf7bb5b8f6a9a80_780881-3440x1440-desktop-dual-monitors-mount-fuji-wallpaper-image.jpg'),
(194, 132, 'e04a019281334784a2e52e47c1c42df5_thumb-1920-1360883.jpeg'),
(195, 132, '69b1cc83c1274f08b0992e85794c60b8_whatsapp.png'),
(213, 129, '290765ba35514078a8d093e8a9212a42_angel_2.webp'),
(214, 129, '604b30dbb51644dd8dee1a0dc68e31f5_angel2.webp');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `localidad`
--

CREATE TABLE `localidad` (
  `id_localidad` int(11) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `provincia` varchar(200) NOT NULL,
  `pais` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `localidad`
--

INSERT INTO `localidad` (`id_localidad`, `nombre`, `provincia`, `pais`) VALUES
(1, 'Obera', 'Misiones', 'Argentina'),
(2, 'Proximamente en otras ciudades...', 'Misiones', 'Argentina');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificacion` int(11) NOT NULL,
  `id_usuario_receptor` int(11) NOT NULL,
  `tipo_notificacion` varchar(50) NOT NULL COMMENT 'Ej: nuevo_favorito, nueva_resena, sistema',
  `mensaje` varchar(255) NOT NULL,
  `id_departamento_ref` int(11) DEFAULT NULL COMMENT 'Referencia a un departamento si aplica',
  `id_resena_ref` int(11) DEFAULT NULL COMMENT 'Referencia a una reseña si aplica',
  `leida` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = no leída, 1 = leída',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `notificaciones`
--

INSERT INTO `notificaciones` (`id_notificacion`, `id_usuario_receptor`, `tipo_notificacion`, `mensaje`, `id_departamento_ref`, `id_resena_ref`, `leida`, `fecha_envio`) VALUES
(3, 25, 'nueva_resena', 'Has recibido una nueva reseña en tu departamento \'depto hanne\'.', NULL, NULL, 1, '2025-06-11 14:50:57'),
(4, 25, 'NUEVA_RESENA', 'El usuario \'prueba5\' ha dejado una reseña en tu departamento \'departamento de hanne2\'.', 129, NULL, 1, '2025-06-11 23:22:14');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resena`
--

CREATE TABLE `resena` (
  `id_resena` int(11) NOT NULL,
  `id_departamento` int(11) NOT NULL,
  `id_usuario_calificador` int(11) NOT NULL,
  `puntaje` tinyint(1) NOT NULL COMMENT 'Calificación de 1 a 5 estrellas',
  `comentario` text DEFAULT NULL,
  `fecha_calificacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `resena`
--

INSERT INTO `resena` (`id_resena`, `id_departamento`, `id_usuario_calificador`, `puntaje`, `comentario`, `fecha_calificacion`) VALUES
(12, 120, 12, 3, 'rtbrtbrt', '2025-07-09 17:36:18');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(255) NOT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `fecha_ultima_modificacion` date DEFAULT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `rol` varchar(30) NOT NULL,
  `ediciones_ultimos_dos_dias` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `name`, `email`, `password`, `fecha_registro`, `fecha_ultima_modificacion`, `telefono`, `rol`, `ediciones_ultimos_dos_dias`) VALUES
(12, 'facundo', 'facu-202020@hotmail.com', '$2b$12$3Qa07TGrV7luYdwS2mBHkOhOjqilpO2cYd73s9jz3Kv6fFa09ABRm', '2025-07-07 16:53:03', NULL, '3755384591', 'admin', 0),
(13, 'maiaa', 'moramaia@gmail.com', '$2b$12$cSH6hwOYj8nGsT0RHHdaQejy1vEXyzYB2q3hr/jeIU.SfhTpQq3.W', '2025-07-09 17:39:30', NULL, '3755339833', 'admin', 0),
(25, 'hanne', 'hanne_schallmoser@hotmial.com', 'pbkdf2:sha256:1000000$2xQ6JYLagTndE7Al$795be233771fd224d78ad29a46d1142e5276b71622c53a9403a3771ab61c221e', '2025-07-12 20:38:24', NULL, '3755571611', 'user', 0),
(27, 'Orlando', 'orlando123@hotmail.com', '$2b$12$tdkkt4ErYGKWC/tFhSwTyO1QqqoMU30fL2O8s9rBVagk7fWn37DoG', '2025-07-07 16:53:17', NULL, '543755654788', 'user', 0),
(32, 'mydeptos', 'mydeptos@gmail.com', 'pbkdf2:sha256:1000000$3B5wFuOt6gtvYQuC$3d442a60b35ac08ad672ce96c9ed9b3b7e50f1cd532e56cf23fdcacf139ce888', '2025-07-07 16:51:39', '2025-07-05', '3755339833', 'user', 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `configuracion_usuario`
--
ALTER TABLE `configuracion_usuario`
  ADD PRIMARY KEY (`id_configuracion`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `coordenadas`
--
ALTER TABLE `coordenadas`
  ADD PRIMARY KEY (`id_coordenadas`),
  ADD KEY `id_departamento` (`id_departamento`);

--
-- Indices de la tabla `departamento`
--
ALTER TABLE `departamento`
  ADD PRIMARY KEY (`id_departamento`),
  ADD KEY `id_usuario` (`id_usuario`,`id_localidad`),
  ADD KEY `id_coordenadas` (`id_coordenadas`),
  ADD KEY `id_localidad` (`id_localidad`);

--
-- Indices de la tabla `favorito`
--
ALTER TABLE `favorito`
  ADD PRIMARY KEY (`id_favorito`),
  ADD KEY `id_usuario` (`id_usuario`,`id_departamento`);

--
-- Indices de la tabla `foto`
--
ALTER TABLE `foto`
  ADD PRIMARY KEY (`id_foto`),
  ADD KEY `id_departamento` (`id_departamento`);

--
-- Indices de la tabla `localidad`
--
ALTER TABLE `localidad`
  ADD PRIMARY KEY (`id_localidad`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificacion`),
  ADD KEY `idx_notificaciones_usuario_receptor` (`id_usuario_receptor`),
  ADD KEY `idx_notificaciones_departamento_ref` (`id_departamento_ref`),
  ADD KEY `idx_notificaciones_resena_ref` (`id_resena_ref`);

--
-- Indices de la tabla `resena`
--
ALTER TABLE `resena`
  ADD PRIMARY KEY (`id_resena`),
  ADD KEY `idx_resena_departamento` (`id_departamento`),
  ADD KEY `idx_resena_usuario_calificador` (`id_usuario_calificador`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `configuracion_usuario`
--
ALTER TABLE `configuracion_usuario`
  MODIFY `id_configuracion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `coordenadas`
--
ALTER TABLE `coordenadas`
  MODIFY `id_coordenadas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT de la tabla `departamento`
--
ALTER TABLE `departamento`
  MODIFY `id_departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=139;

--
-- AUTO_INCREMENT de la tabla `favorito`
--
ALTER TABLE `favorito`
  MODIFY `id_favorito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=236;

--
-- AUTO_INCREMENT de la tabla `foto`
--
ALTER TABLE `foto`
  MODIFY `id_foto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=215;

--
-- AUTO_INCREMENT de la tabla `localidad`
--
ALTER TABLE `localidad`
  MODIFY `id_localidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `resena`
--
ALTER TABLE `resena`
  MODIFY `id_resena` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `configuracion_usuario`
--
ALTER TABLE `configuracion_usuario`
  ADD CONSTRAINT `configuracion_usuario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `coordenadas`
--
ALTER TABLE `coordenadas`
  ADD CONSTRAINT `coordenadas_ibfk_1` FOREIGN KEY (`id_departamento`) REFERENCES `departamento` (`id_departamento`);

--
-- Filtros para la tabla `departamento`
--
ALTER TABLE `departamento`
  ADD CONSTRAINT `departamento_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `departamento_ibfk_2` FOREIGN KEY (`id_localidad`) REFERENCES `localidad` (`id_localidad`);

--
-- Filtros para la tabla `favorito`
--
ALTER TABLE `favorito`
  ADD CONSTRAINT `favorito_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `foto`
--
ALTER TABLE `foto`
  ADD CONSTRAINT `foto_ibfk_1` FOREIGN KEY (`id_departamento`) REFERENCES `departamento` (`id_departamento`);

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `fk_notificaciones_departamento_ref` FOREIGN KEY (`id_departamento_ref`) REFERENCES `departamento` (`id_departamento`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_notificaciones_resena_ref` FOREIGN KEY (`id_resena_ref`) REFERENCES `resena` (`id_resena`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_notificaciones_usuario_receptor` FOREIGN KEY (`id_usuario_receptor`) REFERENCES `usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `resena`
--
ALTER TABLE `resena`
  ADD CONSTRAINT `fk_resena_departamento` FOREIGN KEY (`id_departamento`) REFERENCES `departamento` (`id_departamento`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_resena_usuario_calificador` FOREIGN KEY (`id_usuario_calificador`) REFERENCES `usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
