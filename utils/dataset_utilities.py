import ast

import emoji
import pandas as pd
import re
import string

import nltk
from nltk import word_tokenize, MWETokenizer
from nltk.corpus import stopwords
from utils.config import exchange_rates

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

def join_party_information_deprecated(df):
    """
        Join party information from a separate file. The join is done on:
        - page_name and/or
        - funding_entity
        """
    party_info = pd.read_csv('../../data/external/party_information.csv')
    # rename spend coplumn to party_spend
    party_info.rename(columns={'spend': 'party_spend'}, inplace=True)

    df['merge_key'] = df['page_name'].fillna(df['funding_entity'])
    party_info['merge_key'] = party_info['page_name'].fillna(party_info['funding_entity'])

    # Perform a single left join on the new merge key
    df = pd.merge(df, party_info, on='merge_key', how='left', suffixes=('', '_y'))

    # Cleanup: remove any redundant or unnecessary columns post-merge
    df.drop(columns=['merge_key', 'page_name_y', 'funding_entity_y'], inplace=True)

    # Optionally, handle duplicates that may have arisen from the merge
    df.drop_duplicates(inplace=True)

    df = _clean_parties(df)

    return df


def join_party_information(df):
    """
    Join party information from a separate file. The join is done on:
    - page_name and/or
    - funding_entity
    """
    length = df.shape[0]
    # IMPORTANT: page_name cannot be null
    assert df['page_name'].notnull().all(), "ERROR: page_name cannot be null"

    party_info = pd.read_csv('../../data/external/party_information.csv')
    party_info.rename(columns={'spend': 'party_spend'}, inplace=True)
    assert party_info['page_name'].nunique() == party_info.shape[0], "ERROR: page_name has duplicates"

    df = pd.merge(df, party_info, on='page_name', how='left', suffixes=('', '_party_info'), indicator=True)


    # print how many rows joined and how many rows are left only
    print('Merge operation results:')
    print(df['_merge'].value_counts())
    # drop the _merge column
    df.drop(columns=['_merge'], inplace=True)
    df.drop(columns=[col for col in df.columns if col.endswith('_party_info')], inplace=True)

    # Fill party for unmatched rows based on page_name or funding_entity
    mask = df['party'].isna() & (
            df['page_name'].str.lower().str.contains('labor|liberal', na=False) |
            df['funding_entity'].str.lower().str.contains('labor|liberal', na=False)
    )
    df.loc[mask & df['page_name'].str.lower().str.contains('labor|labour', na=False), 'party'] = 'Labor'
    df.loc[mask & df['page_name'].str.lower().str.contains('liberal', na=False), 'party'] = 'Liberal'
    df.loc[mask & df['funding_entity'].str.lower().str.contains('labor|labour', na=False), 'party'] = 'Labor'
    df.loc[mask & df['funding_entity'].str.lower().str.contains('liberal', na=False), 'party'] = 'Liberal'

    # Apply the clean_parties function (assuming it exists)
    df = _clean_parties(df)

    assert length == df.shape[0], "ERROR: Rows have been added or removed during the join operation"

    return df


def join_ocr_information(df):
    ocr_info = pd.read_csv('../data/external/img_text_ocr_full.csv')

    ocr_info.columns = ['ocr_id', 'ocr_text', 'ocr_clean_text']

    df['merge_key'] = df['id'].astype(str)

    ocr_info['merge_key'] = ocr_info['ocr_id'].apply(lambda x: x.split('__')[1])

    # Perform a single left join on the new merge key
    merged_df = df.merge(ocr_info, on='merge_key', how='left')

    merged_df.drop('merge_key', axis=1, inplace=True)

    return merged_df


def _clean_parties(df):
    minor_party_labels = ['Other minor party', 'Other minor parties', 'Other Minor Parties', 'Other Minor Party']
    df['party'] = df['party'].apply(lambda x: 'Other minor parties' if x in minor_party_labels else x)

    kap = ['Katter\'s Australian Party (KAP)', 'Katter\'s Australian Party']
    df['party'] = df['party'].apply(lambda x: 'Katter\'s Australian Party' if x in kap else x)

    return df


