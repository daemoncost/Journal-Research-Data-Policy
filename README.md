# Journal Research Data Policies in Materials Science

## Description

This repository contains supplementary materials and code for the publication *"Journal Research Data Policies in Materials Science"*. It provides the data, analysis notebooks, and reusable tools to reproduce all figures and results from the article, which surveys research data policies (RDPs) of 171 materials science journals across 17 publishers.

## Installation

This project consists of Jupyter notebooks along with a set of reusable analysis tools (`daemon_analysis_tools`). To run the notebooks and use the tools, follow these steps:

1. Install Jupyter: If you don't have Jupyter installed, you can install it by following the instructions on the [Jupyter website](https://jupyter.org/install).

2. Install the analysis tools: Navigate to the root directory of the project and run:

```bash
pip install -e .
```

## Reproducing the Figures

| Figure | Description | Notebook |
|--------|-------------|----------|
| Fig. 1 | Overview of data and code sharing requirements (donut charts) | [analysis_data_sharing_requirements.ipynb](notebooks/exploration/analysis_data_sharing_requirements.ipynb) |
| Fig. 2 | Average open data score by question (bar chart) | [analysis_average_score_per_question.ipynb](notebooks/exploration/analysis_average_score_per_question.ipynb) |
| Fig. 3a | Open data score vs. impact factor | [analysis_policy_vs_impact_factor.ipynb](notebooks/exploration/analysis_policy_vs_impact_factor.ipynb) |
| Fig. 3b | Open data score vs. year of establishment | [analysis_policy_vs_year_of_establishment.ipynb](notebooks/exploration/analysis_policy_vs_year_of_establishment.ipynb) |
| Fig. 3c | Open data score vs. type of publisher (society/for-profit) | [analysis_policy_vs_society.ipynb](notebooks/exploration/analysis_policy_vs_society.ipynb) |
| Fig. 3d | Open data score vs. open access policy | [analysis_policy_vs_open_access.ipynb](notebooks/exploration/analysis_policy_vs_open_access.ipynb) |
| Fig. 4a | Consistency of the encoding process (pie chart) | [analyse_inconsistencies.ipynb](notebooks/exploration/analyse_inconsistencies.ipynb) |
| Fig. 4b | Open data score vs. encoding consistency | [analysis_policy_vs_consistency.ipynb](notebooks/exploration/analysis_policy_vs_consistency.ipynb) |

## Additional Analysis Notebooks

The following notebooks provide supplementary analyses beyond the main publication figures:

| Notebook | Description |
|----------|-------------|
| [analysis_policy_vs_consistency_per_journal.ipynb](notebooks/exploration/analysis_policy_vs_consistency_per_journal.ipynb) | Open data score vs. encoding consistency at the individual journal level (171 journals) rather than by publisher |
| [analysis_answer_question_sankey.ipynb](notebooks/exploration/analysis_answer_question_sankey.ipynb) | Sankey diagram showing the flow from coding questions to answers to open data scores |
| [Sankey_example.ipynb](notebooks/exploration/Sankey_example.ipynb) | Sankey diagram illustrating policy pathways from RDP existence through data availability to sharing requirements |
| [comparison_resnik2019_code_requirements.ipynb](notebooks/exploration/comparison_resnik2019_code_requirements.ipynb) | Comparison of code deposition requirements with Resnik et al. (2019) |
| [check_coverage.ipynb](notebooks/exploration/check_coverage.ipynb) | Overview of encoding coverage: number of independent encodings per journal and publisher |
| [Create_summary_table.ipynb](notebooks/exploration/Create_summary_table.ipynb) | Generates a comprehensive summary table with all publisher, journal, question, answer, and score data |

## Data Processing Notebooks

The [notebooks/fix_inconsistencies/](notebooks/fix_inconsistencies/) directory contains notebooks used during the data cleaning phase:

| Notebook | Description |
|----------|-------------|
| [check_inconsistencies.ipynb](notebooks/fix_inconsistencies/check_inconsistencies.ipynb) | Identifies all encoding discrepancies across publishers and journals |
| `fix_[publisher].ipynb` (14 notebooks) | Manually resolves encoding conflicts for each publisher by comparing answers from two independent encoders and documenting the reason for each discrepancy |
| [update_format.ipynb](notebooks/fix_inconsistencies/update_format.ipynb) | Reformats processed data files after schema changes |


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

This article is a result of joint work in
COST Action CA22154 - Data-driven Applications towards the Engineering of functional Materials: an Open
Network (DAEMON) supported by COST (European
Cooperation in Science and Technology)
