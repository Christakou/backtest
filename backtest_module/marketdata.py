from functools import cache
import backtest_module.backtest_config as backtest_config
import requests
import json


class APIError(Exception):
    pass


class MDClient:
    def __init__(self, backend) -> None:
        pass


class MarketStackBackEnd:

    def __init__(self) -> None:
        self.session = requests.session()
        self.api_key = self._read_secrets()
        self.base_url = 'http://api.marketstack.com/v1'

    def _read_secrets(self) -> str:
        with open(backtest_config.API_KEY_PATH) as file:
            api_key = file.read()
        return api_key

    def _eod_data(self, symbol_list, start_date=None, end_date=None, limit=100, offset=0):
        params = {
            'access_key': self.api_key,
            'symbols': ','.join(symbol_list),
            'date_from': start_date,
            'date_to': end_date,
            'limit': limit,
            'offset': offset,
        }
        response = self.session.get(f'{self.base_url}/eod/latest', params=params)
        if response.ok:
            return json.loads(response.content)
        else:
            raise APIError(f'{response.status_code} ERROR: {response.content}')
