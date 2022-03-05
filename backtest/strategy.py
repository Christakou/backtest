import datetime

from backtest.marketdata import MarketData, Instrument
from dataclasses import dataclass, field
import pandas as pd
import math
@dataclass
class TradeAction:
    symbol: str
    date: str
    type: str
    quantity: int
    price: float
    value: float = field(init=False)
    def __post_init__(self):
        self.value = self.price * self.quantity

    def __str__(self):
        return f'|{self.type} {self.quantity} of {self.symbol} at {self.price} on {self.date:%Y-%m-%d} for {self.value}|'

    def __repr__(self):
        return self.__str__()

class Strategy:
    def __init__(self, relevant_symbols=(), initial_capital=1000000, start_date=None, end_date=None, market_data=MarketData()):
        self.symbols = relevant_symbols
        self.market_data = market_data
        self.start_date = start_date if start_date else self.market_data.start_date
        self.end_date = end_date if end_date else self.market_data.end_date
        self.holdings = {}
        self.trades = []
        self.initial_capital = self.cash = initial_capital


    def execute(self):
        """
            To be implemented by child class, this should
            iterate through dates and outputs actions based on signals
        """
        pass

    def buy(self, instrument, date, quantity):
        price = instrument.prices.loc[date].close
        self.trades.append(TradeAction(instrument.symbol, date, 'BUY', quantity, price))
        if self.holdings.get(instrument.symbol):
            self.holdings[instrument.symbol] += quantity
        else:
            self.holdings.update({instrument.symbol: quantity})
        self.cash -= price*quantity

    def sell(self, instrument, date, quantity):
        # should handle shorts?
        price = instrument.prices[date]
        self.trades.append(TradeAction(instrument.symbol, 'SELL', date, quantity, price))
        if self.holdings.get(instrument.symbol):
            self.holdings[instrument.symbol] -= quantity
        else:
            self.holdings.update({instrument.symbol: -quantity})
        self.cash += price * quantity

    def evaluate(self,date):
        print(f'Initial investment = {self.initial_capital}')
        print(f'Portfolio Gross value at {date}: {self.portfolio_gross_value_at(date)}')
        print(f'Total Net Profit: {self.portfolio_gross_value_at(date) - self.initial_capital-self.cash}')

        print(f'Fractional contributions: {self.fractional_portfolio_gross_value_at(date)}')

    def fractional_portfolio_gross_value_at(self, date):
        holdings_to_date = self._holdings_at(date)
        pgv = {}
        for symbol, quantity in holdings_to_date.items():
            pgv.update({symbol:self.market_data.close_at(symbol,date)*quantity})
        return pgv
    def portfolio_gross_value_at(self, date):
        pgv_dict = self.fractional_portfolio_gross_value_at(date)
        return sum(pgv_dict.values())

    def _holdings_at(self, date):
        '''Reads trade records to return the positions held at a given date'''
        holdings_at = {}
        relevant_trades = [trade_record for trade_record in self.trades if trade_record.date <= datetime.date.fromisoformat(date)]
        for trade in relevant_trades:
            if holdings_at.get(trade.symbol) is None:
                holdings_at.update({trade.symbol:trade.quantity})
            else:
                holdings_at[trade.symbol] += trade.quantity
        return holdings_at




class BuyAndHoldEqualAllocation(Strategy):
    """
    Dummy strategy that splits exposure equaly across all symbols and buys
    """
    def execute(self):
            relevant_instruments = [instrument for symbol, instrument in self.market_data.instruments.items() if
                                    symbol in self.symbols]
            for date in self.market_data.dates:
                cash_to_allocate = round(self.cash / len(relevant_instruments))
                for instrument in relevant_instruments:

                    quantity_to_buy = math.floor(cash_to_allocate / instrument.prices.loc[date].close)
                    if quantity_to_buy <= 0:
                        break
                    self.buy(instrument, date, quantity_to_buy)
                else:
                    continue
                break
if __name__ == '__main__':
    test = 'a'
    symbols = ('AAPL', 'GOOG')
    a = BuyAndHoldEqualAllocation(relevant_symbols=symbols)
    a.execute()
    a.evaluate('2021-12-31')
