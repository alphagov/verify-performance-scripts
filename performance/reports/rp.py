import os

import pandas
import pygsheets

import performance.piwik as piwik
import performance.billing as billing
from performance.rp_federation_config import rp_mapping

from performance import prod_config as config
import performance
from performance.reports.tests import conftest


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


class GoogleSheetsRelyingPartyReportExporter:
    SHEET_TAB_NAME = 'Sheet1'  # TODO hmmm

    def __init__(self, config, pygsheets_client):
        self._config = config
        self._pygsheets_client = pygsheets_client

    def export(self, data_frame, column_heading):
        data_frame = data_frame.fillna('')
        for row in data_frame.itertuples():
            rp_name = row.rp
            sheet_key = self._config.rp_information[rp_name]['sheet_key']
            if sheet_key:
                values_list = self.format_for_gsheets(row, column_heading if column_heading is not None else rp_name)
                # TODO check that column 1 contains expected field names
                self.send_to_gsheets(values_list, sheet_key, self.SHEET_TAB_NAME)

    def send_to_gsheets(self, values_list, sheet_key, sheet_tab_name):
        sheet = self._pygsheets_client.open_by_key(sheet_key)
        worksheet = sheet.worksheet_by_title(sheet_tab_name)

        # insert a new column right after the one showing field name
        worksheet.insert_cols(1, 1, values=values_list)

    def format_for_gsheets(self, row, column_heading):
        return [
            column_heading,
            row.all_referrals_with_intent,
            row.success,
            row.success_fraction_signup,
            row.success_fraction_signin,
            row.visits_will_not_work,
            row.visits_might_not_work,
        ]


def test_upload(gsheets_key, date_start):
    """
    Similar to our unit test `test_export_metrics_to_google_sheets`, however because
    in this case we're actually going to do the upload the Google Sheets, this one is
    runnable independently from the command line.
    """
    # Get test configuration because we need our rp_information to refer to the same set
    # of test RP's as are used in the rp_report_weekly fixture. We're using the fixture
    # because if you want to test the upload process, you don't want to have to wait around
    # for Piwik - any data will do.
    config = performance.config.TestConfig()
    pygsheets_client = pygsheets.authorize(service_file=config.GSHEETS_CREDENTIALS_FILE)
    for rp_info in config.rp_information.values():
        rp_info['sheet_key'] = gsheets_key

    exporter = GoogleSheetsRelyingPartyReportExporter(config, pygsheets_client)
    # setting column_heading to None to trigger special behaviour that's useful when all RP data ends up in one sheet
    # consequently we are ignoring date_start
    exporter.export(conftest.rp_report_weekly(), column_heading=None)


def is_loa2(rp):
    return rp not in LOA1_RP_LIST


def get_rp_names_from_df(df_verifications_by_rp):
    return df_verifications_by_rp.rp.unique().tolist()


def get_df_successes_by_rp(df_verifications_by_rp):
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


def export_metrics_to_google_sheets(df_export, date_start):
    pygsheets_client = pygsheets.authorize(service_file=config.GSHEETS_CREDENTIALS_FILE)
    exporter = GoogleSheetsRelyingPartyReportExporter(config, pygsheets_client)
    exporter.export(df_export, column_heading=date_start)


def generate_weekly_report_for_date(date_start, report_output_path):
    # load billing csv file
    df_verifications_by_rp = billing.extract_verifications_by_rp_csv_for_date(date_start)
    billing.augment_verifications_by_rp_with_rp_name(df_verifications_by_rp)
    df_all = generate_weekly_report_df(date_start, df_verifications_by_rp)
    # Re-order columns and choose the ones we actually (currently) want in our report
    df_export = df_all[RP_REPORT_COLUMNS]
    export_metrics_to_csv(df_export, report_output_path, date_start)
    export_metrics_to_google_sheets(df_export, date_start)


def generate_weekly_report_df(date_start, df_verifications_by_rp):
    df = add_piwik_data(date_start, df_verifications_by_rp)
    transform_metrics(df)
    return df


def transform_metrics(df):
    df['all_referrals_with_intent'] = df['signin_attempt'] + df['signup_attempt'] + df['single_idp_attempt']
    df['success'] = df['signin_success'] + df['signup_success']
    df['success_fraction_signup'] = df['signup_success'] / df['success']
    df['success_fraction_signin'] = df['signin_success'] / df['success']
    # Note: The below metrics are no longer used, and so have been disabled.
    # df['signin_rate (deprecated)'] = df['signin_success'] / df['signin_attempt']
    # df['signup_rate (deprecated)'] = df['signup_success'] / df['signup_attempt']
    # df['success_rate'] = df['success'] / df['all_referrals_with_intent']
    # df['success_signup_rate'] = df['signup_success'] / df['all_referrals_with_intent']
    # df['success_signin_rate'] = df['signin_success'] / df['all_referrals_with_intent']
    # df['dropout'] = df['all_referrals_with_intent'] - df['signin_success'] - df['signup_success']
    # df['dropout_rate'] = df['dropout'] / df['all_referrals_with_intent']


def add_piwik_data(date_start, df_verifications_by_rp):
    df_successes_rp = get_df_successes_by_rp(df_verifications_by_rp)
    df_all_rp = get_df_for_all_rps(df_successes_rp)
    for rp in get_rp_names_from_df(df_all_rp):
        add_piwik_data_for_rp(date_start, df_all_rp, rp)
    return df_all_rp


def get_df_for_all_rps(df_successes_rp):
    all_rp_names = set(rp_mapping.values())
    rp_names_with_successes = set(get_rp_names_from_df(df_successes_rp))
    rp_names_missing = sorted(list(all_rp_names.difference(rp_names_with_successes)))
    df_missing_rp = pandas.DataFrame.from_dict({k: [v, 0, 0] for k, v in enumerate(rp_names_missing)},
                                               orient="index",
                                               columns=["rp", "signup_success", "signin_success"])
    df_all_rp = df_successes_rp.append(df_missing_rp, ignore_index=True)
    return df_all_rp


def add_piwik_data_for_rp(date_start, df_successes_rp, rp):
    print("Getting data for {}".format(rp))
    # Note: The below metric is no longer used, and so has been disabled.
    # all_referrals = piwik.get_all_referrals_for_rp(rp, date_start)
    # df_all.loc[(df_all['rp'] == rp), 'all_referrals'] = all_referrals
    signin_attempts = piwik.get_all_signin_attempts_for_rp(rp, date_start)
    signup_attempts = piwik.get_all_signup_attempts_for_rp(rp, date_start)
    single_idp_attempts = piwik.get_all_single_idp_attempts_for_rp(rp, date_start)
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'signin_attempt'] = signin_attempts
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'signup_attempt'] = signup_attempts
    df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'single_idp_attempt'] = single_idp_attempts
    if is_loa2(rp):
        visits_will_not_work = piwik.get_visits_will_not_work(rp, date_start)
        visits_might_not_work = piwik.get_visits_might_not_work(rp, date_start)
        df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'visits_will_not_work'] = visits_will_not_work
        df_successes_rp.loc[(df_successes_rp['rp'] == rp), 'visits_might_not_work'] = visits_might_not_work
