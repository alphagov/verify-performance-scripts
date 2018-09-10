from unittest.mock import patch
from performance.piwikclient import PiwikClient


@patch('requests.get')
def test_get_nb_visits_for_rp(mock_requests_get):
    mock_requests_get.return_value.json.return_value = {"value": 5}
    date = "test-date"
    token = "test-piwik-token"
    segment = "test-segment"
    piwik_base_url = "piwik-url"
    piwik_client = PiwikClient(token, piwik_base_url)

    expected_piwik_query_string = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': '-1',
        'date': date,
        'period': 'week',
        'method': 'VisitsSummary.getVisits',
        'expanded': '1',
        'token_auth': token,
        'segment': segment
    }

    visits_for_rp = piwik_client.get_nb_visits_for_rp(date, segment)

    assert visits_for_rp == 5
    mock_requests_get.assert_called_with(piwik_base_url, expected_piwik_query_string)
