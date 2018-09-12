import requests


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
