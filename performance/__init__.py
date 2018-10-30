import os
from performance.config import Config, TestConfig

if os.getenv('ENV') == 'test':
    prod_config = TestConfig()
else:
    prod_config = Config()
