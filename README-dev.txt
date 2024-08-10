0. Installation

To install the package as a developer, run:
bash: pip install -e .[dev]
zsh: pip install -e .\[dev\]  

1. Repository Structure

This is an exmpale of how this repo can be organised.

root/
│
├── notebooks/              # Contains Jupyter notebooks for analysis
│   ├── exploration/        # Notebooks for initial data exploration and experiments
│   └── reports/            # Finalized analysis reports, cleaned and well-documented
│
├── daemon_analysis_tools/  # Python scripts and modules containing reusable functions
│   ├── __init__.py         # Makes this directory a package
│   ├── data_processing.py  # Functions for data cleaning and preprocessing
│   ├── analysis.py         # Core functions for analysis
│   └── visualization.py    # Functions for generating plots and visualizations
│
├── data/                   # Data used in analysis (avoid committing large datasets)
│   ├── raw/                # Raw data files
│   └── processed/          # Processed data files ready for analysis
│
├── tests/                  # Unit tests for the functions in the tools directory
│   ├── test_data_processing.py   # Tests for data processing functions
│   ├── test_analysis.py    # Tests for analysis functions
│   └── test_visualization.py   # Tests for visualization functions
│
├── .github/                # GitHub-specific files (e.g., workflows for CI/CD)
│   └── workflows/          # YAML files for GitHub Actions workflows
│
├── .gitignore              # Specifies files and directories to be ignored by git
├── README.md               # Overview of the project, how to get started, and structure
└── requirements.txt        # Python package dependencies

2. Coding Standards
PEP 8 Compliance: Follow the PEP 8 style guide for Python code. This includes naming conventions, indentation, line length, and more.

Docstrings: Use clear and descriptive docstrings for all functions and classes. Follow the PEP 257 guidelines.

Type Annotations: Include type annotations for function arguments and return types to enhance code readability and facilitate debugging.

Modular Code: Write modular code with functions and classes in the tools directory. Avoid putting complex logic directly 
in Jupyter notebooks—keep notebooks focused on using and combining functions for analysis.

Dependencies: add all the dependencies to the requirements.txt file. When choosing not a standard package, 
make sure that it is maintained and doesn't have weird dependencies itself. 

3. Version Control Best Practices
Branching Strategy:

Main Branch: The main branch should always be stable and ready for production. Only well-tested code should be merged here.
Feature Branches: For new features or bug fixes, create a separate branch (feature/feature-name or bugfix/bug-description) and submit a pull request for review.
Pull Requests (PRs): Before merging a PR, ensure it is reviewed by at least one other team member. Use descriptive titles and include a summary of changes.

Commit Messages:

Use clear and concise commit messages.
Follow the format: Type: Short description (fixes #issue-number)

4. Documentation

Notebooks:

Each notebook should start with a markdown cell that outlines its purpose, data sources, and any relevant background information.
Use markdown cells within notebooks to explain the steps and logic used in the analysis.
Avoid duplicating code in notebooks—use functions from the tools directory.

In-Line Comments:

Use in-line comments sparingly to explain complex or non-obvious code sections.

5. Testing
Unit Tests:

Write unit tests for all functions in the tools directory. Store tests in the tests/ directory.
Use pytest for testing and ensure that tests cover a range of possible inputs, including edge cases.
Run tests locally before pushing changes to ensure nothing is broken.

6. Pre-Commit 
Email Detection and Removal:
This repository is configured with a pre-commit hook that automatically checks for the presence of emails
in csv files before every commit. To manually run the pre-commit checks on all files, you can use the following command:

pre-commit run --all-files

Handling Detected Emails:
If emails are detected in any file, you can remove them using the remove_emails.py script. The script offers the following options:

Delete emails in a specific file:
python remove_emails.py -f ./data/processed/test_fail.csv

Delete emails in a directory:
python remove_emails.py -d ./data/processed

The remove_emails.py script automatically creates a backup of the modified files. These backup files are configured to be ignored by git, 
ensuring they are not accidentally committed to the repository.

7. Continuous Integration (CI)
This repository is equipped with automatic workflows that enforce checks before every commit. These workflows ensure that our code adheres to the standards we are trying to defend.