"""
Made by @plutus
"""
import json
from types import SimpleNamespace

import requests


class Binom:
    """
    Main Binom class that is used to update costs and fetch list of campaigns
    """
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

    def __init__(self, tracking_domain: str, api_key: str):
        self.tracking_domain = tracking_domain
        self.v1 = BinomV1API("%s/" % tracking_domain, api_key)
        self.v2 = BinomV2API("%s/" % tracking_domain, api_key)

    def update_cost(self, camp_id: int, cost_type: int, date: str, timezone: int, cost: float):
        """
        :param camp_id: Binom campaign ID
        :param cost_type: one of Binom.COST_*
        :param date: date used for cost updating
        :param timezone: timezone used for cost updating
        :param cost: new cost to be updated
        :return: response object
        """
        return self.v1.update_cost({
            'camp_id': camp_id,
            'type': cost_type,
            'date': date,
            'timezone': timezone,
            'cost': cost
        })

    def get_campaign(self, camp_id: int):
        """
        :param camp_id: Binom campaign ID
        :return: binom campaign object
        """
        return self.v2.get_campaign(camp_id)

    def get_all_campaigns(self):
        """
        :return: list of binom campaign objects
        """
        return self.v2.get_all_campaigns()

    def get_tracking_domain(self):
        """
        :return: Binom tracking domain
        """
        return self.tracking_domain


class BinomV1API:
    """
    V1 version of the Binom API
    """
    def __init__(self, tracking_domain, api_key):
        self.domain = tracking_domain
        self.api_key = api_key

    def __get(self, payload=None):
        """
        :param payload: payload dict
        :return: response object
        """
        payload = payload if payload else {}
        payload['api_key'] = self.api_key

        response = requests.get(self.domain, payload)

        return json.loads(
            response.text,
            object_hook=lambda d: SimpleNamespace(**d)
        )

    def update_cost(self, payload):
        """
        :param payload: payload dict
        :return: response object
        """
        payload['page'] = 'save_update_costs'

        return self.__get(payload)


class BinomV2API:
    """
    V2 version of the Binom API
    """
    def __init__(self, tracking_domain, api_key):
        self.domain = tracking_domain
        self.api_key = api_key
        self.endpoint = self.domain.rstrip('/') + '/arm.php'

    def __get(self, payload=None):
        """
        :param payload: payload dict
        :return: response object
        """
        payload = payload if payload else {}
        payload['api_key'] = self.api_key

        response = requests.get(self.endpoint, payload)

        return json.loads(
            response.text,
            object_hook=lambda d: SimpleNamespace(**d)
        )

    def get_campaign(self, camp_id: int):
        """
        :param camp_id: Binom campaign ID
        :return: response object
        """
        return self.__get({'action': 'campaign@get', 'id': camp_id})

    def get_all_campaigns(self):
        """
        :return: response object
        """
        return self.__get({'action': 'campaign@get_all'})
