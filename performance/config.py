"""
Functions to config and initialise the system. Expects environment variables for most
"""

import json
import os


class Config:

    ENV = 'prod'

    VERIFY_DATA_PIPELINE_CONFIG_PATH = '../verify-data-pipeline-config'
    PIWIK_PERIOD = 'week'
    PIWIK_LIMIT = '-1'
    PIWIK_BASE_URL = 'https://analytics-hub-prod-a-dmz.ida.digital.cabinet-office.gov.uk/index.php'

    def __init__(self):
        # TODO: grab these from ENV variables
        self.PIWIK_AUTH_TOKEN = self._get_piwik_token()

    def _get_piwik_token(self):
        with open(f'{self.VERIFY_DATA_PIPELINE_CONFIG_PATH}/credentials/piwik_token.json') as fileHandle:
            token = json.load(fileHandle)['production' if self.ENV == 'prod' else 'dr_token']
            return token


class MissingEnvironmentVariableError(Exception):
    def __init__(self, env_var):
        return super().__init__(f"Missing environment variable {env_var}")


def check_get_env(key):
    """Return the value of the environment variable _key_.

    Use this instead of os.getenv when the environment variable must be present
    and if not an exception should be raised.
    """
    value = os.getenv(key)
    if value is None:
        raise MissingEnvironmentVariableError(key)
    return value
