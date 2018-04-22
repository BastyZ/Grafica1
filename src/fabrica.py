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
from matplotlib.colors import LogNorm

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
    x = int(x1)
    y = int(y1)

    # incremento para avance inclinado
    if dy == 0:
        inc_yi = 0
    else:
        inc_yi = int(dy / abs(dy))
    dy = abs(dy)
    if dx == 0:
        inc_xi = 0
    else:
        inc_xi = int(dx / abs(dx))
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
    while y != y2:
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
                    continue
                if cell == SEA:
                    continue
                if cell == FACTORY:
                    continue
                if cell == MOUNTAIN:
                    is_mountains = True
                    if y <= alto - int(float(1800 / dh)):
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

    def __init__(self, dh, t):
        """"
        Constructor
        :param dh: Tamaño de la Grilla
        """
        self.omega = 0
        self.iteracion = 0
        self.time = t
        self.dh = int(dh)

        # Distancias relativas por grilla
        self.ancho = int(float(4000 / self.dh))
        self.alto = int(float(2000 / self.dh))
        self._h = int(float(self.alto))
        self._w = int(float(self.ancho))

        # Distancias de elementos (metros)
        self.mar = int(float((1200 + 400*RRR) / self.dh))
        self.fin_playa = int(float(400 / self.dh + self.mar))
        self.ancho_fabrica = int(float(120 / self.dh))
        self.centro_fabrica = int(self.mar + (self.ancho_fabrica / 2))
        self.centro_cerro_1 = int(float(1200 / self.dh + self.mar))
        self.centro_depresion = int(float(1500 / self.dh + self.mar))
        self.centro_cerro_2 = int(float(2000 / self.dh + self.mar))

        self.alto_playa = int(float(self._h - ((400/3) / self.dh)))
        self.alto_cerro_1 = int(float(self._h - ((1500 + 200 * RRR) / self.dh)))
        self.alto_depresion = int(float(self._h - (1300 + 200 * RRR) / self.dh))
        self.alto_cerro_2 = int(float(self._h - ((1850 + 100 * RRR) / self.dh)))

        self._matrix = np.zeros((self._h, self._w))
        self._elements = np.zeros((self._h, self._w))
        # Se genera terreno y pobla con temperaturas correspondientes para cada cb:
        self.generate_elements()
        self.init_temps()

    def init_temps(self):
        time = self.time
        for x in range(self.ancho):
            for y in range(self.alto):
                if self._elements[y][x] == SEA:
                    self._matrix[y][x] = cb_mar(time)
                elif self._elements[y][x] == SKY:
                    self._matrix[y][x] = cb_sky(time, self._h-y, self.dh)
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
        bresenham_line(self._elements, self._h-1, self.mar,
                       self._h-1, self.mar + self.ancho_fabrica, FACTORY)
        # Linea de playa
        bresenham_line(self._elements, self._h-1, self.mar+self.ancho_fabrica,
                       self.alto_playa, self.fin_playa, MOUNTAIN)
        # Lineas de cerro  despresion intermedia
        bresenham_line(self._elements, self.alto_playa, self.fin_playa,
                       self.alto_cerro_1, self.centro_cerro_1, MOUNTAIN)
        bresenham_line(self._elements, self.alto_cerro_1, self.centro_cerro_1,
                       self.alto_depresion, self.centro_depresion, MOUNTAIN)
        bresenham_line(self._elements, self.alto_depresion, self.centro_depresion,
                       self.alto_cerro_2, self.centro_cerro_2, MOUNTAIN)
        # con la última linea se decide dejarla a 1600 mts sobre el nivel del mar
        bresenham_line(self._elements, self.alto_cerro_2, self.centro_cerro_2,
                       self._h - int(1500/self.dh), self._w, MOUNTAIN)
        fill_elements(self._elements, self._h, self._w, self.dh)

    def reset(self, time, func):
        self.__init__(self.dh, time, func)

    def plot(self):
        """
        funcion de plot basado en rio.py de Pablo Piarro
        :fuente: https://github.com/ppizarror/CC3501-2018-1/blob/master/tareita%201/rio.py
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Se agrega grafico al plot
        cax = ax.imshow(self._matrix, interpolation='none', norm=LogNorm(vmin=19, vmax=self._matrix.max()))
        fig.colorbar(cax)
        plt.title("t = "+str(self.time)+", dh = "+str(self.dh)+", it = "+str(self.iteracion)+", w = "+str(self.omega))
        plt.show()

    def plot_ambient(self):
        """
        funcion de plot basado en rio.py de Pablo Piarro
        :fuente: https://github.com/ppizarror/CC3501-2018-1/blob/master/tareita%201/rio.py
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Se agrega grafico al plot
        cax = ax.imshow(self._matrix, interpolation='none', norm=LogNorm(vmin=0.1, vmax=30))
        fig.colorbar(cax)
        plt.title("t = "+str(self.time)+", dh = "+str(self.dh)+", it = "+str(self.iteracion))
        plt.show()

    def plot_elements(self):
        """
        funcion de plot basado en rio.py de Pablo Piarro
        :fuente: https://github.com/ppizarror/CC3501-2018-1/blob/master/tareita%201/rio.py
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Se agrega grafico al plot
        cax = ax.imshow(self._elements, interpolation='none')
        fig.colorbar(cax)
        plt.title("t = "+str(self.time)+", dh = "+str(self.dh)+", it = "+str(self.iteracion))
        plt.show()

    def start(self, omega, f):
        """
        Inicia iteraciones
        :return:
        """
        self.omega = omega
        epsilon = 15
        error = 0
        for _ in tqdm.tqdm(range(1000)):
            error = 0
            for x in range(1, self._w-1):
                for y in range(1, self._h-1):  # Evitando los bordes de la matriz
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
                self.iteracion = _
                print("Proceso detenido por error menor a "+str(epsilon)+", error igual a "+str(error))
                print("en iteración numero "+str(_))
                break
        print("Error: "+str(error))

    def imprime(self):
        print(self._matrix)


def main():
    # Instancia de Corte
    print("- - - - - - - - - - Estudio de impacto ambiental - - - - - - - - - -\n"
          "- - - - - - - - - - - - - Planta Anonima - - - - - - - - - - - - - -")
    # Se deja esta función con varias partes comentadas para correr
    # distintos experimentos con el modelo
    print("")

    # Inputs
    #omega = input("ingrese omega")
    grilla, tiempo = input("Tamaño grilla y hora separado por espacio").split(" ")
    #grilla, tiempo = 10, 0

    # Opciones de instancias:
    corte = Corte(int(grilla), int(tiempo))
    #Para usar el rho del enunciado escribir 'rho',
    # para usar laplaciano escribir '0'
    #corte.start(float(omega), 0)
    corte.start(set_omega(2000, 4000), 0)
    corte.plot()

# No se que hace esto, pero todos lo tenían
# Solo quería ser popular
if __name__ == '__main__':
    main()
