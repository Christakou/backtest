from backtest_module.marketdata import MarketData
class Strategy:
    """
    Abstract Class outlining the implementation of a strategy
    """
    def __init__(self, name, symbols, start_date=None, end_date=None, market_data=MarketData()):
        self.name = name
        self.market_data = market_data
        self.start_date = start_date if start_date else self.market_data.start_date
        self.end_date = end_date if end_date else self.market_data.end_date
        self.holdings = {}
    def execute(self):
        for instrument in self.market_data.instruments:
    """
        Iterates through daily data and outputs actions
    """
    def buy_signal(self, instrument, date):
        # implement buy_signal function that return list of
        pass

    def sell_signal(self, instrument, date):
        pass

    def evaluate(self):

class TradeAction:
    def __init__(self, quantity, instrument, date, market_data=MarketData()):
        self.symbol = symbol
        self.quantity = quantity
        self.price = self.instrument.prices['date']