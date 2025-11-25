-- Schema para Base de Datos LavaderoAl
-- MySQL Database

DROP DATABASE IF EXISTS lavadero_al;
CREATE DATABASE lavadero_al CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lavadero_al;

-- Tabla de usuarios para autenticación
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'empleado', 'usuario') DEFAULT 'usuario',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    INDEX idx_username (username),
    INDEX idx_estado (estado)
);

-- Tabla de empleados
CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rut VARCHAR(12) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    porcentaje_comision INT DEFAULT 0,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_rut (rut)
);

-- Tabla de convenios
CREATE TABLE convenios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL,
    rut_empresa VARCHAR(12) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(15),
    email VARCHAR(100),
    direccion TEXT,
    tipo_descuento ENUM('porcentaje', 'monto_fijo') DEFAULT 'porcentaje',
    valor_descuento DECIMAL(10, 2) DEFAULT 0,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_rut_empresa (rut_empresa)
);

-- Tabla de vehículos de convenio
CREATE TABLE vehiculos_convenio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_convenio INT NOT NULL,
    patente VARCHAR(10) NOT NULL,
    tipo_vehiculo ENUM('auto', 'camioneta', 'suv', 'furgon') NOT NULL,
    modelo VARCHAR(50),
    color VARCHAR(30),
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_convenio) REFERENCES convenios(id) ON DELETE CASCADE,
    INDEX idx_patente (patente),
    INDEX idx_convenio (id_convenio)
);

-- Tabla de tarifas
CREATE TABLE tarifas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_vehiculo ENUM('auto', 'camioneta', 'suv', 'furgon') NOT NULL,
    tipo_servicio ENUM('lavado_simple', 'lavado_completo', 'encerado', 'lavado_motor', 'pulido', 'descontaminacion') NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_vehiculo_servicio (tipo_vehiculo, tipo_servicio),
    INDEX idx_tipo_vehiculo (tipo_vehiculo),
    INDEX idx_tipo_servicio (tipo_servicio)
);

-- Tabla de servicios
CREATE TABLE servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patente VARCHAR(10) NOT NULL,
    tipo_vehiculo ENUM('auto', 'camioneta', 'suv', 'furgon') NOT NULL,
    tipo_servicio ENUM('lavado_simple', 'lavado_completo', 'encerado', 'lavado_motor', 'pulido', 'descontaminacion') NOT NULL,
    monto_total DECIMAL(10, 2) NOT NULL,
    monto_comision DECIMAL(10, 2) DEFAULT 0,
    id_empleado INT,
    id_convenio INT NULL,
    es_convenio BOOLEAN DEFAULT FALSE,
    descuento DECIMAL(10, 2) DEFAULT 0,
    observaciones TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'completado', 'cancelado') DEFAULT 'completado',
    FOREIGN KEY (id_empleado) REFERENCES empleados(id) ON DELETE SET NULL,
    FOREIGN KEY (id_convenio) REFERENCES convenios(id) ON DELETE SET NULL,
    INDEX idx_patente (patente),
    INDEX idx_fecha (fecha),
    INDEX idx_empleado (id_empleado),
    INDEX idx_convenio (id_convenio)
);

-- Tabla de inventario
CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria ENUM('quimicos', 'ceras', 'herramientas', 'accesorios', 'otros') NOT NULL,
    stock INT DEFAULT 0,
    stock_minimo INT DEFAULT 10,
    precio_unitario DECIMAL(10, 2) DEFAULT 0,
    unidad ENUM('unidad', 'litro', 'kilo', 'caja', 'galon') DEFAULT 'unidad',
    estado_stock ENUM('optimo', 'bajo', 'critico') GENERATED ALWAYS AS (
        CASE
            WHEN stock > stock_minimo * 2 THEN 'optimo'
            WHEN stock > stock_minimo THEN 'bajo'
            ELSE 'critico'
        END
    ) STORED,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_categoria (categoria),
    INDEX idx_estado_stock (estado_stock)
);

-- Tabla de movimientos de inventario
CREATE TABLE movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_insumo INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste') NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(255),
    usuario VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_insumo) REFERENCES inventario(id) ON DELETE CASCADE,
    INDEX idx_insumo (id_insumo),
    INDEX idx_fecha (fecha)
);

-- Tabla de liquidaciones
CREATE TABLE liquidaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    total_servicios INT DEFAULT 0,
    monto_total_servicios DECIMAL(10, 2) DEFAULT 0,
    total_comisiones DECIMAL(10, 2) DEFAULT 0,
    estado ENUM('pendiente', 'pagada', 'cancelada') DEFAULT 'pendiente',
    fecha_pago DATE NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id) ON DELETE CASCADE,
    INDEX idx_empleado (id_empleado),
    INDEX idx_estado (estado),
    INDEX idx_periodo (periodo_inicio, periodo_fin)
);

