import requests

from performance import prod_config


class PiwikClient:
    def __init__(self, config):
        """
        Args:
            token: Piwik access token
            piwik_base_url: URL of Piwik instance to query
            :param config:
        """
        self.token = config.PIWIK_AUTH_TOKEN
        self.piwik_base_url = config.PIWIK_BASE_URL
        self.limit = config.PIWIK_LIMIT
        self.period = config.PIWIK_PERIOD

    def get_nb_visits_for_rp(self, date, segment):
        qs = {
            'module': 'API',
            'idSite': '1',
            'format': 'JSON',
            'filter_limit': self.limit,
            'date': date,
            'period': self.period,
            'method': 'VisitsSummary.getVisits',
            'expanded': '1',
            'token_auth': self.token,
            'segment': segment
        }

        response = requests.get(self.piwik_base_url, qs)

        raw_result = response.json()
        return raw_result.get('value', 0)

    def get_nb_visits_for_page(self, date, segment):
        qs = {
            'module': 'API',
            'idSite': '1',
            'format': 'JSON',
            'filter_limit': self.limit,
            'date': date,
            'period': self.period,
            'method': 'Actions.getPageTitles',
            'token_auth': self.token,
            'segment': segment,
        }

        response = requests.get(self.piwik_base_url, qs)

        raw_result = response.json()
        nb_visits = next(iter(raw_result), {}).get('nb_visits', 0)
        return nb_visits


_piwik_client = PiwikClient(prod_config)


def get_segment_query_string(rp_name, journey_type=None, page_title=None):
    segment = f"customVariableValue1=={rp_name}"
    if journey_type:
        segment += f";customVariableValue3=={journey_type}"
    if page_title:
        segment += f";pageTitle={page_title}"
    return segment


def get_all_visits_for_rp_and_journey_type(date_start_string, rp_name, journey_type):
    segment = get_segment_query_string(rp_name, journey_type)
    return _piwik_client.get_nb_visits_for_rp(date_start_string, segment)


def get_all_referrals_for_rp(rp, date_start_string):
    segment_by_rp = get_segment_query_string(rp)
    return _piwik_client.get_nb_visits_for_rp(date_start_string, segment_by_rp)


def get_all_signin_attempts_for_rp(rp, date_start_string):
    journey_type = 'SIGN_IN'
    return get_all_visits_for_rp_and_journey_type(date_start_string, rp, journey_type)


def get_all_signup_attempts_for_rp(rp, date_start_string):
    journey_type = 'REGISTRATION'
    return get_all_visits_for_rp_and_journey_type(date_start_string, rp, journey_type)


def get_all_single_idp_attempts_for_rp(rp, date_start_string):
    journey_type = 'SINGLE_IDP'
    return get_all_visits_for_rp_and_journey_type(date_start_string, rp, journey_type)


def get_visits_will_not_work(rp, date_start_string):
    will_not_work_page = "@GOV.UK Verify will not work for you - GOV.UK Verify - GOV.UK - LEVEL_2"
    journey_type = 'REGISTRATION'
    will_not_work_segment = get_segment_query_string(rp, journey_type, will_not_work_page)

    return _piwik_client.get_nb_visits_for_page(date_start_string, will_not_work_segment)


def get_visits_might_not_work(rp, date_start_string):
    might_not_work_page = "@Why might this not work for me - GOV.UK Verify - GOV.UK - LEVEL_2"
    journey_type = 'REGISTRATION'
    might_not_work_segment = get_segment_query_string(rp, journey_type, might_not_work_page)

    return _piwik_client.get_nb_visits_for_page(date_start_string, might_not_work_segment)
