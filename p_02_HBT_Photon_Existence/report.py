import os

def save_table(df, name, out_dir):
    path = os.path.join(out_dir, name)
    df.to_csv(path, index=False)
    return path

def headline_min_delay(df, which="counts", normalized=False):
    """
    Quick headline: value (+std) at smallest delay/window.
    """
    if df is None or df.empty:
        return {}
    series = "g2_counts" if which == "counts" else "g2_file"
    y  = f"{series}_norm" if normalized else f"{series}_mean"
    es = f"{series}_norm_std" if normalized else f"{series}_std"
    row = df.iloc[df["delay_ns"].argmin()]
    return {
        "min_delay_ns": float(row["delay_ns"]),
        "value": float(row.get(y, float("nan"))),
        "std": float(row.get(es, float("nan")))
    }
