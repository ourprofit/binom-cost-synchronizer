"""
Made by @plutus
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self, config):
        self.config = config

    def get(self, key):
        """
        :param key: key to get
        :return: config value for given key
        """
        return self.config[key]

    def set(self, key, value):
        """
        :param key: key to set
        :param value: new value
        :return:
        """
        self.config[key] = value


config = Config({
    "TIMEZONE": os.getenv('CS_TIMEZONE'),
    "BINOM_DOMAIN": os.getenv('CS_BINOM_DOMAIN'),
    "BINOM_API_KEY": os.getenv('CS_BINOM_API_KEY'),
    "PROPELLER_ADS_API_KEY": os.getenv('CS_PROPELLER_ADS_API_KEY')
})
