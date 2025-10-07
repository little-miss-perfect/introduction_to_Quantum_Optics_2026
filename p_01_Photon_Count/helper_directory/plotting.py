import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# nos piden obtener el histograma asociado a cada dataframe,
# para luego normalizarlo y obtener la densidad
# (que debe distribuirse como Poisson de parámetro "promedio de fotones")

def fdp_histograma(df, *, ax=None, title=None):
    """
    dado un dataframe (de una columna), grafica la función de densidad mediante un histograma normalizado,
    y regresa la función de densidad como una serie de Pandas donde
    los índices son los valores que toma la variable aleatoria discreta y
    los valores de la serie son las probabilidades asociadas a esos valores.
    """
    # redefinimos el dataframe en una serie (ya evitando un par de problemas)
    s = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().astype(int)  # "df.iloc[:, 0]" agarra todas las filas de la columna "0"
                                                                            # 'errors="coerce"' es para evitar mini irregularidades (cualquier irregularidad las vuelve "NaN")
                                                                            # ".dropna()" justo quita esas filas dadas por 'errors="coerce"'
                                                                            # ".astype(int)" lo tenemos por si algo se pasa como un "float" (porque los conteos son, pues, enteros)

    # Relative frequencies (probabilities), sorted by value
    fdp = s.value_counts(normalize=True).sort_index()
                                                       # "value_counts()" cuenta las veces que una entrada distinta aparece (obtiene las frequencias). la documentación dice: 'Return a Series containing the frequency of each distinct row in the Dataframe.'
                                                       #
                                                       # "normalize" divide las entradas por el número total de observaciones. la documentación dice: 'Return proportions rather than frequencies.'
                                                       #
                                                       # "sort_index" lo tenemos para reordenar la serie en términos de los índices del dataframe. la documentación dice: 'Returns a new Series sorted by label if inplace argument is False, otherwise updates the original series and returns None.'

    # esto ya es para hacer los histogramas
    if ax is None:
        fig, ax = plt.subplots()  # como cuando graficamos

    # Bar plot: heights sum to 1
    ax.bar(fdp.index.values, fdp.values, align="center", edgecolor="black")  # "fdp.index.values" nos da los valores posibles que toma nuestra variable aleatoria discreta
                                                                             # "fdp.values" nos da las probabilidades (por cómo definimos esta serie)
    ax.set_xlabel("número de fotones")  # lo de "fdp.index.values"
    ax.set_ylabel("probabilidad")  # lo de "fdp.values"
    if title:  # por si a esta función sí le damos como argumento un título
        ax.set_title(title)

    return fdp  # y que nos regrese la serie. entonces esta función "grafica" y aparte nos regresa una serie
                # que si quisiéramos checar que quedó bien normalizada nuestra función de densidad, entonces la suma de las entradas de la serie debería de darnos aproximadamente "1" (usando algo como "pmf.sum()")

def fdp_histograma(df, *, ax=None, title=None):
    """
    dado un dataframe (de una columna), grafica la función de densidad mediante un histograma normalizado,
    y regresa la función de densidad como una serie de Pandas donde
    los índices son los valores que toma la variable aleatoria discreta y
    los valores de la serie son las probabilidades asociadas a esos valores.
    """
    # redefinimos el dataframe en una serie (ya evitando un par de problemas)
    s = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().astype(int)  # "df.iloc[:, 0]" agarra todas las filas de la columna "0"
                                                                            # 'errors="coerce"' es para evitar mini irregularidades (cualquier irregularidad las vuelve "NaN")
                                                                            # ".dropna()" justo quita esas filas dadas por 'errors="coerce"'
                                                                            # ".astype(int)" lo tenemos por si algo se pasa como un "float" (porque los conteos son, pues, enteros)

    # "relative frequencies (probabilities), sorted by value"
    fdp = s.value_counts(normalize=True).sort_index()
                                                       # "value_counts()" cuenta las veces que una entrada distinta aparece (obtiene las frequencias). la documentación dice: 'Return a Series containing the frequency of each distinct row in the Dataframe.'
                                                       #
                                                       # "normalize" divide las entradas por el número total de observaciones. la documentación dice: 'Return proportions rather than frequencies.'
                                                       #
                                                       # "sort_index" lo tenemos para reordenar la serie en términos de los índices del dataframe. la documentación dice: 'Returns a new Series sorted by label if inplace argument is False, otherwise updates the original series and returns None.'

    # esto ya es para hacer los histogramas
    if ax is None:
        fig, ax = plt.subplots()  # como cuando graficamos

    # elegimos bordes de bins centrados en enteros: [..., k-0.5, k+0.5, ...] para todos los k observados.
    # con bin width = 1 y density=True, la altura de cada barra es (conteo/N)/1 = probabilidad.
    kmin = int(s.min())
    kmax = int(s.max())
    edges = np.arange(kmin - 0.5, kmax + 1.5, 1)  # bordes con paso 1 (ancho de bin = 1)

    # histograma normalizado (PDF) pero con bins de ancho 1 donde las alturas corresponden a la densidad de probabilidad
    ax.hist(s, bins=edges, density=True, edgecolor="black", align="mid", color="darkmagenta", alpha=0.7)

    ax.set_xlabel("número de fotones")  # lo de "fdp.index.values"
    ax.set_ylabel("probabilidad")       # alturas = probabilidades porque width=1
    if title:  # por si a esta función sí le damos como argumento un título
        ax.set_title(title)

    return fdp  # mantiene el mismo retorno (series con probabilidades por k)

