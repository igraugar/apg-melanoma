"""Figure 1 of the manuscript. Schematic of the interpretability pipeline, from local SOFI explanations to a
global explanation. The rankings, arrows and support values are illustrative and are not read from the results."""

import itertools

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from scipy.spatial import ConvexHull

from style import *

# ---------------- permutohedron of order 4 (truncated octahedron) ----------------
P = np.array(list(itertools.permutations([1, 2, 3, 4])), float)
P -= P.mean(1, keepdims=True)
Bs = np.linalg.qr(np.vstack([np.ones(4), np.eye(4)[:3]]).T)[0][:, 1:4]
V = P @ Bs
V /= np.abs(V).max()
hull = ConvexHull(V)
faces = []
for eq in np.unique(np.round(hull.equations, 6), axis=0):
    idx = np.where(np.abs(V @ eq[:3] + eq[3]) < 1e-6)[0]
    c = V[idx].mean(0)
    n = eq[:3]
    u = V[idx[0]] - c
    u /= np.linalg.norm(u)
    w = np.cross(n, u)
    ang = np.arctan2((V[idx] - c) @ w, (V[idx] - c) @ u)
    faces.append((idx[np.argsort(ang)], n))
edges = {
    tuple(sorted((a, b)))
    for a, b in itertools.combinations(range(24), 2)
    if np.sum(P[a] != P[b]) == 2 and abs(np.abs(P[a] - P[b]).max() - 1) < 1e-9
}


def rot(ax_, ay_, az_=0.0):
    """Return the 3D rotation matrix for rotations about the x, y and z axes."""
    cx, sx, cy, sy, cz, sz = np.cos(ax_), np.sin(ax_), np.cos(ay_), np.sin(ay_), np.cos(az_), np.sin(az_)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


SC_BLUE_D, SC_BLUE, SC_BLUE_L, SC_RED, SC_RED_L, SC_GREYV, SC_NAVY = (
    "#2c63ad",
    "#4a86cf",
    "#a9c7ea",
    "#c9362c",
    "#eab3a8",
    "#8c9199",
    "#2d3e52",
)
SC_CMAP = LinearSegmentedColormap.from_list("bw", [SC_RED, "#f3dcd6", "#eef2f8", "#bcd3ee", SC_BLUE])


def draw_poly(ax, cx, cy, s, R, face_color, vert_color, lw=1.6, vsize=1.0, alpha=0.78):
    """Draw the rotated permutohedron with shaded faces, edges and front vertices."""
    X = V @ R.T
    xy = np.c_[cx + s * X[:, 0], cy + s * X[:, 1]]
    order = sorted(range(len(faces)), key=lambda i: (R @ faces[i][1])[2])
    for i in order:
        idx, n = faces[i]
        front = (R @ n)[2] > 0
        fc = face_color(i, X[idx][:, 1].mean())
        ax.add_patch(
            Polygon(
                xy[idx],
                closed=True,
                facecolor=fc,
                edgecolor="none",
                alpha=alpha if front else 0.35,
                zorder=2 if front else 1,
            )
        )
    for a, b in edges:
        front = any((R @ faces[i][1])[2] > 0 for i in range(len(faces)) if a in faces[i][0] and b in faces[i][0])
        ax.plot(
            xy[[a, b], 0],
            xy[[a, b], 1],
            color=SC_NAVY if front else "#9aa7b8",
            lw=lw if front else lw * 0.6,
            alpha=0.85 if front else 0.5,
            zorder=3 if front else 1.5,
            solid_capstyle="round",
        )
    for k in range(24):
        if X[k, 2] < -0.25:
            continue
        ax.add_patch(
            Circle(xy[k], 0.06 * s * vsize, facecolor=vert_color(k, X[k, 1]), edgecolor="#1e2a38", lw=0.8, zorder=4)
        )
    return xy, X


def ycol(y):
    """Map a vertical coordinate in [-1, 1] to the colormap of concept positions."""
    return SC_CMAP((y + 1) / 2)


