import json
import os
from unittest.mock import patch, mock_open

from pandas.util.testing import assert_frame_equal

import performance.billing as billing
from performance.tests.fixtures import get_sample_verifications_by_rp_dataframe, get_sample_rp_mapping


@patch('pandas.read_csv')
@patch('performance.billing.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='my_path')
def test_extract_verifications_by_rp_csv_for_date(mock_config, mock_pandas_read_csv):
    date_start = '2018-07-02'
    expected_verification_csv_filepath_to_load = os.path.join(
        'my_path',
        'data/verifications/verifications_by_rp_2018-07-02_2018-07-08.csv')

    billing.extract_verifications_by_rp_csv_for_date(date_start)

    mock_pandas_read_csv.assert_called_with(expected_verification_csv_filepath_to_load)


RP_MAPPING_STREAM = """
{"entityid-1": "rp-name-1", "entityid-2": "rp-name-2"}
"""


@patch('performance.billing.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='config-path')
def test_get_rp_name(mock_config):
    sample_rp_mapping = json.loads(RP_MAPPING_STREAM)

    verify_data_pipeline_config_path = 'config-path'
    with patch('performance.billing.open', mock_open(read_data=RP_MAPPING_STREAM),
               create=True) as mock_main_open:
        rp_federation_config = billing.RPFederationConfig(mock_config)

    mock_main_open.assert_called_with(f"{verify_data_pipeline_config_path}/configuration/rp_mapping.json")
    assert rp_federation_config == sample_rp_mapping

    assert "rp-name-2" == rp_federation_config["entityid-2"]


@patch('performance.billing._rp_mapping', new=get_sample_rp_mapping())
def test_augment_verifications_by_rp_with_rp_name():
    sample_verifications_by_rp = get_sample_verifications_by_rp_dataframe()
    expected_transformed_data = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    billing.augment_verifications_by_rp_with_rp_name(sample_verifications_by_rp)
    assert_frame_equal(expected_transformed_data, sample_verifications_by_rp)
