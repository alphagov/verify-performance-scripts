import json
import os


class RPFederationConfig(dict):
    """
        rp_mapping translates the referrer url reported in the verifications csv
    """
    rp_mapping_config_path = 'configuration/rp_mapping.json'

    def __init__(self, config):
        with open(os.path.join(config.VERIFY_DATA_PIPELINE_CONFIG_PATH, self.rp_mapping_config_path)) as fn:
            super().__init__(json.load(fn))
