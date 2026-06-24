import pandas as pd
from pathlib import Path
import os
import re

# set-up output path
REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = REPO_ROOT / 'data' / 'processed'

# other configurations
EMAIL_PAT = re.compile(r'\.?\s*(?:electronic address:|email:|e-mail:)?\s*[\w\.-]+@[\w\.-]+\.\w+\.?$', flags=re.IGNORECASE)

# build dictionary of common alternate forms of different countries that show up in the data
koreas = ['Republic of Korea', 'Korea', 'South Korea']
netherlands = ['the Netherlands', 'The Netherlands', 'Netherlands']
china = ['China', 'P.R. China', "People's Republic of China", "PRC", 'Fujian', 'Chinese Academy of Sciences', 'Hefei Comprehensive National Science Center']
uk = ['UK', 'United Kingdom', 'Oxford UK OX BN']
usa = ['Howard Hughes Medical Institute', 'MA', 'CA', 'NY', 'PA', 'MD', 'Massachusetts', 'NC', 'Texas', 'Maryland', 'CA USA', 'TX -', 'CT', 'CA -' 'http://www.jcsg.org']
mexico = ['México', 'Mexico']

COUNTRY_MAP = {}
for item in koreas:
    COUNTRY_MAP[item] = 'South Korea'
for item in netherlands:
    COUNTRY_MAP[item] = 'the Netherlands'
for item in china:
    COUNTRY_MAP[item] = 'China'
for item in uk:
    COUNTRY_MAP[item] = 'UK'
for item in usa:
    COUNTRY_MAP[item] = 'USA'
for item in mexico:
    COUNTRY_MAP[item] = 'Mexico'

# function to match the country (last value in the affiliation string), clean, and return it.
# substitutes many common alternate versions of a country name according to the COUNTRY_MAP dictionary
def extract_country(affiliation:str) -> str:
    remove_email_text = re.sub(EMAIL_PAT, '', affiliation)
    cleaned = remove_email_text.strip().rstrip('.')
    country = cleaned.split(',')[-1].strip()
    country = re.sub(r'\d+', '', country).strip()
    country = COUNTRY_MAP.get(country, country)
    
    return country

# function to extract the country of each author's primary affiliation.
# pass a dataframe and the source of dataframe (in this case, either Nature or Cell)
# source required since formatting slightly different between the publications
def process_author_data(df, source):
    cell_author_info = cell_author_info.drop(columns = ['Unnamed: 0']).set_index('PMID')

    if source == 'Cell':
        cell_author_info['affiliations'] = cell_author_info['affiliations'].str.split(';')
    elif source == 'Nature':
        cell_author_info['affiliations'] = cell_author_info['affiliations'].str.split('|')
    else:
        print('incorrect source input - please input either Nature or Cell')
        return

    # set primary affiliation as the first affiliation to appear in the affiliation list
    cell_author_info['primary_affiliation'] = [affil[0] for affil in cell_author_info['affiliations']]

    # extract country for the primary affiliation
    cell_author_info['primary_country'] = cell_author_info['primary_affiliation'].apply(extract_country)

