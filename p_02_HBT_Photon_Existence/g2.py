import numpy as np
import pandas as pd
from p_02_HBT_Photon_Existence.io_utils import (
    read_csv_flexible, normalize_cols, detect_dataset_type,
    parse_delay_from_path, find_all_csvs, find_g2_column_name
)

class G2Analyzer:
    """
    ONE class for both 2-detector (unheralded) and 3-detector (heralded) g2 analysis.

    Key features:
    - normalize (bool): if True, create *_norm columns using tail normalization so g2(τ→∞)=1
    - compute(kind): kind="2d" or "3d"; returns an aggregated DataFrame by delay with:
        delay_ns,
        g2_counts_mean, g2_counts_std, g2_counts_sem, n_counts,
        g2_file_mean,   g2_file_std,   g2_file_sem,   n_file,
        (and if normalize=True) g2_counts_norm, g2_counts_norm_std/sem,
                                 g2_file_norm,   g2_file_norm_std/sem
    """

    def __init__(self, data_dir, normalize=True, tail_k=3):
        self.data_dir = data_dir
        self.normalize = normalize       # <— turn normalization on/off here
        self.tail_k = int(max(1, tail_k))

    # ---------- per-sample estimators ----------
    def _g2_per_sample_counts(self, df_norm, kind):
        eps = 1e-12
        if kind == "2d":
            d = df_norm[["nt","nr","ntr"]].copy()
            valid = (d["nt"] > 0) & (d["nr"] > 0) & (d["ntr"] >= 0)
            d = d[valid]
            if len(d) == 0: return np.array([])
            return (d["ntr"] / (d["nt"]*d["nr"] + eps)).to_numpy()

        if kind == "3d":
            d = df_norm[["ng","ngt","ngr","ngtr"]].copy()
            valid = (d["ng"] > 0) & (d["ngt"] > 0) & (d["ngr"] > 0) & (d["ngtr"] >= 0)
            d = d[valid]
            if len(d) == 0: return np.array([])
            num = (d["ngtr"]*d["ng"]).to_numpy()
            den = (d["ngt"]*d["ngr"] + eps).to_numpy()
            return num/den

        return np.array([])

    def _g2_per_sample_file(self, df_norm, g2_col):
        if g2_col is None or g2_col not in df_norm.columns:
            return np.array([])
        arr = df_norm[g2_col].to_numpy(dtype=float)
        return arr[~np.isnan(arr)]

    # ---------- helpers ----------
    def _summarize(self, arr):
        arr = arr[~np.isnan(arr)]
        if arr.size == 0:
            return np.nan, np.nan, np.nan, 0
        mean = float(np.mean(arr))
        std  = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
        sem  = float(std / np.sqrt(arr.size)) if arr.size > 1 else 0.0
        return mean, std, sem, int(arr.size)

    def _collapse_records(self, bucket):
        rows = []
        for delay, dct in bucket.items():
            counts_vec = np.concatenate(dct["counts"]) if dct["counts"] else np.array([])
            file_vec   = np.concatenate(dct["file"])   if dct["file"]   else np.array([])
            c_mean, c_std, c_sem, c_n = self._summarize(counts_vec)
            f_mean, f_std, f_sem, f_n = self._summarize(file_vec)
            rows.append({
                "delay_ns": float(delay),
                "g2_counts_mean": c_mean, "g2_counts_std": c_std, "g2_counts_sem": c_sem, "n_counts": c_n,
                "g2_file_mean":   f_mean, "g2_file_std":   f_std, "g2_file_sem":   f_sem, "n_file":   f_n,
            })
        df = pd.DataFrame(rows).sort_values("delay_ns")
        return df

    def _add_normalized(self, df):
        if df is None or df.empty or not self.normalize:
            return df  # do nothing if normalization is disabled

        # counts-based normalization
        tail_counts = df.nlargest(min(self.tail_k, len(df)), "delay_ns")["g2_counts_mean"].mean()
        if tail_counts and tail_counts != 0:
            df["g2_counts_norm"]     = df["g2_counts_mean"] / tail_counts
            df["g2_counts_norm_std"] = df["g2_counts_std"]  / tail_counts
            df["g2_counts_norm_sem"] = df["g2_counts_sem"]  / tail_counts

        # file-based normalization (if that series exists)
        if "g2_file_mean" in df.columns and df["g2_file_mean"].notna().any():
            tail_file = df.nlargest(min(self.tail_k, len(df)), "delay_ns")["g2_file_mean"].mean()
            if tail_file and tail_file != 0:
                df["g2_file_norm"]     = df["g2_file_mean"] / tail_file
                df["g2_file_norm_std"] = df["g2_file_std"]  / tail_file
                df["g2_file_norm_sem"] = df["g2_file_sem"]  / tail_file

        return df

    # ---------- main API ----------
    def compute(self, kind):
        """
        kind ∈ {"2d","3d"}.
        Returns aggregated DataFrame by delay with means/std/sem (and *_norm if normalize=True).
        """
        assert kind in {"2d","3d"}
        bucket = {}  # delay -> {"counts":[...], "file":[...]}

        for csv_path in find_all_csvs(self.data_dir):
            df  = read_csv_flexible(csv_path)
            dfn = normalize_cols(df)
            k   = detect_dataset_type(dfn.columns)
            if k != kind:
                continue
            delay = parse_delay_from_path(csv_path)
            if delay is None:
                continue

            g2_col = find_g2_column_name(dfn.columns)
            arr_counts = self._g2_per_sample_counts(dfn, kind)
            arr_file   = self._g2_per_sample_file(dfn, g2_col)

            rec = bucket.setdefault(delay, {"counts":[], "file":[]})
            if arr_counts.size: rec["counts"].append(arr_counts)
            if arr_file.size:   rec["file"].append(arr_file)

        df_out = self._collapse_records(bucket)
        df_out = self._add_normalized(df_out)  # no-op if self.normalize == False
        return df_out
