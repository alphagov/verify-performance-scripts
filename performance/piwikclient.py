import requests


class PiwikClient:
    PIWIK_PERIOD = 'week'
    PIWIK_LIMIT = '-1'

    def __init__(self, token, piwik_base_url):
        """
        Args:
            token: Piwik access token
            piwik_base_url: URL of Piwik instance to query
        """
        self.token = token
        self.piwik_base_url = piwik_base_url

    def get_nb_visits_for_rp(self, date, segment):
        qs = {
            'module': 'API',
            'idSite': '1',
            'format': 'JSON',
            'filter_limit': self.PIWIK_LIMIT,
            'date': date,
            'period': self.PIWIK_PERIOD,
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
            'filter_limit': self.PIWIK_LIMIT,
            'date': date,
            'period': self.PIWIK_PERIOD,
            'method': 'Actions.getPageTitles',
            'token_auth': self.token,
            'segment': segment,
        }

        response = requests.get(self.piwik_base_url, qs)

        raw_result = response.json()
        nb_visits = next(iter(raw_result), {}).get('nb_visits', 0)
        return nb_visits
