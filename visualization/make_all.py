"""Build every figure and the table of the manuscript from the csv files in ../results."""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = [
    "fig0_pipeline.py",
    "fig1_reliance.py",
    "fig2_ambiguity.py",
    "fig3_pairs.py",
    "fig4_exchanges_tiers.py",
    "fig5_seeds.py",
    "fig6_global_local.py",
    "tables.py",
]


def main():
    """Run every figure script and the table script in turn."""
    sys.path.insert(0, str(HERE))
    argv = sys.argv
    try:
        for name in SCRIPTS:
            print(f"Running {name}")
            sys.argv = [name]
            runpy.run_path(str(HERE / name), run_name="__main__")
    finally:
        sys.argv = argv
    print("Figures written to visualization/figures")
    print("Table written to visualization/tables")


if __name__ == "__main__":
    main()
