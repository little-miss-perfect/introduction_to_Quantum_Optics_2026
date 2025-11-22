# double_slit/__init__.py

from .config import ExperimentConfig, make_default_config
from .analysis import DoubleSlitAnalysis

__all__ = [
    "ExperimentConfig",
    "make_default_config",
    "DoubleSlitAnalysis",
]