-- Tabla de detalle de liquidaciones
CREATE TABLE detalle_liquidaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_liquidacion INT NOT NULL,
    id_servicio INT NOT NULL,
    monto_servicio DECIMAL(10, 2) NOT NULL,
    monto_comision DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_liquidacion) REFERENCES liquidaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_servicio) REFERENCES servicios(id) ON DELETE CASCADE,
    INDEX idx_liquidacion (id_liquidacion),
    INDEX idx_servicio (id_servicio)
);

-- Insertar datos de prueba

-- Usuarios
INSERT INTO usuarios (username, password, rol) VALUES
('admin', 'admin123', 'admin'),
('empleado1', 'emp123', 'empleado');

-- Empleados
INSERT INTO empleados (nombre, rut, telefono, email, porcentaje_comision, estado) VALUES
('Juan Pérez', '12345678-9', '+56912345678', 'juan.perez@lavaderoal.cl', 15, 'activo'),
('María González', '98765432-1', '+56998765432', 'maria.gonzalez@lavaderoal.cl', 18, 'activo'),
('Pedro Sánchez', '11223344-5', '+56911223344', 'pedro.sanchez@lavaderoal.cl', 12, 'activo'),
('Ana Martínez', '55667788-9', '+56955667788', 'ana.martinez@lavaderoal.cl', 20, 'inactivo');

-- Tarifas
INSERT INTO tarifas (tipo_vehiculo, tipo_servicio, precio, descripcion) VALUES
-- Autos
('auto', 'lavado_simple', 8000, 'Lavado exterior básico'),
('auto', 'lavado_completo', 15000, 'Lavado exterior e interior completo'),
('auto', 'encerado', 12000, 'Encerado y brillo'),
('auto', 'lavado_motor', 10000, 'Lavado de motor'),
('auto', 'pulido', 25000, 'Pulido profesional'),
('auto', 'descontaminacion', 20000, 'Descontaminación de pintura'),

-- Camionetas
('camioneta', 'lavado_simple', 10000, 'Lavado exterior básico'),
('camioneta', 'lavado_completo', 18000, 'Lavado exterior e interior completo'),
('camioneta', 'encerado', 15000, 'Encerado y brillo'),
('camioneta', 'lavado_motor', 12000, 'Lavado de motor'),
('camioneta', 'pulido', 30000, 'Pulido profesional'),
('camioneta', 'descontaminacion', 25000, 'Descontaminación de pintura'),

-- SUVs
('suv', 'lavado_simple', 12000, 'Lavado exterior básico'),
('suv', 'lavado_completo', 20000, 'Lavado exterior e interior completo'),
('suv', 'encerado', 18000, 'Encerado y brillo'),
('suv', 'lavado_motor', 14000, 'Lavado de motor'),
('suv', 'pulido', 35000, 'Pulido profesional'),
('suv', 'descontaminacion', 30000, 'Descontaminación de pintura'),

-- Furgones
('furgon', 'lavado_simple', 15000, 'Lavado exterior básico'),
('furgon', 'lavado_completo', 25000, 'Lavado exterior e interior completo'),
('furgon', 'encerado', 20000, 'Encerado y brillo'),
('furgon', 'lavado_motor', 16000, 'Lavado de motor'),
('furgon', 'pulido', 40000, 'Pulido profesional'),
('furgon', 'descontaminacion', 35000, 'Descontaminación de pintura');

-- Inventario
INSERT INTO inventario (nombre, categoria, stock, stock_minimo, precio_unitario, unidad) VALUES
('Shampoo Automotriz Premium', 'quimicos', 45, 10, 12500, 'litro'),
('Cera Líquida', 'ceras', 8, 15, 18000, 'litro'),
('Desengrasante Industrial', 'quimicos', 25, 10, 8500, 'litro'),
('Microfibra Premium', 'accesorios', 35, 20, 3500, 'unidad'),
('Cera en Pasta', 'ceras', 5, 10, 22000, 'unidad'),
('Limpia Vidrios', 'quimicos', 18, 15, 4500, 'litro'),
('Pulidor de Metales', 'quimicos', 12, 8, 15000, 'litro'),
('Aspiradora Industrial', 'herramientas', 3, 2, 250000, 'unidad'),
('Hidrolavadora', 'herramientas', 2, 1, 450000, 'unidad'),
('Esponja Premium', 'accesorios', 50, 30, 2500, 'unidad');

