# coding=utf-8
"""
Esto inicia y ejecuta la Tarea
@version 1.1
"""

# Importar librerías
import matplotlib.pyplot as plt  # grafico
import tqdm
import numpy as np

RUT = 577;

class Corte:
    def __init__(self, dh):
        """"
        Constructor
        :param dh: Tamaño de la Grilla
        """
