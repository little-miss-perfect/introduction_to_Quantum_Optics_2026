import os
import matplotlib.pyplot as plt
import numpy as np
from p_02_HBT_Photon_Existence.config import OUT_DIR, FIG_DPI, ERRORBAR_KIND, XAXIS_LABEL, ERRORBAR_COLOR, ERRORBAR_COLOR_COUNTS, ERRORBAR_COLOR_FILE, XAXIS_LABEL, YLABEL_G2, YLABEL_G2_N

def _series_cols(which, normalized):
    series = "g2_counts" if which == "counts" else "g2_file"
    y = f"{series}_norm" if normalized else f"{series}_mean"
    if ERRORBAR_KIND == "std":
        e = f"{series}_norm_std" if normalized else f"{series}_std"
    else:
        e = f"{series}_norm_sem" if normalized else f"{series}_sem"
    return y, e

def plot_scatter(df, which="counts", normalized=False, title="", filename=""):
    """
    Single series (either 'counts' or 'file') with error bars.
    Autoscale is enabled; margins give headroom for error bars.
    """
    if df is None or df.empty:
        return None

    ycol, ecol = _series_cols(which, normalized)
    if ycol not in df.columns or ecol not in df.columns:
        return None

    xvals = df["delay_ns"].values
    yvals = df[ycol].values
    yerr  = df[ecol].values

    plt.figure()
    plt.errorbar(xvals, yvals, yerr=yerr, fmt='o-', capsize=3, ecolor=ERRORBAR_COLOR, elinewidth=1.2)  # marker circle; autoscaled
    plt.margins(y=0.12)  # add headroom so error bars aren’t clipped
    plt.xlabel(XAXIS_LABEL)
    plt.ylabel(YLABEL_G2 if not normalized else YLABEL_G2_N)
    plt.title(title)
    out = os.path.join(OUT_DIR, filename)
    plt.savefig(out, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    return out

def plot_overlay(df, normalized=False, title="", filename=""):
    """
    Overlay counts vs file on the same axes (with error bars).
    - Different marker styles (o vs s); colors come from Matplotlib’s default cycle.
    - If one series is missing, falls back to plotting the one that exists.
    - Autoscale + margins to keep full error bars visible.
    """
    if df is None or df.empty:
        return None

    # Determine columns for both series
    y_counts, e_counts = _series_cols("counts", normalized)
    y_file,   e_file   = _series_cols("file",   normalized)

    have_counts = (y_counts in df.columns and e_counts in df.columns and df[y_counts].notna().any())
    have_file   = (y_file   in df.columns and e_file   in df.columns and df[y_file].notna().any())
    if not have_counts and not have_file:
        return None

    xvals = df["delay_ns"].values

    plt.figure()

    # Plot counts series if present
    if have_counts:
        plt.errorbar(
            xvals, df[y_counts].values, yerr=df[e_counts].values,
            fmt='o-', capsize=3, ecolor=ERRORBAR_COLOR_COUNTS, elinewidth=1.2, label="from counts"
        )

    # Plot file series if present
    if have_file:
        plt.errorbar(
            xvals, df[y_file].values, yerr=df[e_file].values,
            fmt='s--', capsize=3, ecolor=ERRORBAR_COLOR_FILE, elinewidth=1.2, label="from CSV g2 column"
        )

    plt.margins(y=0.12)  # ensure error bars have headroom
    plt.xlabel("Delay / coincidence window (ns)")
    plt.ylabel("g2 (normalized)" if normalized else "g2 (mean)")
    plt.title(title)
    plt.legend()
    out = os.path.join(OUT_DIR, filename)
    plt.savefig(out, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    return out