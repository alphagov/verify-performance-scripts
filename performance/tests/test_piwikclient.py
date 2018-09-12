from unittest.mock import patch, Mock
from performance.piwikclient import PiwikClient


def sample_get_page_titles_response(nb_visits_value):
    return [
        {
            "label": " GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2",
            "nb_visits": nb_visits_value,
            "nb_hits": 141,
            "sum_time_spent": 400,
            "nb_hits_with_time_generation": 200,
            "min_time_generation": "0.005",
            "max_time_generation": "3.000",
            "exit_nb_visits": 20,
            "sum_daily_nb_uniq_visitors": 100,
            "sum_daily_exit_nb_uniq_visitors": 50,
            "avg_time_on_page": 38,
            "bounce_rate": "0%",
            "exit_rate": "30%",
            "avg_time_generation": 0.102
        }
    ]


@patch('requests.get')
def test_get_nb_visits_for_rp(mock_requests_get):
    mock_requests_get.return_value.json.return_value = {"value": 5}
    date = "test-date"
    piwik_token = "test-piwik-token"
    piwik_period = 'week'
    piwik_filter_limit = '-1'
    piwik_base_url = 'url'
    segment = "test-segment"

    mock_config = Mock()
    mock_config.PIWIK_PERIOD = piwik_period
    mock_config.PIWIK_LIMIT = piwik_filter_limit
    mock_config.PIWIK_BASE_URL = piwik_base_url
    mock_config.PIWIK_AUTH_TOKEN = piwik_token

    piwik_client = PiwikClient(mock_config)

    expected_piwik_query_string = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': piwik_filter_limit,
        'date': date,
        'period': piwik_period,
        'method': 'VisitsSummary.getVisits',
        'expanded': '1',
        'token_auth': piwik_token,
        'segment': segment
    }

    visits_for_rp = piwik_client.get_nb_visits_for_rp(date, segment)

    assert visits_for_rp == 5
    mock_requests_get.assert_called_with(piwik_base_url, expected_piwik_query_string)


@patch('requests.get')
def test_get_nb_visits_for_page(mock_requests_get):
    nb_visits_value = 8
    mock_requests_get.return_value.json.return_value = sample_get_page_titles_response(nb_visits_value)

    date = "test-date"
    piwik_token = "test-piwik-token"
    piwik_period = 'week'
    piwik_filter_limit = '-1'
    piwik_base_url = 'url'
    segment = "test-segment"

    mock_config = Mock()
    mock_config.PIWIK_PERIOD = piwik_period
    mock_config.PIWIK_LIMIT = piwik_filter_limit
    mock_config.PIWIK_BASE_URL = piwik_base_url
    mock_config.PIWIK_AUTH_TOKEN = piwik_token

    piwik_client = PiwikClient(mock_config)

    expected_piwik_query_string = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': piwik_filter_limit,
        'date': date,
        'period': piwik_period,
        'method': 'Actions.getPageTitles',
        'token_auth': piwik_token,
        'segment': segment
    }

    visits_for_page = piwik_client.get_nb_visits_for_page(date, segment)

    assert visits_for_page == nb_visits_value
    mock_requests_get.assert_called_with(piwik_base_url, expected_piwik_query_string)
