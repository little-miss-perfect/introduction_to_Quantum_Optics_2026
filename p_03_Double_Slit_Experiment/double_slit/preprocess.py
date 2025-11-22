# double_slit/preprocess.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from .config import ExperimentConfig
from .dataio import DoubleSlitDataset, PositionData


@dataclass
class CoincidencePreprocessor:
    """
    Handles accidental subtraction and per-position statistics.

    It uses ExperimentConfig to decide whether to use:
        - raw coincidences NTR, or
        - background-subtracted coincidences N_true = NTR - N_acc.
    """
    config: ExperimentConfig

    def subtract_accidentals(self, pos: PositionData) -> None:
        """
        Add columns 'N_acc' and 'N_true' to pos.df, if they are not present.

        N_acc = (NT * NR * tau) / T
            where:
                NT, NR: singles per interval
                tau   : coincidence window (seconds)
                T     : measurement_time_s (seconds)
        N_true = NTR - N_acc
        """
        df = pos.df

        # If already computed, don't do it again
        if "N_acc" in df.columns and "N_true" in df.columns:
            return

        T = pos.measurement_time_s
        tau = pos.window_ns * 1e-9  # ns -> s

        df["N_acc"] = df["NT"] * df["NR"] * tau / T
        df["N_true"] = df["NTR"] - df["N_acc"]

        # Optional: avoid negative values from fluctuations
        df.loc[df["N_true"] < 0, "N_true"] = 0.0

    def compute_summary_for_position(self, pos: PositionData) -> Dict[str, Any]:
        """
        Compute statistics for ONE position.

        Returns a dict with at least:
            x_mm, dt_s, window_ns,
            N_mean, N_std, N_sem, N_total,
            N_mean_raw, N_total_raw,
            g2_mean, g2_std, g2_sem,
            n_intervals
        """
        df = pos.df
        n = len(df)

        # Always have access to raw coincidences
        NTR = df["NTR"].to_numpy()
        N_mean_raw = float(np.mean(NTR))
        N_total_raw = float(np.sum(NTR))

        # Decide which coincidences to use for the interference pattern
        if self.config.use_true_coincidences:
            # Make sure N_true exists
            if "N_true" not in df.columns:
                self.subtract_accidentals(pos)
            N = df["N_true"].to_numpy()
        else:
            N = NTR

        N_mean = float(np.mean(N))
        N_std = float(np.std(N, ddof=1)) if n > 1 else 0.0
        N_sem = N_std / np.sqrt(n) if n > 0 else 0.0
        N_total = float(np.sum(N))

        # g2(0) from acquisition (already normalized in their definition)
        g2_vals = df["g2(0)"].to_numpy()
        g2_mean = float(np.mean(g2_vals))
        g2_std = float(np.std(g2_vals, ddof=1)) if n > 1 else 0.0
        g2_sem = g2_std / np.sqrt(n) if n > 0 else 0.0

        return {
            "x_mm": pos.x_mm,
            "dt_s": pos.measurement_time_s,
            "window_ns": pos.window_ns,
            "N_mean": N_mean,
            "N_std": N_std,
            "N_sem": N_sem,
            "N_total": N_total,
            "N_mean_raw": N_mean_raw,
            "N_total_raw": N_total_raw,
            "g2_mean": g2_mean,
            "g2_std": g2_std,
            "g2_sem": g2_sem,
            "n_intervals": n,
        }


def build_summary(dataset: DoubleSlitDataset, preproc: CoincidencePreprocessor) -> pd.DataFrame:
    """
    Loop over all PositionData in the dataset, compute statistics,
    and return a summary DataFrame with one row per x_mm.

    Also stores the DataFrame in dataset.summary.
    """
    rows: List[dict] = []

    for pos in dataset.positions:
        stats = preproc.compute_summary_for_position(pos)
        rows.append(stats)

    summary = pd.DataFrame(rows).sort_values("x_mm").reset_index(drop=True)
    dataset.summary = summary
    return summary
