# coding=utf-8
"""
Esto inicia y ejecuta la Tarea
@version 1.1
@author Bastián Inostroza
"""

# Importar librerías
import matplotlib.pyplot as plt  # grafico
import tqdm
import numpy as np
import math

# Variable dada según enunciado
RRR = .577

SKY = 0
SEA = 1
MOUNTAIN = 2
SNOWY_MOUNTAIN = 3
FACTORY = 4
TEMP_MOUNTAIN = 20
TEMP_SNOW = 0


def rho(x, y):
    return 1 / (x ** 2 + y ** 2 + 120) ** .5


# Estudiar linea Bresenham
def bresenham_line(matrix, x1, y1, x2, y2, value=0):
    """"
    Tiralinea de Bresenham
      La idea es que lance las lineas para cualquier matriz, por lo que
      debe darsele los valores incluyendo el dh correspondiente, mejor
      dicho, las distancias escaladas. Creado a partir del pseudocodigo
      de Wikipedia
    """
    dy = y2 - y1
    dx = x2 - x1
    x = x1
    y = y1

    # incremento para avance inclinado
    inc_yi = dy / abs(dy)
    dy = abs(dy)
    inc_xi = dx / abs(dx)
    dx = abs(dx)

    # incremento para avance recto
    if dx >= dy:
        inc_yr = 0
        inc_xr = inc_xi
    else:
        inc_yr = inc_yi
        inc_xr = 0
        # dy > dx por lo que se intercambian
        k = dx
        dx = dy
        dy = k

    # inicialización de valores
    av_r = 2 * dy
    av = av_r - dx
    av_i = av - dx

    # trazado de linea
    while x != x2:
        matrix[x][y] = value
        if av >= 0:
            # avance inclinado
            x += inc_xi
            y += inc_yi
            av += av_i
        else:
            # avance recto
            x += inc_xr
            y += inc_yr
            av += av_r


def fill_elements(matrix, alto, ancho, dh):
    """
    Rellena las montañas, solo con fines visuales excepto por
    la creación de montañas nevadas, que sevirá para establecer temperaturas

    :param matrix: matriz en la que dibuja
    :param alto: alto de la matriz
    :param ancho: ancho de la matriz
    :param dh: delta, para calcular distancias
    """
    for x in range(ancho):
        is_mountains = False
        for y in range(alto):
            cell = matrix[y][x]
            if not is_mountains:
                if cell == SKY:
                    break
                if cell == SEA:
                    break
                if cell == FACTORY:
                    break
                if cell == MOUNTAIN:
                    is_mountains = True
                    if y < alto - int(float(1800 / dh)):
                        matrix[y][x] = SNOWY_MOUNTAIN
            else:
                if y < alto - int(float(1800 / dh)):
                    matrix[y][x] = SNOWY_MOUNTAIN
                else:
                    matrix[y][x] = MOUNTAIN


def cb_mar(t):
    t = t % 24
    if 0 <= t < 8:
        return 4
    elif 8 <= t < 16:
        return 4 + 2 * (t - 8)
    elif 16 <= t < 24:
        return 20 - 2 * (24 - t)


def cb_sky(t, y, dh):
    y_metros = y * dh
    return cb_mar(t) - (6 / 1000) * y_metros


def temp_factory(t):
    t = t % 24
    return 450 * (2 + np.cos((np.pi * t) / 12))


def set_omega(n, m):
    return 4 / (2 + (math.sqrt(4 - (math.cos(math.pi / (n - 1)) + math.cos(math.pi / (m - 1))) ** 2)))


