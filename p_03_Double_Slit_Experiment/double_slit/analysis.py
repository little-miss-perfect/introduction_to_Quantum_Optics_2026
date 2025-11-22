# double_slit/analysis.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pandas as pd

from .config import ExperimentConfig
from .dataio import DoubleSlitDataset
from .preprocess import CoincidencePreprocessor, build_summary
from .models import Eq9Model
from .fitters import DoubleSlitFitter, FitResult
from .plotting import DoubleSlitPlotter


@dataclass
class DoubleSlitAnalysis:
    """
    High-level orchestration of the double-slit experiment analysis.
    """

    config: ExperimentConfig

    def run_full_analysis(self) -> Tuple[pd.DataFrame, FitResult | None]:
        """
        Execute the full pipeline:

            - load raw data,
            - subtract accidentals (optional),
            - build summary DataFrame,
            - fit Eq. (9) (optional, depending on config.perform_fit),
            - make plots.

        Returns
        -------
        summary : pd.DataFrame
            One row per position x_mm.
        fit_result : FitResult or None
            Fit result if config.perform_fit is True, else None.
        """
        # 1) Load all positions
        dataset = DoubleSlitDataset(self.config)
        dataset.load_positions()

        # 2) Preprocess + build summary
        preproc = CoincidencePreprocessor(self.config)
        summary = build_summary(dataset, preproc)

        # 3) Build model, fitter, plotter
        model = Eq9Model(self.config)
        plotter = DoubleSlitPlotter(self.config, model)

        fit_result: FitResult | None = None

        if self.config.perform_fit:
            fitter = DoubleSlitFitter(self.config, model)
            fit_result = fitter.fit_counts(summary)

            # Optionally, you can print a small fit summary:
            perr = None
            if fit_result.cov is not None:
                diag = fit_result.cov.diagonal()
                perr = (diag ** 0.5).tolist()

            print("\n=== Fit results ===")
            for (name, val), err in zip(fit_result.params.items(), perr or []):
                print(f"{name:8s} = {val:10.4g} ± {err:10.4g}")
            print(f"x0_mm   = {fit_result.x0_mm:.4g} mm")

            # You could also compute a reduced chi^2 here if you like.

        # 4) Plot coincidences vs position (with or without fit overlay)
        plotter.plot_counts_with_fit(summary, fit_result, show=True)

        # 5) Plot g2(0) vs position
        plotter.plot_g2_vs_position(summary, show=True)

        return summary, fit_result
