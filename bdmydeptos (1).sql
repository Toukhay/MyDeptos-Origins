-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 17-05-2025 a las 20:44:29
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
(30, 101, -27.4796, -55.1143),
(36, 107, -27.4714, -55.1448),
(41, 112, -27.474, -55.1004),
(45, 116, -27.4901, -55.114),
(46, 117, -27.4824, -55.0985),
(47, 118, -27.49, -55.1138),
(48, 119, -27.4996, -55.116),
(49, 120, -27.4879, -55.1145),
(50, 121, -27.4835, -55.1112),
(51, 122, -27.4751, -55.0539);

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
(79, 12, 1, 0, 'Dueño directo', 'Una casita', 'Una casitaUna casitaUna casitaUna casitaUna casitaUna casitaUna casita123123123123', 'venta', 200000, 'ARS', 1, 1, 2, 324, 'Sanchez123', '2025-03-24 22:07:08', 0),
(80, 12, 1, 0, 'Dueño directo', 'aaaaaaaaaaaa', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'venta', 123, 'ARS', 1, 1, 1, 1, '1asd3', '2025-03-24 22:24:12', 0),
(81, 12, 1, 0, 'Dueño directo', 'Ejemplooo', 'Mate y facturasMate y facturasMate y facturasMate y facturasMate y facturasMate y facturas', 'alquiler', 989898, 'ARS', 1, 2, 2, 100, 'Avenida Inventorio', '2025-03-27 22:47:27', 0),
(101, 15, 1, 0, 'Dueño directo', 'KLKALSDAKSD', 'qsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasdqsdasdasdasd12312', 'venta', 999999, 'ARS', 2, 3, 1, 42, '1asdas11', '2025-04-27 22:56:08', 0),
(107, 15, 1, 0, 'Dueño directo', 'gggggggggggggg', 'fdgggggggggggggggdfgdfgr', 'venta', 44, 'ARS', 3, 2, 1, 222222000000, 'ertetert', '2025-04-27 23:10:36', 0),
(112, 15, 1, 0, 'Dueño directo', 'qqqqqqqqqqqqqqqqq', 'dsssssssssssssssssssssssssss', 'venta', 123, 'ARS', 3, 3, 3, 33, 'ddd233', '2025-04-27 23:24:13', 0),
(116, 15, 1, 0, 'Inmobiliaria', 'Departamento en Centro de obera', 'Departamento publicado en el centro de obera, manteniendo la estetica y flujo en el cual los estudiantes puedan tener un logro que es encontrar un alquiler disponible para tenerlo siempre', 'alquiler', 150000, 'ARS', 1, 1, 1, 200, 'Av. Italia 323', '2025-05-05 20:55:37', 0),
(117, 13, 1, 0, 'Dueño directo', 'Lindo departamento a la vista de la facultdad', 'Departamento echo para estudiantes y trabajadores', 'alquiler', 130000, 'ARS', 2, 1, 1, 1200, 'Barrio Obera Mar de la Flota', '2025-05-05 21:35:49', 0),
(118, 13, 1, 0, 'Inmobiliaria', 'Casa de Ejemplo', 'Ejemplo de Casa para probar 123123 ¬¬¬+54\r\n\r\n***', 'alquiler', 150000, 'ARS', 1, 1, 1, 50, 'Av. Italia 200', '2025-05-15 16:52:29', 0),
(119, 13, 1, 0, 'Inmobiliaria', 'departamento mono ambiente', 'Especialmente diseñado para estudiantes\r\nNO SE HACEPTAN MASCOTAS\r\n', 'alquiler', 300, 'ARS', 1, 1, 1, 20, 'haiti 1199', '2025-05-17 12:54:37', 0),
(120, 13, 1, 0, 'Dueño directo', 'Departamento para estudiantes o trabajadores', 'Este departamento esta ubicado en el microcentro de Obera, fecha 2025', 'alquiler', 170000, 'ARS', 1, 1, 1, 50, 'Maipu 100', '2025-05-17 15:47:46', 0),
(121, 13, 1, 0, 'Dueño directo', 'aaaaaaaaaaaaaaaaaaaaaa', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'alquiler', 123000, 'ARS', 1, 1, 1, 50, 'aaaaaaaaaaaaaaaaaaaaaaa', '2025-05-17 18:15:29', 0),
(122, 17, 1, 0, 'Inmobiliaria', 'ciriciriciriciriciriciriciri', 'ciriciriciriciriciriciriciri', 'venta', 2000000, 'ARS', 2, 2, 1, 100, 'ciriciriciri', '2025-05-17 18:38:07', 0);

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
(184, 13, 116, '2025-05-13 00:28:06');

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
(97, 79, 'angel2.webp'),
(98, 79, 'gamer123.jpg'),
(99, 79, 'arbol1.jpg'),
(100, 80, 'arbol1.jpg'),
(101, 80, 'gamer123.jpg'),
(102, 81, 'b4656768a9fbae8e3c58dffd0f2e85cc.jpg'),
(103, 81, 'asdas.jpg'),
(123, 101, 'PublicaDepto.png'),
(124, 101, 'DepartamentoHome.webp'),
(126, 107, 'PublicaDepto.png'),
(129, 112, 'PublicaDepto.png'),
(135, 116, 'arbol.jpeg'),
(136, 117, 'arbol.jpeg'),
(137, 117, 'DepartamentoHome.webp'),
(138, 118, 'DepartamentoHome.webp'),
(139, 118, 'arbol.jpeg'),
(140, 119, 'arbol.jpeg'),
(141, 119, 'DepartamentoHome.webp'),
(142, 119, 'PublicaDepto.png'),
(143, 120, '489371184_667085076207472_50246891497294917_n.jpg'),
(144, 120, '489371896_668933249470576_5831833776925473544_n.jpg'),
(145, 121, '489371896_668933249470576_5831833776925473544_n.jpg'),
(146, 121, '489371184_667085076207472_50246891497294917_n.jpg'),
(147, 121, '496063745_3621494658156466_1751569581737620015_n.jpg'),
(148, 122, '496063745_3621494658156466_1751569581737620015_n.jpg'),
(149, 122, '489371184_667085076207472_50246891497294917_n.jpg'),
(150, 122, '489371896_668933249470576_5831833776925473544_n.jpg');

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
(2, 'Apostoles', 'Misiones', 'Argentina');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificacion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `leida` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resena`
--

CREATE TABLE `resena` (
  `id_resena` int(11) NOT NULL,
  `id_usuario_resenado` int(11) NOT NULL,
  `id_usuario_calificador` int(11) NOT NULL,
  `calificacion` int(11) NOT NULL,
  `comentario` varchar(200) NOT NULL,
  `fecha_calificacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
  `telefono` VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `name`, `email`, `password`, `fecha_registro`, `telefono`) VALUES
