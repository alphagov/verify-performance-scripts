from unittest.mock import patch

from pandas.util.testing import assert_frame_equal

import performance.billing as billing
from performance.tests.fixtures import get_sample_verifications_by_rp_dataframe, get_sample_rp_mapping
from performance import prod_config as config


@patch('os.path.exists', return_value=True)
@patch('pandas.read_csv')
@patch('performance.billing.get_report_file')
def test_extract_verifications_with_local_rp_csv_for_date(mock_get_report,
                                                          mock_pandas_read_csv, mock_path_exists):
    date_start = '2018-07-02'
    expected_verification_csv_filepath_to_load = f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications/verifications_by_rp_2018-07-02_2018-07-08.csv'  # noqa

    billing.extract_verifications_by_rp_csv_for_date(date_start)

    mock_get_report.assert_not_called()
    mock_pandas_read_csv.assert_called_with(expected_verification_csv_filepath_to_load)


@patch('os.path.exists', side_effect=[False, True])  # File does not exist but data/verifications directory does
@patch('pandas.read_csv', return_value={})
@patch('performance.billing.get_report_file')
def test_retrieve_report_file_from_s3_when_no_local_exists(mock_get_report, mock_pandas_read_csv, mock_path_exists):
    date_start = '2018-07-02'
    file_name = 'verifications_by_rp_2018-07-02_2018-07-08.csv'
    s3_path = f'rp/{file_name}'
    destination_path = f'{config.VERIFY_DATA_PIPELINE_CONFIG_PATH}/data/verifications/{file_name}'

    billing.extract_verifications_by_rp_csv_for_date(date_start)

    mock_get_report.assert_called_with(config.S3_BILLING_REPORTS_BUCKET, s3_path, destination_path)


@patch('performance.billing.config.rp_mapping', get_sample_rp_mapping())
def test_augment_verifications_by_rp_with_rp_name():
    sample_verifications_by_rp = get_sample_verifications_by_rp_dataframe()
    expected_transformed_data = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    billing.augment_verifications_by_rp_with_rp_name(sample_verifications_by_rp)
    assert_frame_equal(expected_transformed_data, sample_verifications_by_rp)