def vcol(k, y):
    """Color a vertex by its height, with alternating colors in the middle band."""
    if y > 0.45:
        return SC_BLUE
    if y < -0.45:
        return SC_RED
    return [SC_GREYV, SC_NAVY, SC_RED, SC_BLUE][k % 4]


W_, H_ = WIDTH, 18.05
fig = plt.figure(figsize=(W_, H_))
M, G, T, PH = 0.2, 0.3, 0.95, 5.4
PW = (W_ - 2 * M - G) / 2
fig.text(
    0.5,
    1 - 0.45 / H_,
    "From local to global explanations via algebraic population geometry",
    ha="center",
    va="center",
    fontsize=FS + 5,
)


def panel(r, c, title):
    """Add a framed, titled panel at row r and column c of the grid."""
    x0 = M + c * (PW + G)
    y0 = H_ - T - (r + 1) * PH - r * G
    ax = fig.add_axes([x0 / W_, y0 / H_, PW / W_, PH / H_])
    ax.set_xlim(0, PW)
    ax.set_ylim(0, PH)
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0.03, 0.03),
            PW - 0.06,
            PH - 0.06,
            boxstyle="round,pad=0,rounding_size=0.08",
            facecolor="white",
            edgecolor="#3b4450",
            lw=1.4,
            zorder=0,
        )
    )
    ax.text(0.3, PH - 0.42, title, fontsize=FS + 2, fontweight="bold", va="center", ha="left")
    return ax, x0, y0


MINUS = "\u2212"
# ---------------- a) local SOFI explanations ----------------
ax, _, _ = panel(0, 0, "a)   Local SOFI explanations")
bar = [SC_BLUE_D, SC_BLUE, "#76a6de", SC_BLUE_L, "#f0d4cd", "#e39a8d", SC_RED]
rows = [
    ("Image 1", r"$c_3 > c_1 > c_5 > c_2 > c_4 > c_6 > c_7$"),
    ("Image 2", r"$c_1 > c_3 > c_2 > c_5 > c_4 > c_6 > c_7$"),
    ("Image N", r"$c_2 > c_1 > c_4 > c_3 > c_5 > c_6 > c_7$"),
]
ys = [4.0, 2.55, 1.1]
for i, ((lab, rk), y) in enumerate(zip(rows, ys)):
    img = plt.imread(ASSETS / f"lesion{i + 1}.png")
    ax.imshow(img, extent=(0.45, 1.45, y - 0.5, y + 0.5), zorder=3)
    ax.add_patch(Rectangle((0.45, y - 0.5), 1.0, 1.0, fill=False, edgecolor="#b8a79c", lw=0.8, zorder=4))
    ax.text(1.8, y + 0.32, lab, fontsize=FS, va="center")
    for j, cc in enumerate(bar):
        ax.add_patch(Rectangle((3.2 + j * 0.62, y + 0.14), 0.58, 0.36, facecolor=cc, edgecolor="none", zorder=3))
    ax.text(1.8, y - 0.3, rk, fontsize=FS, va="center")
for y in (3.28, 1.83, 0.4):
    ax.text(0.95, y, r"$\vdots$", fontsize=FS, ha="center", va="center")

# ---------------- b) moment polytope ----------------
ax, _, _ = panel(0, 1, "b)   Moment polytope (permutohedron)")
R = rot(0.35, 0.55, 0.12)
cx, cy, s = 3.3, 2.35, 1.45
draw_poly(ax, cx, cy, s, R, lambda i, y: ycol(y), vcol)
ax.add_patch(Circle((cx + 0.05, cy + 0.02), 0.07, facecolor="#1f2d3d", zorder=6))
ax.text(
    cx + 0.18,
    cy + 0.02,
    "population\nbarycenter",
    fontsize=FS,
    va="center",
    ha="left",
    zorder=7,
    linespacing=1.1,
    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.65),
)
for dx, dy, lab, ha, va in [
    (0, 1.0, r"$p_1$", "left", "center"),
    (-1.0, -0.55, r"$p_2$", "right", "top"),
    (1.0, -0.55, r"$p_3$", "left", "top"),
]:
    nrm = np.hypot(dx, dy)
    base = (cx + dx / nrm * 1.28, cy + dy / nrm * 1.28)
    tip = (cx + dx / nrm * 1.85, cy + dy / nrm * 1.85)
    ax.annotate(
        "", xy=tip, xytext=base, arrowprops=dict(arrowstyle="-|>", color="black", lw=2, mutation_scale=22), zorder=5
    )
    ax.text(
        tip[0] + (0.1 if ha == "left" else -0.1),
        tip[1] + (0.0 if va == "center" else -0.02),
        lab,
        fontsize=FS + 2,
        ha=ha,
        va=va,
    )
