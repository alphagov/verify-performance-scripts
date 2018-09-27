import argparse
import os
from datetime import timedelta, datetime

import pandas

from performance import config
from performance.rp_federation_config import rp_mapping
from performance.billing_report_s3_downloader import BillingReportS3Downloader
from performance import aws


def fromisoformat(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_string)
        raise argparse.ArgumentTypeError(msg)


def extract_verifications_by_rp_csv_for_week(date_start):
    """
    Extract billing data from the weekly verifications_by_rp.csv report
    :param date_start: start date for the week
    :return: pandas.Dataframe with non transformed data with matching columns to the original verifications_by_rp
    """
    verifications_by_rp_csv_filename = get_verification_report_filename_for_week(date_start)
    verifications_by_rp_csv_folder = f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications'

    verifications_by_rp_csv_path = \
        f'{verifications_by_rp_csv_folder}/{verifications_by_rp_csv_filename}'

    if not os.path.exists(verifications_by_rp_csv_path):
        download_verifications_by_rp_report_for_week(date_start)

    df_verifications_by_rp = pandas.read_csv(verifications_by_rp_csv_path)
    return df_verifications_by_rp


def get_verification_report_filename_for_week(date_start):
    date_end = fromisoformat(date_start) + timedelta(days=6)
    verifications_by_rp_csv_filename = f'verifications_by_rp_{date_start}_{date_end}.csv'
    return verifications_by_rp_csv_filename


def augment_verifications_by_rp_with_rp_name(df_verifications_by_rp):
    """
    Transformation step that gets the human readable RP name and adds it inplace to a new column
    for verifications_by_rp data
    :param df_verifications_by_rp: dataframe created from a verifications_by_rp report
    """
    df_verifications_by_rp['rp'] = df_verifications_by_rp.apply(lambda row: rp_mapping[row['RP Entity Id']],
                                                                axis=1)


def download_verifications_by_rp_report_for_week(date_start):
    verifications_by_rp_csv_filename = get_verification_report_filename_for_week(date_start)
    verifications_by_rp_csv_local_folder = f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications'

    billing_report_downloader = BillingReportS3Downloader(aws.get_s3_resource())
    billing_report_downloader.download_verifications_by_rp_report_to_folder(
        verifications_by_rp_csv_filename, verifications_by_rp_csv_local_folder)
