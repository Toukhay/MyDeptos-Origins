-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 28-06-2025 a las 20:38:12
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
(46, 117, -27.4823, -55.1098),
(49, 120, -27.4879, -55.1145),
(52, 123, -27.4848, -55.1231),
(57, 128, -27.4883, -55.1144),
(58, 129, -27.4851, -55.1163),
(60, 131, -27.4904, -55.1076),
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
  `telefono_opcional` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `departamento`
--

INSERT INTO `departamento` (`id_departamento`, `id_usuario`, `id_localidad`, `id_coordenadas`, `rol_inmo_dir`, `titulo`, `descripcion`, `tipo_publicacion`, `precio`, `moneda`, `ambientes`, `dormitorios`, `banos`, `superficie`, `direccion`, `fecha_publicacion`, `telefono_opcional`) VALUES
(117, 13, 1, 0, 'Dueño directo', 'Depto. Maiaa', 'Departamento echo para estudiantes y trabajadores sin perros', 'alquiler', 130000, 'ARS', 2, 2, 1, 1200, 'Alvar Núñez Cabeza de Vaca 102, Oberá, Provincia de Misiones, Argentina', '2025-05-05 21:35:49', '0'),
(120, 13, 1, 0, 'Dueño directo', 'Departamento para estudiantes o trabajadores', 'Este departamento esta ubicado en el microcentro de Obera, fecha 2025', 'alquiler', 170000, 'ARS', 1, 1, 1, 50, 'Maipu 100', '2025-05-17 15:47:46', '0'),
(123, 21, 1, 0, 'Dueño directo', 'Departamento de prueba4', 'Departamento de prueba 4, para mostrar al publico en zona centro cerca de la calle salta y go. barreyro', 'alquiler', 800000, 'ARS', 1, 1, 1, 300, 'Salta y Gobernador barreyro', '2025-05-18 00:45:01', ''),
(128, 25, 1, 0, 'Dueño directo', 'depto hanne', 'departamento de hanne', 'alquiler', 100000, 'ARS', 2, 1, 1, 30, 'Brasil 505, Oberá, Provincia de Misiones, Argentina', '2025-05-18 14:33:23', ''),
(129, 25, 1, 0, 'Dueño directo', 'departamento de hanne2', 'departamento para estudiantes y/o trabajadores\r\n', 'alquiler', 180000, 'ARS', 1, 1, 1, 500, 'Río Negro 120, Oberá, Provincia de Misiones, Argentina', '2025-06-11 14:53:56', ''),
(131, 25, 1, 0, 'Dueño directo', 'Departamento de prueba', 'Departamento para alquilarse pronto', 'alquiler', 1111110000000, 'ARS', 1, 1, 1, 123, 'España, Oberá, Provincia de Misiones, Argentina', '2025-06-11 23:33:16', ''),
(132, 27, 1, 0, 'Dueño directo', 'Departamento de Orlando', 'Departamento del profe orlando, publicado el dia de hoy 23/06 tiene 1 baño en mal estado', 'alquiler', 650000, 'ARS', 2, 1, 1, 2000, '9 de Julio 796, Oberá, Municipio de Oberá, Provincia de Misiones, Argentina', '2025-06-23 16:35:38', '');

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
(10, 14, 12, '2025-02-21 23:06:42'),
(15, 14, 15, '2025-02-21 23:33:29'),
(16, 14, 16, '2025-02-21 23:33:41'),
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
(141, 15, 93, '2025-04-27 14:39:28'),
(143, 15, 91, '2025-04-27 18:41:03'),
(144, 15, 94, '2025-04-27 18:41:04'),
(145, 15, 95, '2025-04-27 18:41:04'),
(146, 13, 98, '2025-04-27 21:01:54'),
(148, 13, 95, '2025-04-27 21:02:13'),
(182, 13, 117, '2025-05-12 23:09:29'),
(184, 13, 116, '2025-05-13 00:28:06'),
(188, 22, 124, '2025-05-18 06:05:57'),
(192, 24, 125, '2025-05-18 13:17:45'),
(193, 24, 120, '2025-05-18 13:17:53'),
(195, 26, 128, '2025-06-11 11:13:37'),
(201, 15, 125, '2025-06-11 16:31:22'),
(203, 22, 129, '2025-06-11 23:11:33'),
(206, 22, 120, '2025-06-20 18:56:59'),
(209, 13, 131, '2025-06-21 15:48:10'),
(210, 13, 129, '2025-06-21 15:48:11'),
(211, 15, 129, '2025-06-21 15:52:21'),
(212, 27, 132, '2025-06-23 16:41:27'),
(214, 27, 117, '2025-06-23 16:41:40'),
(216, 15, 131, '2025-06-23 16:47:42');

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
(151, 123, 'thumb-1920-1360883.jpeg'),
(152, 123, 'yasuke-dark-3840x1080-21997.jpg'),
(172, 120, 'b4adf95cf26149b780a337feab842692_489372094_1190603509279635_5779781098789826881_n.jpg'),
(173, 120, 'a6bd891418ef4a28a61aec40fac295c2_489374759_687727687335352_8190738063981778176_n.jpg'),
(174, 120, 'b6ddfe5f334a496e9d212fc6e3061553_496063745_3621494658156466_1751569581737620015_n.jpg'),
(178, 128, 'd9ef3efeb0a74fedaf2dda80b0e2ae02_depto2.webp'),
(179, 128, 'f339334c56694a64866801115de2b5ee_depto3.jpg'),
(180, 129, '30f6e87d3c994e86b39a172223f9a7cd_pexels-fabiano-rodrigues-794857-1662298.jpg'),
(181, 129, '3d5915adc06f4e99b0d48f7785b191be_whatsapp.png'),
(185, 131, '3844d9afa1b24894a98da233d7bb0c20_857653-final.jpeg'),
(186, 131, '2a6959645bc44796bff70f76a0799f51_yasuke-dark-3840x1080-21997.jpg'),
(190, 117, '7250836ad2864017a7539f9bdf78621b_1198867-3840x1080-desktop-dual-monitors-studio-ghibli-wallpaper.jpg'),
(191, 117, 'e9f41c5fe1c2463d8bf5fa47b0e46b48_876413.jpg'),
(192, 117, 'a29f7fe3c3e2485d8f004ce3fffd212a_780881-3440x1440-desktop-dual-monitors-mount-fuji-wallpaper-image.jpg'),
(193, 132, 'c1257296671d4e20abf7bb5b8f6a9a80_780881-3440x1440-desktop-dual-monitors-mount-fuji-wallpaper-image.jpg'),
(194, 132, 'e04a019281334784a2e52e47c1c42df5_thumb-1920-1360883.jpeg'),
(195, 132, '69b1cc83c1274f08b0992e85794c60b8_whatsapp.png');

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
(3, 25, 'nueva_resena', 'Has recibido una nueva reseña en tu departamento \'depto hanne\'.', 128, NULL, 1, '2025-06-11 14:50:57'),
(4, 25, 'NUEVA_RESENA', 'El usuario \'prueba5\' ha dejado una reseña en tu departamento \'departamento de hanne2\'.', 129, 5, 1, '2025-06-11 23:22:14'),
(5, 21, 'NUEVA_RESENA', 'El usuario \'hanne\' ha dejado una reseña en tu departamento \'Departamento de prueba4\'.', 123, 6, 0, '2025-06-11 23:50:21'),
(7, 13, 'NUEVA_RESENA', 'El usuario \'prueba5\' ha dejado una reseña en tu departamento \'Departamento para estudiantes o trabajadores\'.', 120, 8, 1, '2025-06-20 18:57:22');

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
(5, 129, 22, 5, 'Departamento optimo y muy interesante el lugar', '2025-06-11 23:22:14'),
(6, 123, 25, 5, 'Departamento super duper', '2025-06-11 23:50:21'),
(8, 120, 22, 4, 'Buen departamento pero le falta iluminación', '2025-06-20 18:57:22'),
(9, 132, 15, 5, 'Muy buen departamento, la atencion tambien', '2025-06-23 16:49:57');

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
  `telefono` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `name`, `email`, `password`, `fecha_registro`, `telefono`) VALUES
