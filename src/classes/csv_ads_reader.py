import numpy as np
import pandas as pd

from utils.dataset_utilities import calculate_mean, join_party_information, join_ocr_information
from utils.dataset_utilities import tokenize_text


class CSVAdsReader:
    def __init__(self, file_path):
        self.dataframe = None
        self.df = pd.read_csv(file_path)
        #self.df['ad_creative_body'] = self.df['ad_creative_body'].apply(clean_text)

    def filter_rows(self):
        # keep rows with body language = en
        self.df = self.df[self.df['ad_body_language'] == 'en']
        # keep rows with currency AUD
        self.df = self.df[self.df['currency'] == 'AUD']
        # drop null values in the following columns
        self.df = self.df.dropna(
            subset=['funding_entity', 'impressions.lower_bound', 'spend.lower_bound', 'spend.upper_bound',
                    'impressions.upper_bound', 'region_distribution', 'demographic_distribution'])

    def save_to_csv(self,
                    save_path='../data/processed/australian_ads_dataframe_election_campaign_only_MarToMay2022_preprocessed.csv'):
        self.df.to_csv(save_path, index=False)

    def random_persuasion(self):
        # Randomly assign a persuasion true or false to each row
        self.df['persuasion'] = np.random.choice([True, False], self.df.shape[0])

    def compute_means(self):
        self.df['mean_spend'] = self.df.apply(
            lambda x: calculate_mean(x['spend.lower_bound'], x['spend.upper_bound']), axis=1)
        self.df['mean_impressions'] = self.df.apply(
            lambda x: calculate_mean(x['impressions.lower_bound'], x['impressions.upper_bound']), axis=1)

    def cost_effectiveness(self):
        self.df['cost_per_impression'] = round(self.df['mean_spend'] / self.df['mean_impressions'], 3)


def main():
    filename = '../data/processed/0-base-australian_ads_dataframe_election_campaign_only_MarToMay2022.csv'
    reader = CSVAdsReader(filename)
    reader.filter_rows()
    reader.compute_means()
    reader.cost_effectiveness()
    #reader.random_persuasion()
    reader.df = join_party_information(reader.df)
    reader.save_to_csv()


def join_with_ocr():
    filename = '../data/processed/australian_ads_dataframe_election_campaign_only_MarToMay2022_persuasion.csv'
    reader = CSVAdsReader(filename)
    reader.df = join_ocr_information(reader.df)
    save_path = '../data/processed/australian_ads_dataframe_election_campaign_only_MarToMay2022_persuasion_ocr.csv'
    reader.save_to_csv(save_path)

def drop_ocr_columns():
    filename = '../data/processed/2022_aus_elections_mar_to_may_ocr_28.csv'
    reader = CSVAdsReader(filename)
    reader.df.drop(columns=['ocr_id', 'ocr_text', 'ocr_clean_text'], inplace=True)
    save_path = '../data/processed/2022_aus_elections_mar_to_may_29.csv'
    reader.save_to_csv(save_path)

def join_party():
    filename = '../data/processed/2022_aus_elections_mar_to_may_31.csv'
    reader = CSVAdsReader(filename)
    reader.df = join_party_information(reader.df)
    save_path = '../data/processed/2022_aus_elections_mar_to_may_31_party.csv'
    reader.save_to_csv(save_path)


def add_tokenized_text():
    filename = '../data/processed/2022_aus_elections_mar_to_may_29_persuasion_party.csv'
    reader = CSVAdsReader(filename)
    reader.df['tokenized_text'] = reader.df['ad_creative_body'].apply(tokenize_text)

    save_path = '../data/processed/2022_aus_elections_mar_to_may_29_persuasion_party_tokenized.csv'
    reader.save_to_csv(save_path)


if __name__ == '__main__':
    join_party()