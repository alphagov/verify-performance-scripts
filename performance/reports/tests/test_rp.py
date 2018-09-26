import os
from unittest.mock import patch, call

import pandas
from pandas.util.testing import assert_frame_equal
from performance import piwik

from performance.reports.rp import get_rp_names_from_df, get_df_successes_by_rp, export_metrics_to_csv, \
    add_piwik_data_for_rp, transform_metrics, get_df_for_all_rps
from performance.tests.fixtures import get_sample_verifications_by_rp_dataframe, get_sample_successes_by_rp_dataframe


def get_test_metrics_dataframe(**kwargs):
    return pandas.DataFrame.from_dict(
        {
            0: ["rp1", 0],
            1: ["rp2", 1],
        },
        orient="index", columns=["rp", "success"])


def test_get_rps_with_successes():
    """
    Given verifications_by_rp report for week starting on YYYY-MM-DD
    And a user successfully signs in to RP 1
    And a user successfully registers to RP 2
    Expect ["RP 1", "RP2"]
    """
    verifications_by_rp_df = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    expected_rp_list = ["RP 1", "RP 2"]
    actual_rp_list = get_rp_names_from_df(verifications_by_rp_df)
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
    verifications_by_rp_df = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    expected_successes_df = pandas.DataFrame.from_dict({
        0: ["RP 1", 0, 1],
        1: ["RP 2", 1, 0]
    },
        orient="index", columns=["rp", "signup_success", "signin_success"])
    actual_successes_df = get_df_successes_by_rp(verifications_by_rp_df)
    assert_frame_equal(expected_successes_df, actual_successes_df)


@patch("os.path.exists", return_value=True)
@patch.object(pandas.DataFrame, "to_csv")
@patch.object(pandas.Series, "to_csv")
def test_export_metrics_to_csv_writes_to_folder_for_week(mock_series_to_csv, mock_dataframe_to_csv, _):
    df_export = get_test_metrics_dataframe()
    report_output_path = "output-path"
    date_start = "2001-01-01"

    export_metrics_to_csv(df_export, report_output_path, date_start)

    mock_dataframe_to_csv.assert_called_with(
        os.path.join(report_output_path, "rp_report", date_start, f'{date_start}-_All-RPs-rp_report.csv'))

    assert mock_series_to_csv.mock_calls == [
        call(os.path.join(report_output_path, "rp_report", date_start, f'{date_start}-rp1-rp_report.csv')),
        call(os.path.join(report_output_path, "rp_report", date_start, f'{date_start}-rp2-rp_report.csv'))

    ]


def test_transform_metrics_calculates_computed_metrics_accurately():
    df = pandas.DataFrame.from_dict({
        0: ['RP 1', 200, 100, 150.0, 250.0, 50.0, 20.0, 30.0],
        1: ['RP 2', 500, 200, 100.0, 200.0, 30.0, 10.0, 20.0]
    },
        orient="index",
        columns=["rp", "signup_success", "signin_success",
                 "signin_attempt", "signup_attempt", "single_idp_attempt",
                 "visits_will_not_work", "visits_might_not_work"])
    additional_metric_df = pandas.DataFrame.from_dict({
        0: [450, 300, 200 / 300, 100 / 300],
        1: [330.0, 700, 500 / 700, 200 / 700]
    },
        orient="index",
        columns=["all_referrals_with_intent", "success", "success_fraction_signup",
                 "success_fraction_signin"])
    expected_df = df.copy(deep=True).join(additional_metric_df)

    transform_metrics(df)

    assert_frame_equal(df, expected_df)


@patch.object(piwik, 'get_visits_might_not_work')
@patch.object(piwik, 'get_visits_will_not_work')
@patch.object(piwik, 'get_all_single_idp_attempts_for_rp')
@patch.object(piwik, 'get_all_signup_attempts_for_rp')
@patch.object(piwik, 'get_all_signin_attempts_for_rp')
def test_add_piwik_data_for_rp(mock_get_all_signin_attempts_for_rp, mock_get_all_signup_attempts_for_rp,
                               mock_get_all_single_idp_attempts_for_rp, mock_get_visits_will_not_work,
                               mock_get_visits_might_not_work):
    date_start = '2018-09-01'
    df_successes_rp = get_sample_successes_by_rp_dataframe()
    rp = 'RP 1'
    mock_get_all_signin_attempts_for_rp.return_value = 150
    mock_get_all_signup_attempts_for_rp.return_value = 250
    mock_get_all_single_idp_attempts_for_rp.return_value = 50
    mock_get_visits_will_not_work.return_value = 20
    mock_get_visits_might_not_work.return_value = 30
    expected_df = pandas.DataFrame.from_dict({
        0: ['RP 1', 200, 100, 150.0, 250.0, 50.0, 20.0, 30.0]
    },
        orient="index",
        columns=["rp", "signup_success", "signin_success", "signin_attempt",
                 "signup_attempt", "single_idp_attempt",
                 "visits_will_not_work", "visits_might_not_work"])

    add_piwik_data_for_rp(date_start, df_successes_rp, rp)
    actual_df = df_successes_rp.loc[df_successes_rp['rp'] == rp]

    assert_frame_equal(expected_df, actual_df)


@patch('performance.reports.rp.rp_mapping', {
    "https://missing-rp-1.local": "Missing RP 1",
    "https://missing-rp-2.local": "Missing RP 2",
    "https://rp-1.local": "RP 1",
})
def test_get_df_for_all_rps_adds_missing_rps():
    df_success_rp = get_sample_successes_by_rp_dataframe()
    missing_expected_df = pandas.DataFrame.from_dict(
        {
            0: ["Missing RP 1", 0, 0],
            1: ["Missing RP 2", 0, 0],
        },
        orient="index", columns=["rp", "signup_success", "signin_success"])
    expected_df = df_success_rp.append(missing_expected_df, ignore_index=True)

    actual_df_with_all_rps = get_df_for_all_rps(df_success_rp)

    assert_frame_equal(actual_df_with_all_rps, expected_df)
