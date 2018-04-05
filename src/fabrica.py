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


        # Calculo donde está la linea de la montaña,
        # luego desde allí hacia abajo declarar los valores fijos de la montaña
        # y sus contornos