cbx, cby0, cby1 = 7.2, 0.5, 3.45
n = 80
for k in range(n):
    ax.add_patch(
        Rectangle(
            (cbx, cby0 + k * (cby1 - cby0) / n),
            0.3,
            (cby1 - cby0) / n + 0.005,
            facecolor=SC_CMAP(k / (n - 1)),
            edgecolor="none",
        )
    )
ax.add_patch(Rectangle((cbx, cby0), 0.3, cby1 - cby0, fill=False, edgecolor="#333", lw=1))
ax.text(cbx + 0.15, cby1 + 0.55, "concept\nposition", fontsize=FS, ha="center", va="center", linespacing=1.1)
ax.text(cbx - 0.12, cby1 - 0.2, "high", fontsize=FS, ha="right", va="center")
ax.text(cbx - 0.12, cby0 + 0.2, "low", fontsize=FS, ha="right", va="center")

# ---------------- c) exchange geometry ----------------
ax, x0, y0 = panel(1, 0, "c)   Exchange geometry")
ia = fig.add_axes([(x0 + 2.0) / W_, (y0 + 1.1) / H_, 4.3 / W_, 3.4 / H_])
ia.set_xlim(-0.4, 0.5)
ia.set_ylim(-0.4, 0.4)
tk = [-0.4, -0.2, 0, 0.2, 0.4]
tl = [MINUS + "0.4", MINUS + "0.2", "0.0", "0.2", "0.4"]
ia.set_xticks(tk, tl)
ia.set_yticks(tk, tl)
ia.grid(False)
for sp in ["top", "right"]:
    ia.spines[sp].set_visible(False)
ia.spines["left"].set_color("black")
ia.spines["bottom"].set_color("black")
th = np.linspace(0, 2 * np.pi, 200)
ia.plot(0.35 * np.cos(th), 0.35 * np.sin(th), ls=(0, (4, 4)), color="#7fa7d8", lw=1.2)
ia.axhline(0, ls=(0, (4, 4)), color="#7fa7d8", lw=1.2)
ia.axvline(0, ls=(0, (4, 4)), color="#7fa7d8", lw=1.2)
arrows = [
    ((0.12, 0.33), SC_BLUE_D, r"$c_1$ vs $c_2$", (0.14, 0.39), "left"),
    ((0.32, 0.24), SC_BLUE_D, r"$c_1$ vs $c_3$", (0.36, 0.28), "left"),
    ((0.34, 0.0), SC_BLUE, r"$c_2$ vs $c_5$", (0.39, 0.03), "left"),
    ((0.25, -0.2), SC_GREYV, r"$c_4$ vs $c_7$", (0.3, -0.23), "left"),
    ((-0.23, -0.19), SC_RED, r"$c_3$ vs $c_6$", (-0.25, -0.3), "center"),
    ((-0.3, 0.12), SC_RED, r"$c_5$ vs $c_7$", (-0.2, 0.2), "center"),
]
for tip, col, lab, pos, ha in arrows:
    ia.annotate("", xy=tip, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=3, mutation_scale=24))
    ia.text(*pos, lab, fontsize=FS, ha=ha, va="center", clip_on=False)
ia.set_xlabel("exchange coordinate 1")
ia.set_ylabel("exchange coordinate 2")

