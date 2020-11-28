"""
Made by @plutus
"""
import json
from types import SimpleNamespace

import requests

from traffic_source import TSProvider, TSCampaign


class TSPropellerAdsProvider(TSProvider):
    """
    PropellerAds Provider
    """

    def __init__(self, ts_name: str, api_key: str):
        super().__init__(ts_name)
        self.api = PropellerAdsAPIV5(api_key)

    def get_ts_campaigns(self, page: int = None, page_size: int = None):
        """
        Fetch PropellerAds campaigns and store them.
        :param page: page number
        :param page_size: page size
        :return:
        """
        if self.ts_campaigns:
            return self.ts_campaigns

        response = self.api.get_campaigns_list(
            is_archived=0,
            status=[
                TSPropellerAdsCampaign.STATUS_WORKING,
                TSPropellerAdsCampaign.STATUS_PAUSED,
                TSPropellerAdsCampaign.STATUS_STOPPED,
                TSPropellerAdsCampaign.STATUS_COMPLETED,
            ],
            page=page,
            page_size=page_size)

        ts_campaigns = {}

        for data in response.result:
            ts_campaigns[data.id] = TSPropellerAdsCampaign(
                ts_name=self.ts_name,
                id=data.id,
                url=data.target_url,
                name=data.name
            )

        self.ts_campaigns = ts_campaigns

        return self.ts_campaigns

    def match(self, binom_campaign_url: str):
        """
        :param binom_campaign_url: Binom campaign URL
        :return: list of matched PropellerAds campaigns
        """
        return [
            ts_campaign
            for ts_campaign_id, ts_campaign in self.get_ts_campaigns().items()
            if binom_campaign_url in ts_campaign.url
        ]

    def get_cost(
            self,
            ts_campaign_ids: list,
            date_from: str,
            date_to: str,
            timezone: int
    ):
        """
        :param ts_campaign_ids: list of campaigns ids
        :param date_from: date from
        :param date_to: date to
        :param timezone: timezone
        :return: list of costs grouped by campaign ids
        """
        timezone_sign = '+' if timezone > 0 else '-'

        ts_campaigns_stats = self.api.get_statistics({
            "group_by": "campaign_id",
            "day_from": date_from,
            "day_to": date_to,
            "tz": "{:s}{:02d}00".format(timezone_sign, abs(timezone)),
            "campaign_id": ts_campaign_ids
        })

        ts_campaigns = self.get_ts_campaigns()

        for stats in ts_campaigns_stats:
            ts_campaigns[stats.campaign_id].set_cost(stats.money)

        costs = {}

        for ts_campaign_id, ts_campaign in self.ts_campaigns.items():
            costs[ts_campaign_id] = ts_campaign.cost

        return costs


class PropellerAdsAPIV5:
    """
    V5 PropellerAds API handler
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_uri = 'https://ssp-api.propellerads.com/v5/'

    def __get(self, endpoint: str, payload: dict, headers: dict = None):
        """
        :param endpoint: request endpoint
        :param payload: payload dict
        :param headers: headers dict
        :return: response object
        """
        headers = headers if headers else {}
        response = requests.get(
            "%s%s" % (self.base_uri, endpoint),
            payload,
            headers={
                'Authorization':
                    'Bearer %s' % self.api_key,
                **headers
            }
        )

        return json.loads(
            response.text,
            object_hook=lambda d: SimpleNamespace(**d)
        )

    def __post(
            self,
            endpoint: str,
            payload: dict = None,
            json_data: dict = None,
            headers: dict = None
    ):
        """
        :param endpoint: request endpoint
        :param payload: payload dict
        :param json_data: json dict
        :param headers: headers dict
        :return: response object
        """
        headers = headers if headers else {}
        response = requests.post(
            "%s%s" % (self.base_uri, endpoint),
            payload,
            json=json_data,
            headers={
                'Authorization':
                    'Bearer %s' % self.api_key,
                **headers
            }
        )

        return json.loads(
            response.text,
            object_hook=lambda d: SimpleNamespace(**d)
        )

    def get_campaigns_list(
            self,
            id=None,
            status=None,
            direction_id=None,
            rate_model=None,
            is_archived=0,
            page=None,
            page_size=None
    ):
        """
        :param id:
        :param status:
        :param direction_id:
        :param rate_model:
        :param is_archived:
        :param page:
        :param page_size:
        :return:
        """
        payload = {'is_archived': is_archived}

        if id:
            payload['id[]'] = id
        if status:
            payload['status[]'] = status
        if direction_id:
            payload['direction_id[]'] = direction_id
        if rate_model:
            payload['rate_model[]'] = rate_model
        if page:
            payload['page'] = page
        if page_size:
            payload['page_size'] = page_size

        return self.__get('adv/campaigns', payload)

    def get_statistics(self, payload):
        """
        :param payload: payload dict
        :return: response object
        """
        return self.__post(
            'adv/statistics',
            json_data=payload,
            headers={'Content-Type': 'application/json'}
        )


class TSPropellerAdsCampaign(TSCampaign):
    """
    PropellerAds Campaign
    """
    STATUS_DRAFT = 1
    STATUS_MODERATION_PENDING = 2
    STATUS_REJECTED = 3
    STATUS_READY = 4
    STATUS_TEST_RUN = 5
    STATUS_WORKING = 6
    STATUS_PAUSED = 7
    STATUS_STOPPED = 8
    STATUS_COMPLETED = 9

    def __init__(self, ts_name, id, url, name):
        super().__init__(ts_name, id, url, name)
