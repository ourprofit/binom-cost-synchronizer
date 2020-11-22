from binom import Binom
from traffic_source import TSProviders


class Match:
    def __init__(self, binom_campaign):
        self.binom_campaign = binom_campaign
        self.ts_campaigns = {}

    def add_ts_campaign(self, ts_name, ts_campaign):
        if ts_name not in self.ts_campaigns.keys():
            self.ts_campaigns[ts_name] = {}

        self.ts_campaigns[ts_name][ts_campaign.id] = ts_campaign

    def has_ts_campaign(self, ts_name, ts_campaign_id):
        if ts_name not in self.ts_campaigns.keys():
            return False

        return ts_campaign_id in self.ts_campaigns[ts_name].keys()

    def get_ts_campaigns_by_ts_name(self, ts_name):
        if ts_name not in self.ts_campaigns.keys():
            return []

        return self.ts_campaigns[ts_name]

    def get_ts_campaigns_count(self):
        return sum([len(ts_campaigns) for ts_campaigns in self.ts_campaigns.values()])

    def get_binom_campaign(self):
        return self.binom_campaign

    def get_matched_ts_campaigns(self):
        for ts_name in self.ts_campaigns:
            yield (ts_name, self.ts_campaigns[ts_name])


def match_campaigns(binom: Binom, binom_domain: str, ts_providers: TSProviders):
    matches = []
    matched_ts_campaigns = {}

    for binom_campaign in binom.get_all_campaigns():
        if not binom_campaign.click_key: continue

        match = Match(binom_campaign)
        binom_campaign_url = "%s/click.php?key=%s" % (binom_domain, binom_campaign.click_key)

        for ts_name, ts_campaigns in ts_providers.match(binom_campaign_url):
            if ts_name not in matched_ts_campaigns.keys():
                matched_ts_campaigns[ts_name] = []

            for ts_campaign in ts_campaigns:
                match.add_ts_campaign(ts_name, ts_campaign)
                matched_ts_campaigns[ts_name].append(ts_campaign)

        if match.get_ts_campaigns_count() > 0:
            matches.append(match)

    return matches, matched_ts_campaigns