def calculate_mean(lower_bound, upper_bound):
    if lower_bound is not None and upper_bound is not None:
        lower_bound = float(lower_bound)
        upper_bound = float(upper_bound)
        return (lower_bound + upper_bound) / 2
    elif lower_bound is not None:
        return float(lower_bound)
    elif upper_bound is not None:
        return float(upper_bound)
    else:
        raise ValueError('Both lower_bound and upper_bound are None')


def convert_to_aud(amount, currency):
    amount = float(amount)
    if currency in exchange_rates:
        return amount * exchange_rates[currency]
    else:
        raise ValueError(f'Currency {currency} not found in exchange rates')


# def expand_rows_spend_on_day_one(row):
#     """
#         Expand a single row of ad data across multiple days based on the ad campaign duration.
#         Spending is applied only on the first day of the ad campaign, while impressions are
#         distributed evenly across all days.
#
#         Parameters:
#         - row (pd.Series): A pandas Series containing data for a single ad campaign, expected
#           to include 'ad_delivery_start_time', 'ad_delivery_stop_time', 'mean_spend',
#           'mean_impressions', 'spend.lower_bound', 'spend.upper_bound', 'impressions.lower_bound',
#           'impressions.upper_bound', and 'id'.
#
#         Returns:
#         - pd.DataFrame: A DataFrame where each row represents a single day of the ad campaign.
#           The 'mean_spend', 'spend.lower_bound', and 'spend.upper_bound' are only applied on the
#           first day, set to zero on subsequent days. 'mean_impressions', 'impressions.lower_bound',
#           and 'impressions.upper_bound' are evenly distributed across all days of the campaign.
#           Each row also contains the 'ad_id' which is the 'id' from the input row.
#     """
#     days = pd.date_range(start=row['ad_delivery_start_time'], end=row['ad_delivery_stop_time'])
#     rows = pd.DataFrame({
#         'date': days,
#         'mean_spend': [row['mean_spend'] if i == 0 else 0 for i in range(len(days))],  # Only apply spend on the first day
#         'mean_impressions': row['mean_impressions'] / len(days),  # Distribute impressions evenly
#         'spend.lower_bound': [row['spend.lower_bound'] if i == 0 else 0 for i in range(len(days))],  # Only apply lower spend bound on the first day
#         'spend.upper_bound': [row['spend.upper_bound'] if i == 0 else 0 for i in range(len(days))],  # Only apply upper spend bound on the first day
#         'impressions.lower_bound': row['impressions.lower_bound'] / len(days),
#         'impressions.upper_bound': row['impressions.upper_bound'] / len(days),
#         'ad_id': row['id']
#     })
#     return rows

def expand_rows_spreading_spend(row):
    """
        Expand a single row of ad data across multiple days based on the ad campaign duration.
        Both spending and impressions are distributed evenly across all days of the ad campaign.

        Parameters:
        - row (pd.Series): A pandas Series containing data for a single ad campaign, expected
          to include 'ad_delivery_start_time', 'ad_delivery_stop_time', 'mean_spend',
          'mean_impressions', 'spend.lower_bound', 'spend.upper_bound', 'impressions.lower_bound',
          'impressions.upper_bound', and 'id'.

        Returns:
        - pd.DataFrame: A DataFrame where each row represents a single day of the ad campaign.
          The 'mean_spend', 'spend.lower_bound', 'spend.upper_bound', 'mean_impressions',
          'impressions.lower_bound', and 'impressions.upper_bound' are evenly distributed
          across all days of the campaign. Each row also contains the 'ad_id' which is the 'id'
          from the input row.
    """
    days = pd.date_range(start=row['ad_delivery_start_time'], end=row['ad_delivery_stop_time'])
    days_count = len(days)
    return pd.DataFrame({
        'date': days,
        'mean_spend': row['mean_spend'] / days_count,
        'mean_impressions': row['mean_impressions'] / days_count,
        'spend.lower_bound': row['spend.lower_bound'] / days_count,
        'spend.upper_bound': row['spend.upper_bound'] / days_count,
        'impressions.lower_bound': row['impressions.lower_bound'] / days_count,
        'impressions.upper_bound': row['impressions.upper_bound'] / days_count,
        'ad_id': row['id'],
        'macro_party_uap': row['macro_party_uap']
    })


