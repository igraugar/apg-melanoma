"""Figure 5 of the manuscript. Concept exchanges that drive the distance between explanations, and the ordered tiers."""

from style import *
from matplotlib.patches import FancyBboxPatch

ex = csv("case_T6_pairs").query("seed == @SEL")
face = csv("case_T7_face").query("seed == @SEL").set_index("population")
bd = csv("case_T7_boundaries").query("seed == @SEL & tiering == 'selected face'")
fig = plt.figure(figsize=(WIDTH, 16), layout="constrained")
fig.get_layout_engine().set(**LAYOUT)
gs = fig.add_gridspec(3, 2, height_ratios=[6, 4.2, 4.2])
pops = ["melanoma", "non_melanoma"]
for k, p in enumerate(pops):
    ax = fig.add_subplot(gs[0, k])
    e = ex[ex.population == p].sort_values("distance_share", ascending=False).head(6).reset_index(drop=True)
    y = np.arange(len(e))
    ax.barh(y, e.distance_share, color=PCOL[p], height=0.6)
    ax.errorbar(
        e.distance_share,
        y,
        xerr=[e.distance_share - e.share_lo, e.share_hi - e.distance_share],
        fmt="none",
        ecolor=BLACK,
        elinewidth=2.5,
        capsize=7,
        capthick=2.5,
    )
    ax.set_yticks(y, [f"{SHORT[a]} \u2194 {SHORT[b]}" for a, b in zip(e.concept_a, e.concept_b)])
    ax.set_ylim(len(e) - 0.5, -0.5)
    ax.set_xlim(0, 0.175)
    ax.set_xticks([0, 0.05, 0.1, 0.15], ["0%", "5%", "10%", "15%"])
    ax.set_xlabel("Share of the distance")
    ax.set_title(f"{'ab'[k]})   {PLAB[p]}")
    ax.grid(axis="y", visible=False)
    if k == 1:
        ax.yaxis.tick_right()
# ordered tiers drawn as boxes, with the share of cross-boundary orders that the explanations reverse
for k, p in enumerate(pops):
    ax = fig.add_subplot(gs[1 + k, :])
    tiers = [[AB2SHORT[a] for a in t.split(",")] for t in face.loc[p, "tiers"].split(" | ")]
    rev = bd[bd.population == p].crossing_share.tolist()
    q = len(tiers)
    bw, gap = 3.0, 1.6
    xs = [i * (bw + gap) for i in range(q)]
    hmax = max(len(t) for t in tiers)
    for i, t in enumerate(tiers):
        hgt = 0.62 * len(t) + 0.4
        ax.add_patch(
            FancyBboxPatch(
                (xs[i], (hmax * 0.62 + 0.4 - hgt) / 2),
                bw,
                hgt,
                boxstyle="round,pad=0.05,rounding_size=0.15",
                facecolor="white",
                edgecolor=PCOL[p],
                lw=3,
            )
        )
        for j, c in enumerate(t):
            ax.text(
                xs[i] + bw / 2, (hmax * 0.62 + 0.4) / 2 + (len(t) - 1) * 0.31 - j * 0.62, c, ha="center", va="center"
            )
        ax.text(
            xs[i] + bw / 2,
            hmax * 0.62 + 0.75,
            f"Tier {i + 1}",
            ha="center",
            va="center",
            fontweight="bold",
            color=PCOL[p],
        )
        if i < q - 1:
            xm = xs[i] + bw + gap / 2
            ax.annotate(
                "",
                xy=(xm + 0.35, (hmax * 0.62 + 0.4) / 2),
                xytext=(xm - 0.35, (hmax * 0.62 + 0.4) / 2),
                arrowprops=dict(arrowstyle="-|>", color=BLACK, lw=2.5, mutation_scale=28),
            )
            ax.text(xm, (hmax * 0.62 + 0.4) / 2 - 0.55, f"{100 * rev[i]:.0f}%", ha="center", va="top", color=GREY)
    total = xs[-1] + bw
    ax.set_xlim(-0.3 - (4 * (bw + gap) - gap - total) / 2, total + 0.3 + (4 * (bw + gap) - gap - total) / 2)
    ax.set_ylim(-0.4, hmax * 0.62 + 1.1)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(f"{'cd'[k]})   {PLAB[p]}, ordered tiers")
arrange(fig, [fig.axes[0:2], [fig.axes[2]], [fig.axes[3]]], widths=[3.16, 15.0, 15.0], heights=[4.44, None, None])
save(fig, "fig4_exchanges_tiers")
