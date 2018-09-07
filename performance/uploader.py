class Uploader:
    def __init__(self, resource):
        """
        Args:
            resource: AWS S3 resource object.
        """
        self._resource = resource

    def upload(self, bucket_name, file_name):
        """
        Upload a file given by its name to an S3 bucket.

        Args:
            bucket_name: Name of the bucket to upload the file to.
            file_name: Name of the file to upload.
        """
        bucket = self._resource.Bucket(bucket_name)
        bucket.upload_file(file_name, f'output/rp/{file_name}', {'ServerSideEncryption': 'AES256'})