def get_daily_data(df):
    expanded_df = pd.concat([expand_rows_spreading_spend(row) for _, row in df.iterrows()])

    daily_data = expanded_df.groupby(['date', 'macro_party_uap']).agg({
        'mean_spend': 'sum',
        'mean_impressions': 'sum',
        'spend.lower_bound': 'sum',
        'spend.upper_bound': 'sum',
        'impressions.lower_bound': 'sum',
        'impressions.upper_bound': 'sum',
        'ad_id': 'count'
    }).rename(columns={'ad_id': 'ad_count'}).reset_index()

    metrics = ['mean_spend', 'mean_impressions', 'ad_count',
               'spend.lower_bound', 'spend.upper_bound',
               'impressions.lower_bound', 'impressions.upper_bound']

    for metric in metrics:
        daily_data[f'{metric}_ma3'] = daily_data.groupby('macro_party_uap')[metric].transform(
            lambda x: x.rolling(window=3).mean())

    return daily_data



def clean_text(text):
    if text is None:
        return None

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove email addresses
    text = re.sub(r'\S*@\S*\s?', '', text, flags=re.MULTILINE)
    # Remove non-basic Unicode characters (emojis etc.)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.MULTILINE)
    text = emoji.replace_emoji(text, '')
    # Replace newlines and tabs with a space
    text = text.replace('\n', ' ').replace('\t', ' ')

    # remove leading spaces and punctuation
    unwanted_chars = string.punctuation + string.whitespace
    # Create a regular expression that matches these characters at the start of the string
    pattern = f'^[{re.escape(unwanted_chars)}]+'
    text = re.sub(pattern, '', text)

    return text

def tokenize_text(text):
    if text is None:
        return None
    # remove punctuation
    text = text.lower()
    # text = "".join(
    #    [i for i in text if i not in string.punctuation])  # might be inefficient (TEXT CLUSTERER CHAT)
    text = re.sub(r'[{}]+'.format(string.punctuation), " ", text)  # Efficient punctuation removal
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # lemmatize text
    lemmatizer = nltk.WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens if len(token) > 1]

    return tokens


def tokenize_text_multiword(text, multi_word_expressions=None, name_mappings=None):
    if text is None:
        return None

    if multi_word_expressions is None:
        multi_word_expressions = []

    if name_mappings is None:
        name_mappings = {}

    mwe_tokenizer = MWETokenizer([tuple(expression.split()) for expression in multi_word_expressions])

    # Remove punctuation and lowercase the text
    text = text.lower()
    text = re.sub(r'[{}]+'.format(string.punctuation), " ", text)

    # Tokenize text
    tokens = word_tokenize(text)

    # Apply MWE tokenizer
    tokens = mwe_tokenizer.tokenize(tokens)

    # Apply name mappings
    tokens = [map_names(token, name_mappings) for token in tokens]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize text
    lemmatizer = nltk.WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens if len(token) > 1]

    return tokens


def normalize_filenames(files):
    """
        Normalizes filenames for 'FBads' files by ensuring consistent date formatting.

        This function processes a list of filenames starting with 'FBads'.
        It normalizes the date part of these filenames to ensure a consistent 8-digit format.
        Non-'FBads' files are ignored and logged.

        Args:
            files (list): A list of filename strings to be processed.

        Returns:
            dict: A dictionary where keys are normalized filenames and values are original filenames.
                  Only 'FBads' files are included in this dictionary.

        Example:
            files = ['FBads-example-202301.csv', 'other-file.txt']
            normalize_filenames(files)
            {'FBads-example-20230100.csv': 'FBads-example-202301.csv'}
            ignoring other-file.txt

        Note:
            - Filenames are expected to be in the format 'FBads-<something>-<date>.<extension>'.
            - The date part is assumed to be the third element when split by '-'.
            - If the date part is 7 digits, a '0' is inserted after the first 4 digits.
            - Non-'FBads' files are printed to console with an 'ignoring' message.
        """
    normalized_files = {}
    for filename in files:
        parts = filename.split('/')[1].split('-')
        if parts[0] == 'FBads':
            date_str = parts[2]
            if len(date_str) == 7:
                date_str = date_str[:4] + '0' + date_str[4:]

            parts[2] = date_str
            normalized_filename = '-'.join(parts)
            normalized_files[normalized_filename] = filename
        else:
            print(f'ignoring {filename}')

    return normalized_files


