-- This file is part of Nuntiare project. 
-- The COPYRIGHT file at the top level of this repository 
-- contains the full copyright notices and license terms.


CREATE TABLE province (
	id integer NOT NULL,
	name varchar(100) NOT NULL, 
	area float NOT NULL, 

	CONSTRAINT pk_province PRIMARY KEY (id)

) WITH (OIDS=FALSE);

INSERT INTO province (id, name, area) VALUES 
   (1, 'Panamá', 11670.92),
   (2, 'Chiriquí', 6490.9),
   (3, 'Colón', 4868.4),
   (4, 'Bocas del Toro', 4643.9),
   (5, 'Los Santos', 3804.6),
   (6, 'Herrara', 2340),
   (7, 'Veraguas', 10677.2),
   (8, 'Darién', 11896.5),
   (9, 'Coclé', 4946.6);


CREATE TABLE city (
	id integer NOT NULL,
	name varchar(100) NOT NULL, 
	province integer NOT NULL,
    population integer NOT NULL,
	is_capital bool NOT NULL,

	CONSTRAINT pk_city PRIMARY KEY (id)

) WITH (OIDS=FALSE);

INSERT INTO city (id, name, province, population, is_capital) VALUES 
    (1, 'Santiago de Veraguas', 7, 80000, TRUE),
    (2, 'Atalaya', 7, 8916, FALSE),
    (3, 'Calobre', 7, 12184, FALSE),
    (4, 'Cañazas', 7, 15999, FALSE),
    (5, 'La Mesa', 7, 11746, FALSE),
    (6, 'Las Palmas', 7, 17924, FALSE),
    (7, 'Montijo', 7, 12211, FALSE),
    (8, 'Rio de Jesús', 7, 5256, FALSE),
    (9, 'Santa Fé', 7, 12890, FALSE),
    (10, 'Las Tablas', 5, 24298, TRUE),
    (11, 'Guararé', 5, 9485, FALSE),
    (12, 'Macaracas', 5, 9137, FALSE),
    (13, 'Pedasí', 5, 3864, FALSE),
    (14, 'Pocrí', 5, 3397, FALSE),
    (15, 'Tonosí', 5, 9736, FALSE);

