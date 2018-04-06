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

RRR = 577

class Corte:
    def __init__(self, dh):
        """"
        Constructor
        :param dh: Tamaño de la Grilla
        """

        # Distancias fijas (metros)
        self.ancho = 4000
        self.alto = 2000
        self.ancho_playa = 400
        self.ancho_fabrica = 120

        # Distancias relativas por grilla
        self.dh = dh
        self._h = int(float(self.ancho) / self.dh)
        self._w = int(float(self.alto) / self.dh)

# Estudiar linea Bresenham
    def bresenham_line(matrix, x1, y1, x2, y2):
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
        av_r = 2*dy
        av = av_r - dx
        av_i = av - dx

        # trazado de linea
        while x != x2:
            matrix[x][y] = 1
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

        # Calculo donde está la linea de la montaña,
        # luego desde allí hacia abajo declarar los valores fijos de la montaña
        # y sus contornos

