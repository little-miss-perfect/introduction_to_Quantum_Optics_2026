# double_slit/plotting.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import ExperimentConfig
from .models import Eq9Model
from .fitters import FitResult


@dataclass
class DoubleSlitPlotter:
    """
    Handles plotting of:
        - coincidences vs position (scatter + optional fit curve),
        - g2(0) vs position.
    """

    config: ExperimentConfig
    model: Eq9Model

    # --------------------------------------------------------------
    # Helper: figure saving
    # --------------------------------------------------------------
    def _save_fig(self, fig: plt.Figure, filename: str) -> None:
        if not self.config.save_figures:
            return

        fig_dir: Path = self.config.fig_dir  # type: ignore[assignment]
        fig_dir.mkdir(parents=True, exist_ok=True)
        out_path = fig_dir / filename
        fig.savefig(out_path, dpi=300)
        print(f"Saved figure to {out_path}")

    # --------------------------------------------------------------
    # Coincidences vs position with optional fit
    # --------------------------------------------------------------
    def plot_counts_with_fit(
        self,
        summary: pd.DataFrame,
        fit_result: Optional[FitResult] = None,
        show: bool = True,
    ) -> None:
        """
        Scatter plot of mean coincidences vs x, with error bars.
        If fit_result is provided, overlay the fitted Eq. (9) curve.
        """
        x = summary["x_mm"].to_numpy()
        y = summary["N_mean"].to_numpy()
        yerr = summary["N_sem"].to_numpy()

        window_ns = summary["window_ns"].iloc[0]
        dt_s = summary["dt_s"].iloc[0]

        fig, ax = plt.subplots(figsize=(8, 5))

        # Data points
        ax.errorbar(
            x, y, yerr=yerr,
            fmt="o", capsize=3,
            label=f"Data: mean coincidences per interval\n"
                  f"({window_ns:.0f} ns window, dt = {dt_s:.3f} s)",
        )

        # Optional: overlay fit
        if fit_result is not None:
            x0_mm = fit_result.x0_mm
            params = fit_result.params

            # Dense x for smooth curve
            x_dense = np.linspace(x.min(), x.max(), 1000)
            x_rel_dense = x_dense - x0_mm

            if "x_scale" in params and "N_bg" in params:
                # Extended model
                y_fit = self.model.counts_extended(
                    x_rel_dense,
                    params["N0"],
                    params["V"],
                    params["delta"],
                    params["x_scale"],
                    params["N_bg"],
                )
                label_fit = (
                    r"Fit (extended Eq. 9): "
                    + rf"V = {params['V']:.2f}, "
                    + rf"$\delta$ = {params['delta']:.2f} rad, "
                    + rf"$s$ = {params['x_scale']:.2f}, "
                    + rf"$N_{{bg}}$ = {params['N_bg']:.1f}"
                )
            else:
                # Basic model
                y_fit = self.model.counts_basic(
                    x_rel_dense,
                    params["N0"],
                    params["V"],
                    params["delta"],
                )
                label_fit = (
                    r"Fit (basic Eq. 9): "
                    + rf"V = {params['V']:.2f}, "
                    + rf"$\delta$ = {params['delta']:.2f} rad"
                )

            ax.plot(x_dense, y_fit, label=label_fit)

            ax.set_title(
                f"Double-slit interference (coincidences, {window_ns:.0f} ns window)\n"
                f"Estimated center x0 = {x0_mm:.2f} mm"
            )
        else:
            # No fit: just a simple title
            ax.set_title(
                f"Double-slit interference (coincidences, {window_ns:.0f} ns window)"
            )

        ax.set_xlabel("Position x (mm)")
        ax.set_ylabel("Mean coincidences per interval")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        self._save_fig(fig, "coincidences_vs_position.svg")

        if show:
            plt.show()
        else:
            plt.close(fig)

    # --------------------------------------------------------------
    # g2(0) vs position
    # --------------------------------------------------------------
    def plot_g2_vs_position(self, summary: pd.DataFrame, show: bool = True) -> None:
        """
        Plot the mean g2(0) per position, with SEM error bars, and a reference
        horizontal line at g2(0) = 1.
        """
        x = summary["x_mm"].to_numpy()
        g2_mean = summary["g2_mean"].to_numpy()
        g2_sem = summary["g2_sem"].to_numpy()

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.errorbar(
            x,
            g2_mean,
            yerr=g2_sem,
            fmt="o",
            capsize=3,
            label=r"Mean $g^{(2)}(0)$ per position",
        )

        ax.axhline(1.0, color="gray", linestyle="--", label=r"$g^{(2)}(0)=1$")

        ax.set_xlabel("Position x (mm)")
        ax.set_ylabel(r"Mean $g^{(2)}(0)$")
        ax.set_title(r"Second-order correlation $g^{(2)}(0)$ vs position")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        self._save_fig(fig, "g2_vs_position.svg")

        if show:
            plt.show()
        else:
            plt.close(fig)
