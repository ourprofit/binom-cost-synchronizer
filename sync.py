"""
Main cost synchronization script
Made by @plutus
"""

import datetime
import logging

import pytz

from binom import Binom
from config import config
from match import match_campaigns
from provider import get_ts_providers
from traffic_source import TSProviders


class CostSynchronizer:
    """
    Core class used to handle cost synchronization
    """

    def __init__(self, binom: Binom, timezone: int, ts_providers: TSProviders, yesterday):
        self.binom = binom
        self.timezone = timezone
        self.ts_providers = ts_providers
        self.costs_by_ts = {}
        self.matched_ts_campaigns = {}
        self.yesterday = yesterday

    def sync(self):
        """
        Fetch Binom campaigns, match them with traffic sources campaigns and sync costs.
        """

        matches, matched_ts_campaigns = match_campaigns(self.binom, self.ts_providers)

        self.matched_ts_campaigns = matched_ts_campaigns

        for match in matches:
            binom_campaign = match.get_binom_campaign()
            real_cost = 0.0

            for ts_name, ts_campaigns in match.get_matched_ts_campaigns():
                self.fetch_cost(ts_name=ts_name)
                for ts_campaign in ts_campaigns.values():
                    if ts_campaign.cost:
                        real_cost += float(ts_campaign.cost)

            # skip zeros
            if not real_cost:
                continue

            self.update_cost(binom_campaign, real_cost)

    def fetch_cost(self, ts_name: str):
        """
        Fetch campaigns cost and store it in the TSProvider items

        :param ts_name: traffic source name
        """

        ts_provider = self.ts_providers.get_ts_provider(ts_name)

        if ts_name not in self.costs_by_ts.keys():
            self.costs_by_ts[ts_name] = ts_provider.get_cost(
                [
                    matched_campaign.id for ts_name, matched_campaigns in
                    self.matched_ts_campaigns.items()
                    for matched_campaign in matched_campaigns
                ],
                date_from="%s 00:00:00" % self.yesterday.date(),
                date_to="%s 23:59:59" % self.yesterday.date(),
                timezone=self.timezone
            )

    def update_cost(self, binom_campaign, real_cost: float):
        """
        Update Binom campaign cost

        :param binom_campaign: Binom campaign object
        :param real_cost: new cost that will be applied
        """
        response = self.binom.update_cost(
            camp_id=binom_campaign.id,
            cost_type=Binom.COST_TYPE_FULL,
            date=Binom.DATE_YESTERDAY,
            timezone=self.timezone,
            cost=real_cost
        )

        if hasattr(
                response,
                'update_status'
        ) and bool(response.update_status) is True:
            info_msg = 'Updated Binom Campaign(camp_id=%s, cost=%s, date=%s)' \
                       % (binom_campaign.id, real_cost, self.yesterday.date())
            logging.info(info_msg)
            print(info_msg)

        if hasattr(response, 'warning'):
            print('Warning(s): %s' % "\n".join(response.warning))


if __name__ == "__main__":
    logging.basicConfig(
        filename='update.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    )

    binom = Binom(config.get('BINOM_DOMAIN').rstrip('/'), config.get('BINOM_API_KEY'))
    timezone = int(config.get('TIMEZONE'))
    today = datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=timezone)
    # script executes after midnight, we need yesterday date
    yesterday = today + datetime.timedelta(days=-1)

    synchronizer = CostSynchronizer(
        binom,
        timezone,
        get_ts_providers(config),
        yesterday
    )
    synchronizer.sync()