# ---------------- d) Lie algebra closure ----------------
ax, _, _ = panel(1, 1, "d)   Lie algebra closure")
R = rot(0.45, 0.35, -0.1)
cx, cy, s = 3.5, 2.35, 1.4
dcols = [SC_BLUE_L, "#e7b1a8", "#cfd2d6", "#9fbfe6", "#d98f86", "#bfc4ca", "#b5cfee"]
draw_poly(ax, cx, cy, s, R, lambda i, y: dcols[i % len(dcols)], vcol, vsize=0.85)
arcs = [
    ((-1.35, 1.35), (-0.4, 1.7), SC_GREYV),
    ((0.1, 1.72), (1.05, 1.4), SC_BLUE_D),
    ((1.55, 0.8), (1.6, -0.3), SC_BLUE_D),
    ((1.35, -0.75), (0.6, -1.4), SC_RED),
    ((0.2, -1.6), (-0.8, -1.4), SC_GREYV),
    ((-1.45, -0.9), (-1.65, 0.1), SC_RED),
    ((-1.65, 0.5), (-1.45, 1.0), SC_RED),
    ((1.2, 1.25), (1.6, 0.95), SC_GREYV),
]
for a, b, col in arcs:
    ax.add_patch(
        FancyArrowPatch(
            (cx + a[0], cy + a[1]),
            (cx + b[0], cy + b[1]),
            connectionstyle="arc3,rad=-0.45",
            arrowstyle="-|>",
            color=col,
            lw=2.2,
            mutation_scale=20,
            zorder=6,
        )
    )
ax.text(6.9, 3.85, "Lie generators", fontsize=FS, ha="center", va="center")
for k, (col, lab) in enumerate([(SC_BLUE_D, "g_1"), (SC_RED, "g_2"), (SC_GREYV, "g_3")]):
    yy = 3.15 - 0.65 * k
    ax.annotate(
        "", xy=(6.95, yy), xytext=(6.05, yy), arrowprops=dict(arrowstyle="-|>", color=col, lw=2.6, mutation_scale=22)
    )
    ax.text(7.15, yy, f"${lab}$", fontsize=FS + 2, va="center")
o = (1.45, 0.8)
for d, lab, off in [
    ((0, 0.7), "g_3", (-0.4, 0.05)),
    ((0.75, -0.25), "g_1", (0.12, -0.15)),
    ((-0.6, -0.35), "g_2", (-0.4, -0.12)),
]:
    ax.annotate(
        "",
        xy=(o[0] + d[0], o[1] + d[1]),
        xytext=o,
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.6, mutation_scale=16),
    )
    ax.text(o[0] + d[0] + off[0], o[1] + d[1] + off[1], f"${lab}$", fontsize=FS + 1, va="center")

# ---------------- e) ordered concept tiers ----------------
ax, _, _ = panel(2, 0, "e)   Ordered concept tiers")
SC_TIER = ["#5b8fd1", "#cbb9a8", "#d8544b"]


def tier_col(i, y):
    """Color a face by the tier its height falls into."""
    return SC_TIER[0] if y > 0.3 else (SC_TIER[1] if y > -0.3 else SC_TIER[2])


def tier_v(k, y):
    """Color a vertex by the tier its height falls into."""
    return SC_BLUE if y > 0.3 else (SC_GREYV if y > -0.3 else SC_RED)


draw_poly(ax, 2.0, 2.75, 1.45, rot(0.35, 0.5, 0.1), tier_col, tier_v)
for cxs, rr in [(4.3, rot(0.2, 0.9)), (5.5, rot(0.6, 0.2, 0.3)), (7.45, rot(-0.2, 1.2))]:
    draw_poly(ax, cxs, 1.45, 0.55, rr, lambda i, y: SC_CMAP((y + 1) / 2), tier_v, lw=0.9, vsize=1.3)
ax.text(6.5, 1.4, r"$\cdots$", fontsize=FS + 2, ha="center", va="center")
ax.annotate(
    "",
    xy=(8.0, 0.55),
    xytext=(0.35, 0.55),
    arrowprops=dict(arrowstyle="<|-|>", color="black", lw=1.6, mutation_scale=18),
)
ax.text(4.2, 0.3, "different views", fontsize=FS, ha="center", va="center")
ax.text(4.9, 4.2, "tiers", fontsize=FS, va="center")
for k, (col, lab) in enumerate(zip(SC_TIER, ["primary", "secondary", "tertiary"])):
    yy = 3.7 - 0.5 * k
    ax.add_patch(Rectangle((4.9, yy - 0.18), 0.38, 0.36, facecolor=col, edgecolor="none"))
    ax.text(5.42, yy, lab, fontsize=FS, va="center")

