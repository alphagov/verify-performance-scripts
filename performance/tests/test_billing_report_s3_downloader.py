from performance.billing_report_s3_downloader import BillingReportS3Downloader
from unittest.mock import Mock, patch


@patch('performance.billing_report_s3_downloader.check_get_env', return_value='verifications_bucket_name')
def test_download_verifications_by_rp_report_to_folder(mock_env):

    filename = 'verifications_by_rp_2018-09-03_2018-09-09.csv'
    destination_folder = 'destination_folder_path'

    aws_resource_mock = Mock()
    bucket = Mock()
    aws_resource_mock.Bucket.return_value = bucket
    billing_report_downloader = BillingReportS3Downloader(aws_resource_mock)

    billing_report_downloader.download_verifications_by_rp_report_to_folder(filename, destination_folder)

    expected_folder_name_in_s3 = 'rp'

    aws_resource_mock.Bucket.assert_called_with('verifications_bucket_name')
    bucket.download_file.assert_called_with(
        f'{expected_folder_name_in_s3}/{filename}',
        f'{destination_folder}/{filename}')
