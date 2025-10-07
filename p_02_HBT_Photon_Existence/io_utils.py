import os
import re
import pandas as pd

def read_csv_flexible(path):
    """Read CSV with flexible delimiter/encoding."""
    try:
        return pd.read_csv(path, sep=None, engine="python")
    except Exception:
        return pd.read_csv(path, sep=None, engine="python", encoding="latin-1")

def normalize_cols(df):
    """Lowercase/strip/collapse whitespace in column names."""
    import re as _re
    out = df.copy()
    out.columns = [_re.sub(r"\s+", " ", c).strip().lower() for c in df.columns]
    return out

def detect_dataset_type(columns):
    """
    Classify CSV columns: '2d' -> {nt,nr,ntr}; '3d' -> {ng,ngt,ngr,ngtr};
    'cuentas' -> {ch 1,ch 2,ch 3} variants; else 'other'.
    """
    cols = set([c.lower() for c in columns])
    if {"nt","nr","ntr"}.issubset(cols):
        return "2d"
    if {"ng","ngt","ngr","ngtr"}.issubset(cols):
        return "3d"
    ch1 = {"ch 1","ch1","channel 1"}
    ch2 = {"ch 2","ch2","channel 2"}
    ch3 = {"ch 3","ch3","channel 3"}
    if (cols & ch1) and (cols & ch2) and (cols & ch3):
        return "cuentas"
    return "other"

def parse_delay_from_path(csv_path):
    """
    Extract delay (ns) from parent folder name (e.g., '..._delay_150').
    Fallback: any number >= 5 in the parent folder name.
    """
    parent = os.path.basename(os.path.dirname(csv_path)).lower()
    m = re.search(r"delay[_\-\s]*([0-9]+(\.[0-9]+)?)", parent)
    if m:
        return float(m.group(1))
    m = re.search(r"([0-9]+(\.[0-9]+)?)\s*ns", parent)
    if m:
        return float(m.group(1))
    nums = re.findall(r"([0-9]+(\.[0-9]+)?)", parent)
    if nums:
        vals = [float(x[0]) for x in nums if float(x[0]) >= 5.0]
        if vals:
            return vals[-1]
    return None

def find_all_csvs(root_dir):
    """Return list of CSV paths under root_dir (recursive)."""
    csvs = []
    for base, _, files in os.walk(root_dir):
        for fname in files:
            if fname.lower().endswith(".csv"):
                csvs.append(os.path.join(base, fname))
    return sorted(csvs)

def find_g2_column_name(columns):
    """
    Identify an existing g2 column (e.g. 'g2(0)', 'g2', 'g2_0', ...).
    Returns None if not found.
    """
    cands = [c for c in columns if "g2" in c.lower()]
    if not cands:
        return None
    for c in cands:
        cl = c.lower()
        if "g2(0)" in cl or "g2_0" in cl:
            return c
    return cands[-1]
