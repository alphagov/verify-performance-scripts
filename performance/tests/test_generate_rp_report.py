import numpy
import os
from unittest.mock import patch, call

import pandas
import pytest

from pandas.util.testing import assert_frame_equal
from performance import generate_rp_report
from performance.generate_rp_report import export_metrics_to_csv, get_rps_with_successes, get_successes_by_rp
from performance.piwikclient import PiwikClient


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

    all_signin_attempts = function_under_test(rp_name, date_start)

    mock_get_nb_visits_for_rp.assert_called_with(date_start, expected_segment)
    assert all_signin_attempts == nb_visits_for_rp


@patch.object(PiwikClient, 'get_nb_visits_for_rp')
def test_get_all_referrals_from_piwik(mock_get_nb_visits_for_rp):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_rp = 1
    mock_get_nb_visits_for_rp.return_value = nb_visits_for_rp

    expected_segment = f"customVariableValue1=={rp_name}"

    all_referrals = generate_rp_report.get_all_referrals_for_rp_from_piwik(rp_name, date_start)

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
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_will_not_work = generate_rp_report.get_visits_will_not_work_from_piwik(rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_will_not_work == nb_visits_for_page


@patch.object(PiwikClient, 'get_nb_visits_for_page')
def test_get_visits_might_not_work_from_piwik(mock_get_nb_visits_for_page):
    date_start = 'date-start'
    rp_name = 'rp_name'
    nb_visits_for_page = 1
    mock_get_nb_visits_for_page.return_value = nb_visits_for_page
    expected_segment_string = \
        "customVariableValue1==rp_name;customVariableValue3==REGISTRATION;" \
        "pageTitle=@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"

    visits_might_not_work = generate_rp_report.get_visits_might_not_work_from_piwik(rp_name, date_start)

    mock_get_nb_visits_for_page.assert_called_with(date_start, expected_segment_string)
    assert visits_might_not_work == nb_visits_for_page


@patch('pandas.read_csv')
@patch('performance.generate_rp_report.config', VERIFY_DATA_PIPELINE_CONFIG_PATH='my_path')
def test_extract_verifications_by_rp_csv_for_date(mock_config, mock_pandas_read_csv):
    date_start = '2018-07-02'
    expected_verification_csv_filepath_to_load = os.path.join(
        'my_path',
        'data/verifications/verifications_by_rp_2018-07-02_2018-07-08.csv')

    generate_rp_report.extract_verifications_by_rp_csv_for_date(date_start)

    mock_pandas_read_csv.assert_called_with(expected_verification_csv_filepath_to_load)


def get_test_metrics_dataframe(**kwargs):
    return pandas.DataFrame.from_dict(
        {
            0: ["rp1", 0],
            1: ["rp2", 1],
        },
        orient="index", columns=["rp", "success"])


def get_sample_verifications_by_rp_with_rp_name_dataframe():
    return pandas.DataFrame.from_dict(
        {
            0: ["https://rp-entity-id-1.test.id", "2018-07-23T01:22:03.478Z",
                "RETURNING", "https://sample-idp-1/sso", "RP 1"],
            1: ["https://rp-entity-id-2.test.id", "2018-07-23T04:56:19.156Z",
                "NEW", "https://sample-idp-2/sso", "RP 2"]
        },
        orient="index", columns=["RP Entity Id", "Timestamp", "Response type", "IDP Entity Id", "rp"])


def test_get_rps_with_successes():
    """
    Given verifications_by_rp report for week starting on YYYY-MM-DD
    And a user successfully signs in to RP 1
    And a user successfully registers to RP 2
    Expect ["RP 1", "RP2"]
    """
    verifications_by_rp_df = get_sample_verifications_by_rp_with_rp_name_dataframe()

    expected_rp_list = ["RP 1", "RP 2"]
    actual_rp_list = get_rps_with_successes(verifications_by_rp_df)
    assert expected_rp_list == actual_rp_list


def test_get_successes_by_rp():
    """
    Given a verifications_by_rp report for week starting on YYYY-MM-DD
    And a user successfully signs in to RP 1
    And a user successfully registers to RP 2
    Expect a DataFrame
     | 'rp'   | 'signup_success' | 'signin_success' |
     | 'RP 1' | 0                | 1                |
     | 'RP 2' | 1                | 0                |
    """
    verifications_by_rp_df = get_sample_verifications_by_rp_with_rp_name_dataframe()

    # TODO: Fix code to return int64 instead of float64
    # TODO: Fix code to return 0 instead of nan when no successes
    expected_successes_df = pandas.DataFrame.from_dict({
        0: ["RP 1", numpy.nan, 1.0],
        1: ["RP 2", 1.0, numpy.nan]
    },
        orient="index", columns=["rp", "signup_success", "signin_success"])
    actual_successes_df = get_successes_by_rp(verifications_by_rp_df)
    assert_frame_equal(expected_successes_df, actual_successes_df)


@patch("os.path.exists", return_value=True)
@patch.object(pandas.DataFrame, "to_csv")
@patch.object(pandas.Series, "to_csv")
def test_export_metrics_to_csv(mock_series_to_csv, mock_dataframe_to_csv, _):
    df_export = get_test_metrics_dataframe()
    report_output_path = "output-path"
    date_start = "2001-01-01"

    export_metrics_to_csv(df_export, report_output_path, date_start)

    mock_dataframe_to_csv.assert_called_with(os.path.join(report_output_path, f'rp_report-{date_start}.csv'))
    assert mock_series_to_csv.mock_calls == [
        call(os.path.join(report_output_path, f'rp_report-{date_start}-rp1.csv')),
        call(os.path.join(report_output_path, f'rp_report-{date_start}-rp2.csv'))

    ]
