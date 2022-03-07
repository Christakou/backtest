import pytest
from backtest.strategy import  BuyAndHoldEqualAllocation

@pytest.fixture
def strategy():
    symbols = ('AAPL', 'GOOG')
    strategy = BuyAndHoldEqualAllocation(relevant_symbols=symbols)
    return strategy

def test_strategy_execute(strategy):
    strategy.execute()
    assert len(strategy.holdings) > 0
    assert len(strategy.trades) > 0


def test_holdings_at(strategy):
    strategy.execute()
    assert (strategy._holdings_at('2018-05-05') =={})
    assert (strategy._holdings_at('2021-05-06') == {'AAPL': 7466})
    assert (strategy._holdings_at('2021-05-07') == {'AAPL': 3862, 'GOOG': 209})
    assert (strategy._holdings_at('2021-05-08') == {'AAPL': 3862, 'GOOG': 209})