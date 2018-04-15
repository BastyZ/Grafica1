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

# Variable dada según enunciado
RRR = .577

SEA = 0
SKY = 1
MOUNTAIN = 2
SNOWY_MOUNTAIN = 3
FACTORY = 4


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


class Corte:
    def __init__(self, dh):
        """"
        Constructor
        :param dh: Tamaño de la Grilla
        """
        # Distancias relativas por grilla
        self.dh = dh
        self._h = int(float(self.alto) / self.dh)
        self._w = int(float(self.ancho) / self.dh)

        # Distancias de elementos (metros)
        self.ancho = int(float( 4000 / self.dh ))
        self.mar = int(float((1200 + 400*RRR) / self.dh))
        self.fin_playa = int(float(400 / self.dh + self.mar ))
        self.ancho_fabrica = int(float(120 / self.dh))
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
        # En elements se agregaran los elementos del terreno según:

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
                       self._h - 1500)


    def reset(self):
        self.__init__(self.dh)

        # Calculo donde está la linea de la montaña,
        # luego desde allí hacia abajo declarar los valores fijos de la montaña
        # y sus contornos. La idea es:
        #   0. Crear la skybox (bordes de cielo)
        #   1. Crear la linea de mar, fabrica y playa
        #   2. Crear las lineas de montaña
        #   3. Rellenar las montañas
        #   4. Restarle al skybox la montaña
        #   5. Asignar las temperaturas inicales

