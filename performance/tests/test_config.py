import json
from unittest.mock import patch, mock_open

import performance.config

RP_MAPPING_STREAM = """
{"entityid-1": "rp-name-1", "entityid-2": "rp-name-2"}
"""

RP_INFORMATION_STREAM = """
  [{
    "rp_name" : "rp-name-1",
    "department" : "department-1",
    "service_description" : "description-1",
    "loa" : "LOA_1",
    "sheet_key" : ""
  },
   {
    "rp_name" : "rp-name-2",
    "department" : "department-2",
    "service_description" : "description-2",
    "loa" : "LOA_1",
    "sheet_key" : ""
  }]
"""


@patch('performance.config.Config.VERIFY_DATA_PIPELINE_CONFIG_PATH', 'config-path')
def test_instantiation_loads_rp_config():
    sample_rp_mapping = json.loads(RP_MAPPING_STREAM)

    verify_data_pipeline_config_path = 'config-path'

    mock_open_rp_information = mock_open(read_data=RP_INFORMATION_STREAM)
    mock_open_rp_mapping = mock_open(read_data=RP_MAPPING_STREAM)

    m = mock_open()
    m.side_effect = [mock_open_rp_information.return_value, mock_open_rp_mapping.return_value]

    with patch('performance.config.open', m, create=True) as mock_main_open:
        config = performance.config.Config()

    mock_main_open.assert_any_call(
        f"{verify_data_pipeline_config_path}/configuration/rp_information.json"
    )
    mock_main_open.assert_any_call(
        f"{verify_data_pipeline_config_path}/configuration/rp_mapping.json"
    )

    assert config.rp_mapping == sample_rp_mapping

    assert "rp-name-2" == config.rp_mapping["entityid-2"]
