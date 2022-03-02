from backtest_module.marketdata import MarketStackBackEnd, APIError
import pytest

@pytest.fixture()
def test_backend():
    test_backend = MarketStackBackEnd()
    return test_backend

def test_market_stack_back_end_reads_secrets():
    test_backend = MarketStackBackEnd()
    print(test_backend.api_key)
    assert len(test_backend.api_key) != 0


def test_eod_data_fetches_data_from_endpoint(test_backend):
    symbols = ['AAPL']
    assert len(test_backend._eod_data(symbols,'2021-02-03')) != 0

def test_eod_data_raises_invalid_symbol(test_backend):
    """ Test that the _eod function raises an error if no valid symbols are passed"""
    symbols = ['gamestonk']
    with pytest.raises(APIError):
        test_backend._eod_data(symbols, '2021-02-03')

