import json
from unittest.mock import patch, mock_open

import performance.rp_federation_config

RP_MAPPING_STREAM = """
{"entityid-1": "rp-name-1", "entityid-2": "rp-name-2"}
"""


@patch('performance.rp_federation_config.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='config-path')
def test_instantiation_loads_rp_mappings(mock_config):
    sample_rp_mapping = json.loads(RP_MAPPING_STREAM)

    verify_data_pipeline_config_path = 'config-path'
    with patch('performance.rp_federation_config.open', mock_open(read_data=RP_MAPPING_STREAM),
               create=True) as mock_main_open:
        rp_federation_config = performance.rp_federation_config.RPFederationConfig(mock_config)

    mock_main_open.assert_called_with(f"{verify_data_pipeline_config_path}/configuration/rp_mapping.json")
    assert rp_federation_config == sample_rp_mapping

    assert "rp-name-2" == rp_federation_config["entityid-2"]
