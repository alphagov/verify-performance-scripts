#!/usr/bin/env python3

"""
Generate RP reports from Piwik and Successful verifications data

expects: the following files to be present in verify-data-pipeline-config:
verifications_by_rp_<for-required-week>.csv
piwik configuration in piwik.json
"""

import bootstrap  # noqa
import argparse

from performance import prod_config
from performance.reports.rp import generate_weekly_report_for_date

from performance.reports.rp import test_upload


def load_args_from_command_line():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--report_start_date', help='expected format: YYYY-MM-DD', required=True)
    parser.add_argument('--report_output_path', help='relative path to output report CSV',
                        default=('%s' % prod_config.DEFAULT_OUTPUT_PATH))
    parser.add_argument('--test-upload-to-gsheets-key',
                        help='Set a sheet key to test uploading to GSheets only: dummy data will be used.')
    return parser.parse_args()


if __name__ == '__main__':
    args = load_args_from_command_line()

    if args.test_upload_to_gsheets_key:
        test_upload(args.test_upload_to_gsheets_key, args.report_start_date)

    else:
        generate_weekly_report_for_date(args.report_start_date, args.report_output_path)
