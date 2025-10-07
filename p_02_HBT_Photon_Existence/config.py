import os

# Root = this folder
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "samples")
OUT_DIR  = os.path.join(ROOT_DIR, "outputs")
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR, exist_ok=True)

# Aggregation & plotting
# If you want normalized plots by default, leave this True; set False for raw.
NORMALIZE_DEFAULT = True
NORMALIZE_TAIL_K  = 3   # Use mean of largest K delays to set g2(τ→∞)=1

# Error bars: "std" (requested) or "sem"
ERRORBAR_KIND = "std"

# Matplotlib figure DPI
FIG_DPI = 160

# NEW: overlay counts vs file in the same plot?
COMPARE_OVERLAY = False    # set False if you prefer separate plots

# Add this (semi-transparent black works nicely)
ERRORBAR_COLOR = (0, 0, 0, 0.55)  # RGBA
# (Optionally, two shades if you want counts vs file different)
ERRORBAR_COLOR_COUNTS = (0, 0, 0, 0.55)
ERRORBAR_COLOR_FILE   = (0, 0, 0, 0.35)

XAXIS_LABEL = r'$\tau$'
YLABEL_G2   = r'$g^{(2)}(\tau)$ (sin normalizar)'
YLABEL_G2_N = r'$g^{(2)}(\tau)$'

