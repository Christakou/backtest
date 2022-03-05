from backtest.marketdata import MarketStackBackEnd, APIError, MarketData
import pytest
import pandas as pd

@pytest.fixture
def test_backend_fixture():
    test_backend = MarketStackBackEnd()
    return test_backend

@pytest.fixture
def market_data_fixture():
    market_data = MarketData(('AAPL','GOOG'))
    return market_data

@pytest.fixture
def instrument_fixture():
    market_data = MarketData(('AAPL', 'GOOG'))
    return market_data.instruments['AAPL']

def test_market_stack_back_end_reads_secrets():
    test_backend = MarketStackBackEnd()
    print(test_backend.api_key)
    assert len(test_backend.api_key) != 0


def test_eod_data_fetches_data_from_endpoint(test_backend_fixture):
    symbols = ('AAPL')
    assert len(test_backend_fixture._eod_data(symbols,'2021-02-03')) != 0

def test_eod_data_raises_invalid_symbol(test_backend_fixture):
    """ Test that the _eod function raises an error if no valid symbols are passed"""
    symbols = 'gamestonk'
    with pytest.raises(APIError):
        test_backend_fixture._eod_data(symbols, '2021-02-03')

def test_parse_data(test_backend_fixture):
    """
    Test that our parse function outputs the expected data
    """
    data = test_backend_fixture._eod_data(symbols=('AAPL','GOOG'),start_date='2022-02-01',end_date='2022-02-02')
    resultant_df = test_backend_fixture._parse(data)
    assert resultant_df.mean()['high'] == 1539.13875 # Using this .mean()['high'] trick to avoid comparing the whole DF

def test_market_data(market_data_fixture):

    assert(str(market_data_fixture) == 'MarketData-2021-01-01 - 2022-01-01 - AAPL,GOOG')
    assert(market_data_fixture.close_at('GOOG','2021-04-20') == 2293.6299)
    assert len(market_data_fixture.instruments['GOOG'].prices) > 10

def test_instrument_truncated_prices(instrument_fixture):
    print(instrument_fixture.prices[:'2021-05-01'])
