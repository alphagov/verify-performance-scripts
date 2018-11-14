import os
import argparse
import logging
from datetime import timedelta, datetime

import pandas

from performance import prod_config as config
from performance.aws import get_report_file


def fromisoformat(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_string)
        raise argparse.ArgumentTypeError(msg)


def extract_verifications_by_rp_csv_for_date(date_start):
    """
    Extract billing data from the weekly verifications_by_rp.csv report
    :param date_start: start date for the week
    :return: pandas.Dataframe with non transformed data with matching columns to the original verifications_by_rp
    """
    date_end = fromisoformat(date_start) + timedelta(days=6)
    file_name = f'verifications_by_rp_{date_start}_{date_end}.csv'
    verifications_directory = os.path.join(config.VERIFY_DATA_PIPELINE_CONFIG_PATH,
                                           'data',
                                           'verifications')
    verifications_by_rp_csv_path = os.path.join(verifications_directory, file_name)

    if os.path.exists(verifications_by_rp_csv_path):
        logging.info(f'Using local copy of {file_name}')
    else:
        logging.info(f'Downloading verifications report: {file_name}')
        if not os.path.exists(verifications_directory):
            logging.info('Creating data/verifications directories')
            os.makedirs(verifications_directory)

        get_report_file(
            config.S3_BILLING_REPORTS_BUCKET,
            os.path.join(config.S3_VERIFICATIONS_DIRECTORY, file_name),
            verifications_by_rp_csv_path
        )

    df_verifications_by_rp = pandas.read_csv(verifications_by_rp_csv_path)
    return df_verifications_by_rp


def augment_verifications_by_rp_with_rp_name(df_verifications_by_rp):
    """
    Transformation step that gets the human readable RP name and adds it inplace to a new column
    for verifications_by_rp data
    :param df_verifications_by_rp: dataframe created from a verifications_by_rp report
    """
    df_verifications_by_rp['rp'] = df_verifications_by_rp.apply(lambda row: config.rp_mapping[row['RP Entity Id']],
                                                                axis=1)
