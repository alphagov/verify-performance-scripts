import boto3


def get_aws_session():
    return boto3.Session()


def get_s3_resource():
    session = get_aws_session()
    return session.resource('s3')
