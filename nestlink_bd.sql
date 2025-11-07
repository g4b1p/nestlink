-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-11-2025 a las 21:38:00
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
-- Base de datos: `nestlink_bd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `campanas`
--

CREATE TABLE `campanas` (
  `id_campana` int(11) NOT NULL,
  `nombre_campana` varchar(100) NOT NULL,
  `objetivo` text DEFAULT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `resultados` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `candidatos`
--

CREATE TABLE `candidatos` (
  `id_candidato` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `etapa_proceso` varchar(50) NOT NULL,
  `fecha_postulacion` date DEFAULT NULL,
  `cv_path` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `candidatos`
--

INSERT INTO `candidatos` (`id_candidato`, `nombre`, `email`, `etapa_proceso`, `fecha_postulacion`, `cv_path`) VALUES
(1, 'Ana García', 'ana.garcia@email.com', 'Entrevista agendada', '2025-10-01', 'cv_1.pdf'),
(2, 'Juan Pérez', 'juan.perez@email.com', 'En revisión', '2025-10-02', 'cv_2.pdf'),
(3, 'María López', 'maria.lopez@email.com', 'Contratado', '2025-10-03', 'cv_3.pdf'),
(4, 'Carlos Rodríguez', 'carlos.rodriguez@email.com', 'Descartado', '2025-10-04', 'cv_4.png'),
(5, 'Laura Martínez', 'laura.martinez@email.com', 'Recibido', '2025-10-05', 'cv_5.pdf'),
(6, 'David Sánchez', 'david.sanchez@email.com', 'En proceso de selección', '2025-10-06', 'cv_6.pdf'),
(7, 'Elena Gómez', 'elena.gomez@email.com', 'Entrevista agendada', '2025-10-07', 'cv_7.pdf'),
(8, 'Fernando Díaz', 'fernando.diaz@email.com', 'Descartado', '2025-10-08', 'cv_8.pdf'),
(9, 'Sofía Hernández', 'sofia.hernandez@email.com', 'Contratado', '2025-10-09', 'cv_9.pdf'),
(10, 'Javier Torres', 'javier.torres@email.com', 'Descartado', '2025-10-10', 'cv_10.pdf'),
(11, 'Paula Ruiz', 'paula.ruiz@email.com', 'Recibido', '2025-10-11', 'cv_1.pdf'),
(12, 'Ricardo Castro', 'ricardo.castro@email.com', 'En proceso de selección', '2025-10-12', 'cv_2.pdf'),
(13, 'Lucía Morales', 'lucia.morales@email.com', 'Entrevista agendada', '2025-10-13', 'cv_3.pdf'),
(14, 'Miguel Jiménez', 'miguel.jimenez@email.com', 'En revisión', '2025-10-14', 'cv_4.pdf'),
(15, 'Adriana Reyes', 'adriana.reyes@email.com', 'Contratado', '2025-10-15', 'cv_5.pdf'),
(16, 'Roberto Silva', 'roberto.silva@email.com', 'Descartado', '2025-10-16', 'cv_6.pdf'),
(17, 'Valeria Vidal', 'valeria.vidal@email.com', 'Recibido', '2025-10-17', 'cv_7.pdf'),
(18, 'Andrés Soto', 'andres.soto@email.com', 'En proceso de selección', '2025-10-18', 'cv_8.pdf'),
(19, 'Natalia Bravo', 'natalia.bravo@email.com', 'Entrevista agendada', '2025-10-19', 'cv_9.pdf'),
(20, 'Esteban Peña', 'esteban.pena@email.com', 'En revisión', '2025-10-20', 'cv_10.pdf'),
(21, 'Gabriela Plata', 'gabi.plata@gmail,com', 'Recibido', '2025-10-13', '20251013011759_CV-Gabriela-Plata.pdf'),
(22, 'Nairel Ortega', 'nai.ortega@gmail.com', 'Recibido', '2025-10-14', '20251014140044_cv_nai.png'),
(23, 'Matias', 'porteromatias@gmail.com', 'Recibido', '2025-10-14', '20251014140939_cv_nai.png');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `capacitaciones`
--

CREATE TABLE `capacitaciones` (
  `id_capacitacion` int(11) NOT NULL,
  `nombre_curso` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `capacitaciones`
--

INSERT INTO `capacitaciones` (`id_capacitacion`, `nombre_curso`) VALUES
(1, 'Liderazgo Ágil'),
(2, 'Python Avanzado'),
(3, 'Gestión de Proyectos con Scrum'),
(4, 'Excel Avanzado para Negocios'),
(5, 'Comunicación Efectiva Interpersonal'),
(6, 'Ciberseguridad Básica Empresarial'),
(7, 'Toma de Decisiones Estratégicas');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `nombre`) VALUES
(1, 'Cliente Mayorista A'),
(2, 'Cliente Mayorista B'),
(3, 'Cliente Mayorista C'),
(4, 'Cliente Mayorista D');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `sector` varchar(50) NOT NULL,
  `historial_formacion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleado`, `nombre`, `sector`, `historial_formacion`) VALUES
(1, 'Lucas', 'rrhh', 'Nombre de Capacitación: Gestión de Rendimiento\nFecha de finalización: 2024-11-01'),
(2, 'Rosa', 'ventas', 'Nombre de Capacitación: Estrategias de Fidelización\nFecha de finalización: 2024-10-15'),
(3, 'Juan', 'marketing', 'Nombre de Capacitación: Análisis de ROI\nFecha de finalización: 2024-09-20'),
(4, 'Maria', 'logistica', 'Nombre de Capacitación: Optimización de Rutas\nFecha de finalización: 2024-08-10'),
(5, 'Carlos', 'produccion', 'Nombre de Capacitación: Metodología 5S\nFecha de finalización: 2024-07-05'),
(6, 'María López', 'ventas', '-'),
(7, 'Sofía Hernández', 'rrhh', '-'),
(8, 'Adriana Reyes', 'produccion', '-'),
(9, 'Andrea Fernández', 'marketing', '-'),
(10, 'Jorge Guzmán', 'ventas', '-'),
(11, 'Tamara Núñez', 'rrhh', '-'),
(12, 'Oscar Ríos', 'produccion', '-'),
(13, 'Sara Morales', 'logistica', '-'),
(14, 'Pablo Alarcón', 'marketing', '-'),
(15, 'Verónica Díaz', 'ventas', '-'),
(16, 'Mauricio Castro', 'rrhh', '-'),
(17, 'Elisa Herrera', 'produccion', '-'),
(18, 'Matías Soto', 'logistica', '-');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleado_capacitacion`
--

