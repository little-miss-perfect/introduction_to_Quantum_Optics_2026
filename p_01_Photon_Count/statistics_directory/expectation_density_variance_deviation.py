import pandas as pd

def expected_value_from_df(df):
    """
    el valor esperado muestral de una columna (que usamos para calcular 'e_v')
    """
    return pd.to_numeric(df.iloc[:, 0], errors="coerce").mean()
