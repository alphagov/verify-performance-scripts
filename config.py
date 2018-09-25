"""
Functions to config and initialise the system. Expects environment variables for most
"""

import json
import os
import logging  # noqa

# logging.basicConfig(level=logging.DEBUG)  #noqa

BASE_DIR = os.path.dirname(__file__)


class Config:
    ENV = 'prod'

    VERIFY_DATA_PIPELINE_CONFIG_PATH = os.path.abspath(
        os.path.join(BASE_DIR, '..', 'verify-data-pipeline-config'))
    PIWIK_PERIOD = 'week'
    PIWIK_LIMIT = '-1'
    PIWIK_BASE_URL = 'https://analytics-hub-prod-a-dmz.ida.digital.cabinet-office.gov.uk/index.php'
    DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, 'output')

    def __init__(self):
        # TODO: grab these from ENV variables
        self.PIWIK_AUTH_TOKEN = self._get_piwik_token()
        self.GSHEETS_CREDENTIALS_FILE = os.path.join(self.VERIFY_DATA_PIPELINE_CONFIG_PATH, 'credentials',
                                                     'google_sheets_credentials.json')
        self.rp_information = {rp['rp_name']: rp for rp in self._load_json_configuration('rp_information')}
        self.rp_mapping = self._load_json_configuration('rp_mapping')
        self._validate_rp_information()

    def _get_piwik_token(self):
        with open(f'{self.VERIFY_DATA_PIPELINE_CONFIG_PATH}/credentials/piwik_token.json') as fileHandle:
            token = json.load(fileHandle)['production' if self.ENV == 'prod' else 'dr_token']
            return token

    def _load_json_configuration(self, name):
        config_file = os.path.join(self.VERIFY_DATA_PIPELINE_CONFIG_PATH, 'configuration', '{}.json'.format(name))
        with open(config_file) as f:
            return json.load(f)

    def _validate_rp_information(self):
        diff = set(self.rp_information.keys()).symmetric_difference(self.rp_mapping.values())
        if diff:
            raise LookupError('RP information and RP mappings are different:', diff)
