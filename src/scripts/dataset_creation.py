"""
This script creates the PAK and PAP datasets from the raw data.

- PAP (Political Ads Party) dataset: contains all the ads that are related to political parties.
- PAK (Political Ads Keywords) dataset: contains all the ads that contain political keywords.
"""
import os
import sys
print(f'default sys.path: {sys.path}')
PROJ_ROOT = os.path.abspath(os.path.join(os.pardir))
PROJ_ROOT = os.path.abspath(os.path.join(PROJ_ROOT, os.pardir))
sys.path.append(PROJ_ROOT)
print(f'Project root: {PROJ_ROOT}')

import argparse
import nltk
import numpy as np
from matplotlib import pyplot as plt
from nltk.stem import PorterStemmer
import pandas as pd
from src.classes.ads_reader import AdsReader
from utils.dataset_utilities import join_party_information, assign_macro_party, load_data, tokenize_text_multiword, \
    assign_macro_party_with_uap
from data.external.keywords import keywords

from utils import mpl_settings, config
import missingno as msno

mpl_settings.apply_settings()

nltk.download('punkt')

print(f'default sys.path: {sys.path}')
PROJ_ROOT = os.path.abspath(os.path.join(os.pardir))
sys.path.append(PROJ_ROOT)
print(f'Project root: {PROJ_ROOT}')


def print_datasets_stats(df, title):
    # Count total ads
    total_ads = len(df)

    # Count ads kept by each method
    party_ads = df['has_party'].sum()
    keyword_ads = df['has_political_keywords'].sum()

    # Count ads kept by both methods (overlap)
    overlap_ads = df[df['has_party'] & df['has_political_keywords']].shape[0]

    # Count ads kept by at least one method (union)
    union_ads = df[df['has_party'] | df['has_political_keywords']].shape[0]

    # Count ads kept only by party method
    only_party_ads = df[df['has_party'] & ~df['has_political_keywords']].shape[0]

    # Count ads kept only by keyword method
    only_keyword_ads = df[~df['has_party'] & df['has_political_keywords']].shape[0]

    # Calculate percentages
    percent_party = (party_ads / total_ads) * 100
    percent_keyword = (keyword_ads / total_ads) * 100
    percent_overlap = (overlap_ads / total_ads) * 100
    percent_union = (union_ads / total_ads) * 100

    # Calculate Jaccard similarity
    jaccard_similarity = overlap_ads / union_ads

    # Print results
    print(f"\n{'-' * 50}")
    print(f"{title.center(50)}")
    print(f"{'-' * 50}\n")

    print(f"{'Total ads:':<40} {total_ads:,}")
    print(f"\n{'Ads kept by:':<40} {'Count':<10} {'Percentage'}")
    print(f"{'-' * 60}")
    print(f"{'Party method:':<40} {party_ads:<10} {percent_party:.2f}%")
    print(f"{'Keyword method:':<40} {keyword_ads:<10} {percent_keyword:.2f}%")
    print(f"{'Both methods (overlap):':<40} {overlap_ads:<10} {percent_overlap:.2f}%")
    print(f"{'At least one method (union):':<40} {union_ads:<10} {percent_union:.2f}%")
    print(f"{'Only party method:':<40} {only_party_ads:,}")
    print(f"{'Only keyword method:':<40} {only_keyword_ads:,}")

    print(f"\n{'Jaccard similarity between methods:':<40} {jaccard_similarity:.4f}")

    print(f"\n{'Percentage of party ads that have a keyword:':<40} {overlap_ads / party_ads:.2f}")

    # Create a confusion matrix
    confusion_matrix = pd.crosstab(df['has_party'], df['has_political_keywords'],
                                   rownames=['Party Method'], colnames=['Keyword Method'])
    print("\nConfusion Matrix:")
    print(confusion_matrix)
    print(f"\n{'-' * 50}\n")


def plot_datasets_sovapposition(df):
    combinations = [
        (1, 1), (1, 0),
        (0, 1), (0, 0)
    ]

    # Create labels for each combination
    labels = [
        'Party\nKeywords', 'Party',
        'Keywords', 'None'
    ]

    # Count the number of ads in each combination
    counts = []
    for combo in combinations:
        count = df[
            (df['has_party'] == combo[0]) &
            (df['has_political_keywords'] == combo[1])
            ].shape[0]
        counts.append(count)

    # Sort the combinations and labels by count in descending order
    sorted_indices = np.argsort(counts)[::-1]
    sorted_counts = np.array(counts)[sorted_indices]
    sorted_combinations = np.array(combinations)[sorted_indices]
    sorted_labels = np.array(labels)[sorted_indices]

    # Create the plot
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 8),
                                   gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    # Bar plot
    colors = ['C0' if label != 'None' else 'firebrick' for label in sorted_labels]
    bars = ax1.bar(range(len(sorted_counts)), sorted_counts, color=colors)
    ax1.set_ylabel('Number of Ads')

    # Set labels
    ax1.set_xticks(range(len(sorted_labels)))
    ax1.set_xticklabels(sorted_labels, rotation=45, ha='right')

    # Add count labels on top of bars
    for i, count in enumerate(sorted_counts):
        ax1.text(i, count, str(count), ha='center', va='bottom')

    # Category indicators
    for i, combo in enumerate(sorted_combinations):
        for j, value in enumerate(combo):
            if value:
                ax2.plot(i, j, 'o', color='black', markersize=10)
            else:
                ax2.plot(i, j, 'o', color='lightgray', markersize=10)

    ax2.set_yticks(range(2))
    ax2.set_yticklabels(['Party', 'Keywords'])
    ax2.set_ylabel('Categories')

    # Remove x-axis labels from the bottom plot
    ax2.set_xticks([])

    plt.tight_layout()
    plt.show()

    # Print percentages
    total = sum(counts)
    for label, count in zip(sorted_labels, sorted_counts):
        percentage = (count / total) * 100
        print(f"{label}: {count} ({percentage:.2f}%)")


