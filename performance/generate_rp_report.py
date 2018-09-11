"""
Generate RP reports from Piwik and Successful verifications data

expects: the following files to be present in verify-data-pipeline-config:
verifications_by_rp_<for-required-week>.csv
piwik configuration in piwik.json
"""
import argparse

import pandas as pd
import json
import requests
import os
from datetime import date, timedelta
from performance.piwikclient import PiwikClient

VERIFY_DATA_PIPELINE_CONFIG_PATH = '../../verify-data-pipeline-config'
PIWIK_BASE_URL = 'https://analytics-hub-prod-a-dmz.ida.digital.cabinet-office.gov.uk/index.php'
ENV = 'prod'

PIWIK_PERIOD = 'week'
PIWIK_LIMIT = '-1'


# TODO this should come from config
LOA1_RP_LIST = ["DFT DVLA VDL", "Get your State Pension", "NHS TRS"]


def get_piwik_token(env):
    with open(f'{VERIFY_DATA_PIPELINE_CONFIG_PATH}/credentials/piwik_token.json') as fileHandle:
        token = json.load(fileHandle)['production' if env == 'prod' else 'dr_token']
        return token


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

    response = requests.get(PIWIK_BASE_URL, qs)

    raw_result = response.json()
    nb_visits = next(iter(raw_result), {}).get('nb_visits', 0)
    return nb_visits


def get_segment_query_string(rp_name, journey_type=None):
    segment = f"customVariableValue1=={rp_name}"
    if journey_type:
        segment += f";customVariableValue3=={journey_type}"
    return segment


def get_all_visits_for_rp_and_journey_type_from_piwik(piwik_client, date_start_string, rp_name, journey_type):
    segment = get_segment_query_string(rp_name, journey_type)
    return piwik_client.get_nb_visits_for_rp(date_start_string, segment)


def get_all_referrals_for_rp_from_piwik(piwik_client, rp, date_start_string):
    segment_by_rp = get_segment_query_string(rp)
    return piwik_client.get_nb_visits_for_rp(date_start_string, segment_by_rp)


def get_all_signin_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string):
    journey_type = 'SIGN_IN'
    return get_all_visits_for_rp_and_journey_type_from_piwik(piwik_client, date_start_string, rp, journey_type)


def get_all_signup_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string):
    journey_type = 'REGISTRATION'
    return get_all_visits_for_rp_and_journey_type_from_piwik(piwik_client, date_start_string, rp, journey_type)


def get_all_single_idp_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string):
    journey_type = 'SINGLE_IDP'
    return get_all_visits_for_rp_and_journey_type_from_piwik(piwik_client, date_start_string, rp, journey_type)


def get_visits_will_not_work_from_piwik(rp, date_start_string, token):
    will_not_work_page = "@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"
    will_not_work_segment = "pageTitle={};customVariableValue1=={};customVariableValue3==REGISTRATION".format(
        will_not_work_page, rp)

    return get_nb_visits_for_page(date_start_string, PIWIK_PERIOD, token, PIWIK_LIMIT, will_not_work_segment)


def get_visits_might_not_work_from_piwik(rp, date_start_string, token):
    might_not_work_page = "@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"
    might_not_work_segment = "pageTitle={};customVariableValue1=={};customVariableValue3==REGISTRATION".format(
        might_not_work_page, rp)
    return get_nb_visits_for_page(date_start_string, PIWIK_PERIOD, token, PIWIK_LIMIT, might_not_work_segment)


def is_loa2(rp):
    return rp not in LOA1_RP_LIST


def load_args_from_command_line():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--report_start_date', help='expected format: YYYY-MM-DD', required=True)
    parser.add_argument('--report_output_path', help='relative path to output report CSV', default='../output')

    args = parser.parse_args()
    return args


def run():
    params = load_args_from_command_line()
    date_start = date.fromisoformat(params.report_start_date)
    date_end = date_start + timedelta(days=6)
    date_start_string = params.report_start_date
    verifications_by_rp_csv = \
        f'{VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications/verifications_by_rp_{date_start}_{date_end}.csv'
    report_output_path = params.report_output_path

    token = get_piwik_token(ENV)

    piwik_client = PiwikClient(token, PIWIK_BASE_URL)

    df_verifications_by_rp = pd.read_csv(verifications_by_rp_csv)
    # ## Getting the volume of sessions for sign up and sign in
    # No longer uses unique page views - gets the number of sessions for each value of the JOURNEY_TYPE custom variable
    # rp_mapping translates the referrer url reported in the verifications csv
    with open(f'{VERIFY_DATA_PIPELINE_CONFIG_PATH}/configuration/rp_mapping.json') as ft:
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
    for rp in ls_rp:
        print("Getting data for {}".format(rp))

        all_referrals = get_all_referrals_for_rp_from_piwik(piwik_client, rp, date_start_string)

        signin_attempts = get_all_signin_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string)

        signup_attempts = get_all_signup_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string)

        single_idp_attempts = get_all_single_idp_attempts_for_rp_from_piwik(piwik_client, rp, date_start_string)

        # TODO if the RP is not found (e.g. due to no successful signins) then we may need to add a row?
        df_all.loc[(df_all['rp'] == rp), 'all_referrals'] = all_referrals
        df_all.loc[(df_all['rp'] == rp), 'signin_attempt'] = signin_attempts
        df_all.loc[(df_all['rp'] == rp), 'signup_attempt'] = signup_attempts
        df_all.loc[(df_all['rp'] == rp), 'single_idp_attempt'] = single_idp_attempts
    df_all['signin_rate (deprecated)'] = df_all['signin_success'] / df_all['signin_attempt']
    df_all['signup_rate (deprecated)'] = df_all['signup_success'] / df_all['signup_attempt']
    df_all['all_referrals_with_intent'] = df_all['signin_attempt'] + df_all['signup_attempt'] + df_all[
        'single_idp_attempt']
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
    for rp in ls_rp:
        if is_loa2(rp):
            visits_will_not_work = get_visits_will_not_work_from_piwik(rp, date_start_string, token)

            visits_might_not_work = get_visits_might_not_work_from_piwik(rp, date_start_string, token)

            df_all.loc[(df_all['rp'] == rp), 'visits_will_not_work'] = visits_will_not_work
            df_all.loc[(df_all['rp'] == rp), 'visits_might_not_work'] = visits_might_not_work
    # ## Export results
    # Re-order columns and choose the ones we actually (currently) want in our report
    df_export = df_all[
        ['rp', 'all_referrals_with_intent', 'success', 'success_fraction_signup', 'success_fraction_signin',
         'visits_will_not_work', 'visits_might_not_work']]
    if not os.path.exists(report_output_path):
        os.makedirs(report_output_path)
    # Create export file with all RPs data
    df_export.to_csv(f'{report_output_path}/rp_report-{date_start_string}.csv')
    # Create export file per RP
    for index, rp_data_row in df_export.iterrows():
        rp_name = rp_data_row['rp']
        rp_data_row.to_csv(f'{report_output_path}/rp_report-{date_start_string}-{rp_name}.csv')


if __name__ == '__main__':
    run()
