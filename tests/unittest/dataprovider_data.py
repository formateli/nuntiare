# -*- coding: utf-8 -*-
# This file is part of Nuntiare project.
# The COYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Data used in dataprovider.py test"


class City(object):
    def __init__(
            self, city_id, name,
            province, population, is_capital):
        self.id = city_id
        self.name = name
        self.province = province
        self.population = population
        self.is_capital = is_capital


CITIES_OBJ = []
CITIES_OBJ.append(City(1, "Santiago de Veraguas", "Veraguas", 80000, True))
CITIES_OBJ.append(City(2, "Atalaya", "Veraguas", 8916, False))
CITIES_OBJ.append(City(3, "Calobre", "Veraguas", 12184, False))
CITIES_OBJ.append(City(4, "Cañazas", "Veraguas", 15999, False))
CITIES_OBJ.append(City(5, "La Mesa", "Veraguas", 11746, False))
CITIES_OBJ.append(City(6, "Las Palmas", "Veraguas", 17924, False))
CITIES_OBJ.append(City(7, "Montijo", "Veraguas", 12211, False))
CITIES_OBJ.append(City(8, "Rio de Jesús", "Veraguas", 5256, False))
CITIES_OBJ.append(City(9, "Santa Fé", "Veraguas", 12890, False))
CITIES_OBJ.append(City(10, "Las Tablas", "Los Santos", 24298, True))
CITIES_OBJ.append(City(11, "Guararé", "Los Santos", 9485, False))
CITIES_OBJ.append(City(12, "Macaracas", "Los Santos", 9137, False))
CITIES_OBJ.append(City(13, "Pedasí", "Los Santos", 3864, False))
CITIES_OBJ.append(City(14, "Pocrí", "Los Santos", 3397, False))
CITIES_OBJ.append(City(15, "Tonosí", "Los Santos", 9736, False))

CITIES_LIST = []
CITIES_LIST.append((1, "Santiago de Veraguas", "Veraguas", 80000, True))
CITIES_LIST.append((2, "Atalaya", "Veraguas", 8916, False))
CITIES_LIST.append((3, "Calobre", "Veraguas", 12184, False))
CITIES_LIST.append((4, "Cañazas", "Veraguas", 15999, False))
CITIES_LIST.append((5, "La Mesa", "Veraguas", 11746, False))
CITIES_LIST.append((6, "Las Palmas", "Veraguas", 17924, False))
CITIES_LIST.append((7, "Montijo", "Veraguas", 12211, False))
CITIES_LIST.append((8, "Rio de Jesús", "Veraguas", 5256, False))
CITIES_LIST.append((9, "Santa Fé", "Veraguas", 12890, False))
CITIES_LIST.append((10, "Las Tablas", "Los Santos", 24298, True))
CITIES_LIST.append((11, "Guararé", "Los Santos", 9485, False))
CITIES_LIST.append((12, "Macaracas", "Los Santos", 9137, False))
CITIES_LIST.append((13, "Pedasí", "Los Santos", 3864, False))
CITIES_LIST.append((14, "Pocrí", "Los Santos", 3397, False))
CITIES_LIST.append((15, "Tonosí", "Los Santos", 9736, False))