def filter_dataframe(df):
    df = df[df['ad_delivery_start_time'] >= config.START_DATE]
    df = df[df['ad_delivery_stop_time'] <= config.END_DATE]

    # drop rows where ad_delivery_stop_time is missing
    df = df.dropna(subset=['ad_delivery_stop_time'])
    # drop ads where the ad_creative_link_caption is atsijobs.com.au
    df = df[df['ad_creative_link_caption'] != 'atsijobs.com.au']
    df = df[df['ad_creative_link_caption'] != 'arcstream.solutions']
    # drop ads where the page_name is Indigenous Employment Australia
    df = df[df['page_name'] != 'Indigenous Employment Australia']

    # drop columns with more than <threshold> missing values
    df = df.loc[:, df.isnull().mean() < config.missing_values_threshold]

    # concatenate ad_creative_body and ad_creative_link_caption
    # First, perform the concatenation as before
    df['custom_body'] = (
            df['ad_creative_body'].fillna('') + ' ' +
            df['ad_creative_link_title'].fillna('') + ' ' +
            df['ad_creative_link_description'].fillna('')
    ).str.strip()

    # Then, drop rows where ad_creative_body is an empty string
    df = df[df['custom_body'].str.strip() != '']

    df = df.dropna(subset=['custom_body', 'mean_spend'])  # should drop 0 rows


    # drop columns
    df.drop(columns=config.columns_to_drop, inplace=True)

    return df


def apply_stemming(text, stemmer, tokenizer):
    words = tokenizer(text)
    return ' '.join([stemmer.stem(word) for word in words])


def safe_tokenize_text(text):
    try:
        return tokenize_text_multiword(text, config.multi_word_expressions, name_mappings=config.name_mappings)
    except:
        print(f'Error tokenizing text: {text}')
        return []


def main(args, keywords_pattern):
    if args.use_cache and os.path.exists("../../data/interim/unique_ads.csv"):
        print("Using cached data.")
        pre_filtering_df = load_data("../../data/interim/unique_ads.csv")
    else:
        print("Loading data from scratch.")
        ads_reader = AdsReader(args.folder_path)
        ads_reader.load_ads_from_jsonl()
        ads_reader.convert_currency()
        ads_reader.ads_df = join_party_information(ads_reader.ads_df)
        ads_reader.write_to_csv("../../data/interim/unique_ads.csv")
        pre_filtering_df = ads_reader.ads_df

    print(f'ads entries before filtering: {pre_filtering_df.shape[0]}')
    filtered_df = filter_dataframe(pre_filtering_df)
    print(f'ads entries after filtering: {filtered_df.shape[0]}')
    filtered_df.to_csv("../../data/interim/filtered_ads.csv")

    filtered_df['stemmed_body'] = filtered_df['custom_body'].apply(
        lambda x: apply_stemming(x, stemmer, nltk.word_tokenize))

    filtered_df['multiword_safe_lemmatized'] = filtered_df['custom_body'].apply(
        lambda x: ' '.join(safe_tokenize_text(x)))

    filtered_df['has_political_keywords'] = (filtered_df['stemmed_body']
                                             .str.contains(keywords_pattern, regex=True, na=False))

    filtered_df['has_party'] = filtered_df['party'].notna()

    filtered_df['macro_party'] = filtered_df.apply(assign_macro_party, axis=1)

    filtered_df['macro_party_uap'] = filtered_df.apply(assign_macro_party_with_uap, axis=1)

    # This is how PAP and PAK are defined but we don't actually need them
    # pap_df = filtered_df[filtered_df['party'].notna()]
    # pak_df = filtered_df[filtered_df['has_political_keywords']]

    filtered_df.to_csv(args.output_filename, index=False)

    print_datasets_stats(filtered_df, 'All Ads')

    plot_datasets_sovapposition(filtered_df)

    msno.matrix(filtered_df)
    # Save the plot to a file
    plt.savefig('missingno_plot.png')




if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--folder_path', type=str,
                        default='../../data/raw/2022_AU_election_raw.zip',
                        help='Path to the folder containing the raw data.')
    parser.add_argument('--output_filename', type=str,
                        default='../../data/processed/2022_aus_elections_mar_to_may.csv',
                        help='Path to the output file.')
    parser.add_argument('--use_cache', type=bool, default=True, 
                        help='Whether to use the cached data.')
    args = parser.parse_args()

    keywords = set(keywords)

    # stem the keywords
    stemmer = PorterStemmer()
    keywords = set([stemmer.stem(word) for word in keywords])

    keywords_pattern = '|'.join([f'(?i){word}' for word in keywords])

    main(args, keywords_pattern)
