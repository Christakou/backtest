from backtest_module.marketdata import MarketStackBackEnd

def test_market_stack_back_end_reads_secrets():
    test_backend = MarketStackBackEnd()
    print(test_backend.api_key)
    assert len(test_backend.api_key) != 0

