import json
import os

import langid

from tqdm import tqdm
from datetime import datetime

from utils.dataset_utilities import calculate_mean, clean_text, join_party_information, normalize_filenames

import pandas as pd
from utils import config
from collections import OrderedDict


def flatten_region_distribution(entry):
    flat_entry = {}
    # Flatten the region_distribution into columns.
    for region_info in entry['region_distribution']:
        region_name = region_info['region'].replace(' ', '_')  # Remove spaces for column naming.
        flat_entry[f'region_{region_name}_percentage'] = region_info['percentage']

    return flat_entry

def detect_language(text):
    sample_text = text[:1500]
    lang, _ = langid.classify(sample_text)
    return lang


def unify_date_fields(ad):
    for date_label in config.date_labels:
        if date_label in ad:
            date = ad[date_label]
            if 'T' in date:
                date = date.split('T')[0]
                ad[date_label] = date


class AdsReader:
    """
    Reads ads data from the raw jsonl files taken from the Meta API

    Parameters:
        directory (str): The directory containing the raw jsonl files.
        keep_last (bool): Whether to keep only the last version of each ad.
    """

    def __init__(self, directory='../data/raw'):
        """
        If keep_last is True, only the last version of each ad is kept, overriding the older versions.
        """
        self.directory = directory
        self.ads_df = None
        self.active_ads = set()
        self.ad_languages_dict = {}

    def load_ads_from_jsonl(self, unpack_dictionaries=True):
        """Load all ads from JSONL files in the specified directory into a DataFrame."""
        ads_dict = {}
        # Sort files based on the date and time in the filename
        files = os.listdir(self.directory)

        normalized_files = normalize_filenames(files)

        sorted_keys = sorted(normalized_files.keys(), key=lambda x: (x.split('-')[2], x.split('-')[3], x.split('-')[4]))

        for normalized_filename in tqdm(sorted_keys):
            filename = normalized_files[normalized_filename]
            file_path = os.path.join(self.directory, filename)
            date_str = normalized_filename.split('-')[2]
            file_date = datetime.strptime(date_str, '%Y%m%d')
            current_active_ads = set()
            with open(file_path, 'r') as file:
                # loop on the ads in the file
                for line in file:
                    ad = json.loads(line)

                    # OPERATIONS ON THE AD ------------------------------------------------
                    ad = self.process_ad(ad, unpack_dictionaries)

                    ad_id = int(ad['id'])
                    current_active_ads.add(ad_id)
                    # END OF OPERATIONS ON THE AD -----------------------------------------

                    ads_dict[ad_id] = ad

            # Set ad_delivery_stop_time for ads not in the current file
            stopped_ads = self.active_ads - current_active_ads
            for ad_id in stopped_ads:
                if ad_id in ads_dict:
                    ads_dict[ad_id]['ad_delivery_stop_time'] = file_date

            # Update active_ads for the next iteration
            self.active_ads = current_active_ads

        df = pd.DataFrame.from_dict(ads_dict, orient='index')
        self.convert_dates_to_datetime(df)
        self.ads_df = df

    def process_ad(self, ad, unpack_dictionaries):
        # create a deep copy of the ad
        ad = ad.copy()

        self.cast_numerical_values(ad)
        # save key values for debugging

        self.unify_body_fields(ad)

        self.assign_unique_body_id(ad)

        self.calculate_metrics(ad)

        unify_date_fields(ad)

        self.clean_text_fields(ad)

        if ad.get('languages', '') == '':
            ad_body_id = ad['ad_creative_body_id']
            if ad_body_id in self.ad_languages_dict:
                ad['languages'] = self.ad_languages_dict[ad_body_id]
            else:
                ad['languages'] = detect_language(ad.get('ad_creative_body', ''))  # expensive operation
                self.ad_languages_dict[ad_body_id] = ad['languages']
        else:
            ad['languages'] = ad['languages'][0]

        self.unify_region_informatin(ad)

        if unpack_dictionaries:
            self.unpack_dictionaries(ad)
        return ad

    def convert_dates_to_datetime(self, df):
        """
        Convert date columns to datetime format.
        """
        for column in config.date_labels:
            if column in df:
                df[column] = pd.to_datetime(df[column], errors='coerce')

    def assign_unique_body_id(self, ad):
        """
        Assign a unique ID to the ad_creative_body field.
        """
        ad['ad_creative_body_id'] = hash(ad['ad_creative_body'])


    def cast_numerical_values(self, ad):
        """
        Casts numerical values in the ad dictionary to integers.
        """
        for key in config.numerical_labels:
            if key in ad:
                ad[key] = int(ad[key])

    def unify_body_fields(self, ad):
        """
        Unify the ad_creative_body and ad_creative_bodies fields into a single field.
        """
        if 'ad_creative_bodies' in ad:
            unique_strings = list(OrderedDict.fromkeys(ad['ad_creative_bodies']))
            ad['ad_creative_body'] = '\n'.join(unique_strings)
            ad.pop('ad_creative_bodies')
        elif 'ad_creative_body' in ad:
            ad['ad_creative_body'] = ad['ad_creative_body']
        else:
            ad['ad_creative_body'] = ''

    def calculate_metrics(self, ad):
        """
        Calculate additional metrics for the ad.
        """
        ad['mean_spend'] = calculate_mean(ad.get('spend', {}).get('lower_bound'),
                                          ad.get('spend', {}).get('upper_bound'))
        ad['mean_impressions'] = calculate_mean(ad.get('impressions', {}).get('lower_bound'),
                                                ad.get('impressions', {}).get('upper_bound'))

        # cost effectiveness
        if ad['mean_spend'] is None or ad['mean_impressions'] is None:
            ad['cost_per_impression'] = None
        else:
            ad['cost_per_impression'] = round(ad['mean_spend'] / ad['mean_impressions'], 3)

    def unify_region_informatin(self, ad):
        """
        Unify the region_distribution and delivery_by_region fields into a single field.
        """
        if 'region_distribution' in ad and 'delivery_by_region' in ad:
            assert ad['region_distribution'] == ad[
                'delivery_by_region'], "region_distribution and delivery_by_region are not the same! Can't drop one"
        elif 'delivery_by_region' in ad and 'region_distribution' not in ad:
            ad['region_distribution'] = ad['delivery_by_region']

        # drop delivery_by_region
        ad.pop('delivery_by_region', None)

    def clean_text_fields(self, ad):
        """
        Clean text fields in the ad dictionary.
        """
        for column in config.text_labels:
            if column in ad:
                ad[column] = clean_text(ad[column])

    def unpack_dictionaries(self, ad):
        """
        Unpack dictionaries in the ad dictionary.
        """
        for key in list(ad.keys()):
            if isinstance(ad[key], dict):
                for sub_key, sub_value in ad[key].items():
                    ad[f"{key}.{sub_key}"] = sub_value
                ad.pop(key)



    def assert_no_reappeared_ads(self):
        """Checks all files in the specified directory to ensure no ads reappear after disappearing."""
        files = sorted(os.listdir(self.directory),
                       key=lambda x: (x.split('-')[2], x.split('-')[3], x.split('-')[4]))
        all_seen_ads = set()  # All ads ever seen
        active_ads = set()  # Ads seen in the current file
        disappeared_ads = set()  # Ads that were active but not seen in subsequent files

        for filename in files:
            print(f"Checking file: {filename}")
            current_active_ads = set()
            file_path = os.path.join(self.directory, filename)
            with open(file_path, 'r') as file:
                for line in file:
                    ad = json.loads(line)
                    ad_id = int(ad['id'])
                    current_active_ads.add(ad_id)

            # Check for reappeared ads
            reappeared_ads = disappeared_ads & current_active_ads
            assert not reappeared_ads, f"Reappeared ads detected: {reappeared_ads}"

            # Update the sets for the next iteration
            new_disappearances = active_ads - current_active_ads
            disappeared_ads.update(new_disappearances)
            disappeared_ads -= current_active_ads  # Remove any that reappear from disappeared_ads
            active_ads = current_active_ads
            all_seen_ads.update(current_active_ads)

        print("No reappeared ads detected across all files.")

    def count_unique_ad_ids(self):
        # initialize a set to store unique ad ids
        non_unique_ids = []
        unique_ad_ids = set()
        # iterate over the raw data files and store the ids
        for filename in tqdm(os.listdir(self.directory)):
            file_path = os.path.join(self.directory, filename)
            with open(file_path, 'r') as file:
                for line in file:
                    ad = json.loads(line)
                    unique_ad_ids.add(int(ad['id']))
                    non_unique_ids.append(int(ad['id']))

        return len(unique_ad_ids), len(non_unique_ids)

    def filter_rows(self):
        """
        Not used for the analysis in the paper.
        """
        # keep rows with body language = en
        self.ads_df = self.ads_df[self.ads_df['languages'] == 'en']
        # keep rows with currency AUD
        self.ads_df = self.ads_df[self.ads_df['currency'] == 'AUD']

        # drop rows where ad_creative_body is an empty string
        self.ads_df = self.ads_df[self.ads_df['ad_creative_body'] != '']

        # drop rows with null values in the following columns
        self.ads_df = self.ads_df.dropna(
            subset=['impressions.lower_bound',
                    'spend.lower_bound',
                    'spend.upper_bound',
                    'impressions.upper_bound',
                    'demographic_distribution',
                    'region_distribution'])

        # drop columns that are not needed
        self.ads_df.drop(columns=config.columns_to_drop, inplace=True)

    def convert_currency(self):
        spend_columns = ['spend.lower_bound', 'spend.upper_bound', 'mean_spend']
        for column in spend_columns:
            self.ads_df[column] = self.ads_df.apply(
                lambda row: float(row[column]) * config.exchange_rates[row['currency']]
                if row[column] is not None and row['currency'] in config.exchange_rates
                else None,
                axis=1
            )

        # set the currency to AUD
        self.ads_df['currency'] = 'AUD'


    def write_to_csv(self, output_filename):
        if not self.ads_df.empty:
            self.ads_df.to_csv(output_filename, index=False)



def main():
    folder_path = '../data/raw/2022_aus_election'
    output_filename = '../data/processed/2022_aus_elections_mar_to_may_3_party.csv'

    ads_reader = AdsReader(folder_path)
    ads_reader.load_ads_from_jsonl()
    ads_reader.convert_currency()
    #ads_reader.filter_rows()
    ads_reader.ads_df = join_party_information(ads_reader.ads_df)
    ads_reader.write_to_csv(output_filename)
    print('Done!')


def count_unique_ad_ids():
    folder_path = '../data/raw/2022_aus_election'
    ads_reader = AdsReader(folder_path)
    n_unique, n_non_unique = ads_reader.count_unique_ad_ids()
    print(f"Number of unique ad IDs: {n_unique}")
    print(f"Number of non-unique ad IDs: {n_non_unique}")

def check_for_reappeared_ads():
    folder_path = '../data/raw/2022_aus_election'
    ads_reader = AdsReader(folder_path)
    ads_reader.assert_no_reappeared_ads()

if __name__ == '__main__':
    main()
    # count_unique_ad_ids()
