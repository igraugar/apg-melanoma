"""Figure 2 of the manuscript. Mean position of every concept per population, and its shift with the predicted state."""

from style import *
from matplotlib.lines import Line2D

con = csv("case_T3_consensus").query("seed == @SEL")
st = csv("case_T3_states").query("seed == @SEL")
fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 15), layout="constrained", gridspec_kw={"height_ratios": [7, 9]})
fig.get_layout_engine().set(**LAYOUT)
for k, pop in enumerate(["melanoma", "non_melanoma"]):
    ax = axes[0, k]
    c = con[con.population == pop].sort_values("mean_position").reset_index(drop=True)
    y = np.arange(len(c))
    ax.errorbar(
        c.mean_position,
        y,
        xerr=[c.mean_position - c.mean_position_lo, c.mean_position_hi - c.mean_position],
        fmt="o",
        color=PCOL[pop],
        ms=13,
        elinewidth=3,
        capsize=6,
    )
    ax.set_yticks(y, [SHORT[x] for x in c.concept])
    ax.invert_yaxis()
    ax.set_xlim(0.6, 7.4)
    ax.set_xticks(range(1, 8))
    ax.set_xlabel("Mean position")
    ax.set_title(f"{'ab'[k]})   {PLAB[pop]}")
    # states of the three concepts whose position depends most on the predicted state
    ax = axes[1, k]
    ok = st[(st.population == pop) & (st.images >= 5)].groupby("concept").size()
    cand = c[c.concept.isin(ok[ok >= 2].index)]
    top = cand.sort_values("between_explained_by_state", ascending=False).concept.head(3).tolist()
    s = st[(st.population == pop) & st.concept.isin(top) & (st.images >= 5)].copy()
    s["order"] = s.concept.map({x: i for i, x in enumerate(top)})
    s = s.sort_values(["order", "mean_position"]).reset_index(drop=True)
    y = np.arange(len(s))
    for i, r in s.iterrows():
        ax.hlines(
            i, c.set_index("concept").loc[r.concept, "mean_position"], r.mean_position, color=GREY, lw=2, zorder=1
        )
    ax.scatter(
        c.set_index("concept").loc[s.concept, "mean_position"], y, marker="|", s=500, color=BLACK, lw=3, zorder=2
    )
    ax.scatter(s.mean_position, y, color=PCOL[pop], s=170, zorder=3)
    ax.set_yticks(
        y, [f"{SHORT[a]}, {b}" for a, b in zip(s.concept, s.predicted_state.str.replace("localized", "local."))]
    )
    ax.invert_yaxis()
    ax.set_xlim(0.6, 7.4)
    ax.set_xticks(range(1, 8))
    ax.set_xlabel("Mean position")
    ax.set_title(f"{'cd'[k]})   {PLAB[pop]} by state")
for ax in axes[:, 1]:
    ax.yaxis.tick_right()
h = [
    Line2D([], [], marker="o", ls="", color=BLUE, ms=13),
    Line2D([], [], marker="o", ls="", color=BROWN, ms=13),
    Line2D([], [], marker="|", ls="", color=BLACK, ms=22, mew=3),
]
arrange(
    fig,
    [list(axes[0]), list(axes[1])],
    widths=[3.94, 3.94],
    legend=(h, ["Melanoma", "Non-melanoma", "Mean position of the concept"], 3),
)
save(fig, "fig1_reliance")
