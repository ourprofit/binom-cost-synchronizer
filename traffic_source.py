class TSProvider:
    def __init__(self, ts_name: str):
        self.ts_name = ts_name
        self.ts_campaigns = None

    def __repr__(self):
        return 'TSProvider <%s>' % self.ts_name

    def get_ts_campaigns(self):
        raise Exception('get_campaings function must be implemented')

    def match(self, binom_campaign_url: str):
        raise Exception('match function must be implemented')

    def get_cost(self, ts_campaign_ids: list, date_from: str, date_to: str, timezone: int):
        raise Exception('get_cost function must be implemented')


class TSProviders:
    def __init__(self, ts_providers: dict = None):
        self.ts_providers = ts_providers if ts_providers else {}

    def add_ts_provider(self, name, ts_provider):
        self.ts_providers[name] = ts_provider

    def get_ts_providers(self):
        return self.ts_providers

    def get_ts_provider(self, ts_name):
        if ts_name in self.ts_providers.keys():
            return self.ts_providers[ts_name]
        return None

    def get_ts_campaigns(self):
        for ts_name, ts_provider in self.ts_providers.items():
            yield ts_name, ts_provider.get_ts_campaigns()

    def match(self, binom_campaign_url):
        for ts_name, ts_provider in self.ts_providers.items():
            ts_campaigns = ts_provider.match(binom_campaign_url)
            yield ts_name, ts_campaigns


class TSCampaign:
    def __init__(self, ts_name, id, url, name='Placeholder', cost=None):
        self.ts_name = ts_name
        self.id = id
        self.url = url
        self.name = name
        self.cost = cost

    def set_cost(self, cost):
        self.cost = cost