# ---------------- f) global explanation ----------------
ax, _, _ = panel(2, 1, "f)   Global explanation")
ax.text(0.3, 4.4, "Consensus ranking (Borda)", fontsize=FS, va="center")
labs = ["c_3", "c_1", "c_5", "c_2", "c_4", "c_6", "c_7"]
cols = [SC_BLUE_D, SC_BLUE, "#76a6de", "#9fb0c6", "#d8c2b6", "#e39a8d", SC_RED]
for j, (cc, lb) in enumerate(zip(cols, labs)):
    ax.add_patch(Rectangle((0.3 + j * 0.62, 3.78), 0.58, 0.38, facecolor=cc, edgecolor="none"))
    ax.text(0.3 + j * 0.62 + 0.29, 3.52, f"${lb}$", fontsize=FS, ha="center", va="center")
ax.text(0.3, 3.12, "Majority cycles", fontsize=FS, va="center")
nodes = {"c_1": (1.25, 2.72, SC_BLUE), "c_3": (0.72, 2.2, SC_RED), "c_5": (1.78, 2.2, SC_GREYV)}
for lb, (x, y, cc) in nodes.items():
    ax.add_patch(Circle((x, y), 0.23, facecolor=cc, edgecolor="white", lw=1.5, zorder=3))
    ax.text(x, y, f"${lb}$", fontsize=FS, ha="center", va="center", color="white", zorder=4)
for a, b, cc in [("c_3", "c_1", SC_RED), ("c_1", "c_5", SC_BLUE), ("c_5", "c_3", SC_RED)]:
    ax.add_patch(
        FancyArrowPatch(
            nodes[a][:2],
            nodes[b][:2],
            connectionstyle="arc3,rad=-0.35",
            arrowstyle="-|>",
            color=cc,
            lw=2.2,
            mutation_scale=18,
            shrinkA=15,
            shrinkB=15,
            zorder=2,
        )
    )
ax.plot([2.45, 2.45], [2.0, 2.95], color="#555", lw=1)
ax.text(
    2.65, 2.48, "No single ranking agrees with\nthe majority on every pair.", fontsize=FS, va="center", linespacing=1.15
)
ax.text(0.3, 1.72, "Ordered tiers", fontsize=FS, va="center")
trow = [
    ("Tier 1 (primary)", ["c_3", "c_1", "c_5"], "#bcd7f3"),
    ("Tier 2 (secondary)", ["c_2", "c_4"], "#e3dfdb"),
    ("Tier 3 (tertiary)", ["c_6", "c_7"], "#f1c1bd"),
]
for k, (lb, cs, cc) in enumerate(trow):
    yy = 1.28 - 0.44 * k
    ax.add_patch(
        FancyBboxPatch(
            (0.3, yy - 0.2), 4.45, 0.4, boxstyle="round,pad=0,rounding_size=0.06", facecolor=cc, edgecolor="none"
        )
    )
    ax.text(0.4, yy, lb, fontsize=FS, va="center")
    for m, c_ in enumerate(cs):
        ax.text(3.35 + m * 0.5, yy, f"${c_}$", fontsize=FS, va="center", ha="center")
ax.plot([4.95, 4.95], [0.15, 1.85], color="#555", lw=1)
ax.text(5.15, 1.72, "Support", fontsize=FS, va="center")
for k, t in enumerate(["Consensus: 0.72", "Majority sign: 0.68", r"Tier ($c_3 > c_1$): 0.64", "..."]):
    ax.text(5.15, 1.28 - 0.32 * k, t, fontsize=FS, va="center")

FIGURES.mkdir(parents=True, exist_ok=True)
fig.savefig(FIGURES / "fig0_pipeline.pdf")
plt.close(fig)
