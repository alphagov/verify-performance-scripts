from unittest.mock import Mock, ANY

from performance.uploader import Uploader


def test_upload():
    aws_resource_mock = Mock()
    bucket = Mock()
    aws_resource_mock.Bucket.return_value = bucket
    uploader = Uploader(aws_resource_mock)

    uploader.upload('bucket_name', 'file_name')

    aws_resource_mock.Bucket.assert_called_with('bucket_name')
    bucket.upload_file.assert_called_with('file_name', ANY, ANY)
