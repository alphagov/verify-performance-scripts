#!/usr/bin/env python3

"""
Upload a file to S3.

Usage:
    python3 upload.py <file-name>
"""

import bootstrap  # noqa
import argparse
from performance.config import check_get_env
from performance import aws
from performance.uploader import Uploader

RP_REPORT_OUTPUT_BUCKET = check_get_env('RP_REPORT_OUTPUT_BUCKET')


def main(file_name):
    resource = aws.get_s3_resource()
    uploader = Uploader(resource)
    uploader.upload(RP_REPORT_OUTPUT_BUCKET, file_name)
    print('File uploaded successfully.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='File to upload', type=str)
    args = parser.parse_args()
    main(args.filename)
