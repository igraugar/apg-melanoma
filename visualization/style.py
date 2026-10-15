"""Shared style, data access and panel layout for all figures of the manuscript."""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.transforms import Bbox

# Folders relative to this file. The csv files of the experiments are read from RESULTS,
# the figures are written to FIGURES and the table to TABLES.
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
ASSETS = HERE / "assets"
FIGURES = HERE / "figures"
TABLES = HERE / "tables"
FS = 21  # one font size for every text element of every figure
WIDTH = 17.5  # every figure has the same width, so the printed font size is the same

BLUE, BROWN, BLACK, GREY = "tab:blue", "tab:brown", "black", "grey"
PCOL = {"melanoma": BLUE, "non_melanoma": BROWN}
PLAB = {"melanoma": "Melanoma", "non_melanoma": "Non-melanoma"}
SHORT = {
    "pigment network": "Network",
    "streaks": "Streaks",
    "pigmentation": "Pigmentation",
    "regression structures": "Regression",
    "dots and globules": "Dots/globules",
    "blue-whitish veil": "Veil",
    "vascular structures": "Vessels",
}
AB2SHORT = {
    "PN": "Network",
    "ST": "Streaks",
    "PIG": "Pigmentation",
    "RS": "Regression",
    "DG": "Dots/globules",
    "BWV": "Veil",
    "VS": "Vessels",
}

LAYOUT = dict(w_pad=0.2, h_pad=0.3, wspace=0.1, hspace=0.06)  # identical separation in every figure
GAP_H, GAP_V = 0.5, 0.6  # separation between panel decorations, inches, the same in every figure
TITLE_CLEAR = 0.35  # minimum distance between the titles of neighbouring panels, inches

sns.set_theme(
    style="whitegrid",
    rc={
        "font.size": FS,
        "axes.titlesize": FS,
        "axes.labelsize": FS,
        "xtick.labelsize": FS,
        "ytick.labelsize": FS,
        "legend.fontsize": FS,
        "legend.title_fontsize": FS,
        "figure.titlesize": FS,
        "font.family": "DejaVu Sans",
        "axes.edgecolor": GREY,
        "grid.color": "#dddddd",
        "axes.titleweight": "bold",
        "axes.titlelocation": "center",
        "axes.titlepad": 12,
        "legend.frameon": False,
        "pdf.fonttype": 42,
    },
)


def csv(name):
    """Read one table written by the experiment notebook."""
    return pd.read_csv(RESULTS / f"{name}.csv")


# Seeds of the trained models and the seed of the model studied in the first and third experiments,
# both as recorded by the experiment notebook.
_selection = csv("model_selection")
SEEDS = sorted(int(s) for s in _selection["seed"])
SEL = int(_selection.loc[_selection["selected"], "seed"].iloc[0])


def save(fig, name):
    """Save the figure as a PDF that spans the full canvas width."""
    fig.canvas.draw()
    # every figure is saved with the full canvas width, so all figures scale identically in the manuscript
    tb = fig.get_tightbbox(fig.canvas.get_renderer())
    W, H = fig.get_size_inches()
    if tb.x0 < 0 or tb.x1 > W:
        warnings.warn(f"The content of {name} exceeds the canvas width.")
    box = Bbox([[0, tb.y0 - 0.15], [W, tb.y1 + 0.15]])
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches=box)
    plt.close(fig)


def _measure(fig, ax):
    """Measure a panel and the space its labels and ticks take on each side (inches)."""
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    p = ax.get_window_extent(r)
    t = ax.get_tightbbox(r)
    ttl = ax.title
    vis = ttl.get_visible()
    ttl.set_visible(False)  # centered titles may overhang the gap, so they do not count horizontally
    th = ax.get_tightbbox(r)
    ttl.set_visible(vis)
    return dict(
        x0=p.x0 / dpi,
        x1=p.x1 / dpi,
        y0=p.y0 / dpi,
        y1=p.y1 / dpi,
        l=max(p.x0 - th.x0, 0) / dpi,
        r=max(th.x1 - p.x1, 0) / dpi,
        b=(p.y0 - t.y0) / dpi,
        t=(t.y1 - p.y1) / dpi,
    )


