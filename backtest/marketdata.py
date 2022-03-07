from functools import cache
import backtest.backtest_config as backtest_config
import requests
import json
import pandas as pd

class APIError(Exception):
    pass

class MarketStackBackEnd:
    """
    A specific class to handle the particularities of the market stack API, can be swapped out for other classes with
    the similar interface if needed
    """
    def __init__(self):
        self.session = requests.session()
        self.api_key = self._read_secrets()
        self.base_url = 'http://api.marketstack.com/v1'

    def _read_secrets(self):
        """
        Reads API secret from file
        """
        with open(backtest_config.API_KEY_PATH) as file:
            api_key = file.read()
        return api_key

    def _load_from_file(self):
        """
        Loads market data stored in json file
        """
        with open('backend_data.json', 'r') as file:
            data = json.load(file)
            df = pd.DataFrame(data)
        return df

    def get_market_data(self, symbols, start_date=None, end_date=None):
        """
        Gets marketdata from API
        """
        try:
            df = self._load_from_file()
        except FileNotFoundError as e:
            self._eod_data(symbols,start_date,end_date)
            df = self._load_from_file()

        df['date'] = pd.to_datetime(df['date'])
        return df

    @cache
    def _eod_data(self, symbols, start_date=None, end_date=None, limit=1000, offset=0):
        """
        Makes the API calls and handles pagination
        """
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

            first_page_content = json.loads(response.content)
            total=first_page_content['pagination']['total']
            extra_requests = total//first_page_content['pagination']['limit']

            if extra_requests > 0:
                print('handling pagination')
                total_data=first_page_content['data']
                for i in range(extra_requests+1):
                    params['offset'] = i*limit
                    next_request = self.session.get(f'{self.base_url}/eod', params=params)
                    if next_request.ok:
                        parsed_content = json.loads(next_request.content)
                        print(parsed_content['pagination'])
                        total_data += parsed_content['data']
                with open('backend_data.json', 'w') as file:
                    json.dump(total_data, file)

            else:
                with open('backend_data.json', 'w') as file:
                    json.dump(first_page_content['data'], file)
        else:
            raise APIError(f'{response.status_code} ERROR: {response.content}')

    def _parse(self, response_content):
        """
        Parses response into pandas dataframe
        """
        df = pd.DataFrame(response_content['data'])
        return df


class MarketData:
    """Generic class to supply other functions with market data, default values were added to simplify instantiation"""
    def __init__(self, symbols=('AAPL','GOOG','IBM','AAPL','MSFT','CSCO','NOK'), start_date='2018-01-01', end_date='2022-03-05', backend=MarketStackBackEnd()):
        self.data = backend.get_market_data(symbols,start_date,end_date)
        self.start_date = start_date
        self.end_date = end_date
        self.dates = sorted(self.data['date'].unique())
        self.instruments = {}
        self.get_instruments()
        self.name = f'MarketData - {start_date} - {end_date} - {",".join(self.instruments)}'

    def __str__(self):
        return self.name

    def close_at(self,symbol,date):
        """
        Fetches close price for a symbol at a given date
        """
        return self.data[(self.data['symbol']==symbol) & (self.data['date']==date)]['close'].values[0]


    def get_instruments(self):
        """
        Populates our instruments dictionary
        """
        for symbol in self.data['symbol'].unique():
            instrument = Instrument(symbol, self)
            self.instruments.update({symbol: instrument})

    def get_instrument_prices(self, symbol):
        """
        Fetches prices from market data for a particular instrument
        """
        price_series = self.data[(self.data['symbol']==symbol)][['date','close']]
        price_series['close'] = price_series['close']
        price_series = price_series.drop_duplicates()
        price_series = price_series.set_index('date')
        return price_series


class Instrument():
    """
    Defines an instrument, this is an abstraction layer to represent stocks and their historical prices
    """
    def __init__(self, symbol, marketdata):
        self.symbol = symbol
        self.marketdata = marketdata
        self.prices = self.fetch_prices()

    def fetch_prices(self):
        """
        Uses our market data object to return a price series indexed by date which will later be used in analysis
        """
        prices = self.marketdata.get_instrument_prices(self.symbol)
        prices.name = f'Close prices for {self.symbol}'
        return prices

    def __str__(self):
        return f'Instrument({self.symbol})'

    def __repr__(self):
        return self.__str__()