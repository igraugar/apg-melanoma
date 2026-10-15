"""Figure 3 of the manuscript. Disagreement within and between images, and its sensitivity to the inverse temperature."""

from style import *
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

dec = csv("case_T3_decomposition").query("seed == @SEL").set_index("population")
sb = csv("sensitivity_beta0")
fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 11), layout="constrained")
fig.get_layout_engine().set(**LAYOUT)
ax = axes[0, 0]
pops = ["melanoma", "non_melanoma"]
for i, p in enumerate(pops):
    w = dec.loc[p, "within_share"]
    ax.barh(i, w, color=PCOL[p], height=0.55)
    ax.barh(i, 1 - w, left=w, color=GREY, alpha=0.55, height=0.55)
ax.set_yticks(range(2), [PLAB[p] for p in pops])
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Share of the disagreement")
ax.set_title("a)   Within versus between images")
ax.grid(axis="y", visible=False)
panels = [
    ("within_share", "b)   Share within images", "Share within images", True),
    ("kappa", r"c)   Agreement $\kappa$", r"Agreement $\kappa$", False),
    ("kendall_tau_to_frozen_consensus", "d)   Stability of the consensus", r"Kendall $\tau$ to frozen order", False),
]
for ax, (col, title, ylab, pct) in zip([axes[0, 1], axes[1, 0], axes[1, 1]], panels):
    for p in pops:
        d = sb[sb.population == p]
        ax.plot(d.beta0, d[col], color=PCOL[p], lw=3, marker="o", ms=12)
        f = d[d.frozen]
        ax.scatter(f.beta0, f[col], s=420, facecolor="none", edgecolor=BLACK, lw=2.5, zorder=4)
    ax.set_xscale("log")
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10], ["0.25", "0.5", "1", "2", "5", "10"])
    ax.minorticks_off()
    ax.set_xlabel(r"Inverse temperature $\beta_0$")
    ax.set_ylabel(ylab)
    ax.set_title(title)
    if pct:
        ax.set_ylim(0, 1.02)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
axes[1, 0].set_ylim(0, 1)
axes[1, 1].set_ylim(0.5, 1.02)
axes[1, 1].set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
h = [
    Patch(color=BLUE),
    Patch(color=BROWN),
    Patch(color=GREY, alpha=0.55),
    Line2D([], [], marker="o", ls="", mfc="none", mec=BLACK, mew=2.5, ms=19),
]
arrange(
    fig,
    [list(axes[0]), list(axes[1])],
    widths=[5.4, 5.4],
    heights=[3.6, 3.6],
    legend=(h, ["Melanoma", "Non-melanoma", "Between images", "Frozen choice"], 4),
)
save(fig, "fig2_ambiguity")
