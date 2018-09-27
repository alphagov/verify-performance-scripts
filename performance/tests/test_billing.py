import os
from unittest.mock import patch

from pandas.util.testing import assert_frame_equal

import performance.billing as billing
from performance.tests.fixtures import get_sample_verifications_by_rp_dataframe, get_sample_rp_mapping


@patch('os.path.exists', return_value=True)
@patch('performance.billing.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='my_path')
@patch('performance.billing.BillingReportS3Downloader')
@patch('pandas.read_csv')
def test_extract_verifications_by_rp_csv_for_week(mock_pandas_read_csv, mock_billing_report_downloader, mock_config, _):
    date_start = '2018-07-02'
    expected_verification_csv_filepath_to_load = os.path.join(
        'my_path',
        'data/verifications/verifications_by_rp_2018-07-02_2018-07-08.csv')

    billing.extract_verifications_by_rp_csv_for_week(date_start)

    mock_pandas_read_csv.assert_called_with(expected_verification_csv_filepath_to_load)
    mock_billing_report_downloader.download_verifications_by_rp_report_to_folder.assert_not_called()


@patch("os.path.exists", return_value=False)
@patch('performance.billing.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='my_path')
@patch('performance.billing.BillingReportS3Downloader')
@patch('pandas.read_csv')
def test_extract_verifications_by_rp_downloads_csv_when_not_present(mock_pandas_read_csv,
                                                                    mock_billing_report_downloader, mock_config, _):
    date_start = '2018-07-02'
    expected_verification_csv_filename = 'verifications_by_rp_2018-07-02_2018-07-08.csv'
    expected_verification_csv_destination_path = os.path.join('my_path', 'data/verifications')

    billing.extract_verifications_by_rp_csv_for_week(date_start)

    mock_billing_report_downloader.return_value.download_verifications_by_rp_report_to_folder.\
        assert_called_with(expected_verification_csv_filename, expected_verification_csv_destination_path)


@patch('performance.billing.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='pipeline_config_path', )
@patch('performance.billing.BillingReportS3Downloader')
def test_download_verifications_by_rp_report_for_week(mock_billing_report_downloader, mock_config):
    start_date = '2018-09-03'
    expected_verifications_report_filename = 'verifications_by_rp_2018-09-03_2018-09-09.csv'

    billing.download_verifications_by_rp_report_for_week(start_date)

    mock_billing_report_downloader.return_value.download_verifications_by_rp_report_to_folder\
        .assert_called_with(expected_verifications_report_filename, 'pipeline_config_path/data/verifications')


@patch('performance.billing.rp_mapping', get_sample_rp_mapping())
def test_augment_verifications_by_rp_with_rp_name():
    sample_verifications_by_rp = get_sample_verifications_by_rp_dataframe()
    expected_transformed_data = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    billing.augment_verifications_by_rp_with_rp_name(sample_verifications_by_rp)
    assert_frame_equal(expected_transformed_data, sample_verifications_by_rp)
