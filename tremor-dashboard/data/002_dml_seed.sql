-- ============================================================
-- DML — Datos de ejemplo desde gastos.duckdb
-- ============================================================
-- Ejecutar DESPUÉS de 001_ddl.sql

BEGIN;

-- -----------------------------------------------------------
-- USUARIO por defecto
-- -----------------------------------------------------------
INSERT INTO users (username, password_hash)
VALUES ('pablo', 'scrypt:32768:8:1$GeDnshsHnqHEdv2i$8f96789c4d2763c154b5ea66d869efa5c820fa99b765b49530ed340ff86e871f93e0954fd33e0336398c61a77a97bde785b954116ed916a94a6abda8249e33df')
ON CONFLICT (username) DO NOTHING;

-- -----------------------------------------------------------
-- SUPERMERCADOS
-- -----------------------------------------------------------
INSERT INTO supermarkets (nombre, direccion, coordenadas) VALUES
  ('Mercadona Mutxamel', '', '')
ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------
-- TICKETS
-- -----------------------------------------------------------
INSERT INTO tickets (ticket_hash, supermercado, fecha, hora, total_gasto, user_id, supermarket_id) VALUES
  ('beaa23a2', 'Mercadona Mutxamel', '2026-06-03', '18:40', 84.98, 1, 1),
  ('70a15460', 'Mercadona Mutxamel', '2026-05-19', '16:06', 52.73, 1, 1),
  ('4b981804', 'Mercadona Mutxamel', '2026-05-18', '20:14', 17.95, 1, 1),
  ('597e5d3f', 'Mercadona Mutxamel', '2026-05-16', '13:51', 18.62, 1, 1);

-- -----------------------------------------------------------
-- LÍNEAS DE TICKET
-- -----------------------------------------------------------
INSERT INTO lineas_ticket (ticket_hash, nombre_original, nombre_normalizado, cantidad, precio_unitario, precio_total, categoria, subcategoria) VALUES

