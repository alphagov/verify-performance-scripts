import json
import os
from datetime import date, timedelta

import pandas

from performance import config


class RPFederationConfig(dict):
    """
        rp_mapping translates the referrer url reported in the verifications csv
    """
    rp_mapping_config_path = 'configuration/rp_mapping.json'

    def __init__(self, config):
        with open(os.path.join(config.VERIFY_DATA_PIPELINE_CONFIG_PATH, self.rp_mapping_config_path)) as fn:
            super().__init__(json.load(fn))


_rp_mapping = RPFederationConfig(config)


def extract_verifications_by_rp_csv_for_date(date_start):
    """
    Extract billing data from the weekly verifications_by_rp.csv report
    :param date_start: start date for the week
    :return: pandas.Dataframe with non transformed data with matching columns to the original verifications_by_rp
    """
    date_end = date.fromisoformat(date_start) + timedelta(days=6)
    verifications_by_rp_csv_path = \
        f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications/verifications_by_rp_{date_start}_{date_end}.csv'

    df_verifications_by_rp = pandas.read_csv(verifications_by_rp_csv_path)
    return df_verifications_by_rp


def augment_verifications_by_rp_with_rp_name(df_verifications_by_rp):
    """
    Transformation step that gets the human readable RP name and adds it inplace to a new column
    for verifications_by_rp data
    :param df_verifications_by_rp: dataframe created from a verifications_by_rp report
    """
    df_verifications_by_rp['rp'] = df_verifications_by_rp.apply(lambda row: _rp_mapping[row['RP Entity Id']],
                                                                axis=1)