(11, 'maimora', 'moramaia18@gmail.com', '$2b$12$q3FrPZbXIQZVrNe211DXSOWyn7T/t.5eaHGg74Ok8b3btQG1dDq2C', '2025-02-13 15:33:26', 0),
(12, 'facundo', 'facu-202020@hotmail.com', '$2b$12$biygPUvU6eR/SI3fZiUfcu6ZMDvBHov9vXdTSG6BNFkvgyr9h/4ve', '2025-04-17 19:37:36', 0),
(13, 'maiaa', 'moramaia@gmail.com', '$2b$12$cSH6hwOYj8nGsT0RHHdaQejy1vEXyzYB2q3hr/jeIU.SfhTpQq3.W', '2025-02-22 00:17:57', 0),
(14, 'marta', 'test@teset.com', '$2b$12$ohU2zMHfG89AHFHmeox7Q.5Gf1cDMjPr5u3UFnMosATs8zX.fISOu', '2025-02-21 23:06:26', 0),
(15, 'facu875', 'facu-202020@hotmail.com', '$2b$12$hBO7uykz0TKodKT9HIWY8OB69ZCzFjBxyfmyMKzcpdrEj0ZA6/jNu', '2025-04-24 17:39:01', 0),
(16, 'prueba2', 'prueba2@hotmail.com', '$2b$12$0qBxnF0khlkJg22OXDYGbORmKd5BCAGxSkHz1ILz5g.CzAh58V3KW', '2025-05-05 18:37:05', 0),
(17, 'ciri', 'ciri123@gmail.com', '$2b$12$UNST3Pc6.Wfy2A2g3.h7VutoDDCQNvmE1NQEBUwdyIHqV5ZRSSoga', '2025-05-17 18:34:43', 2147483647),
(18, 'lolita', 'lolita@gmail.com', '$2b$12$tAOO2g8wsK7VfcLb5UR6s.s9X3ufnrTv2pWp.i.6uJ5FBieBZOVo6', '2025-05-17 18:35:38', 2147483647),
(19, 'lala', 'test@teset.com', '$2b$12$7I8PH0/R8Frip3MhehJ2l.vIrvq6exdY1Z7mVxh2DEiJPZ6unxMRm', '2025-05-17 18:39:58', 2147483647);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_rol`
--

CREATE TABLE `usuario_rol` (
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `resena`
--
ALTER TABLE `resena`
  ADD PRIMARY KEY (`id_resena`),
  ADD UNIQUE KEY `id_usuario_resenado` (`id_usuario_resenado`),
  ADD UNIQUE KEY `id_usuario_calificador` (`id_usuario_calificador`),
  ADD KEY `id_usuario_resenado_2` (`id_usuario_resenado`,`id_usuario_calificador`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuario_rol`
--
ALTER TABLE `usuario_rol`
  ADD KEY `id_usuario` (`id_usuario`,`id_rol`);

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
  MODIFY `id_coordenadas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT de la tabla `departamento`
--
ALTER TABLE `departamento`
  MODIFY `id_departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=123;

--
-- AUTO_INCREMENT de la tabla `favorito`
--
ALTER TABLE `favorito`
  MODIFY `id_favorito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=185;

--
-- AUTO_INCREMENT de la tabla `foto`
--
ALTER TABLE `foto`
  MODIFY `id_foto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=151;

--
-- AUTO_INCREMENT de la tabla `localidad`
--
ALTER TABLE `localidad`
  MODIFY `id_localidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `resena`
--
ALTER TABLE `resena`
  MODIFY `id_resena` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

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
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `usuario_rol`
--
ALTER TABLE `usuario_rol`
  ADD CONSTRAINT `usuario_rol_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
