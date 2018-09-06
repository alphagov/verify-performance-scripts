#!/usr/bin/env python3

"""
Upload a file to S3.

Usage:
    python3 upload.py -f <file-name>
"""

import argparse
import boto3
from scripts.env import check_get_env
from dotenv import load_dotenv

load_dotenv(override=True)

RP_REPORT_OUTPUT_BUCKET = check_get_env('RP_REPORT_OUTPUT_BUCKET')


def get_aws_session():
    return boto3.Session()


def get_s3_resource():
    session = get_aws_session()
    return session.resource('s3')


def upload_file(file_name):
    """
    Upload a file given by its name to S3.

    Args:
        file_name: Name of the file to upload.
    """
    s3 = get_s3_resource()
    bucket = s3.Bucket(RP_REPORT_OUTPUT_BUCKET)
    bucket.upload_file(file_name, f'output/rp/{file_name}', {'ServerSideEncryption': 'AES256'})


def main(file_name):
    upload_file(file_name)
    print('File uploaded successfully.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='File to upload', type=str)
    args = parser.parse_args()
    main(args.filename)
