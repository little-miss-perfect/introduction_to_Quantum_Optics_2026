# double_slit/models.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import ExperimentConfig


@dataclass
class Eq9Model:
    """
    Implements Eq. (9) (and a slightly extended version) for the double-slit
    coincidence pattern, using the physical parameters stored in ExperimentConfig.

    All x inputs are in mm; they are internally converted to meters.
    """

    config: ExperimentConfig

    # ------------------------------------------------------------------
    # Basic Eq. (9): no background, no horizontal scaling
    # ------------------------------------------------------------------
    def counts_basic(self, x_mm: np.ndarray, N0: float, V: float, delta: float) -> np.ndarray:
        """
        Eq. (9) evaluated at positions x_mm (in mm):

            N(x) = N0 * (sin beta / beta)^2 * 1/2 [1 + V cos(2 alpha + delta)]

        with:
            alpha = π d x / (λ L),
            beta  = π b x / (λ L).

        Parameters
        ----------
        x_mm : array-like
            Positions in mm, measured from the center (x=0 at central maximum).
        N0 : float
            Overall amplitude.
        V : float
            Visibility (0 ≤ V ≤ 1).
        delta : float
            Phase offset (radians).

        Returns
        -------
        N(x) : np.ndarray
            Predicted mean coincidence counts (arbitrary units).
        """
        x_m = np.asarray(x_mm, dtype=float) * 1e-3  # mm -> m

        lam = self.config.wavelength_m
        L = self.config.L_m
        d = self.config.d_m
        b = self.config.b_m

        alpha = np.pi * d * x_m / (lam * L)
        beta = np.pi * b * x_m / (lam * L)

        # np.sinc(z) = sin(pi z) / (pi z), so we use beta/pi
        envelope = np.sinc(beta / np.pi) ** 2
        interference = 0.5 * (1.0 + V * np.cos(2.0 * alpha + delta))

        return N0 * envelope * interference

    # ------------------------------------------------------------------
    # Extended model: horizontal scale factor and constant background
    # ------------------------------------------------------------------
    def counts_extended(
        self,
        x_mm: np.ndarray,
        N0: float,
        V: float,
        delta: float,
        x_scale: float,
        N_bg: float,
    ) -> np.ndarray:
        """
        Extended Eq. (9) with:
            - x_scale : dimensionless horizontal scaling factor
            - N_bg    : constant background level

        Effectively replace x -> x_eff = x_scale * x in alpha and beta
        and then add N_bg:

            N(x) = N_bg + N0 * (sin beta' / beta')^2 * 1/2[1 + V cos(2 alpha' + delta)]
        """
        x_m = np.asarray(x_mm, dtype=float) * 1e-3  # mm -> m
        x_eff_m = x_scale * x_m

        lam = self.config.wavelength_m
        L = self.config.L_m
        d = self.config.d_m
        b = self.config.b_m

        alpha = np.pi * d * x_eff_m / (lam * L)
        beta = np.pi * b * x_eff_m / (lam * L)

        envelope = np.sinc(beta / np.pi) ** 2
        interference = 0.5 * (1.0 + V * np.cos(2.0 * alpha + delta))

        return N_bg + N0 * envelope * interference

    # ------------------------------------------------------------------
    # Optional: theoretical visibility (Eq. (10) in the PDF)
    # ------------------------------------------------------------------
    def visibility_theory(self) -> float | None:
        """
        Compute the theoretical visibility from Eq. (10) of the PDF:

            |V| = exp[- (π d w0)^2 / (λ z)^2 ]

        using:
            d  : slit separation
            w0 : pump beam waist at the crystal
            z  : source-to-slits distance

        Returns None if w0 or z are not set in the config.
        """
        d = self.config.d_m
        lam = self.config.wavelength_m
        w0 = self.config.w0_m
        z = self.config.z_src_to_slits_m

        if w0 is None or z is None:
            return None

        argument = (np.pi * d * w0 / (lam * z)) ** 2
        return float(np.exp(-argument))