CREATE TABLE `empleado_capacitacion` (
  `id_empleado_capacitacion` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `id_capacitacion` int(11) NOT NULL,
  `fecha_finalizacion` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleado_capacitacion`
--

INSERT INTO `empleado_capacitacion` (`id_empleado_capacitacion`, `id_empleado`, `id_capacitacion`, `fecha_finalizacion`) VALUES
(1, 1, 1, '2025-09-15'),
(2, 2, 1, '2025-03-10'),
(3, 3, 2, '2025-05-14'),
(4, 6, 1, '2025-11-01'),
(5, 6, 2, '2025-11-01'),
(6, 7, 3, '2025-11-01'),
(7, 7, 5, '2025-11-01'),
(8, 8, 4, '2025-11-01'),
(9, 8, 1, '2025-11-01'),
(10, 9, 3, '2025-11-15'),
(11, 9, 5, '2025-11-15'),
(12, 10, 2, '2025-11-15'),
(13, 11, 1, '2025-11-15'),
(14, 12, 4, '2025-11-15'),
(15, 13, 1, '2025-11-15'),
(16, 13, 3, '2025-11-15'),
(17, 14, 2, '2025-11-15'),
(18, 15, 5, '2025-11-15'),
(19, 16, 4, '2025-11-15'),
(20, 17, 1, '2025-11-15'),
(21, 17, 2, '2025-11-15'),
(22, 18, 5, '2025-11-15');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientoslogisticos`
--

CREATE TABLE `movimientoslogisticos` (
  `id_movimiento` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `tipo_movimiento` varchar(20) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `fecha_movimiento` datetime NOT NULL,
  `origen_destino` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `precio_unitario` decimal(10,0) NOT NULL,
  `stock` int(11) NOT NULL,
  `categoria` varchar(50) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `lote` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre`, `precio_unitario`, `stock`, `categoria`, `estado`, `lote`) VALUES
(1, 'Café Nescafé Clásico', 9, 300, 'Bebidas', 'Listo para distribución', 'L-LC001'),
(2, 'Leche Condensada La Lechera', 4, 150, 'Lácteos', 'En revisión de calidad', 'L-NC002'),
(3, 'Chocolate KitKat 4 dedos', 2, 450, 'Chocolates', 'En embalaje', 'L-KK003'),
(4, 'Agua Mineral Pureza Vital 1L', 2, 4980, 'Bebidas', 'Listo para distribución', 'L-PV004'),
(5, 'Cereal Fitness Original', 6, 210, 'Alimentos', 'En revisión de calidad', 'L-FO005'),
(6, 'Leche en Polvo Nido Entera', 12, 90, 'Lácteos', 'En embalaje', 'L-NE006'),
(7, 'Cubos Caldo Maggi Gallina', 4, 320, 'Alimentos', 'Listo para distribución', 'L-MG007'),
(8, 'Chocolate Crunch Barra', 3, 180, 'Chocolates', 'En revisión de calidad', 'L-CB008'),
(9, 'Fórmula Infantil Nan Optipro 1', 26, 65, 'Lácteos', 'En embalaje', 'L-NO009'),
(10, 'Café Dolce Gusto Lungo Cápsulas', 8, 140, 'Bebidas', 'Listo para distribución', 'L-DL010'),
(11, 'Sopa de Pollo Maggi Instantánea', 2, 160, 'Alimentos', 'En revisión de calidad', 'L-SP011'),
(12, 'Helado Savory Dinos (Unidad)', 2, 75, 'Chocolates', 'En embalaje', 'L-SD012'),
(13, 'Chocolate Blanco Galak', 3, 100, 'Chocolates', 'Listo para distribución', 'L-GB013'),
(14, 'Té Lipton Amarillo (Caja)', 5, 280, 'Bebidas', 'En revisión de calidad', 'L-TL014'),
(15, 'Cereal Chocapic', 6, 240, 'Alimentos', 'En embalaje', 'L-CP015'),
(16, 'Puré de Papas Maggi Instantáneo', 3, 100, 'Alimentos', 'Listo para distribución', 'L-PP016'),
(17, 'Chocolate Trencito', 2, 220, 'Chocolates', 'En revisión de calidad', 'L-TT017'),
(18, 'Barra de Cereal Nesquik', 2, 310, 'Alimentos', 'En embalaje', 'L-NQ018'),
(19, 'Yogur Griego Svelty Durazno', 4, 190, 'Lácteos', 'Listo para distribución', 'L-YG019'),
(20, 'Cereal Zucaritas', 6, 200, 'Alimentos', 'En revisión de calidad', 'L-ZU020');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `sector` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre_usuario`, `contrasena_hash`, `sector`) VALUES
(1, 'Lucas', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'rrhh'),
(2, 'Rosa', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'ventas'),
(3, 'Juan', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'marketing'),
(4, 'Maria', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'logistica'),
(5, 'Carlos', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'produccion'),
(6, 'marial', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'ventas'),
(7, 'sofiah', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'rrhh'),
(8, 'adrianar', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'produccion'),
(9, 'usuario_andrea', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'marketing'),
(10, 'usuario_jorge', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'ventas'),
(11, 'usuario_tamara', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'rrhh'),
(12, 'usuario_oscar', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'produccion'),
(13, 'usuario_sara', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'logistica'),
(14, 'usuario_pablo_a', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'marketing'),
(15, 'usuario_veronica', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'ventas'),
(16, 'usuario_mauricio', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'rrhh'),
(17, 'usuario_elisa', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'produccion'),
(18, 'usuario_matias', '$2b$12$iYNwIP/087KUgTl58OG8U.V3elK5qTr44120SWzDcZff2B9ahnTlG', 'logistica');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `id_cliente` int(11) NOT NULL,
  `id_usuario_vendedor` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `fecha_venta` datetime NOT NULL,
  `monto_total` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id_venta`, `id_producto`, `categoria`, `id_cliente`, `id_usuario_vendedor`, `cantidad`, `fecha_venta`, `monto_total`) VALUES
(21, 1, 'Bebidas', 1, 2, 5, '2025-09-01 00:00:00', 45.00),
(22, 3, 'Chocolates', 2, 2, 10, '2025-09-01 00:00:00', 20.00),
(23, 5, 'Alimentos', 3, 3, 2, '2025-09-02 00:00:00', 12.00),
(24, 8, 'Chocolates', 4, 4, 15, '2025-09-02 00:00:00', 45.00),
(25, 2, 'Lácteos', 1, 5, 1, '2025-09-03 00:00:00', 4.00),
(26, 4, 'Bebidas', 2, 2, 8, '2025-09-03 00:00:00', 16.00),
(27, 6, 'Lácteos', 3, 2, 3, '2025-09-04 00:00:00', 36.00),
(28, 9, 'Lácteos', 4, 3, 20, '2025-09-04 00:00:00', 520.00),
(29, 10, 'Bebidas', 1, 4, 5, '2025-09-05 00:00:00', 40.00),
(30, 7, 'Alimentos', 2, 5, 7, '2025-09-05 00:00:00', 28.00),
(31, 1, 'Bebidas', 3, 2, 4, '2025-09-06 00:00:00', 36.00),
(32, 3, 'Chocolates', 4, 2, 6, '2025-09-06 00:00:00', 12.00),
(33, 5, 'Alimentos', 1, 3, 12, '2025-09-07 00:00:00', 72.00),
(34, 8, 'Chocolates', 2, 4, 3, '2025-09-07 00:00:00', 9.00),
(35, 2, 'Lácteos', 3, 5, 2, '2025-09-08 00:00:00', 8.00),
(36, 4, 'Bebidas', 4, 2, 9, '2025-09-08 00:00:00', 18.00),
(37, 6, 'Lácteos', 1, 2, 1, '2025-09-09 00:00:00', 12.00),
(38, 9, 'Lácteos', 2, 3, 11, '2025-09-09 00:00:00', 286.00),
(39, 10, 'Bebidas', 3, 4, 4, '2025-09-10 00:00:00', 32.00),
(40, 7, 'Alimentos', 4, 5, 15, '2025-09-10 00:00:00', 60.00),
(42, 4, 'Bebidas', 1, 2, 10, '2025-11-06 13:23:01', 23.20),
(43, 4, 'Bebidas', 3, 2, 10, '2025-11-06 13:29:55', 23.20),
(44, 13, 'Chocolates', 1, 1, 20, '2025-11-07 17:14:13', 69.60),
(45, 7, 'Alimentos', 1, 1, 10, '2025-11-07 17:28:16', 46.40),
(46, 7, 'Alimentos', 2, 6, 20, '2025-11-07 17:35:07', 92.80);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `campanas`
--
ALTER TABLE `campanas`
  ADD PRIMARY KEY (`id_campana`);

--
-- Indices de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  ADD PRIMARY KEY (`id_candidato`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `capacitaciones`
--
ALTER TABLE `capacitaciones`
  ADD PRIMARY KEY (`id_capacitacion`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleado`);

