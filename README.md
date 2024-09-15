# Political Advertising on Facebook During the 2022 Australian Federal Election

This repository contains the code and analysis notebooks for the paper "Political Advertising on Facebook During the 2022 Australian Federal Election".

## Data

The data used in this analysis is not included in this repository due to size constraints. All data files can be downloaded from [Zenodo](https://doi.org/10.5281/zenodo.13661563). After downloading, place the files as follows:

- Raw data file `2022_AU_election_raw.zip` should be placed in the `data/raw/` directory without unzipping
- All other data files should be placed in the `data/external/` directory
- The `maps_australia.zip` file should be unzipped and its contents placed directly in the `data/external/` directory

## Setup

1. Clone this repository
2. Download the data files from Zenodo and place them in the appropriate directories as described above
3. Install the required dependencies (`pip install -r requirements.txt` from the folder containing the requirements.txt file)

## Data Processing

The `src/scripts/dataset_creation.py` script processes the raw data and produces a dataset that is saved in the `data/processed/` directory. This script uses external CSV files (`keywords.csv` and `party_affiliation.csv`) to add columns to the dataset indicating whether each ad contains specific keywords or party affiliations, as described in Section 3.2 of our paper.

## Analysis

The analysis is split into three Jupyter notebooks:

1. `general_analysis.ipynb`: Produces general analysis results (Section 4 of the paper)
2. `keyword_analysis.ipynb`: Analyzes keyword usage in the ads (Subsection 5.5 of the paper)
3. `party_analysis.ipynb`: Analyzes ad data by political party (Section 5 of the paper)

These notebooks can be used to reproduce the results presented in the paper.

## Usage

To reproduce the analysis:

1. Ensure all data files are correctly placed as described in the **Data** section
2. Run the `dataset_creation.py` script to process the raw data
3. Open and run the Jupyter notebooks in the `src/notebooks/` directory to reproduce specific parts of the analysis
   
## Contributing

We welcome contributions to improve the analysis or extend it to other contexts. Please open an issue to discuss proposed changes before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

For any questions or feedback, please open an issue in this repository or contact us directly at the following email:
- [anonymous for blind review]
- [anonymous for blind review]
