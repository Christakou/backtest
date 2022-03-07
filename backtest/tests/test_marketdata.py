from backtest.marketdata import MarketStackBackEnd, APIError, MarketData, Instrument
import pytest
import pandas as pd

@pytest.fixture
def market_data_fixture():
    market_data = MarketData()
    return market_data

@pytest.fixture
def instrument_fixture():
    market_data = MarketData()
    return market_data.instruments['AAPL']

def test_instrument_type(instrument_fixture):
    assert type(instrument_fixture) == Instrument

def test_market_stack_back_end_reads_secrets():
    test_backend = MarketStackBackEnd()
    print(test_backend.api_key)
    assert len(test_backend.api_key) != 0

def test_market_data_is_correctly_fetched(market_data_fixture):
    assert(type(market_data_fixture.data) is pd.DataFrame)

def test_instrument_truncated_prices(instrument_fixture):
    assert(instrument_fixture.prices[:'2021-05-01'].mean()['close'] == 127.88647540983608)

def test_close_at(market_data_fixture):
    assert(market_data_fixture.close_at('GOOG','2021-03-01') == 2081.51)


def test_get_instrument_prices(market_data_fixture):
    data = market_data_fixture.get_instrument_prices('GOOG')
    assert (type(data) is pd.DataFrame)
    assert (len(data) >0)
