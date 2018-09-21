import os
from unittest.mock import patch, call

import pandas
from pandas.util.testing import assert_frame_equal

from performance.reports.rp import get_rps_with_successes, get_successes_by_rp, export_metrics_to_csv
from performance.tests.fixtures import get_sample_verifications_by_rp_dataframe


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
    verifications_by_rp_df = get_sample_verifications_by_rp_dataframe(with_rp_name=True)

    expected_successes_df = pandas.DataFrame.from_dict({
        0: ["RP 1", 0, 1],
        1: ["RP 2", 1, 0]
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
