from unittest.mock import Mock

from performance.uploader import Uploader


def test_upload():
    aws_resource_mock = Mock()
    bucket = Mock()
    aws_resource_mock.Bucket.return_value = bucket
    uploader = Uploader(aws_resource_mock)

    uploader.upload('bucket_name', 'file_name')

    aws_resource_mock.Bucket.assert_called()
    bucket.upload_file.assert_called()
