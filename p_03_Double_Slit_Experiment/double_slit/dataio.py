# double_slit/dataio.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

from .config import ExperimentConfig


@dataclass
class PositionData:
    """
    Raw data for ONE position (one numeric folder under 'samples/').

    Attributes
    ----------
    x_mm : float
        Stage position in millimetres (folder name).
    df : pandas.DataFrame
        DataFrame with at least columns ['NT', 'NR', 'NTR', 'g2(0)'].
        Additional columns (e.g. 'N_acc', 'N_true') can be added later.
    measurement_time_s : float
        Duration of each acquisition interval (seconds).
    window_ns : float
        Coincidence window (nanoseconds).
    folder_path : Path
        Path to the folder containing HBT_2D.csv and infoMedicion.txt.
    """
    x_mm: float
    df: pd.DataFrame
    measurement_time_s: float
    window_ns: float
    folder_path: Path

    @classmethod
    def from_folder(cls, folder_path: Path, x_mm: float) -> "PositionData":
        """
        Create a PositionData from a folder containing:
            - HBT_2D.csv
            - infoMedicion.txt
        """
        csv_path = folder_path / "HBT_2D.csv"
        info_path = folder_path / "infoMedicion.txt"

        if not csv_path.exists():
            raise FileNotFoundError(f"Missing HBT_2D.csv in {folder_path}")
        if not info_path.exists():
            raise FileNotFoundError(f"Missing infoMedicion.txt in {folder_path}")

        df = pd.read_csv(csv_path)
        measurement_time_s, window_ns = read_info_file(info_path)

        return cls(
            x_mm=float(x_mm),
            df=df,
            measurement_time_s=measurement_time_s,
            window_ns=window_ns,
            folder_path=folder_path,
        )


def read_info_file(info_path: Path) -> Tuple[float, float]:
    """
    Parse infoMedicion.txt and extract:
        - measurement_time_s : acquisition time per interval (seconds)
        - window_ns          : coincidence window (nanoseconds)

    The exact format of infoMedicion.txt can vary a bit, so we parse it
    in a robust way: look for the first number in lines containing
    'us' or 'micro' for the time, and 'ns' for the window.
    """
    text = info_path.read_text(encoding="utf-8", errors="ignore").lower()
    lines = text.splitlines()

    measurement_time_s: float | None = None
    window_ns: float | None = None

    for line in lines:
        # Remove equals, commas, etc. for simpler splitting
        clean = line.replace("=", " ").replace(":", " ")
        tokens = clean.split()

        # Try to pick out a float in front of 'us' or 'micro'
        if ("us" in tokens or "micro" in tokens) and measurement_time_s is None:
            # find first numeric token
            for tok in tokens:
                try:
                    val = float(tok)
                    # assume microseconds -> convert to seconds
                    measurement_time_s = val * 1e-6
                    break
                except ValueError:
                    continue

        # Try to pick out a float in front of 'ns' for the window
        if "ns" in tokens and window_ns is None:
            for tok in tokens:
                try:
                    val = float(tok)
                    window_ns = val
                    break
                except ValueError:
                    continue

    if measurement_time_s is None:
        raise ValueError(f"Could not parse measurement time from {info_path}")
    if window_ns is None:
        raise ValueError(f"Could not parse coincidence window from {info_path}")

    return measurement_time_s, window_ns


class DoubleSlitDataset:
    """
    Represents the full collection of PositionData objects
    (one per numeric subfolder under samples/).
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.positions: List[PositionData] = []
        self.summary: pd.DataFrame | None = None

    def load_positions(self) -> None:
        """
        Scan data_base_dir for numeric-named folders, create PositionData
        for each, and store them sorted by x_mm.
        """
        base = self.config.data_base_dir
        if not base.exists():
            raise FileNotFoundError(f"Data base dir does not exist: {base}")

        position_dirs: List[Tuple[float, Path]] = []

        for entry in base.iterdir():
            if not entry.is_dir():
                continue
            try:
                # folder names like "0", "0.3", "24.7"
                x_mm = float(entry.name)
                position_dirs.append((x_mm, entry))
            except ValueError:
                # ignore non-numeric folders
                continue

        # Sort by numeric x_mm
        position_dirs.sort(key=lambda tpl: tpl[0])

        positions: List[PositionData] = []
        for x_mm, folder_path in position_dirs:
            pos = PositionData.from_folder(folder_path, x_mm)
            positions.append(pos)

        self.positions = positions

    def __len__(self) -> int:
        return len(self.positions)
