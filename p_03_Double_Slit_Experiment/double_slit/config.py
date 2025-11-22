# double_slit/config.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentConfig:
    """
    Container for paths, physical parameters, and analysis options.

    All units with suffix `_m` are in meters.
    Positions from the stage are in millimeters (mm).
    """

    # --- Paths ---
    project_root: Path
    data_base_dir: Path  # folder containing numeric subfolders (0.0, 0.3, ...)

    # --- Physical parameters (from your lab setup / PDF) ---
    wavelength_m: float  # photon wavelength (m), e.g. 810e-9
    L_m: float           # effective slit-to-detector distance (m)
    d_m: float           # slit separation (m)
    b_m: float           # slit width (m)

    # Optional: parameters used for theoretical visibility (Eq. 10 in the PDF)
    w0_m: float | None = None            # pump beam waist (m)
    z_src_to_slits_m: float | None = None  # source-to-slits distance (m)

    # --- Analysis options ---
    use_true_coincidences: bool = True   # subtract accidental coincidences?
    perform_fit: bool = True             # do we actually run the regression?
    use_extended_model: bool = True      # include x_scale, N_bg, etc. (later)
    fit_region: str = "full"             # "full", "up_to_center", etc.

    # --- Plotting options ---
    save_figures: bool = True
    fig_dir: Path | None = None          # where to save figures (if None, project_root)

    def resolve_paths(self) -> None:
        """
        Normalize paths (expand ~, make them absolute, etc.).
        Call this once right after creating the config.
        """
        self.project_root = self.project_root.expanduser().resolve()
        self.data_base_dir = self.data_base_dir.expanduser().resolve()
        if self.fig_dir is None:
            self.fig_dir = self.project_root / "figures"
        else:
            self.fig_dir = self.fig_dir.expanduser().resolve()


def make_default_config() -> ExperimentConfig:
    """
    Helper to build a reasonable default ExperimentConfig assuming:

    - This file lives inside the 'double_slit' package,
    - 'samples/' is directly under the project root.

    You should still CHANGE the physical parameters to your actual lab values.
    """
    project_root = Path(__file__).resolve().parents[1]
    data_base_dir = project_root / "samples"

    # TODO: replace these with your real experimental values.
    wavelength_m = 444e-9   # 810 nm from the PDF (change if needed)
    L_m = 56.3e-2           # effective slit-to-detector distance (m)
    d_m = 0.04e-3           # slit separation (m)
    b_m = 0.02e-3           # slit width (m)
    w0_m = 0.064e-3         # pump beam waist (64 µm) as in the PDF
    z_src_to_slits_m = 60.0e-2 # example value (30 cm) – change to your actual

    cfg = ExperimentConfig(
        project_root=project_root,
        data_base_dir=data_base_dir,
        wavelength_m=wavelength_m,
        L_m=L_m,
        d_m=d_m,
        b_m=b_m,
        w0_m=w0_m,
        z_src_to_slits_m=z_src_to_slits_m,
        use_true_coincidences=True,
        perform_fit=True,       # you can toggle this in main.py
        use_extended_model=True,
        fit_region="full",
        save_figures=True,
        fig_dir=project_root / "figures",
    )
    cfg.resolve_paths()
    return cfg
