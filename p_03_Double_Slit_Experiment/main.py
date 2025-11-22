# main.py

from __future__ import annotations

from double_slit import make_default_config, DoubleSlitAnalysis


def main():
    # 1) Build default config (edit physical parameters inside config.py if needed)
    config = make_default_config()

    # Toggle these if you want:
    config.use_true_coincidences = True   # subtract accidentals
    config.perform_fit = True             # <-- set False to get scatter only
    config.use_extended_model = True      # extended model with x_scale, background
    config.fit_region = "up_to_center"    # e.g. "full", "up_to_center", "around_center"
    config.save_figures = True            # save SVGs into figures/

    # 2) Run analysis
    analysis = DoubleSlitAnalysis(config)
    summary, fit_result = analysis.run_full_analysis()

    print("\nSummary head:")
    print(summary.head())
    print(f"\nLoaded {len(summary)} positions.")


if __name__ == "__main__":
    main()
