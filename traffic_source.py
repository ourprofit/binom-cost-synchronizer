"""
Base classes for traffic source provider(s) and campaign.
Those classes must be extended when adding new provider to the list.
Made by @plutus
"""


class TSProvider:
    """
    Base traffic source provider class.

    It is used to fetch campaigns, match them with Binom campaigns and to fetch costs.
    """

    def __init__(self, ts_name: str):
        self.ts_name = ts_name
        self.ts_campaigns = None

    def __repr__(self):
        return 'TSProvider <%s>' % self.ts_name

    def get_ts_campaigns(self):
        """
        Fetch traffic source campaigns.

        :return: list of campaigns
        """
        raise Exception('get_campaings function must be implemented')

    def match(self, binom_campaign_url: str):
        """
        Match any campaigns from this provider with the binom campaign URL

        :param binom_campaign_url: url to match
        :return: list of TSCampaign objects
        """
        raise Exception('match function must be implemented')

    def get_cost(
            self,
            ts_campaign_ids: list,
            date_from: str,
            date_to: str,
            timezone: int
    ):
        """
        :param ts_campaign_ids:
        :param date_from:
        :param date_to:
        :param timezone:
        """
        raise Exception('get_cost function must be implemented')


class TSProviders:
    """
    Storage for traffic source providers.

    This class should NOT be extended.
    """

    def __init__(self, ts_providers: dict = None):
        self.ts_providers = ts_providers if ts_providers else {}

    def add_ts_provider(self, name, ts_provider: TSProvider):
        """
        Add TSProvider to the dict

        :param name: traffic source name
        :param ts_provider: TSProvider
        :return:
        """
        self.ts_providers[name] = ts_provider

    def get_ts_providers(self):
        """
        :return: dict of TSProvider objects
        """
        return self.ts_providers

    def get_ts_provider(self, ts_name):
        """
        :param ts_name: traffic source name
        :return: TSProvider or None
        """
        if ts_name in self.ts_providers.keys():
            return self.ts_providers[ts_name]
        return None

    def get_ts_campaigns(self):
        """
        :return: list of campaigns grouped by traffic sources
        """
        for ts_name, ts_provider in self.ts_providers.items():
            yield ts_name, ts_provider.get_ts_campaigns()

    def match(self, binom_campaign_url: str):
        """
        :param binom_campaign_url: Binom campaign URL
        :return: list of matched campaigns grouped by traffic sources
        """
        for ts_name, ts_provider in self.ts_providers.items():
            ts_campaigns = ts_provider.match(binom_campaign_url)
            yield ts_name, ts_campaigns


class TSCampaign:
    """
    Wrapper for traffic source campaign to remain consistent
    across different traffic sources APIs implementations.
    """

    def __init__(self, ts_name: str, id: int, url: str, name: str = 'Placeholder', cost: float = None):
        """
        :param ts_name: traffic source name
        :param id: traffic source campaign id
        :param url: traffic source campaign url
        :param name: traffic source campaign name
        :param cost: traffic source campaign cost
        """
        self.ts_name = ts_name
        self.id = id
        self.url = url
        self.name = name
        self.cost = cost

    def set_cost(self, cost):
        """
        :param cost: cost to set
        """
        self.cost = cost
