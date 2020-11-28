"""
Made by @plutus
"""

from binom import Binom
from traffic_source import TSProviders


class Match:
    """
    Contains matched traffic sources campaigns for given Binom campaign
    """
    def __init__(self, binom_campaign):
        self.binom_campaign = binom_campaign
        self.ts_campaigns = {}

    def add_ts_campaign(self, ts_name, ts_campaign):
        """
        :param ts_name: traffic source name
        :param ts_campaign: TSCampaign object
        :return:
        """
        if ts_name not in self.ts_campaigns.keys():
            self.ts_campaigns[ts_name] = {}

        self.ts_campaigns[ts_name][ts_campaign.id] = ts_campaign

    def has_ts_campaign(self, ts_name, ts_campaign_id):
        """
        :param ts_name: traffic source name
        :param ts_campaign_id: traffic source campaign id
        :return: boolean
        """
        if ts_name not in self.ts_campaigns.keys():
            return False

        return ts_campaign_id in self.ts_campaigns[ts_name].keys()

    def get_ts_campaigns_by_ts_name(self, ts_name):
        """
        :param ts_name: traffic source name
        :return: list of TSCampaign objects for given traffic source
        """
        if ts_name not in self.ts_campaigns.keys():
            return []

        return self.ts_campaigns[ts_name]

    def get_ts_campaigns_count(self):
        """
        :return: int representing total matched campaigns
        """
        return sum(
            [len(ts_campaigns) for ts_campaigns in self.ts_campaigns.values()])

    def get_binom_campaign(self):
        """
        :return: Binom campaign
        """
        return self.binom_campaign

    def get_matched_ts_campaigns(self):
        """
        :return: list of matched campaigns grouped by traffic sources
        """
        for ts_name in self.ts_campaigns:
            yield ts_name, self.ts_campaigns[ts_name]


def match_campaigns(binom: Binom, ts_providers: TSProviders):
    """
    :param binom: Binom object
    :param ts_providers: TSProviders object
    :return: list of Match objects, matched traffic sources campaigns
    """
    matches = []
    matched_ts_campaigns = {}
    binom_domain = binom.get_tracking_domain()

    for binom_campaign in binom.get_all_campaigns():
        if not binom_campaign.click_key:
            continue

        match = Match(binom_campaign)
        binom_campaign_url = "%s/click.php?key=%s" \
                             % (binom_domain, binom_campaign.click_key)

        for ts_name, ts_campaigns in ts_providers.match(binom_campaign_url):
            if ts_name not in matched_ts_campaigns.keys():
                matched_ts_campaigns[ts_name] = []

            for ts_campaign in ts_campaigns:
                match.add_ts_campaign(ts_name, ts_campaign)
                matched_ts_campaigns[ts_name].append(ts_campaign)

        if match.get_ts_campaigns_count() > 0:
            matches.append(match)

    return matches, matched_ts_campaigns
