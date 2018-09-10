"""
Generate RP reports from Piwik and Successful verifications data

expects: the following files to be present in verify-data-pipeline-config:
verifications_by_rp_<for-required-week>.csv
piwik configuration in piwik.json
"""

import pandas as pd
import json
import requests
import os
from datetime import date, timedelta

period = 'week'
limit = '-1'
date_start = date(2018, 7, 23)
date_end = date_start + timedelta(days=6)
date_start_string = date_start.isoformat()
verify_data_pipeline_config_path = '../../verify-data-pipeline-config'
verifications_by_rp_csv = \
    f'{verify_data_pipeline_config_path}/data/verifications/verifications_by_rp_{date_start}_{date_end}.csv'
report_output_path = '../output'
env = 'prod'

if env == 'prod':
    base_url = 'https://analytics-hub-prod-a-dmz.ida.digital.cabinet-office.gov.uk/index.php'
else:
    base_url = 'https://analytics-hub-dr-dmz.ida.digital.cabinet-office.gov.uk/index.php'


def get_piwik_token(env):
    with open(f'{verify_data_pipeline_config_path}/credentials/piwik_token.json') as fileHandle:
        token = json.load(fileHandle)['production' if env == 'prod' else 'dr_token']
        return token


token = get_piwik_token(env)

df_verifications_by_rp = pd.read_csv(verifications_by_rp_csv)


def get_nb_visits_for_page(date, period, token, limit, segment):
    qs = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': limit,
        'date': date,
        'period': period,
        'method': 'Actions.getPageTitles',
        'token_auth': token,
        'segment': segment,
    }

    response = requests.get(base_url, qs)

    raw_result = response.json()
    nb_visits = next(iter(raw_result), {}).get('nb_visits', 0)
    return nb_visits


# ## Getting the volume of sessions for sign up and sign in
# No longer uses unique page views - gets the number of sessions for each value of the JOURNEY_TYPE custom variable


def get_nb_visits_for_rp(date, period, token, limit, segment):
    qs = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': limit,
        'date': date,
        'period': period,
        'method': 'VisitsSummary.getVisits',
        'expanded': '1',
        'token_auth': token,
        'segment': segment
    }

    response = requests.get(base_url, qs)

    raw_result = response.json()
    return raw_result.get('value', 0)


# rp_mapping translates the referrer url reported in the verifications csv
with open(f'{verify_data_pipeline_config_path}/configuration/rp_mapping.json') as ft:
    rp_mapping = json.load(ft)


def get_rp_name(rp_entity_id):
    return rp_mapping[rp_entity_id]


# Get the human readable IDP name and add it to a new column


df_verifications_by_rp['rp'] = df_verifications_by_rp.apply(lambda row: get_rp_name(row['RP Entity Id']), axis=1)
df_verifications_by_rp.head()

df_verifications_by_rp = df_verifications_by_rp.rename(columns={'Response type': 'response_type'})

df_totals = df_verifications_by_rp.groupby(['rp', 'response_type']).count().reset_index()
df_totals.head()

df_totals.drop(['Timestamp', 'RP Entity Id'], axis=1, inplace=True)

df_totals = df_totals.rename(columns={'IDP Entity Id': 'successes'})

df_all = pd.pivot_table(df_totals, values='successes', index='rp', columns='response_type')
df_all.reset_index(inplace=True)
df_all.columns = ['rp', 'signup_success', 'signin_success']

# ### Success rate (sign in)


ls_rp = list(df_verifications_by_rp.rp.unique())

df = pd.DataFrame()

