"""Figure 7 of the manuscript. Removal curves of local and global rankings, and the local score kept by the best fixed
ranking."""

from style import *
from matplotlib.lines import Line2D

cu = csv("exp3_curves").query("seed == @SEL & fit_on == 'test'")
im = csv("exp3_image_level").query("seed == @SEL & fit_on == 'test' & method == 'best_fixed_ranking'")
fig, axes = plt.subplots(2, 3, figsize=(WIDTH, 10.5), layout="constrained")
fig.get_layout_engine().set(**LAYOUT)
pops = ["melanoma", "non_melanoma"]
lab = iter("abcdef")
for r, p in enumerate(pops):
    for c, curve in enumerate(["MoRF", "LeRF"]):
        ax = axes[r, c]
        d = cu[(cu.population == p) & (cu.curve == curve)]
        for m, g in d.groupby("method"):
            if m in ("local_sofi", "best_fixed_ranking"):
                continue
            ax.plot(g.concepts_removed, g.mean_centered_sd, color=GREY, lw=1.8, alpha=0.8)
        g = d[d.method == "best_fixed_ranking"]
        ax.plot(g.concepts_removed, g.mean_centered_sd, color=BLACK, lw=3)
        g = d[d.method == "local_sofi"]
        ax.fill_between(g.concepts_removed, g.boot_lo, g.boot_hi, color=PCOL[p], alpha=0.25, lw=0)
        ax.plot(g.concepts_removed, g.mean_centered_sd, color=PCOL[p], lw=3.5)
        ax.axhline(0, color=GREY, lw=2, ls="--")
        ax.set_xticks(range(0, 8))
        ax.set_xlim(0, 7)
        ax.set_xlabel("Concepts removed")
        ax.set_ylabel("Centered score" if c == 0 else "")
        ax.set_title(f"{next(lab)})   {PLAB[p]}, {curve}")
    ylim = (
        min(axes[r, 0].get_ylim()[0], axes[r, 1].get_ylim()[0]),
        max(axes[r, 0].get_ylim()[1], axes[r, 1].get_ylim()[1]),
    )
    axes[r, 0].set_ylim(ylim)
    axes[r, 1].set_ylim(ylim)
    ax = axes[r, 2]
    x = im[im.population == p].retained_share.clip(-0.25, 1.0)
    sns.histplot(x, bins=np.linspace(-0.25, 1.0, 16), color=PCOL[p], ax=ax, stat="percent", edgecolor="white", alpha=1)
    ax.axvline(1.0, color=PCOL[p], lw=3)
    ax.axvline(0.0, color=GREY, lw=2, ls="--")
    ax.set_xlim(-0.3, 1.1)
    ax.set_xticks([0, 0.5, 1], ["0%", "50%", "100%"])
    ax.set_xlabel("Local score kept")
    ax.set_ylabel("Images (%)")
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set_title(f"{next(lab)})   {PLAB[p]}, best fixed")
h = [
    Line2D([], [], color=BLUE, lw=3.5),
    Line2D([], [], color=BROWN, lw=3.5),
    Line2D([], [], color=BLACK, lw=3),
    Line2D([], [], color=GREY, lw=1.8),
    Line2D([], [], color=GREY, lw=2, ls="--"),
]
arrange(
    fig,
    [list(axes[0]), list(axes[1])],
    widths=[4.2, 4.2],
    heights=[2.8, 2.8],
    legend=(
        h,
        [
            "Local SOFI, melanoma",
            "Local SOFI, non-melanoma",
            "Best fixed ranking",
            "Other global rankings",
            "Random ordering",
        ],
        3,
    ),
)
save(fig, "fig6_global_local")
