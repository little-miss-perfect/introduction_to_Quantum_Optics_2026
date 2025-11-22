# double_slit/fitters.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .config import ExperimentConfig
from .models import Eq9Model


@dataclass
class FitResult:
    """
    Container for fit results.

    Attributes
    ----------
    params : dict
        Best-fit parameter values.
    cov : np.ndarray
        Covariance matrix returned by curve_fit.
    x0_mm : float
        Estimated center position of the interference pattern (mm),
        defined as the position of the maximum N_mean in the summary.
    mask : np.ndarray
        Boolean mask indicating which points were actually used in the fit.
    """
    params: Dict[str, float]
    cov: np.ndarray
    x0_mm: float
    mask: np.ndarray


class DoubleSlitFitter:
    """
    Handles regression of Eq. (9) (basic or extended) to the
    mean coincidence data stored in 'summary'.

    It only sees arrays x, y, sigma; all pre-processing decisions
    (accidentals, etc.) are done beforehand.
    """

    def __init__(self, config: ExperimentConfig, model: Eq9Model):
        self.config = config
        self.model = model

    # --------------------------------------------------------------
    # Helper: estimate center of pattern
    # --------------------------------------------------------------
    @staticmethod
    def estimate_center(summary: pd.DataFrame) -> float:
        """
        Estimate the center of the interference pattern as the
        position where N_mean is maximum.
        """
        idx_max = int(np.argmax(summary["N_mean"].to_numpy()))
        return float(summary["x_mm"].iloc[idx_max])

    # --------------------------------------------------------------
    # Helper: choose which points to fit
    # --------------------------------------------------------------
    def make_fit_mask(self, x_mm: np.ndarray, x0_mm: float) -> np.ndarray:
        """
        Construct a boolean mask specifying which points to include in the fit,
        based on config.fit_region.

        Options implemented:
            "full"          : use all points
            "up_to_center"  : use points with x <= x0
            "around_center" : use a symmetric window of width 4 mm around x0
        """
        region = self.config.fit_region.lower()
        if region == "full":
            return np.ones_like(x_mm, dtype=bool)
        elif region == "up_to_center":
            return x_mm <= x0_mm
        elif region == "around_center":
            # +/- 2 mm around the center (you can tweak this)
            return (x_mm >= x0_mm - 2.0) & (x_mm <= x0_mm + 2.0)
        else:
            # Fallback: full region if unrecognized option
            return np.ones_like(x_mm, dtype=bool)

    # --------------------------------------------------------------
    # Main fitting method
    # --------------------------------------------------------------
    def fit_counts(self, summary: pd.DataFrame) -> FitResult:
        """
        Fit Eq. (9) (basic or extended) to the mean coincidences in 'summary'.

        Uses:
            x_mm  = summary["x_mm"]
            y     = summary["N_mean"]
            sigma = summary["N_sem"]

        Returns
        -------
        FitResult
            Contains best-fit parameters, covariance, estimated center, and mask.
        """
        x_mm = summary["x_mm"].to_numpy()
        y = summary["N_mean"].to_numpy()
        sigma = summary["N_sem"].to_numpy()

        # 1) Estimate center and work with relative coordinates x_rel = x - x0
        x0_mm = self.estimate_center(summary)
        x_rel = x_mm - x0_mm

        # 2) Decide which points are used
        mask = self.make_fit_mask(x_mm, x0_mm)
        x_fit = x_rel[mask]
        y_fit = y[mask]
        sigma_fit = sigma[mask]

        # 3) Build model function for curve_fit, depending on config.use_extended_model
        if self.config.use_extended_model:
            def model_for_fit(x_rel_local, N0, V, delta, x_scale, N_bg):
                return self.model.counts_extended(
                    x_rel_local, N0, V, delta, x_scale, N_bg
                )

            # Initial guesses
            N0_guess = float(np.max(y_fit) - np.min(y_fit))
            V_guess = 0.5       # moderate visibility
            delta_guess = 0.0
            x_scale_guess = 1.0
            N_bg_guess = float(np.min(y_fit))

            p0 = [N0_guess, V_guess, delta_guess, x_scale_guess, N_bg_guess]
            bounds = (
                [0.0, 0.0, -2.0 * np.pi, 0.3, 0.0],    # lower bounds
                [np.inf, 1.0,  2.0 * np.pi, 3.0, np.inf],  # upper bounds
            )
            param_names = ["N0", "V", "delta", "x_scale", "N_bg"]
        else:
            def model_for_fit(x_rel_local, N0, V, delta):
                return self.model.counts_basic(x_rel_local, N0, V, delta)

            N0_guess = float(np.max(y_fit) - np.min(y_fit))
            V_guess = 0.5
            delta_guess = 0.0

            p0 = [N0_guess, V_guess, delta_guess]
            bounds = (
                [0.0, 0.0, -2.0 * np.pi],
                [np.inf, 1.0,  2.0 * np.pi],
            )
            param_names = ["N0", "V", "delta"]

        # 4) Weighted least squares with uncertainties sigma_fit
        #    If sigma is zero somewhere, curve_fit will complain; in that
        #    case you could set absolute_sigma=False or regularize sigma.
        sigma_nonzero = sigma_fit.copy()
        sigma_nonzero[sigma_nonzero == 0.0] = np.min(sigma_nonzero[sigma_nonzero > 0.0])

        popt, pcov = curve_fit(
            model_for_fit,
            x_fit,
            y_fit,
            p0=p0,
            sigma=sigma_nonzero,
            absolute_sigma=True,
            bounds=bounds,
        )

        params = {name: float(val) for name, val in zip(param_names, popt)}

        return FitResult(
            params=params,
            cov=pcov,
            x0_mm=x0_mm,
            mask=mask,
        )
