import pandas as pd

ELECTION_DAY = pd.Timestamp('2022-05-21')
START_DATE = pd.Timestamp('2022-03-01')
END_DATE = pd.Timestamp('2022-06-01')
missing_values_threshold = 0.9  # drop columns with more than 90% missing values
columns_to_drop = ['bad_format', 'party_spend']

multi_word_expressions = ["united australia party",
                          "scott morrison",
                          "anthony albanese",
                          "climate change",
                          "adam bandt",
                          "young people matter",
                          "animal justice party",
                          "federal election"]
name_mappings = {
    "scott": "scott_morrison",
    "morrison": "scott_morrison",
    "anthony": "anthony_albanese",
    "albanese": "anthony_albanese",
    "adam": "adam_bandt",
    "bandt": "adam_bandt",
    "animaljusticeparty": "animal_justice_party",
}

australian_regions = ['New South Wales', 'Victoria', 'Queensland', 'Western Australia',
                      'South Australia', 'Tasmania', 'Australian Capital Territory', 'Northern Territory'] # Jarvis Bay Territory is not included

color_dict = {
    'Labor': 'firebrick',
    'Liberal': 'blue',
    'Independent': 'darkturquoise',
    'Green': 'olivedrab',
    'United Australia Party': 'darkorange',
}

state_color = {
    'NSW': '#0099ff',
    'VIC': '#0a2056',
    'QLD': '#840f31',
    'WA': '#fbe500',
    'SA': '#d71f37',
    'TAS': '#15684a',
    'ACT': '#003399',
    'NT': '#e45d26',
}


categorical_labels = ['page_name',
                      'publisher_platforms',
                      'languages',
                      'page_id',
                      'currency',
                      'funding_entity',
                      'ad_creative_link_caption']

text_labels = ['ad_creative_body',
               'ad_creative_link_title',  # maybe these can also be used for persuasion detection
               'ad_creative_link_description']

structured_labels = ['region_distribution',
                     'demographic_distribution'
                     'delivery_by_region']

numerical_labels = ['estimated_audience_size_upper_bound',
                    'spend_upper_bound',
                    'spend_lower_bound',
                    'impressions_upper_bound',
                    'impressions_lower_bound',
                    'estimated_audience_size_lower_bound']

date_labels = ['ad_creation_time',
               'ad_delivery_start_time',
               'ad_delivery_stop_time']


exchange_rates = {
    'AUD': 1.0,  # Australian Dollar (base currency)
    'USD': 1.52,  # US Dollar
    'EUR': 1.67,  # Euro
    'GBP': 1.92,  # British Pound
    'RUB': 0.017,  # Russian Ruble
    'INR': 0.018,  # Indian Rupee
    'BRL': 0.31,  # Brazilian Real
    'NOK': 0.14,  # Norwegian Krone
    'KRW': 0.0011,  # South Korean Won
    'HKD': 0.19,  # Hong Kong Dollar
    'CAD': 0.9,  # Canadian Dollar
    'PLN': 0.4,  # Polish Zloty
    'SGD': 1.03,  # Singapore Dollar
}