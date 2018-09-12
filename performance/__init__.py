from .config import Config
from .piwikclient import PiwikClient

config = Config()

piwik_client = PiwikClient(config)
