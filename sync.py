import os
import datetime
import logging

from dotenv import load_dotenv
import pytz

from binom import Binom
from match import match_campaigns
from providers.propeller_ads import TSPropellerAdsProvider
from traffic_source import TSProviders, TSProvider

load_dotenv()


class Config:
    TIMEZONE = os.getenv('CS_TIMEZONE')
    BINOM_DOMAIN = os.getenv('CS_BINOM_DOMAIN')
    BINOM_API_KEY = os.getenv('CS_BINOM_API_KEY')
    PROPELLER_ADS_API_KEY = os.getenv('CS_PROPELLER_ADS_API_KEY')


class ProviderList:
    PROPELLER_ADS = 'propeller_ads'


def get_providers():
    return {
        ProviderList.PROPELLER_ADS: {
            'class': TSPropellerAdsProvider,
            'args': ['PROPELLER_ADS_API_KEY']
        }
    }


def init():
    logging.basicConfig(
        filename='update.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    )

    timezone = int(Config.TIMEZONE)
    ts_providers = TSProviders()

    for name, object in get_providers().items():
        instance = object['class'](name, *[getattr(Config, arg) for arg in object['args']])
        ts_providers.add_ts_provider(name, instance)

    binom = Binom(Config.BINOM_DOMAIN, Config.BINOM_API_KEY)
    binom_domain = Config.BINOM_DOMAIN.rstrip('/')

    matches, matched_ts_campaigns = match_campaigns(binom, binom_domain, ts_providers)

    costs_by_ts = {}

    for match in matches:
        binom_campaign = match.get_binom_campaign()
        real_cost = 0.0

        for ts_name, ts_campaigns in match.get_matched_ts_campaigns():
            fetch_cost(
                ts_name=ts_name,
                ts_provider=ts_providers.get_ts_provider(ts_name),
                costs_by_ts=costs_by_ts,
                matched_ts_campaigns=matched_ts_campaigns,
                timezone=timezone
            )
            for ts_campaign_id, ts_campaign in ts_campaigns.items():
                if ts_campaign.cost:
                    real_cost += float(ts_campaign.cost)

        # skip zeros
        if not real_cost: continue

        update_cost(binom, binom_campaign, timezone, real_cost)


def fetch_cost(ts_name: str, costs_by_ts: dict, ts_provider: TSProvider, matched_ts_campaigns: dict, timezone: int):
    today = datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=timezone)
    # script executes after midnight, we need yesterday date
    yesterday = today + datetime.timedelta(days=-1)

    if ts_name not in costs_by_ts.keys():
        costs_by_ts[ts_name] = ts_provider.get_cost(
            [
                matched_campaign.id
                for ts_name, matched_campaigns in matched_ts_campaigns.items()
                for matched_campaign in matched_campaigns
            ],
            date_from="%s 00:00:00" % yesterday.date(),
            date_to="%s 23:59:59" % yesterday.date(),
            timezone=timezone
        )


def update_cost(binom: Binom, binom_campaign, timezone: int, real_cost: float):
    response = binom.update_cost(
        camp_id=binom_campaign.id,
        cost_type=Binom.COST_TYPE_FULL,
        date=Binom.DATE_YESTERDAY,
        timezone=timezone,
        cost=real_cost
    )

    if hasattr(response, 'update_status') and bool(response.update_status) is True:
        info_msg = 'Updated Binom campaign id %s with the new cost: %s' % (binom_campaign.id, real_cost)
        logging.info(info_msg)
        print(info_msg)

    if hasattr(response, 'warning'):
        print('Warning(s): %s' % "\n".join(response.warning))


if __name__ == "__main__":
    init()
