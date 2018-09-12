import performance.generate_rp_report as generate_rp_report
from unittest.mock import patch
from performance.piwikclient import PiwikClient
import pytest
import pandas


@pytest.mark.parametrize("function_under_test,journey_type", [
    (generate_rp_report.get_all_signin_attempts_for_rp_from_piwik, "SIGN_IN"),
    (generate_rp_report.get_all_signup_attempts_for_rp_from_piwik, "REGISTRATION"),
    (generate_rp_report.get_all_single_idp_attempts_for_rp_from_piwik, "SINGLE_IDP")
])
@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_attempts_per_journey_type(mock_get_nb_visits_for_rp, function_under_test, journey_type):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 6
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name};customVariableValue3=={journey_type}"

    piwik_client = PiwikClient('token', 'url')
    all_signin_attempts = function_under_test(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_signin_attempts == nb_visits_for_rp


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_referrals_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 1
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name}"

    piwik_client = PiwikClient('token', 'url')
    all_referrals = generate_rp_report.get_all_referrals_for_rp_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_referrals == nb_visits_for_rp


def test_get_segment_query_string_for_rp_journey_type_and_page_title():
    rp_name = 'rp_name'
    journey_type = 'journey_type'
    page_title = 'page_title'
    expected_segment_string = "customVariableValue1==rp_name;customVariableValue3==journey_type;pageTitle=page_title"

    segment_string = generate_rp_report.get_segment_query_string(rp_name, journey_type, page_title)

    assert expected_segment_string == segment_string


def test_get_segment_query_string_for_rp_and_journey_type():
    rp_name = 'rp_name'
    journey_type = 'journey_type'
    expected_segment_string = "customVariableValue1==rp_name;customVariableValue3==journey_type"

    segment_string = generate_rp_report.get_segment_query_string(rp_name, journey_type)

    assert segment_string == expected_segment_string


def test_get_segment_query_string_for_rp_only():
    rp_name = 'rp_name'
    expected_segment_string = "customVariableValue1==rp_name"

    segment_string = generate_rp_report.get_segment_query_string(rp_name)

    assert segment_string == expected_segment_string


@patch.object(PiwikClient, 'get_nb_visits_for_page')
def test_get_visits_will_not_work_from_piwik(mock_get_nb_visits_for_page):
    date_start = 'date-start'
    rp_name = 'rp_name'
    piwik_client = PiwikClient('token', 'url')
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_will_not_work = generate_rp_report.get_visits_will_not_work_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_will_not_work == nb_visits_for_page


@patch.object(PiwikClient, 'get_nb_visits_for_page')
def test_get_visits_might_not_work_from_piwik(mock_get_nb_visits_for_page):
    date_start = 'date-start'
    rp_name = 'rp_name'
    piwik_client = PiwikClient('token', 'url')
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_might_not_work = generate_rp_report.get_visits_might_not_work_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_might_not_work == nb_visits_for_page


@patch.object(pandas, 'read_csv')
def test_load_verifications_by_rp_csv_for_date(mock_pandas_read_csv):
    date_start = '2018-07-02'
    expected_verification_csv_filepath_to_load = \
        '../../verify-data-pipeline-config/data/verifications/verifications_by_rp_2018-07-02_2018-07-08.csv'

    generate_rp_report.load_verifications_by_rp_csv_for_date(date_start)

    mock_pandas_read_csv.assert_called_with(expected_verification_csv_filepath_to_load)
