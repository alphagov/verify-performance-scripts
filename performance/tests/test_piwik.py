from unittest.mock import patch, Mock

import pytest
from _pytest.fixtures import fixture

from performance import piwik


@pytest.mark.parametrize("function_under_test,journey_type", [
    (piwik.get_all_signin_attempts_for_rp, "SIGN_IN"),
    (piwik.get_all_signup_attempts_for_rp, "REGISTRATION"),
    (piwik.get_all_single_idp_attempts_for_rp, "SINGLE_IDP")
])
@patch.object(piwik.PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_attempts_per_journey_type(mock_get_nb_visits_for_rp, function_under_test, journey_type):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 6
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name};customVariableValue3=={journey_type}"

    all_signin_attempts = function_under_test(rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_signin_attempts == nb_visits_for_rp


@patch.object(piwik.PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_referrals_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 1
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name}"

    all_referrals = piwik.get_all_referrals_for_rp(rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_referrals == nb_visits_for_rp


def test_get_segment_query_string_for_rp_journey_type_and_page_title():
    rp_name = 'rp_name'
    journey_type = 'journey_type'
    page_title = 'page_title'
    expected_segment_string = "customVariableValue1==rp_name;customVariableValue3==journey_type;pageTitle=page_title"

    segment_string = piwik.get_segment_query_string(rp_name, journey_type, page_title)

    assert expected_segment_string == segment_string


def test_get_segment_query_string_for_rp_and_journey_type():
    rp_name = 'rp_name'
    journey_type = 'journey_type'
    expected_segment_string = "customVariableValue1==rp_name;customVariableValue3==journey_type"

    segment_string = piwik.get_segment_query_string(rp_name, journey_type)

    assert segment_string == expected_segment_string


def test_get_segment_query_string_for_rp_only():
    rp_name = 'rp_name'
    expected_segment_string = "customVariableValue1==rp_name"

    segment_string = piwik.get_segment_query_string(rp_name)

    assert segment_string == expected_segment_string


@patch.object(piwik.PiwikClient, 'get_nb_visits_for_page')
def test_get_visits_will_not_work_from_piwik(mock_get_nb_visits_for_page):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_will_not_work = piwik.get_visits_will_not_work(rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_will_not_work == nb_visits_for_page


@patch.object(piwik.PiwikClient, 'get_nb_visits_for_page')
def test_get_visits_might_not_work_from_piwik(mock_get_nb_visits_for_page):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_might_not_work = piwik.get_visits_might_not_work(rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_might_not_work == nb_visits_for_page


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


@fixture
def test_setup_variables(**update):
    res = {
        "date": "test-date",
        "segment": "test-segment",
        "piwik_auth_token": "test-piwik-token",
        "piwik_base_url": "piwik-url",
        "piwik_filter_limit": "-1",
        "piwik_period": "week"
    }
    res.update(**update)
    return res


@patch('requests.get')
def test_get_nb_visits_for_rp(mock_requests_get, test_setup_variables):
    mock_requests_get.return_value.json.return_value = {"value": 5}

    mock_config = Mock()
    mock_config.PIWIK_PERIOD = test_setup_variables['piwik_period']
    mock_config.PIWIK_LIMIT = test_setup_variables['piwik_filter_limit']
    mock_config.PIWIK_BASE_URL = test_setup_variables['piwik_base_url']
    mock_config.PIWIK_AUTH_TOKEN = test_setup_variables['piwik_auth_token']

    piwik_client = piwik.PiwikClient(mock_config)

    expected_piwik_query_string = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': test_setup_variables['piwik_filter_limit'],
        'date': test_setup_variables['date'],
        'period': test_setup_variables['piwik_period'],
        'method': 'VisitsSummary.getVisits',
        'expanded': '1',
        'token_auth': test_setup_variables['piwik_auth_token'],
        'segment': test_setup_variables['segment']
    }

    visits_for_rp = piwik_client.get_nb_visits_for_rp(test_setup_variables['date'], test_setup_variables['segment'])

    assert visits_for_rp == 5
    mock_requests_get.assert_called_with(test_setup_variables['piwik_base_url'], expected_piwik_query_string)


@patch('requests.get')
def test_get_nb_visits_for_page(mock_requests_get, test_setup_variables):
    nb_visits_value = 8
    mock_requests_get.return_value.json.return_value = sample_get_page_titles_response(nb_visits_value)

    mock_config = Mock()
    mock_config.PIWIK_PERIOD = test_setup_variables['piwik_period']
    mock_config.PIWIK_LIMIT = test_setup_variables['piwik_filter_limit']
    mock_config.PIWIK_BASE_URL = test_setup_variables['piwik_base_url']
    mock_config.PIWIK_AUTH_TOKEN = test_setup_variables['piwik_auth_token']

    piwik_client = piwik.PiwikClient(mock_config)

    expected_piwik_query_string = {
        'module': 'API',
        'idSite': '1',
        'format': 'JSON',
        'filter_limit': test_setup_variables['piwik_filter_limit'],
        'date': test_setup_variables['date'],
        'period': test_setup_variables['piwik_period'],
        'method': 'Actions.getPageTitles',
        'token_auth': test_setup_variables['piwik_auth_token'],
        'segment': test_setup_variables['segment']
    }

    visits_for_page = piwik_client.get_nb_visits_for_page(test_setup_variables['date'], test_setup_variables['segment'])

    assert visits_for_page == nb_visits_value
    mock_requests_get.assert_called_with(test_setup_variables['piwik_base_url'], expected_piwik_query_string)
