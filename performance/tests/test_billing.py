import os
from unittest.mock import patch

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


@patch('performance.billing.rp_mapping', get_sample_rp_mapping())
def test_augment_verifications_by_rp_with_rp_name():
    sample_verifications_by_rp = get_sample_verifications_by_rp_dataframe()
    expected_transformed_data = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    billing.augment_verifications_by_rp_with_rp_name(sample_verifications_by_rp)
    assert_frame_equal(expected_transformed_data, sample_verifications_by_rp)
