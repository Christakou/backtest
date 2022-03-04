from backtest_module.marketdata import MarketStackBackEnd, APIError, MarketData
import pytest
import pandas as pd

@pytest.fixture()
def test_backend():
    test_backend = MarketStackBackEnd()
    return test_backend

def test_market_stack_back_end_reads_secrets():
    test_backend = MarketStackBackEnd()
    print(test_backend.api_key)
    assert len(test_backend.api_key) != 0


def test_eod_data_fetches_data_from_endpoint(test_backend):
    symbols = ('AAPL')
    assert len(test_backend._eod_data(symbols,'2021-02-03')) != 0

def test_eod_data_raises_invalid_symbol(test_backend):
    """ Test that the _eod function raises an error if no valid symbols are passed"""
    symbols = 'gamestonk'
    with pytest.raises(APIError):
        test_backend._eod_data(symbols, '2021-02-03')

def test_parse_data(test_backend):
    """
    Test that our parse function outputs the expected data
    """
    data = test_backend._eod_data(symbols=('AAPL','GOOG'),start_date='2022-02-01',end_date='2022-02-02')
    resultant_df = test_backend._parse(data)
    assert resultant_df.mean()['high'] == 1539.13875 # Using this .mean()['high'] trick to avoid comparing the whole DF

def test_market_data():

    market_data = MarketData(('AAPL','GOOG'))
    assert(str(market_data) == 'MarketData-2021-01-01 - 2022-01-01 - AAPL,GOOG')
    assert(market_data.close_at('GOOG','2021-04-20') == 2293.6299)
    assert len(market_data.instruments['GOOG'].prices) > 10