def arrange(fig, rows, widths=None, heights=None, legend=None, gap_h=None, gap_v=None):
    """Place the panels row by row with the same gap between panel decorations in every row and figure.

    The central gap (even number of panels) or the central panel (odd number) sits on the vertical midline,
    so panels of different rows stay aligned. widths/heights override panel sizes (inches) per row.
    """
    gap_h = GAP_H if gap_h is None else gap_h
    gap_v = GAP_V if gap_v is None else gap_v
    fig.canvas.draw()
    W, H = fig.get_size_inches()

    # target size of every panel, per row
    sizes = []
    for i, row in enumerate(rows):
        ms = [_measure(fig, a) for a in row]
        ws = widths[i] if widths and widths[i] is not None else [m["x1"] - m["x0"] for m in ms]
        hs = heights[i] if heights and heights[i] is not None else [m["y1"] - m["y0"] for m in ms]
        ws = ws if isinstance(ws, (list, tuple)) else [ws] * len(row)
        hs = hs if isinstance(hs, (list, tuple)) else [hs] * len(row)
        sizes.append((ws, hs))

    fig.set_layout_engine("none")
    for _ in range(3):  # decorations change with panel size, so iterate
        fig.canvas.draw()
        meas = [[_measure(fig, a) for a in row] for row in rows]
        cursor = H - 0.05
        ncol = len(rows[0])
        aligned = all(len(r) == ncol for r in rows) and len(rows) > 1

        if aligned:
            # the columns share their spines, so every column takes the widest decorations found in any row
            cl = [max(m[j]["l"] for m in meas) for j in range(ncol)]
            cr = [max(m[j]["r"] for m in meas) for j in range(ncol)]
            cw = [max(sz[0][j] for sz in sizes) for j in range(ncol)]

            # extra room where two centered titles of the same row would come closer than TITLE_CLEAR
            rr = fig.canvas.get_renderer()
            extra = [0.0] * (ncol - 1)
            for row, ms in zip(rows, meas):
                for j in range(ncol - 1):
                    ta, tb2 = row[j].title.get_window_extent(rr), row[j + 1].title.get_window_extent(rr)
                    if ta.width == 0 or tb2.width == 0:
                        continue
                    ha = (ta.width / fig.dpi - cw[j]) / 2  # overhang of each title beyond its panel
                    hb = (tb2.width / fig.dpi - cw[j + 1]) / 2
                    room = cr[j] + gap_h + cl[j + 1] - max(ha, 0) - max(hb, 0)
                    extra[j] = max(extra[j], TITLE_CLEAR - room)
            gaps_j = [gap_h + max(e, 0) for e in extra]

            # left edge of every column, built outwards from the vertical midline
            cols_x = [0.0] * ncol
            k = ncol // 2
            if ncol % 2 == 0:
                x = W / 2 + gaps_j[k - 1] / 2
                for j in range(k, ncol):
                    cols_x[j] = x + cl[j]
                    x = cols_x[j] + cw[j] + cr[j] + (gaps_j[j] if j < ncol - 1 else 0)
                x = W / 2 - gaps_j[k - 1] / 2
                for j in range(k - 1, -1, -1):
                    cols_x[j] = x - cr[j] - cw[j]
                    x = cols_x[j] - cl[j] - (gaps_j[j - 1] if j > 0 else 0)
            else:
                cols_x[k] = W / 2 - cw[k] / 2
                x = cols_x[k] + cw[k] + cr[k] + gaps_j[k]
                for j in range(k + 1, ncol):
                    cols_x[j] = x + cl[j]
                    x = cols_x[j] + cw[j] + cr[j] + (gaps_j[j] if j < ncol - 1 else 0)
                x = cols_x[k] - cl[k] - gaps_j[k - 1]
                for j in range(k - 1, -1, -1):
                    cols_x[j] = x - cr[j] - cw[j]
                    x = cols_x[j] - cl[j] - (gaps_j[j - 1] if j > 0 else 0)

        for row, ms, (ws, hs) in zip(rows, meas, sizes):
            # left edge of every panel in this row
            n = len(row)
            xs = [0.0] * n
            k = n // 2
            if aligned:
                xs = list(cols_x)
            elif n % 2 == 0:
                x = W / 2 + gap_h / 2
                for j in range(k, n):
                    xs[j] = x + ms[j]["l"]
                    x = xs[j] + ws[j] + ms[j]["r"] + gap_h
                x = W / 2 - gap_h / 2
                for j in range(k - 1, -1, -1):
                    xs[j] = x - ms[j]["r"] - ws[j]
                    x = xs[j] - ms[j]["l"] - gap_h
            else:
                xs[k] = W / 2 - ws[k] / 2
                x = xs[k] + ws[k] + ms[k]["r"] + gap_h
                for j in range(k + 1, n):
                    xs[j] = x + ms[j]["l"]
                    x = xs[j] + ws[j] + ms[j]["r"] + gap_h
                x = xs[k] - ms[k]["l"] - gap_h
                for j in range(k - 1, -1, -1):
                    xs[j] = x - ms[j]["r"] - ws[j]
                    x = xs[j] - ms[j]["l"] - gap_h

            # place the row below the previous one
            top = cursor - max(m["t"] for m in ms)
            for a, x0, w, h in zip(row, xs, ws, hs):
                a.set_position([x0 / W, (top - h) / H, w / W, h / H])
            cursor = top - max(hs) - max(m["b"] for m in ms) - gap_v

    # shift every panel horizontally so that the content is centered on the canvas
    fig.canvas.draw()
    tb = fig.get_tightbbox(fig.canvas.get_renderer())
    dx = (W - (tb.x0 + tb.x1)) / 2 / W
    for row in rows:
        for a in row:
            p = a.get_position()
            a.set_position([p.x0 + dx, p.y0, p.width, p.height])

    if legend is not None:
        handles, labels, ncol = legend
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, (cursor + 0.4 * gap_v) / H),
            ncol=ncol,
            frameon=False,
            handletextpad=0.5,
            columnspacing=1.6,
        )
