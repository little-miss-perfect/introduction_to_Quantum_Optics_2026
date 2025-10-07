# --- sys.path guard so absolute package imports work when running this file directly ---
import os, sys
if __package__ is None or __package__ == "":
    # insert the parent directory (that contains 'photon_existence') into sys.path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p_02_HBT_Photon_Existence.config import DATA_DIR, OUT_DIR, NORMALIZE_DEFAULT, COMPARE_OVERLAY
from p_02_HBT_Photon_Existence.g2 import G2Analyzer
from p_02_HBT_Photon_Existence.plotting import plot_scatter, plot_overlay
from p_02_HBT_Photon_Existence.report import save_table, headline_min_delay

def main():
    print("Data root:", DATA_DIR)
    analyzer = G2Analyzer(data_dir=DATA_DIR, normalize=NORMALIZE_DEFAULT, tail_k=3)

    # Compute both experiments
    df2 = analyzer.compute(kind="2d")  # unheralded
    df3 = analyzer.compute(kind="3d")  # heralded

    # Save tables
    if df2 is not None and not df2.empty:
        save_table(df2, "g2_2detectors_by_delay.csv", OUT_DIR)
    if df3 is not None and not df3.empty:
        save_table(df3, "g2_3detectors_by_delay.csv", OUT_DIR)

    # ---- Plotting logic ----
    # RAW scale
    if df2 is not None and not df2.empty:
        if COMPARE_OVERLAY:
            plot_overlay(df2, normalized=False,
                         title="2 detectores (RAW, counts vs CSV)",
                         filename="plot_g2_2detectors_overlay_raw.png")
        else:
            # plot_scatter(df2, which="counts", normalized=False,
            #              title="2 detectores from counts (RAW)",
            #              filename="plot_g2_2detectors_counts_raw.png")  # que es la función de correlación calculada a partir de los "conteos" y las "coincidencias"
            plot_scatter(df2, which="file", normalized=False,  # que son los scatters normalizados
                         title="2 detectores",
                         filename="plot_g2_2detectors_file_raw.png")

    if df3 is not None and not df3.empty:
        if COMPARE_OVERLAY:
            plot_overlay(df3, normalized=False,
                         title="3 detectores (RAW, counts vs CSV)",
                         filename="plot_g2_3detectors_overlay_raw.png")
        else:
            # plot_scatter(df3, which="counts", normalized=False,
            #              title="3 detectores from counts (RAW)",
            #              filename="plot_g2_3detectors_counts_raw.png")  # que es la función de correlación calculada a partir de los "conteos" y las "coincidencias"
            plot_scatter(df3, which="file", normalized=False,  # que son los scatters normalizados
                         title="3 detectores",
                         filename="plot_g2_3detectors_file_raw.png")

    # NORMALIZED scale (only meaningful if analyzer.normalize == True and *_norm columns exist)
    if df2 is not None and not df2.empty:
        if COMPARE_OVERLAY:
            plot_overlay(df2, normalized=True,
                         title="2 detectores (NORMALIZED, counts vs CSV)",
                         filename="plot_g2_2detectors_overlay_norm.png")
        else:
            # plot_scatter(df2, which="counts", normalized=True,
            #              title="2 detectores from counts (NORMALIZED)",
            #              filename="plot_g2_2detectors_counts_norm.png")
            plot_scatter(df2, which="file", normalized=True,  # que son los scatters normalizados
                         title="2 detectores (valores normalizados)",  # de la columna ya existente en el archivo ".csv"
                         filename="plot_g2_2detectors_file_norm.png")

    if df3 is not None and not df3.empty:
        if COMPARE_OVERLAY:
            plot_overlay(df3, normalized=True,
                         title="3 detectores (NORMALIZED, counts vs CSV)",
                         filename="plot_g2_3detectors_overlay_norm.png")
        else:
            # plot_scatter(df3, which="counts", normalized=True,
            #              title="3 detectores from counts (NORMALIZED)",
            #              filename="plot_g2_3detectors_counts_norm.png")
            plot_scatter(df3, which="file", normalized=True,  # que son los scatters normalizados
                         title="3 detectores (valores normalizados)",  # de la columna ya existente en el archivo ".csv"
                         filename="plot_g2_3detectors_file_norm.png")

    # Headlines (optional)
    if df2 is not None and not df2.empty:
        print("2D counts @ min window (raw): ", headline_min_delay(df2, which="counts", normalized=False))
        print("2D counts @ min window (norm):", headline_min_delay(df2, which="counts", normalized=True))
    if df3 is not None and not df3.empty:
        print("3D counts @ min window (raw): ", headline_min_delay(df3, which="counts", normalized=False))
        print("3D counts @ min window (norm):", headline_min_delay(df3, which="counts", normalized=True))

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()