--
-- Indices de la tabla `empleado_capacitacion`
--
ALTER TABLE `empleado_capacitacion`
  ADD PRIMARY KEY (`id_empleado_capacitacion`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_capacitacion` (`id_capacitacion`);

--
-- Indices de la tabla `movimientoslogisticos`
--
ALTER TABLE `movimientoslogisticos`
  ADD PRIMARY KEY (`id_movimiento`),
  ADD KEY `fk_movimiento_producto` (`id_producto`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`),
  ADD KEY `fk_venta_cliente` (`id_cliente`),
  ADD KEY `fk_venta_vendedor` (`id_usuario_vendedor`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `campanas`
--
ALTER TABLE `campanas`
  MODIFY `id_campana` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  MODIFY `id_candidato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `capacitaciones`
--
ALTER TABLE `capacitaciones`
  MODIFY `id_capacitacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `empleado_capacitacion`
--
ALTER TABLE `empleado_capacitacion`
  MODIFY `id_empleado_capacitacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT de la tabla `movimientoslogisticos`
--
ALTER TABLE `movimientoslogisticos`
  MODIFY `id_movimiento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD CONSTRAINT `fk_empleado_usuario` FOREIGN KEY (`id_empleado`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `empleado_capacitacion`
--
ALTER TABLE `empleado_capacitacion`
  ADD CONSTRAINT `empleado_capacitacion_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `empleado_capacitacion_ibfk_2` FOREIGN KEY (`id_capacitacion`) REFERENCES `capacitaciones` (`id_capacitacion`);

--
-- Filtros para la tabla `movimientoslogisticos`
--
ALTER TABLE `movimientoslogisticos`
  ADD CONSTRAINT `fk_movimiento_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `fk_venta_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_venta_vendedor` FOREIGN KEY (`id_usuario_vendedor`) REFERENCES `empleados` (`id_empleado`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
