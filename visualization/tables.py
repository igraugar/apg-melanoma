"""Table 1 of the manuscript and the split counts quoted in the setting of the experiments.

Run with --tex path/to/manuscript.tex to check that the table, the split sentence and the figure files
match the manuscript source.
"""

import argparse
from decimal import ROUND_HALF_UP, Decimal

from style import FIGURES, TABLES, csv

FIGURE_NAMES = [
    "fig0_pipeline",
    "fig1_reliance",
    "fig2_ambiguity",
    "fig3_pairs",
    "fig4_exchanges_tiers",
    "fig5_seeds",
    "fig6_global_local",
]


def r3(x):
    """Round half up to three decimals, as printed in the manuscript."""
    return str(Decimal(str(x)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def split_sentence():
    """Return the sentence with the image counts of the three splits."""
    sp = csv("split_summary").set_index("split")
    return (
        f"The asymmetric-filter split holds {sp.loc['train', 'images']} training images "
        f"({sp.loc['train', 'melanoma']} melanomas), "
        f"{sp.loc['valid', 'images']} validation images ({sp.loc['valid', 'melanoma']} melanomas) as well as "
        f"{sp.loc['test', 'images']} test images ({sp.loc['test', 'melanoma']} melanomas)."
    )


def table_correct():
    """Return Table 1 as LaTeX, with the correctly classified test images and the test performance per seed."""
    sp = csv("split_summary").set_index("split")
    sel = csv("model_selection").set_index("seed")
    perf = csv("model_performance").query("split == 'test'").set_index("seed")
    n_mel, n_non = sp.loc["test", "melanoma"], sp.loc["test", "non_melanoma"]
    best = int(sel["test_label_f1"].idxmax())
    rows = "\n".join(
        f"{s} & {sel.loc[s, 'test_images_melanoma']} of {n_mel} & {sel.loc[s, 'test_images_non_melanoma']} of {n_non} & "
        f"{r3(perf.loc[s, 'label_acc'])} & {r3(perf.loc[s, 'label_f1'])} & {r3(perf.loc[s, 'auroc'])} & "
        f"{r3(perf.loc[s, 'concept_acc'])} \\\\"
        for s in sel.index
    )
    return (
        r"""\begin{table}[!ht]
\caption{Correctly classified test images per seed, with the test diagnosis performance of the deployed hard CBM. Seed """
        + str(best)
        + r""", with the largest F1 score, is the model of the first as well as the third experiment.}\label{tab:correct}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccccc@{}}
\toprule
Seed & Melanoma & Non-melanoma & Accuracy & F1 & AUROC & Concept accuracy \\
\midrule
"""
        + rows
        + r"""
\botrule
\end{tabular*}
\end{table}"""
    )


def check_manuscript(tex_path, table, sentence):
    """Compare the table, the split sentence and the figure files with the manuscript source."""
    src = open(tex_path, encoding="utf-8").read()
    for name, text in [("tab:correct", table), ("split sentence", sentence)]:
        print(name, "identical to the manuscript" if text in src else "DIFFERS from the manuscript")
    for f in FIGURE_NAMES:
        print(
            f,
            "included in the manuscript" if f"figures/{f}.pdf" in src else "NOT referenced in the manuscript",
            "| written" if (FIGURES / f"{f}.pdf").exists() else "| MISSING",
        )


def main():
    """Write Table 1 to the tables folder and print the split sentence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex", help="manuscript source to compare with (optional)")
    args = parser.parse_args()

    sentence, table = split_sentence(), table_correct()
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "tab_correct.tex").write_text(table + "\n", encoding="utf-8")
    print(sentence, "\n")
    print(table, "\n")
    if args.tex:
        check_manuscript(args.tex, table, sentence)


if __name__ == "__main__":
    main()
