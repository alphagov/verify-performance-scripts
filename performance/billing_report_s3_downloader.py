from performance.env import check_get_env


class BillingReportS3Downloader:

    VERIFICATIONS_BY_RP_S3_FOLDER = 'rp'

    def __init__(self, resource):
        """
        Args:
            resource: AWS S3 resource object.
        """
        self._resource = resource
        self.verifications_by_rp_s3_bucket = check_get_env('BILLING_REPORT_S3_BUCKET')

    def download_verifications_by_rp_report_to_folder(self, filename, destination_folder):
        print(f'Downloading verifications_by_RP_report {filename} from AWS S3')
        self.download(
            self.verifications_by_rp_s3_bucket,
            self.VERIFICATIONS_BY_RP_S3_FOLDER,
            filename,
            destination_folder)

    def download(self, bucket_name, bucket_folder_path, file_name, destination_folder):
        bucket = self._resource.Bucket(bucket_name)
        bucket.download_file(f'{bucket_folder_path}/{file_name}', f'{destination_folder}/{file_name}')
