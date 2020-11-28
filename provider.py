"""
Made by @plutus
"""
from providers.propeller_ads import TSPropellerAdsProvider
from traffic_source import TSProviders
from config import Config

PROPELLER_ADS = 'propeller_ads'


def get_ts_providers(config: Config) -> TSProviders:
    """
    Get providers list.

    This is a place when new providers can be defined later on.
    :return:
    """

    provider_details = {
        PROPELLER_ADS: {
            'class': TSPropellerAdsProvider,
            'args': ['PROPELLER_ADS_API_KEY']
        }
    }

    ts_providers = TSProviders()

    for name, data in provider_details.items():
        instance = data['class'](
            name,
            *[config.get(key) for key in data['args']]
        )
        ts_providers.add_ts_provider(name, instance)

    return ts_providers