for rp in ls_rp:
    print("Getting data for {}".format(rp))
    segment_by_rp = f"customVariableValue1=={rp}"
    all_referrals = get_nb_visits_for_rp(date_start_string, period, token, limit, segment_by_rp)
    segment_signin = f"{segment_by_rp};customVariableValue3==SIGN_IN"
    signin_attempts = get_nb_visits_for_rp(date_start_string, period, token, limit, segment_signin)
    segment_signup = f"{segment_by_rp};customVariableValue3==REGISTRATION"
    signup_attempts = get_nb_visits_for_rp(date_start_string, period, token, limit, segment_signup)

    segment_single_idp = f"{segment_by_rp};customVariableValue3==SINGLE_IDP"
    single_idp_attempts = get_nb_visits_for_rp(date_start_string, period, token, limit, segment_single_idp)

    # TODO if the RP is not found (e.g. due to no successful signins) then we may need to add a row?
    df_all.loc[(df_all['rp'] == rp), 'all_referrals'] = all_referrals
    df_all.loc[(df_all['rp'] == rp), 'signin_attempt'] = signin_attempts
    df_all.loc[(df_all['rp'] == rp), 'signup_attempt'] = signup_attempts
    df_all.loc[(df_all['rp'] == rp), 'single_idp_attempt'] = single_idp_attempts

df_all['signin_rate (deprecated)'] = df_all['signin_success'] / df_all['signin_attempt']
df_all['signup_rate (deprecated)'] = df_all['signup_success'] / df_all['signup_attempt']

df_all['all_referrals_with_intent'] = df_all['signin_attempt'] + df_all['signup_attempt'] + df_all['single_idp_attempt']

df_all['success'] = df_all['signin_success'] + df_all['signup_success']
df_all['success_rate'] = df_all['success'] / df_all['all_referrals_with_intent']

df_all['success_fraction_signup'] = df_all['signup_success'] / df_all['success']
df_all['success_fraction_signin'] = df_all['signin_success'] / df_all['success']

df_all['success_signup_rate'] = df_all['signup_success'] / df_all['all_referrals_with_intent']
df_all['success_signin_rate'] = df_all['signin_success'] / df_all['all_referrals_with_intent']

df_all['dropout'] = df_all['all_referrals_with_intent'] - df_all['signin_success'] - df_all['signup_success']
df_all['dropout_rate'] = df_all['dropout'] / df_all['all_referrals_with_intent']

# ### Ineligible (will not work / might not work) - with journey type segment
# upvson 'GOV.UK Verify will not work for you' page, segmented by 'registration' custom variable

# TODO this should come from config
loa1_rp_list = ["DFT DVLA VDL", "Get your State Pension", "NHS TRS"]


def is_loa2(rp):
    return rp not in loa1_rp_list


for rp in ls_rp:
    if is_loa2(rp):
        will_not_work_page = "@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"
        will_not_work_segment = "pageTitle={};customVariableValue1=={};customVariableValue3==REGISTRATION".format(
            will_not_work_page, rp)
        visits_will_not_work = get_nb_visits_for_page(date_start_string, period, token, limit, will_not_work_segment)
        might_not_work_page = "@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"
        might_not_work_segment = "pageTitle={};customVariableValue1=={};customVariableValue3==REGISTRATION".format(
            might_not_work_page, rp)
        visits_might_not_work = get_nb_visits_for_page(date_start_string, period, token, limit, might_not_work_segment)
        row = df_all.loc[(df_all['rp'] == rp), 'visits_will_not_work'] = visits_will_not_work
        row = df_all.loc[(df_all['rp'] == rp), 'visits_might_not_work'] = visits_might_not_work

# ## Export results


# Re-order columns and choose the ones we actually (currently) want in our report
df_export = df_all[['rp', 'all_referrals_with_intent', 'success', 'success_fraction_signup', 'success_fraction_signin',
                    'visits_will_not_work', 'visits_might_not_work']]

if not os.path.exists(report_output_path):
    os.makedirs(report_output_path)

# Create export file with all RPs data
df_export.to_csv(f'{report_output_path}/rp_report-{date_start_string}.csv')

# Create export file per RP

for index, rp_data_row in df_export.iterrows():
    rp_name = rp_data_row['rp']
    rp_data_row.to_csv(f'{report_output_path}/rp_report-{date_start_string}-{rp_name}.csv')
