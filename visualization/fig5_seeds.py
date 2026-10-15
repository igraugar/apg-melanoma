"""Figure 6 of the manuscript. Concept positions and ambiguity across the five trained models."""

from style import *
from matplotlib.lines import Line2D

pos = csv("seeds_positions")
pa = csv("seeds_pair_agreement")
syn = csv("seeds_synthesis")
fig = plt.figure(figsize=(WIDTH, 15), layout="constrained")
fig.get_layout_engine().set(**LAYOUT)
gs = fig.add_gridspec(2, 2, height_ratios=[7, 5])
pops = ["melanoma", "non_melanoma"]
for k, p in enumerate(pops):
    ax = fig.add_subplot(gs[0, k])
    d = pos[pos.population == p].sort_values("mean_position_over_seeds").reset_index(drop=True)
    y = np.arange(len(d))
    for s in SEEDS:
        if s == SEL:
            continue
        ax.scatter(d[f"position_seed{s}"], y, s=120, facecolor="white", edgecolor=GREY, lw=2.2, zorder=2)
    ax.hlines(y, d["min"], d["max"], color=GREY, lw=2, zorder=1)
    ax.scatter(d[f"position_seed{SEL}"], y, s=190, color=PCOL[p], zorder=3)
    ax.set_yticks(y, [SHORT[c] for c in d.concept])
    ax.set_ylim(len(d) - 0.5, -0.5)
    ax.set_xlim(0.6, 7.4)
    ax.set_xticks(range(1, 8))
    ax.set_xlabel("Mean position")
    ax.set_title(f"{'ab'[k]})   {PLAB[p]}")
    if k == 1:
        ax.yaxis.tick_right()
ax = fig.add_subplot(gs[1, 0])
for i, p in enumerate(pops):
    v = pa[pa.population == p].kendall_tau_consensus.values
    ax.boxplot(
        v,
        positions=[i],
        widths=0.45,
        orientation="horizontal",
        patch_artist=True,
        showfliers=False,
        boxprops=dict(facecolor="white", edgecolor=PCOL[p], lw=2.5),
        medianprops=dict(color=PCOL[p], lw=3),
        whiskerprops=dict(color=PCOL[p], lw=2.5),
        capprops=dict(color=PCOL[p], lw=2.5),
    )
    jit = np.random.default_rng(3).uniform(-0.12, 0.12, len(v))
    ax.scatter(v, i + jit, color=PCOL[p], s=110, zorder=3)
ax.set_yticks(range(2), [PLAB[p] for p in pops])
ax.set_ylim(1.6, -0.6)
ax.set_xlim(0, 1)
ax.set_xlabel(r"Kendall $\tau$ between two models")
ax.set_title("c)   Agreement of consensus orders")
ax.grid(axis="y", visible=False)
ax = fig.add_subplot(gs[1, 1])
w = syn.pivot(index="seed", columns="population", values="within_share").loc[SEEDS]
for i, s in enumerate(SEEDS):
    ax.plot([w.loc[s, "melanoma"], w.loc[s, "non_melanoma"]], [i, i], color=GREY, lw=2, zorder=1)
    for p in pops:
        ax.scatter(
            w.loc[s, p],
            i,
            s=190 if s == SEL else 130,
            color=PCOL[p],
            zorder=3,
            edgecolor=BLACK if s == SEL else "none",
            lw=2.5,
        )
ax.set_yticks(range(len(SEEDS)), [f"Seed {s}" for s in SEEDS])
ax.set_ylim(len(SEEDS) - 0.5, -0.5)
ax.yaxis.tick_right()
ax.set_xlim(0, 1)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Share within images")
ax.set_title("d)   Ambiguity within images")
ax.grid(axis="y", visible=False)
h = [
    Line2D([], [], marker="o", ls="", color=BLUE, ms=14),
    Line2D([], [], marker="o", ls="", color=BROWN, ms=14),
    Line2D([], [], marker="o", ls="", mfc="white", mec=GREY, mew=2.2, ms=12),
    Line2D([], [], color=GREY, lw=2),
]
arrange(
    fig,
    [fig.axes[0:2], fig.axes[2:4]],
    widths=[4.87, 4.87],
    heights=[None, 3.25],
    legend=(h, ["Melanoma", "Non-melanoma", "Other seeds", "Range over seeds"], 4),
)
save(fig, "fig5_seeds")