-- Convenios
INSERT INTO convenios (nombre_empresa, rut_empresa, contacto, telefono, email, tipo_descuento, valor_descuento, estado, fecha_inicio) VALUES
('Transportes ABC Ltda.', '76543210-K', 'Carlos Silva', '+56922334455', 'contacto@transportesabc.cl', 'porcentaje', 15.00, 'activo', '2025-01-01'),
('Empresa XYZ S.A.', '87654321-5', 'Laura Ramírez', '+56933445566', 'laura@empresaxyz.cl', 'monto_fijo', 2000.00, 'activo', '2025-01-15'),
('Servicios del Sur', '65432109-8', 'Roberto Muñoz', '+56944556677', 'contacto@serviciosdelsur.cl', 'porcentaje', 20.00, 'inactivo', '2024-06-01');

-- Vehículos de convenio
INSERT INTO vehiculos_convenio (id_convenio, patente, tipo_vehiculo, modelo, color) VALUES
(1, 'ABCD12', 'camioneta', 'Toyota Hilux', 'Blanco'),
(1, 'EFGH34', 'camioneta', 'Chevrolet D-Max', 'Gris'),
(1, 'IJKL56', 'furgon', 'Hyundai H100', 'Blanco'),
(2, 'MNOP78', 'auto', 'Suzuki Swift', 'Rojo'),
(2, 'QRST90', 'suv', 'Kia Sportage', 'Negro');

-- Servicios de ejemplo
INSERT INTO servicios (patente, tipo_vehiculo, tipo_servicio, monto_total, monto_comision, id_empleado, fecha, estado) VALUES
('AAAA11', 'auto', 'lavado_completo', 15000, 2250, 1, '2025-11-20 09:30:00', 'completado'),
('BBBB22', 'camioneta', 'lavado_simple', 10000, 1800, 2, '2025-11-20 10:15:00', 'completado'),
('CCCC33', 'suv', 'encerado', 18000, 2160, 1, '2025-11-20 11:00:00', 'completado'),
('DDDD44', 'auto', 'pulido', 25000, 3000, 3, '2025-11-21 09:00:00', 'completado'),
('EEEE55', 'furgon', 'lavado_completo', 25000, 3000, 2, '2025-11-21 14:30:00', 'completado'),
('ABCD12', 'camioneta', 'lavado_simple', 8500, 1275, 1, '2025-11-22 08:00:00', 'completado');

-- Servicios con convenio (aplicando descuento)
UPDATE servicios SET es_convenio = TRUE, id_convenio = 1, descuento = 1275, monto_total = 8500 WHERE id = 6;

-- Movimientos de inventario
INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo, usuario) VALUES
(1, 'entrada', 50, 'Compra inicial', 'admin'),
(2, 'entrada', 20, 'Compra inicial', 'admin'),
(3, 'entrada', 30, 'Compra inicial', 'admin'),
(1, 'salida', 5, 'Uso en servicios', 'empleado1'),
(4, 'entrada', 50, 'Reposición stock', 'admin');

-- Liquidaciones
INSERT INTO liquidaciones (id_empleado, periodo_inicio, periodo_fin, total_servicios, monto_total_servicios, total_comisiones, estado, fecha_pago) VALUES
(1, '2025-11-01', '2025-11-15', 25, 450000, 67500, 'pagada', '2025-11-16'),
(2, '2025-11-01', '2025-11-15', 18, 320000, 57600, 'pagada', '2025-11-16'),
(3, '2025-11-01', '2025-11-15', 12, 180000, 21600, 'pendiente', NULL);

-- Vista para estadísticas rápidas
CREATE VIEW vista_estadisticas_diarias AS
SELECT
    DATE(fecha) as fecha,
    COUNT(*) as total_servicios,
    SUM(monto_total) as ingresos_totales,
    SUM(monto_comision) as total_comisiones,
    COUNT(DISTINCT id_empleado) as empleados_activos
FROM servicios
WHERE estado = 'completado'
GROUP BY DATE(fecha);

-- Vista para inventario con alertas
CREATE VIEW vista_inventario_alertas AS
SELECT
    i.*,
    CASE
        WHEN i.stock <= i.stock_minimo THEN 'URGENTE'
        WHEN i.stock <= i.stock_minimo * 1.5 THEN 'ADVERTENCIA'
        ELSE 'NORMAL'
    END as nivel_alerta
FROM inventario i;

-- Vista para comisiones por empleado
CREATE VIEW vista_comisiones_empleados AS
SELECT
    e.id,
    e.nombre,
    e.rut,
    e.porcentaje_comision,
    COUNT(s.id) as total_servicios,
    COALESCE(SUM(s.monto_total), 0) as total_vendido,
    COALESCE(SUM(s.monto_comision), 0) as total_comisiones
FROM empleados e
LEFT JOIN servicios s ON e.id = s.id_empleado
    AND s.estado = 'completado'
    AND DATE(s.fecha) = CURDATE()
WHERE e.estado = 'activo'
GROUP BY e.id, e.nombre, e.rut, e.porcentaje_comision;

COMMIT;
