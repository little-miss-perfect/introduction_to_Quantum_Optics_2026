import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from helper_directory.paths_and_constants import (
    path_0, t_0, paths_todos, paths, tiempos_en_micro_segundos, tiempo_requerido
)

from helper_directory.load_csv_files import build_original_y_copia

from helper_directory.plotting import fdp_histograma

df_0_original = pd.read_csv(path_0, encoding='utf-8')
df_0_copia = df_0_original.copy(deep=True)

df_0_copia.head()

e_v = df_0_copia.mean()
e_v = e_v.iloc[0]

print(f"el valor esperado fue de '{e_v:.6f}' fotones a '{t_0} s'")

# y aplicamos la regla de "3" que nos pidieron
escala = "micro"
pruebas = [e_v, 1, 5, 9, 10, 13, 16, 21, 23, 100, 150, 200]

print("en la regla de tres: \n \n \n \n")
for i in pruebas:
    print(f"para un valor esperado de '{i}' fotones, \n"
          f"requerimos de '{tiempo_requerido(i, e_v, escala=escala):.6f}' {escala}segundos \n")

# y creamos los dataframes
original, copia = build_original_y_copia(paths, encoding='utf-8')
print(copia['df_1'].head())

# para luego hacer los histogramas, tomamos
names = list(copia.keys())[:12]
rows, cols = 3, 4
fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3), constrained_layout=True)

for ax, name in zip(axes.ravel(), names):
    fdp_histograma(copia[name], ax=ax, title=name)

for ax in axes.ravel()[len(names):]:
    ax.axis("off")

plt.show()

# los valores esperados que probamos fueron los siguientes
# [1, 5, 9, 10, 13, 16, 21, 23, 100, 150, 200]
