CREATE DATABASE  [master];
USE master;
GO

IF OBJECT_ID('producto', 'U') IS NOT NULL
    DROP TABLE producto;

IF OBJECT_ID('categoria', 'U') IS NOT NULL
    DROP TABLE categoria;

CREATE TABLE categoria (
    id INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE producto (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_categoria INT,
    CONSTRAINT FK_producto_categoria FOREIGN KEY (id_categoria) REFERENCES categoria(id)
);

INSERT INTO categoria (id, nombre) VALUES
(1, 'Electrónicos'),
(2, 'Ropa'),
(3, 'Hogar'),
(4, 'Deportes'),
(5, 'Libros');

INSERT INTO producto (id, nombre, id_categoria) VALUES
(1, 'Smartphone', 1),
(2, 'Laptop', 1),
(3, 'Camiseta', 2),
(4, 'Pantalón', 2),
(5, 'Lámpara', 3),
(6, 'Sartén', 3),
(7, 'Balón de fútbol', 4),
(8, 'Raqueta de tenis', 4),
(9, 'Novela de ficción', 5),
(10, 'Libro de cocina', 5);

ALTER TABLE producto NOCHECK CONSTRAINT FK_producto_categoria;

INSERT INTO producto (id, nombre, id_categoria) VALUES
(11, 'Producto huérfano 1', 6),
(12, 'Producto huérfano 2', 7),
(13, 'Producto huérfano 3', NULL);

ALTER TABLE producto CHECK CONSTRAINT FK_producto_categoria;

SELECT * FROM categoria;
SELECT * FROM producto;

