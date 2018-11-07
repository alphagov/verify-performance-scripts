import boto3


def get_aws_session():
    return boto3.Session()


def get_s3_resource():
    session = get_aws_session()
    return session.resource('s3')


def get_s3_bucket(bucket_name):
    return get_s3_resource().Bucket(bucket_name)


def get_report_file(bucket_name, file_path, destination):
    bucket = get_s3_bucket(bucket_name)
    bucket.download_file(file_path, destination)
