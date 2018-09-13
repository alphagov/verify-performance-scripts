"""
Generate RP reports from Piwik and Successful verifications data

expects: the following files to be present in verify-data-pipeline-config:
verifications_by_rp_<for-required-week>.csv
piwik configuration in piwik.json
"""
import argparse

import pandas
import os
from datetime import date, timedelta

from performance import piwik_client, config, rp_mapping

# TODO this should come from config
LOA1_RP_LIST = ["DFT DVLA VDL", "Get your State Pension", "NHS TRS"]


def get_segment_query_string(rp_name, journey_type=None, page_title=None):
    segment = f"customVariableValue1=={rp_name}"
    if journey_type:
        segment += f";customVariableValue3=={journey_type}"
    if page_title:
        segment += f";pageTitle={page_title}"
    return segment


def get_all_visits_for_rp_and_journey_type_from_piwik(date_start_string, rp_name, journey_type):
    segment = get_segment_query_string(rp_name, journey_type)
    return piwik_client.get_nb_visits_for_rp(date_start_string, segment)


def get_all_referrals_for_rp_from_piwik(rp, date_start_string):
    segment_by_rp = get_segment_query_string(rp)
    return piwik_client.get_nb_visits_for_rp(date_start_string, segment_by_rp)


def get_all_signin_attempts_for_rp_from_piwik(rp, date_start_string):
    journey_type = 'SIGN_IN'
    return get_all_visits_for_rp_and_journey_type_from_piwik(date_start_string, rp, journey_type)


def get_all_signup_attempts_for_rp_from_piwik(rp, date_start_string):
    journey_type = 'REGISTRATION'
    return get_all_visits_for_rp_and_journey_type_from_piwik(date_start_string, rp, journey_type)


def get_all_single_idp_attempts_for_rp_from_piwik(rp, date_start_string):
    journey_type = 'SINGLE_IDP'
    return get_all_visits_for_rp_and_journey_type_from_piwik(date_start_string, rp, journey_type)


def get_visits_will_not_work_from_piwik(rp, date_start_string):
    will_not_work_page = "@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"
    journey_type = 'REGISTRATION'
    will_not_work_segment = get_segment_query_string(rp, journey_type, will_not_work_page)

    return piwik_client.get_nb_visits_for_page(date_start_string, will_not_work_segment)


def get_visits_might_not_work_from_piwik(rp, date_start_string):
    might_not_work_page = "@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"
    journey_type = 'REGISTRATION'
    might_not_work_segment = get_segment_query_string(rp, journey_type, might_not_work_page)

    return piwik_client.get_nb_visits_for_page(date_start_string, might_not_work_segment)


def is_loa2(rp):
    return rp not in LOA1_RP_LIST


def load_args_from_command_line():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--report_start_date', help='expected format: YYYY-MM-DD', required=True)
    parser.add_argument('--report_output_path', help='relative path to output report CSV',
                        default=('%s' % config.DEFAULT_OUTPUT_PATH))

    args = parser.parse_args()
    return args


def load_verifications_by_rp_csv_for_date(date_start):
    date_end = date.fromisoformat(date_start) + timedelta(days=6)
    verifications_by_rp_csv_path = \
        f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications/verifications_by_rp_{date_start}_{date_end}.csv'

    df_verifications_by_rp = pandas.read_csv(verifications_by_rp_csv_path)
    return df_verifications_by_rp


def export_metrics_to_csv(df_export, report_output_path, date_start):
    if not os.path.exists(report_output_path):
        os.makedirs(report_output_path)
    # Create export file with all RPs data
    df_export.to_csv(os.path.join(report_output_path, f'rp_report-{date_start}.csv'))
    # Create export file per RP
    for index, rp_data_row in df_export.iterrows():
        rp_name = rp_data_row['rp']
        rp_data_row.to_csv(os.path.join(report_output_path, f'rp_report-{date_start}-{rp_name}.csv'))


def run(params):
    date_start = params.report_start_date
    report_output_path = params.report_output_path

    df_verifications_by_rp = load_verifications_by_rp_csv_for_date(date_start)

    # ## Getting the volume of sessions for sign up and sign in
    # No longer uses unique page views - gets the number of sessions for each value of the JOURNEY_TYPE custom variable

    # Get the human readable IDP name and add it to a new column
    df_verifications_by_rp['rp'] = df_verifications_by_rp.apply(lambda row: rp_mapping[row['RP Entity Id']],
                                                                axis=1)
    df_verifications_by_rp.head()
    df_verifications_by_rp = df_verifications_by_rp.rename(columns={'Response type': 'response_type'})
    df_totals = df_verifications_by_rp.groupby(['rp', 'response_type']).count().reset_index()
    df_totals.head()
    df_totals.drop(['Timestamp', 'RP Entity Id'], axis=1, inplace=True)
    df_totals = df_totals.rename(columns={'IDP Entity Id': 'successes'})
    df_all = pandas.pivot_table(df_totals, values='successes', index='rp', columns='response_type')
    df_all.reset_index(inplace=True)
    df_all.columns = ['rp', 'signup_success', 'signin_success']
    # ### Success rate (sign in)
    ls_rp = list(df_verifications_by_rp.rp.unique())
    for rp in ls_rp:
        print("Getting data for {}".format(rp))

        all_referrals = get_all_referrals_for_rp_from_piwik(rp, date_start)

        signin_attempts = get_all_signin_attempts_for_rp_from_piwik(rp, date_start)

        signup_attempts = get_all_signup_attempts_for_rp_from_piwik(rp, date_start)

        single_idp_attempts = get_all_single_idp_attempts_for_rp_from_piwik(rp, date_start)

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
            visits_will_not_work = get_visits_will_not_work_from_piwik(rp, date_start)

            visits_might_not_work = get_visits_might_not_work_from_piwik(rp, date_start)

            df_all.loc[(df_all['rp'] == rp), 'visits_will_not_work'] = visits_will_not_work
            df_all.loc[(df_all['rp'] == rp), 'visits_might_not_work'] = visits_might_not_work
    # ## Export results
    # Re-order columns and choose the ones we actually (currently) want in our report
    df_export = df_all[
        ['rp', 'all_referrals_with_intent', 'success', 'success_fraction_signup', 'success_fraction_signin',
         'visits_will_not_work', 'visits_might_not_work']]
    export_metrics_to_csv(df_export, report_output_path, date_start)


if __name__ == '__main__':
    params = load_args_from_command_line()
    run(params)
