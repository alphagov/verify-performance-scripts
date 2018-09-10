from performance.generate_rp_report import get_all_referrals_from_piwik, get_all_signin_attempts_for_rp_from_piwik
from performance.generate_rp_report import get_all_signup_attempts_for_rp_from_piwik, get_all_single_idp_attempts_for_rp_from_piwik
from unittest.mock import patch
from performance.piwikclient import PiwikClient


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_referrals_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 1
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name}"

    piwik_client = PiwikClient('token', 'url')
    all_referrals = get_all_referrals_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_referrals == nb_visits_for_rp


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_signin_attempts_for_rp_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 6
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name};customVariableValue3==SIGN_IN"

    piwik_client = PiwikClient('token', 'url')
    all_signin_attempts = get_all_signin_attempts_for_rp_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_signin_attempts == nb_visits_for_rp


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_signup_attempts_for_rp_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 8
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name};customVariableValue3==REGISTRATION"

    piwik_client = PiwikClient('token', 'url')
    all_signup_attempts = get_all_signup_attempts_for_rp_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_signup_attempts == nb_visits_for_rp


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_single_idp_attempts_for_rp_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 9
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name};customVariableValue3==SINGLE_IDP"

    piwik_client = PiwikClient('token', 'url')
    all_single_idp_attempts = get_all_single_idp_attempts_for_rp_from_piwik(piwik_client, rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_single_idp_attempts == nb_visits_for_rp
