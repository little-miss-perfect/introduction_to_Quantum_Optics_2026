# mediciones para el promedio (primera muestra)
path_0 = "samples/processed/m_0.csv"
# que tomamos a "500000E-6 s"
t_0 = 500000E-6

# muestras para el reporte:

# íbamos a definirlas de uno en uno, pero mejor tomemos una lista de los paths
paths_todos = [ "samples/processed/m_1.csv",          # 'df_1': np.float64(1.04)
                "samples/processed/m_2.csv",          # 'df_2': np.float64(4.71)
                "samples/processed/m_3.csv",          # 'df_3': np.float64(4.925)
                "samples/processed/m_4.csv",          # 'df_4': np.float64(5.095)
                "samples/processed/m_5.csv",          # 'df_5': np.float64(10.01)
                "samples/processed/m_6.csv",          # 'df_6': np.float64(9.32)
                "samples/processed/m_7.csv",          # 'df_7': np.float64(8.825)
                "samples/processed/m_8.csv",          # 'df_8': np.float64(13.07)
                "samples/processed/m_9.csv",          # 'df_9': np.float64(16.2)
                "samples/processed/m_10.csv",         # 'df_10': np.float64(21.015)
                "samples/processed/m_11.csv",         # 'df_11': np.float64(23.185)
                "samples/processed/m_12.csv",         # 'df_12': np.float64(101.71)
                "samples/processed/m_13.csv",         # 'df_13': np.float64(150.83)
                "samples/processed/m_14.csv",         # 'df_14': np.float64(203.35)
                "samples/processed/m_15.csv",         # 'df_15': np.float64(201.585)
                    ]

# pero ahora que sabemos cuáles son las mediciones repetidas,
# y sabiendo que los promedios deben coincidir con la lista

# [e_v, 1, 5, 9, 10, 13, 16, 21, 23, 100, 150, 200]
# sin contar el primer elemento,

# limpiaremos la lista "paths_todos" como sigue

paths = [       "samples/processed/m_1.csv",          # 'df_1': np.float64(1.04)

                # "samples/processed/m_2.csv",          # 'df_2': np.float64(4.71)

                # "samples/processed/m_3.csv",          # 'df_3': np.float64(4.925)

                "samples/processed/m_4.csv",          # 'df_4': np.float64(5.095)

                # "samples/processed/m_6.csv",          # 'df_6': np.float64(9.32)

                "samples/processed/m_7.csv",          # 'df_7': np.float64(8.825)

                "samples/processed/m_5.csv",          # 'df_5': np.float64(10.01)

                "samples/processed/m_8.csv",          # 'df_8': np.float64(13.07)

                "samples/processed/m_9.csv",          # 'df_9': np.float64(16.2)

                "samples/processed/m_10.csv",         # 'df_10': np.float64(21.015)

                "samples/processed/m_11.csv",         # 'df_11': np.float64(23.185)

                "samples/processed/m_12.csv",         # 'df_12': np.float64(101.71)

                "samples/processed/m_13.csv",         # 'df_13': np.float64(150.83)

                # "samples/processed/m_14.csv",         # 'df_14': np.float64(203.35)

                "samples/processed/m_15.csv",         # 'df_15': np.float64(201.585)
                    ]

# que igual reordenamos el "10" que lo habíamos medido antes que el "9".

# print(len(paths))  # es "11" porque no consideramos la medida usada para "e_v"

# ahora vamos a medir en el laboratorio y ver si sí sale.

# de nuestros tiempos propuestos para un valor esperado dado por los elementos de la siguiente lista

# pruebas = [e_v, 1, 5, 9, 10, 13, 16, 21, 23, 100, 150, 200]

# probamos los siguientes tiempos (correspondientes a la lista anterior)

tiempos_en_micro_segundos = [500000, 0.5, 2.7, 4.6, 5.1, 6.6, 8.1, 10.7, 11.7, 50.8, 76.2, 101.6]
# print(len(tiempos_en_micro_segundos))  # son "12" muestras que tomamos. o sea, "12" archivos ".csv"

# y para "la regla de tres":

# 500000 (estámos midiendo en micro segundos)  -->  e_v (número de fotones)  # ya conocemos estos dos valores de la primera muestra (nosotros ajustamos el valor de "500000E-6 s")
#                 ?                            -->   n  (número de fotones)

def tiempo_requerido(n, e_v, escala="micro"):
    '''
    nos regresa el tiempo (en una escala preseleccionada) requerido
    para ver "n" fotones (en promedio)
    dado que sabemos que vimos "e_v" fotones en "500E-6 s".
    inicialmente, la escala está en microsegundos
    porque así funciona el programa que tiene el laboratorio.
    '''

    # para las unidades
    not_scient = {
                "nano": 1E-9,
                "micro": 1E-6,
                "mili": 1E-3,
                "": 1,
                }

    # el tiempo en segundos está dado por: t = n / proporción, proporción = e_v / (500000E-6 s)
    # así que: t = n * 500000E-6 / e_v
    t_segundos = (n * 500000E-6 / e_v)

    # y para la conversión de escala tomamos: segundos / escala_de_segundos
    return t_segundos / not_scient[escala]
