# Political Advertising on Facebook During the 2022 Australian Federal Election

This repository contains the code and analysis notebooks for the paper "Political Advertising on Facebook During the 2022 Australian Federal Election".

## Data

The data used in this analysis is not included in this repository due to size constraints. All data files can be downloaded from [Zenodo](https://doi.org/10.5281/zenodo.13661563). After downloading, place the files as follows:

- Raw data files (2022_AU_election_raw.zip) should be placed in the `data/raw/` directory and not be unzipped
- All other data files should be placed in the `data/external/` directory (NOTE: the zip file containing the australia maps (maps_australia.zip) should be unzipped and the content should be placed in the folder mentioned)

## Setup

1. Clone this repository
2. Download the data files from Zenodo and place them in the appropriate directories as described above
3. Install the required dependencies (`pip install -r requirements.txt` from the folder containing the requirements.txt file)

## Data Processing

The `src/scripts/dataset_creation.py` script processes the raw data and produces a dataset that is saved in the `data/processed/` directory. This script uses external CSV files (e.g., `keywords.csv` and `party_affiliation.csv`) to add columns to the dataset indicating whether each ad contains specific keywords or party affiliations (as we describe in Section 3.2 of our paper).

## Analysis

The analysis is split into three Jupyter notebooks:

1. `general_analysis.ipynb`: Produces general analysis results (the one included in Section 4)
2. `keyword_analysis.ipynb`: Analyzes keyword usage in the ads 
3. `party_analysis.ipynb`: Analyzes ad data by political party (the one included in Section 5)

These notebooks can be used to reproduce the results presented in the paper.

## Usage

To reproduce the analysis:

1. Ensure all data files are in place
2. Run the `dataset_creation.py` script to process the raw data
3. Open and run the Jupyter notebooks in the `src/notebooks/` directory in order to reproduce the part that it is interested in

## Contributing

Instructions for contributing to be added.

## License

License information to be added.

## Contact

Removed for blind review
