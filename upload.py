import os
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

AWS_TARGET_PROFILE = os.getenv("AWS_TARGET_PROFILE")
RP_REPORT_OUTPUT_BUCKET = os.getenv("RP_REPORT_OUTPUT_BUCKET")

session = boto3.Session(profile_name=AWS_TARGET_PROFILE)
s3 = session.resource('s3')

bucket = s3.Bucket(RP_REPORT_OUTPUT_BUCKET)

try:
    bucket.upload_file('dummy.txt', 'output/rp/dummy.txt', {"ServerSideEncryption": 'AES256'})
except Exception as e:
    print(e)
