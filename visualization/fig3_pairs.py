"""Figure 4 of the manuscript. Share of explanations that rank the winner of each concept pair first."""

from style import *
from matplotlib.lines import Line2D

w = csv("case_T4_walls").query("seed == @SEL")
fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 13), layout="constrained")
fig.get_layout_engine().set(**LAYOUT)
pops = ["melanoma", "non_melanoma"]
for k, p in enumerate(pops):
    ax = axes[k]
    d = w[w.population == p].sort_values("share_winner_first", ascending=False).reset_index(drop=True)
    y = np.arange(len(d))
    ax.hlines(y, d.boot_lo, d.boot_hi, color=GREY, lw=2.5, zorder=1)
    c = d.certified.values
    ax.scatter(d.share_winner_first[c], y[c], s=190, color=PCOL[p], zorder=3)
    ax.scatter(d.share_winner_first[~c], y[~c], s=190, facecolor="white", edgecolor=GREY, lw=2.5, zorder=3)
    ax.axvline(0.5, color=BLACK, lw=2, ls="--", zorder=0)
    ax.set_yticks(y, [f"{SHORT[a]} > {SHORT[b]}" for a, b in zip(d.winner, d.loser)])
    ax.set_ylim(len(d) - 0.4, -0.6)
    ax.set_xlim(0.45, 1.05)
    ax.set_xticks([0.5, 0.75, 1.0], ["50%", "75%", "100%"])
    ax.set_xlabel("Explanations")
    ax.set_title(f"{'ab'[k]})   {PLAB[p]}")
    if k == 1:
        ax.yaxis.tick_right()
h = [
    Line2D([], [], marker="o", ls="", color=BLUE, ms=14),
    Line2D([], [], marker="o", ls="", color=BROWN, ms=14),
    Line2D([], [], marker="o", ls="", mfc="white", mec=GREY, mew=2.5, ms=14),
    Line2D([], [], color=BLACK, lw=2, ls="--"),
]
arrange(
    fig,
    [list(axes)],
    widths=[3.5],
    legend=(h, ["Melanoma, certified", "Non-melanoma, certified", "Not certified", "Even split"], 4),
)
save(fig, "fig3_pairs")
