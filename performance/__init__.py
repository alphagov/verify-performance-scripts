from config import Config
from .rp_federation_config import RPFederationConfig
from .piwikclient import PiwikClient

config = Config()

piwik_client = PiwikClient(config)

rp_mapping = RPFederationConfig(config)