-- Ticket beaa23a2 (2026-06-03, 84.98)
('beaa23a2', NULL, '6 Huevos camperos',               1.0,   2.10,  2.10, 'Lácteos y Huevos',           'Huevos'),
('beaa23a2', NULL, 'Aceite de oliva virgen extra',     1.0,   4.95,  4.95, 'Despensa y Ultramarinos',    'Aceite'),
('beaa23a2', NULL, 'Aceitunas rellenas de pimiento',   1.0,   1.75,  1.75, 'Despensa y Ultramarinos',    'Aceitunas'),
('beaa23a2', NULL, 'Agua con gas',                     1.0,   1.00,  1.00, 'Bebidas',                    'Agua'),
('beaa23a2', NULL, 'Agua mineral Blue II Slalom 6',   1.0,   3.00,  3.00, 'Bebidas',                    'Agua'),
('beaa23a2', NULL, 'Agua mineral Neval 8L',            2.0,   0.95,  1.90, 'Bebidas',                    'Agua'),
('beaa23a2', NULL, 'Aguacate en bandeja',              1.0,   3.19,  3.19, 'Frutas y Verduras',          'Frutas'),
('beaa23a2', NULL, 'Atún claro al natural',            1.0,   4.20,  4.20, 'Despensa y Ultramarinos',    'Conservas'),
('beaa23a2', NULL, 'Banana',                           0.962, 1.16,  1.12, 'Frutas y Verduras',          'Frutas'),
('beaa23a2', NULL, 'Banderilla Gilda',                 1.0,   2.30,  2.30, 'Despensa y Ultramarinos',    'Aperitivos'),
('beaa23a2', NULL, 'Bebida de avena con calcio',       1.0,   1.20,  1.20, 'Bebidas',                    'Bebida vegetal'),
('beaa23a2', NULL, 'Bebida de coco',                   1.0,   1.60,  1.60, 'Bebidas',                    'Bebida vegetal'),
('beaa23a2', NULL, 'Brócoli',                          0.372, 2.60,  0.97, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Bífidus cremoso de coco',          1.0,   1.30,  1.30, 'Lácteos y Huevos',           'Yogures'),
('beaa23a2', NULL, 'Cebolla tierna',                   1.0,   1.25,  1.25, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Croquetas de cocido',              1.0,   1.95,  1.95, 'Despensa y Ultramarinos',    'Platos preparados'),
('beaa23a2', NULL, 'Cuajada',                          1.0,   1.20,  1.20, 'Lácteos y Huevos',           'Postre lácteo'),
('beaa23a2', NULL, 'Espinacas',                        1.0,   1.30,  1.30, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Espárrago verde fino',             1.0,   2.45,  2.45, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Filete de salmón salvaje',         1.0,   3.59,  3.59, 'Pescadería',                 'Salmón'),
('beaa23a2', NULL, 'Fresón',                           1.0,   2.29,  2.29, 'Frutas y Verduras',          'Frutas'),
('beaa23a2', NULL, 'Gazpacho tradicional',             1.0,   1.60,  1.60, 'Despensa y Ultramarinos',    'Platos preparados'),
('beaa23a2', NULL, 'Jamón serrano sin aditivos',       1.0,   2.30,  2.30, 'Carnicería y Aves',          'Embutidos'),
('beaa23a2', NULL, 'Leche desnatada',                  1.0,   0.82,  0.82, 'Lácteos y Huevos',           'Leche'),
('beaa23a2', NULL, 'Lenteja cocida',                   1.0,   0.90,  0.90, 'Despensa y Ultramarinos',    'Legumbres cocidas'),
('beaa23a2', NULL, 'Melocotón',                        0.626, 4.90,  3.07, 'Frutas y Verduras',          'Frutas'),
('beaa23a2', NULL, 'Mozzarella fresca',                1.0,   0.90,  0.90, 'Lácteos y Huevos',           'Queso'),
('beaa23a2', NULL, 'Pan de pueblo',                    1.0,   1.60,  1.60, 'Panadería y Pastelería',     'Pan'),
('beaa23a2', NULL, 'Patata',                           1.062, 1.90,  2.02, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Piadina',                          1.0,   2.20,  2.20, 'Panadería y Pastelería',     'Pan'),
('beaa23a2', NULL, 'Picatostes con ajo',               1.0,   0.80,  0.80, 'Despensa y Ultramarinos',    'Pan tostado'),
('beaa23a2', NULL, 'Queso rallado para pizza',         1.0,   1.60,  1.60, 'Lácteos y Huevos',           'Queso'),
('beaa23a2', NULL, 'Salmorejo',                        1.0,   2.20,  2.20, 'Despensa y Ultramarinos',    'Platos preparados'),
('beaa23a2', NULL, 'Sepia',                            0.224, 15.95, 3.57, 'Pescadería',                 'Marisco'),
('beaa23a2', NULL, 'Ternera extratierna',              1.0,   8.14,  8.14, 'Carnicería y Aves',          'Ternera'),
('beaa23a2', NULL, 'Tomate cherry pera negro',         1.0,   1.70,  1.70, 'Frutas y Verduras',          'Verduras'),
('beaa23a2', NULL, 'Tomate receta artesana',           1.0,   1.40,  1.40, 'Despensa y Ultramarinos',    'Salsas y condimentos'),
('beaa23a2', NULL, 'Topping',                          1.0,   1.85,  1.85, 'Despensa y Ultramarinos',    'Salsas y condimentos'),
('beaa23a2', NULL, 'Té Matcha',                        1.0,   2.90,  2.90, 'Bebidas',                    'Té'),
('beaa23a2', NULL, 'Zanahoria 500g',                   1.0,   0.80,  0.80, 'Frutas y Verduras',          'Verduras'),

-- Ticket 70a15460 (2026-05-19, 52.73)
('70a15460', NULL, 'Albaricoque',                      1.0,   2.58,  2.58, 'Frutas y Verduras',          'Frutas'),
('70a15460', NULL, 'Barrita de cacahuete',             1.0,   3.30,  3.30, 'Despensa y Ultramarinos',    'Snacks'),
('70a15460', NULL, 'Bebida de coco',                   1.0,   1.60,  1.60, 'Bebidas',                    'Bebidas vegetales'),
('70a15460', NULL, 'Bolsa de rafia',                   1.0,   0.65,  0.65, 'Otros',                      'Bolsas'),
('70a15460', NULL, 'Bífidus 0% pera',                  1.0,   1.30,  1.30, 'Lácteos y Huevos',           'Yogures'),
('70a15460', NULL, 'Cachopo de ternera sin gluten',    1.0,   5.50,  5.50, 'Carnicería y Aves',          'Ternera'),
('70a15460', NULL, 'Calabaza en trozos',               1.0,   2.07,  2.07, 'Frutas y Verduras',          'Verduras'),
('70a15460', NULL, 'Cebolla tierna',                   1.0,   1.25,  1.25, 'Frutas y Verduras',          'Verduras'),
('70a15460', NULL, 'Chapata cristal 4 unidades',       1.0,   1.30,  1.30, 'Panadería y Pastelería',     'Pan'),
('70a15460', NULL, 'Espinaca baby',                    1.0,   1.15,  1.15, 'Frutas y Verduras',          'Verduras'),
('70a15460', NULL, 'Filete de salmón salvaje',         1.0,   3.44,  3.44, 'Pescadería',                 'Pescado fresco'),
('70a15460', NULL, 'Frambuesa',                        1.0,   2.95,  2.95, 'Frutas y Verduras',          'Frutas'),
('70a15460', NULL, 'Helado stracciatella',             1.0,   3.25,  3.25, 'Despensa y Ultramarinos',    'Helados'),
('70a15460', NULL, 'Mix de frutos rojos',              1.0,   1.90,  1.90, 'Frutas y Verduras',          'Frutas'),
('70a15460', NULL, 'Morcilla de cebolla fresca',       1.0,   1.93,  1.93, 'Carnicería y Aves',          'Embutidos'),
('70a15460', NULL, 'Muesli con chocolate',             1.0,   2.35,  2.35, 'Despensa y Ultramarinos',    'Cereales'),
('70a15460', NULL, 'Queso tierno cortado',             1.0,   3.71,  3.71, 'Lácteos y Huevos',           'Queso'),
('70a15460', NULL, 'Rulo de cabra',                    1.0,   2.65,  2.65, 'Lácteos y Huevos',           'Queso'),
('70a15460', NULL, 'Salmón ahumado',                   1.0,   3.85,  3.85, 'Pescadería',                 'Pescado ahumado'),
('70a15460', NULL, 'Sardinillas en escabeche',         1.0,   1.95,  1.95, 'Despensa y Ultramarinos',    'Conservas de pescado'),
('70a15460', NULL, 'Tomate cherry pera negro',         1.0,   1.80,  1.80, 'Frutas y Verduras',          'Verduras'),
('70a15460', NULL, 'Yogur griego natural pack 6',      1.0,   1.45,  1.45, 'Lácteos y Huevos',           'Yogures'),
('70a15460', NULL, 'Zanahoria 500g',                   1.0,   0.80,  0.80, 'Frutas y Verduras',          'Verduras'),

-- Ticket 4b981804 (2026-05-18, 17.95)
('4b981804', NULL, 'Chapata cristal 4 unidades',       1.0,   1.30,  1.30, 'Panadería y Pastelería',     'Pan'),
('4b981804', NULL, 'Guacamole 200g',                   1.0,   1.80,  1.80, 'Frutas y Verduras',          'Salsas y cremas vegetales'),
('4b981804', NULL, 'Hamburguesa de cordero al romero', 1.0,   3.50,  3.50, 'Carnicería y Aves',          'Cordero'),
('4b981804', NULL, 'Hummus de pimiento',               1.0,   1.45,  1.45, 'Despensa y Ultramarinos',    'Cremas y patés vegetales'),
('4b981804', NULL, 'Jamón serrano sin aditivos',       1.0,   2.30,  2.30, 'Carnicería y Aves',          'Embutidos'),
('4b981804', NULL, 'Nachos',                           1.0,   0.90,  0.90, 'Despensa y Ultramarinos',    'Snacks'),
('4b981804', NULL, 'Pañuelos de loción',               1.0,   1.60,  1.60, 'Cuidado Personal y Perfumería', 'Pañuelos'),
('4b981804', NULL, 'Snack de pipas',                   1.0,   1.32,  1.32, 'Despensa y Ultramarinos',    'Snacks'),
('4b981804', NULL, 'Tomate rosa',                      0.454, 2.60,  1.18, 'Frutas y Verduras',          'Verduras'),
('4b981804', NULL, 'Tortilla de patatas con cebolla',  1.0,   2.60,  2.60, 'Despensa y Ultramarinos',    'Platos preparados'),

-- Ticket 597e5d3f (2026-05-16, 18.62)
('597e5d3f', NULL, '6 Huevos camperos',                1.0,   2.10,  2.10, 'Lácteos y Huevos',           'Huevos'),
('597e5d3f', NULL, 'Allioli tarrina',                  1.0,   1.10,  1.10, 'Despensa y Ultramarinos',    'Salsas'),
('597e5d3f', NULL, 'Baguette',                         2.0,   0.57,  1.14, 'Panadería y Pastelería',     'Pan'),
('597e5d3f', NULL, 'Bebida de avellanas',              1.0,   1.25,  1.25, 'Bebidas',                    'Bebidas vegetales'),
('597e5d3f', NULL, 'Fartons',                          1.0,   2.25,  2.25, 'Panadería y Pastelería',     'Bollería'),
('597e5d3f', NULL, 'Fresón 1 kg',                      1.0,   2.66,  2.66, 'Frutas y Verduras',          'Frutas'),
('597e5d3f', NULL, 'Horchata fresca',                  1.0,   2.25,  2.25, 'Bebidas',                    'Bebidas refrescantes'),
('597e5d3f', NULL, 'Leche desnatada',                  1.0,   0.82,  0.82, 'Lácteos y Huevos',           'Leche'),
('597e5d3f', NULL, 'Mantequilla pasteurizada sin sal', 1.0,   2.10,  2.10, 'Lácteos y Huevos',           'Mantequilla'),
('597e5d3f', NULL, 'Mayonesa 500ml',                   1.0,   1.30,  1.30, 'Despensa y Ultramarinos',    'Salsas'),
('597e5d3f', NULL, 'Pan de espelta integral',          1.0,   1.65,  1.65, 'Panadería y Pastelería',     'Pan');

COMMIT;