(11, 'maimora', 'moramaia18@gmail.com', '$2b$12$q3FrPZbXIQZVrNe211DXSOWyn7T/t.5eaHGg74Ok8b3btQG1dDq2C', '2025-02-13 15:33:26', '0'),
(12, 'facundo', 'facu-202020@hotmail.com', '$2b$12$3Qa07TGrV7luYdwS2mBHkOhOjqilpO2cYd73s9jz3Kv6fFa09ABRm', '2025-05-18 07:28:07', '543755696943'),
(13, 'maiaa', 'moramaia@gmail.com', '$2b$12$cSH6hwOYj8nGsT0RHHdaQejy1vEXyzYB2q3hr/jeIU.SfhTpQq3.W', '2025-02-22 00:17:57', '0'),
(14, 'marta', 'test@teset.com', '$2b$12$ohU2zMHfG89AHFHmeox7Q.5Gf1cDMjPr5u3UFnMosATs8zX.fISOu', '2025-02-21 23:06:26', '0'),
(15, 'facundo875', 'facu-2020@hotmail.com', '$2b$12$VVgW4b.qwDPwxTcEinAKy.VXdMlvWbuK8NjpTMdbVg21Y/Lm4BIYe', '2025-06-20 18:32:30', '543755384591'),
(16, 'prueba2', 'prueba2@hotmail.com', '$2b$12$rFe0Wszb86YswkJvgeEvFOCtS98tPvj8xz/.OYaF2OYv8ZyQwaXR.', '2025-05-17 23:14:10', '0'),
(21, 'prueba9', 'prueba9@hotmail.com', 'pbkdf2:sha256:1000000$GceyfnfTtmC060ZS$2e087d6045248cc8c432d5a9647394d2f02b0c48ed2d9b7d23b9d04efa14946b', '2025-06-11 01:10:51', '543755339833'),
(22, 'prueba5', 'prueba5@hotmail.com', 'pbkdf2:sha256:1000000$QRRnBqDgQekR2JXm$6fc195b3639e9006425eee9532f80d6a286cb7eabeb4cc2eafe5afd395d92a36', '2025-05-18 06:05:25', '543766544585'),
(24, 'prueba21', 'prueba21@gmail.com', 'pbkdf2:sha256:1000000$B7PD7m4R2n8tIbfm$e209223f73b367f2eb445141fd420db096ee8ae6cc3b086c027e3f698aff87a9', '2025-05-18 13:15:16', '2333445533'),
(25, 'hanne', 'hanne_schallmoser@hotmial.com', 'pbkdf2:sha256:1000000$gyLRFJk4fgxZfUFm$59def588f34fd51d1b0c34df31f6f56536a319a0c8c6ef572230533637c8aa3c', '2025-06-11 10:34:26', '5493755571611'),
(26, 'damirafa', 'damirafa@gmail.com', 'pbkdf2:sha256:1000000$D2RW6vm6ia8R6n5Y$d0182532e1ac24c1c768fc5c5caa314223a2bb84abb32b2a095ceb068c2403b2', '2025-06-11 11:12:03', '3755221566'),
(27, 'Orlandoo', 'orlando123@hotmail.com', '$2b$12$tdkkt4ErYGKWC/tFhSwTyO1QqqoMU30fL2O8s9rBVagk7fWn37DoG', '2025-06-23 16:24:17', '543755654788');

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
  MODIFY `id_coordenadas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT de la tabla `departamento`
--
ALTER TABLE `departamento`
  MODIFY `id_departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=133;

--
-- AUTO_INCREMENT de la tabla `favorito`
--
ALTER TABLE `favorito`
  MODIFY `id_favorito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=217;

--
-- AUTO_INCREMENT de la tabla `foto`
--
ALTER TABLE `foto`
  MODIFY `id_foto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=196;

--
-- AUTO_INCREMENT de la tabla `localidad`
--
ALTER TABLE `localidad`
  MODIFY `id_localidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `resena`
--
ALTER TABLE `resena`
  MODIFY `id_resena` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

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
