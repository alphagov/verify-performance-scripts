import json
import os

from performance import config


# TODO: The `Config` class now has RP mappings - use it instead and remove this.
class RPFederationConfig(dict):
    """
        rp_mapping translates the referrer url reported in the verifications csv
    """
    rp_mapping_config_path = 'configuration/rp_mapping.json'

    def __init__(self, passed_config):
        with open(os.path.join(passed_config.VERIFY_DATA_PIPELINE_CONFIG_PATH, self.rp_mapping_config_path)) as fn:
            super().__init__(json.load(fn))


rp_mapping = RPFederationConfig(config)
