from functools import cache
import backtest_module.backtest_config as backtest_config
import requests
import json
import pandas as pd

class APIError(Exception):
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

    def get_market_data(self, symbols, start_date=None, end_date=None):
        df = self._parse(self._eod_data(symbols, start_date, end_date))
        df['date'] = pd.to_datetime(df['date'])
        return df

    @cache
    def _eod_data(self, symbols, start_date=None, end_date=None, limit=1000, offset=0):
        if type(symbols) == tuple:
            symbols = ','.join(symbols)
        else:
            symbols = symbols
        params = {
            'access_key': self.api_key,
            'symbols': symbols,
            'date_from': start_date,
            'date_to': end_date,
            'limit': limit,
            'offset': offset,
        }
        response = self.session.get(f'{self.base_url}/eod', params=params)
        if response.ok:
            return json.loads(response.content)
        else:
            raise APIError(f'{response.status_code} ERROR: {response.content}')

    def _parse(self, response_content):
        df = pd.DataFrame(response_content['data'])
        return df


class MarketData:
    def __init__(self, symbols, start_date='2021-01-01', end_date='2022-01-01', backend=MarketStackBackEnd()):
        self.data = backend.get_market_data(symbols,start_date,end_date)
        self.start_date = start_date
        self.end_date = end_date
        self.instruments = {}
        self.get_instruments()
        self.name = f'MarketData-{start_date} - {end_date} - {",".join(self.instruments)}'
    def __str__(self):
        return self.name

    def close_at(self,symbol,date):
        return self.data[(self.data['symbol']==symbol) & (self.data['date']==date)]['close'].values[0]


    def get_instruments(self):
        for symbol in self.data['symbol'].unique():
            self.instruments.update({symbol:Instrument(symbol,self)})

    def get_instrument_prices(self, symbol):
        return self.data[(self.data['symbol']==symbol)]['close']


class Instrument():
    def __init__(self, symbol, marketdata):
        self.symbol = symbol
        self.prices = marketdata.get_instrument_prices(self.symbol)

    def __str__(self):
        return f'Instrument({self.symbol})'
    def __repr__(self):
        return self.__str__()