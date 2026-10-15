# Algebraic Population Geometry for Concept-Based Explanations in Melanoma Diagnosis

This package reproduces the experiments, figures and tables of the paper "Algebraic Population Geometry for Concept-Based Explanations in Melanoma Diagnosis". We separate the work into two independent stages. The first stage trains the concept bottleneck models and runs every experiment, writing all results to csv files. The second stage reads those csv files and draws the figures and the table without computing any new results.

## Structure

```
reproduction/
├── experiments/
│   ├── Derm7pt_APG_CaseStudy.ipynb   model training and all experiments (Google Colab, GPU)
│   └── requirements.txt
├── results/                          the 49 csv files written by the notebook in our run
└── visualization/
    ├── style.py                      shared style, data access and panel layout
    ├── fig0_pipeline.py ... fig6_global_local.py
    ├── tables.py                     Table 1 and the split counts quoted in the text
    ├── make_all.py                   builds every figure and the table
    ├── make_all.ipynb                runs make_all.py and shows the results inline
    ├── assets/                       the three lesion thumbnails of Figure 1
    └── requirements.txt
```

## Stage 1. Experiments

The notebook `experiments/Derm7pt_APG_CaseStudy.ipynb` runs on Google Colab with a GPU (we used a T4). Part 1 trains a hard concept bottleneck model with an EfficientNet-B4 backbone for each of the five seeds (42, 64, 128, 256 and 512). Part 2 reloads these checkpoints, explains every correctly classified lesion with SOFI and runs the three experiments of the manuscript. The last cell writes one csv file per table type to the `csv` subfolder of the output folder.

The notebook needs the Derm7pt dataset (Kawahara et al., 2019), which is available from https://derm.cs.sfu.ca after registration. The dataset cannot be redistributed, so it is not part of this package. The global settings cell defines every path from `PROJECT_DIR`, and the notebook expects the following layout.

```
PROJECT_DIR/
├── meta/             meta.csv together with train_indexes.csv, valid_indexes.csv and test_indexes.csv
├── images_cropped/   the dermoscopic images
├── models/           written by Part 1 (checkpoints, logs, predictions, manifest)
└── APG_outputs/      written by Part 2 (console log, text summaries, csv folder)
```

The saved outputs of the notebook document our run. The folder `results/` holds the csv files of that run, which are the reference results of the manuscript. Training on a GPU is not bit-exact across hardware and library versions, so a new run may give slightly different numbers. To draw the figures from a new run, copy the `csv` folder of that run into `results/`.

Kawahara, J., Daneshvar, S., Argenziano, G., & Hamarneh, G. (2019). Seven-point checklist and skin lesion classification using multitask multimodal neural nets. *IEEE Journal of Biomedical and Health Informatics*, 23(2), 538–546.

## Stage 2. Figures and tables

The scripts in `visualization/` only read the csv files in `results/`. They filter, sort and arrange the stored values but compute no statistics. The seeds and the model of the first and third experiments are read from `results/model_selection.csv`.

```
pip install -r visualization/requirements.txt
python visualization/make_all.py
```

The notebook `visualization/make_all.ipynb` runs the same command and then shows every figure inline, so it also serves as a quick view of the results without running anything. The figures are written as PDF files to `visualization/figures/` and the table as a LaTeX fragment to `visualization/tables/`. Every script also runs on its own, for instance, `python visualization/fig3_pairs.py`. The command `python visualization/tables.py --tex manuscript.tex` additionally checks the table, the split counts and the figure files against a LaTeX source.

| Manuscript | Script | Output | Input files in `results/` |
|---|---|---|---|
| Figure 1 | `fig0_pipeline.py` | `fig0_pipeline.pdf` | none (schematic) |
| Figure 2 | `fig1_reliance.py` | `fig1_reliance.pdf` | `case_T3_consensus`, `case_T3_states` |
| Figure 3 | `fig2_ambiguity.py` | `fig2_ambiguity.pdf` | `case_T3_decomposition`, `sensitivity_beta0` |
| Figure 4 | `fig3_pairs.py` | `fig3_pairs.pdf` | `case_T4_walls` |
| Figure 5 | `fig4_exchanges_tiers.py` | `fig4_exchanges_tiers.pdf` | `case_T6_pairs`, `case_T7_face`, `case_T7_boundaries` |
| Figure 6 | `fig5_seeds.py` | `fig5_seeds.pdf` | `seeds_positions`, `seeds_pair_agreement`, `seeds_synthesis` |
| Figure 7 | `fig6_global_local.py` | `fig6_global_local.pdf` | `exp3_curves`, `exp3_image_level` |
| Table 1 | `tables.py` | `tab_correct.tex` | `split_summary`, `model_selection`, `model_performance` |

Figure 1 is a schematic of the pipeline. Its rankings, arrows and support values illustrate the method and are not read from the results. The remaining csv files in `results/` hold the complete output of the experiments, including the tables that the manuscript reports only in the text.
