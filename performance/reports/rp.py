import os

import pandas

import performance.piwik as piwik
import performance.billing as billing

RP_REPORT_COLUMNS = [
    'rp',
    'all_referrals_with_intent',
    'success',
    'success_fraction_signup',
    'success_fraction_signin',
    'visits_will_not_work',
    'visits_might_not_work'
]

# TODO this should come from config
LOA1_RP_LIST = ["DFT DVLA VDL", "Get your State Pension", "NHS TRS"]


def is_loa2(rp):
    return rp not in LOA1_RP_LIST


def get_rps_with_successes(df_verifications_by_rp):
    """
    Get list of RPs that have successes under billing
    :param df_verifications_by_rp: Dataframe for verifications_by_rp CSV report
    :return: a list of rp entity ids
    """
    return df_verifications_by_rp.rp.unique().tolist()


def get_successes_by_rp(df_verifications_by_rp):
    df_verifications_by_rp = df_verifications_by_rp.rename(columns={'Response type': 'response_type'})
    df_totals = df_verifications_by_rp.groupby(['rp', 'response_type']).count().reset_index()
    df_totals.drop(['Timestamp', 'RP Entity Id'], axis=1, inplace=True)
    df_totals = df_totals.rename(columns={'IDP Entity Id': 'successes'})
    df_successes_by_rp = pandas.pivot_table(df_totals, values='successes', index='rp', columns='response_type',
                                            fill_value=0)
    df_successes_by_rp.reset_index(inplace=True)
    df_successes_by_rp.columns = ['rp', 'signup_success', 'signin_success']

    return df_successes_by_rp


def export_metrics_to_csv(df_export, report_output_path, date_start):
    if not os.path.exists(report_output_path):
        os.makedirs(report_output_path)
    # Create export file with all RPs data
    df_export.to_csv(os.path.join(report_output_path, f'rp_report-{date_start}.csv'))
    # Create export file per RP
    for index, rp_data_row in df_export.iterrows():
        rp_name = rp_data_row['rp']
        rp_data_row.to_csv(os.path.join(report_output_path, f'rp_report-{date_start}-{rp_name}.csv'))


def generate_weekly_report_for_date(date_start, report_output_path):
    # load billing csv file
    df_verifications_by_rp = billing.extract_verifications_by_rp_csv_for_date(date_start)
    billing.augment_verifications_by_rp_with_rp_name(df_verifications_by_rp)
    df_all = generate_weekly_report_df(date_start, df_verifications_by_rp)
    # Re-order columns and choose the ones we actually (currently) want in our report
    df_export = df_all[RP_REPORT_COLUMNS]
    export_metrics_to_csv(df_export, report_output_path, date_start)


def generate_weekly_report_df(date_start, df_verifications_by_rp):
    df = add_piwik_data(date_start, df_verifications_by_rp)
    transform_metrics(df)
    return df


def transform_metrics(df):
    # df['signin_rate (deprecated)'] = df['signin_success'] / df['signin_attempt']
    # df['signup_rate (deprecated)'] = df['signup_success'] / df['signup_attempt']
    df['all_referrals_with_intent'] = df['signin_attempt'] + df['signup_attempt'] + df[
        'single_idp_attempt']
    df['success'] = df['signin_success'] + df['signup_success']
    df['success_fraction_signup'] = df['signup_success'] / df['success']
    df['success_fraction_signin'] = df['signin_success'] / df['success']
    # df['success_rate'] = df['success'] / df['all_referrals_with_intent']
    # df['success_signup_rate'] = df['signup_success'] / df['all_referrals_with_intent']
    # df['success_signin_rate'] = df['signin_success'] / df['all_referrals_with_intent']
    # df['dropout'] = df['all_referrals_with_intent'] - df['signin_success'] - df['signup_success']
    # df['dropout_rate'] = df['dropout'] / df['all_referrals_with_intent']
    # ### Ineligible (will not work / might not work) - with journey type segment
    # upvson 'GOV.UK Verify will not work for you' page, segmented by 'registration' custom variable
    # iterate over RPs with billing results


def add_piwik_data(date_start, df_verifications_by_rp):
    df_successes_rp = get_successes_by_rp(df_verifications_by_rp)
    rps_with_successes = get_rps_with_successes(df_verifications_by_rp)
    # ## Getting the volume of sessions for sign up and sign in
    # No longer uses unique page views - gets the number of sessions for each value of the JOURNEY_TYPE custom variable
    # ### Success rate (sign in)
    # iterate over rps with Billing results
    for rp in rps_with_successes:
        add_piwik_data_for_rp(date_start, df_successes_rp, rp)
    return df_successes_rp


def add_piwik_data_for_rp(date_start, df_successes_rp, rp):
    print("Getting data for {}".format(rp))
    # all_referrals = piwik.get_all_referrals_for_rp(rp, date_start)
    signin_attempts = piwik.get_all_signin_attempts_for_rp(rp, date_start)
    signup_attempts = piwik.get_all_signup_attempts_for_rp(rp, date_start)
    single_idp_attempts = piwik.get_all_single_idp_attempts_for_rp(rp, date_start)
    # TODO if the RP is not found (e.g. due to no successful signins) then we may need to add a row?
    # df_all.loc[(df_all['rp'] == rp), 'all_referrals'] = all_referrals
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'signin_attempt'] = signin_attempts
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'signup_attempt'] = signup_attempts
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'single_idp_attempt'] = single_idp_attempts
    if is_loa2(rp):
        visits_will_not_work = piwik.get_visits_will_not_work(rp, date_start)
        visits_might_not_work = piwik.get_visits_might_not_work(rp, date_start)
        df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'visits_will_not_work'] = visits_will_not_work
        df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'visits_might_not_work'] = visits_might_not_work