def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    # Drop the 'Unnamed: 0' column if it exists and is just an artifact of saving/loading
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)

    def safe_eval(x):
        if pd.isna(x) or x == '':
            return None
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return None

    # Convert datetime columns if they exist
    if 'ad_creation_time' in df.columns:
        df['ad_creation_time'] = pd.to_datetime(df['ad_creation_time'])

    if 'ad_delivery_start_time' in df.columns:
        df['ad_delivery_start_time'] = pd.to_datetime(df['ad_delivery_start_time'])

    if 'ad_delivery_stop_time' in df.columns:
        df['ad_delivery_stop_time'] = pd.to_datetime(df['ad_delivery_stop_time'],
                                                     errors='coerce')  # Coerce errors for NaNs

    # Apply safe_eval to distribution columns if they exist
    if 'demographic_distribution' in df.columns:
        df['demographic_distribution'] = df['demographic_distribution'].apply(safe_eval)

    if 'region_distribution' in df.columns:
        df['region_distribution'] = df['region_distribution'].apply(safe_eval)

    return df


# def get_categorized_dataframes(df):
#     liberal_mask = (df['party'] == 'Liberal') | \
#                    (df['party'] == 'Liberal Nationals (QLD)') | \
#                    (df['party'] == 'Nationals') | \
#                    (df['party'] == 'Country Liberal (NT)') | \
#                    (df['party'] == 'New Liberals')
#     # Country Liberal (NT) e New Liberals non sarebbero da considere
#
#     labor_mask = df['party'] == 'Labor'
#
#     greens_mask = df['party'] == 'Greens'
#
#     independents_mask = df['party'] == 'Independent'
#
#     other_parties_mask = ~(liberal_mask | labor_mask | greens_mask | independents_mask)
#
#     main_parties_mask = (liberal_mask | labor_mask | greens_mask | independents_mask)
#
#     has_a_party_mask = df['party'].notnull()
#
#     # Using the masks to create DataFrames
#     liberal_df = df[liberal_mask]
#     labor_df = df[labor_mask]
#     greens_df = df[greens_mask]
#     independents_df = df[independents_mask]
#     other_parties_df = df[other_parties_mask]
#     main_parties_df = df[main_parties_mask]
#     has_party_df = df[has_a_party_mask]
#
#     all_dfs = {'liberal_df': liberal_df,
#                'labor_df': labor_df,
#                'greens_df': greens_df,
#                'independents_df': independents_df,
#                'main_parties_df': main_parties_df,
#                'other_parties_df': other_parties_df,
#                'has_party_df': has_party_df}
#
#     party_dfs = {'liberal_df': liberal_df,
#                  'labor_df': labor_df,
#                  'greens_df': greens_df,
#                  'independents_df': independents_df}
#
#     return all_dfs, party_dfs


def assign_macro_party(row):
    if row['party'] in ['Liberal', 'Liberal Nationals (QLD)', 'Nationals', 'Country Liberal (NT)', 'New Liberals']:
        return 'Liberal'
    elif row['party'] == 'Labor':
        return 'Labor'
    elif row['party'] == 'Greens':
        return 'Green'
    elif row['party'] == 'Independent':
        return 'Independent'
        # handle the null case
    elif pd.isna(row['party']):
        return None
    else:
        return 'Other'


def assign_macro_party_with_uap(row):
    if row['party'] in ['Liberal', 'Liberal Nationals (QLD)', 'Nationals', 'Country Liberal (NT)', 'New Liberals']:
        return 'Liberal'
    elif row['party'] == 'Labor':
        return 'Labor'
    elif row['party'] == 'Greens':
        return 'Green'
    elif row['party'] == 'Independent':
        return 'Independent'
    elif row['party'] == 'United Australia Party':
        return 'United Australia Party'
    # handle the null case
    elif pd.isna(row['party']):
        return None
    else:
        return 'Other'


def map_names(token, name_mappings):
    return name_mappings.get(token, token)