class Corte:
    def __init__(self, dh, t, f):
        """"
        Constructor
        :param dh: Tamaño de la Grilla
        """
        self.time = t
        self.function = f

        # Distancias relativas por grilla
        self.dh = dh
        self._h = int(float(self.alto) / self.dh)
        self._w = int(float(self.ancho) / self.dh)

        # Distancias de elementos (metros)
        self.ancho = int(float(4000 / self.dh))
        self.mar = int(float((1200 + 400*RRR) / self.dh))
        self.fin_playa = int(float(400 / self.dh + self.mar))
        self.ancho_fabrica = int(float(120 / self.dh))
        self.centro_fabrica = int(self.mar + (self.ancho_fabrica / 2))
        self.centro_cerro_1 = int(float(1200 / self.dh + self.mar))
        self.centro_depresion = int(float(1500 / self.dh + self.mar))
        self.centro_cerro_2 = int(float(2000 / self.dh + self.mar))

        self.alto = int(float(2000 / self.dh))
        self.alto_playa = int(float(self._h - ((400/3) / self.dh)))
        self.alto_cerro_1 = int(float(self._h - ((1500 + 200 * RRR) / self.dh)))
        self.alto_depresion = int(float(self._h - (1300 + 200 * RRR) / self.dh))
        self.alto_cerro_2 = int(float(self._h - ((1850 + 100 * RRR) / self.dh)))

        self._matrix = np.zeros((self._h, self._w))
        self._elements = np.zeros((self._h, self._w))
        # Se genera terreno y pobla con temperaturas correspondientes para cada cb:
        self.generate_elements()
        fill_elements(self._elements, self.alto, self.ancho, self.dh)
        self.init_temps(self)

    def init_temps(self):
        time = self.time
        for x in range(self.ancho):
            for y in range(self.alto):
                if self._elements[y][x] == SEA:
                    self._matrix[y][x] = cb_mar(time)
                elif self._elements[y][x] == SKY:
                    self._matrix[y][x] = cb_sky(time, y, self.dh)
                elif self._elements[y][x] == FACTORY:
                    self._matrix[y][x] = temp_factory(time)
                elif self._elements[y][x] == MOUNTAIN:
                    self._matrix[y][x] = TEMP_MOUNTAIN
                elif self._elements[y][x] == SNOWY_MOUNTAIN:
                    self._matrix[y][x] = TEMP_SNOW

    def generate_elements(self):
        """
        Esta funcion considera que en numpy las matrices son zeros[y,x] y __no__ que el 0,0
        se encuentra en la esquina superior izquierda.
        """
        # Linea del mar
        bresenham_line(self._elements, self._h-1, 0, self._h-1, self.mar, SEA)
        # Linea de fabrica
        bresenham_line(self._elements, self._h-1, self.mar+1,
                       self._h-1, self.mar + self.ancho_fabrica, FACTORY)
        # Linea de playa
        bresenham_line(self._elements, self._h-1, self.mar+self.ancho_fabrica+1,
                       self.alto_playa, self.fin_playa, MOUNTAIN)
        # Lineas de cerro  despresion intermedia
        bresenham_line(self._elements, self.alto_playa, self.fin_playa+1,
                       self.centro_cerro_1, self.alto_cerro_1, MOUNTAIN)
        bresenham_line(self._elements, self.alto_cerro_1, self.centro_cerro_1+1,
                       self.alto_depresion, self.centro_depresion, MOUNTAIN)
        bresenham_line(self._elements, self.alto_depresion, self.centro_depresion+1,
                       self.alto_cerro_2, self.centro_cerro_2, MOUNTAIN)
        # con la última linea se decide dejarla a 1600 mts sobre el nivel del mar
        bresenham_line(self._elements, self.alto_cerro_2, self.centro_cerro_2,
                       self._h - 1500, self._w - 1, MOUNTAIN)
        fill_elements(self._elements, self._h, self._w, self.dh)

    def reset(self, time, func):
        self.__init__(self.dh, time, func)

    def start(self, omega, f):
        """
        Inicia iteraciones
        :return:
        """
        epsilon = 0.001
        error = 0
        for _ in tqdm.tqdm(range(1000)):
            for x in range(1, self._w):
                for y in range(1, self._h):  # Evitando los bordes de la matriz
                    # Casos borde donde no calcula
                    if self._elements[y][x] == SEA or self._elements[y][x] == FACTORY:
                        continue
                    elif self._elements[y][x] == MOUNTAIN or self._elements[y][x] == SNOWY_MOUNTAIN:
                        continue
                    # Funcion de sobre-relajación sucesiva de las diapos
                    old = self._matrix[y][x]
                    # solo existen condiciones de dirichlet
                    if f != 0:
                        # Poisson equation with f centered on factory
                        self._matrix[y][x] += omega*.25*(self._matrix[y-1][x]+self._matrix[y+1][x]+self._matrix[y][x-1]+self._matrix[y][x+1]-4*self._matrix[y][x]-((self.dh**2)*f(x/self.dh - self.centro_fabrica, y/self.dh)))
                    elif f == 0:
                        # Laplace equation
                        self._matrix[y][x] += omega*.25*(self._matrix[y-1][x]+self._matrix[y+1][x]+self._matrix[y][x-1]+self._matrix[y][x+1]-4*self._matrix[y][x])
                    error = max(error, abs(old - self._matrix[y][x]))
            if error < epsilon:
                print("Proceso detenido por error menor a "+str(epsilon)+", error igual a "+str(error))
                print("en iteración numero "+str(_))
                break


def main():
    # Instancia de Corte
    print("- - - - - - - - - - Estudio de impacto ambiental - - - - - - - - - -")
    print("- - - - - - - - - - - - - Planta Anonima - - - - - - - - - - - - - -")
    print("")
    grilla = input("Tamaño de la grilla en metros:")
    tiempo = input("Hora del día a simular:")
    corte = Corte(grilla, tiempo, 0)

