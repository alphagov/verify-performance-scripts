import pytest
import os
import pandas


BASE_PATH = os.path.dirname(__file__)


@pytest.fixture
def rp_report_weekly():
    """A fixture for the expected output of a run of the RP Report as a Pandas DataFrame."""
    return pandas.read_csv(os.path.join(BASE_PATH, 'data', 'rp_report_weekly.csv'))
