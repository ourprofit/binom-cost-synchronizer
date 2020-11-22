import json
from types import SimpleNamespace

import requests


class Binom:
    COST_TYPE_FULL = 1
    COST_TYPE_CPC = 2
    DATE_TODAY = 1
    DATE_YESTERDAY = 2
    DATE_LAST_7_DAYS = 3
    DATE_LAST_14_DAYS = 4
    DATE_CURRENT_MONTH = 5
    DATE_LAST_MONTH = 6
    DATE_CURRENT_YEAR = 7
    DATE_LAST_YEAR = 8
    DATE_FOR_ALL_TIME = 9
    DATE_CURRENT_WEEK = 11
    DATE_CUSTOM_DATE = 12

    def __init__(self, tracking_domain, api_key):
        self.v1 = BinomV1API(tracking_domain, api_key)
        self.v2 = BinomV2API(tracking_domain, api_key)

    def update_cost(self, camp_id, cost_type, date, timezone, cost):
        return self.v1.update_cost({
            'camp_id': camp_id,
            'type': cost_type,
            'date': date,
            'timezone': timezone,
            'cost': cost
        })

    def get_campaign(self, camp_id):
        return self.v2.get_campaign(camp_id)

    def get_all_campaigns(self):
        return self.v2.get_all_campaigns()


class BinomV1API:
    def __init__(self, tracking_domain, api_key):
        self.domain = tracking_domain
        self.api_key = api_key

    def __get(self, payload=None):
        payload = payload if payload else {}
        payload['api_key'] = self.api_key

        response = requests.get(self.domain, payload)

        return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

    def update_cost(self, payload):
        payload['page'] = 'save_update_costs'

        return self.__get(payload)


class BinomV2API:
    def __init__(self, tracking_domain, api_key):
        self.domain = tracking_domain
        self.api_key = api_key
        self.endpoint = self.domain.rstrip('/') + '/arm.php'

    def __get(self, payload=None):
        payload = payload if payload else {}
        payload['api_key'] = self.api_key

        response = requests.get(self.endpoint, payload)

        return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

    def get_campaign(self, camp_id):
        return self.__get({
            'action': 'campaign@get',
            'id': camp_id
        })

    def get_all_campaigns(self):
        return self.__get({
            'action': 'campaign@get_all'
        })
