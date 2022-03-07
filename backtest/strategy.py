import datetime
from backtest.marketdata import MarketData
from dataclasses import dataclass, field
import math

@dataclass
class TradeAction:
    """
    Data class to store trades
    """
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
    """
    A template class that can be used to define new strategies through inheritence
    """
    def __init__(self, relevant_symbols=(), initial_capital=1000000, start_date=None, end_date=None, market_data=MarketData(), name = None):
        self.name = name if name is not None else type(self).__name__
        self.symbols = relevant_symbols
        self.market_data = market_data
        self.start_date = start_date if start_date else self.market_data.start_date
        self.end_date = end_date if end_date else self.market_data.end_date
        self.holdings = {}
        self.cash_holdings = {}
        self.trades = []
        self.initial_capital = self.cash = initial_capital


    def execute(self):
        """
            To be implemented by child class, this should
            iterate through dates and outputs actions based on signals
        """
        pass

    def buy(self, instrument, date, quantity):
        """
           Defines a 'BUY' operation, handles cash and updates the holdings
           """
        price = instrument.prices.loc[date].close
        self.trades.append(TradeAction(instrument.symbol, date, 'BUY', quantity, price))
        if self.holdings.get(instrument.symbol):
            self.holdings[instrument.symbol] += quantity
        else:
            self.holdings.update({instrument.symbol: quantity})
        self.cash -= price*quantity
        self._update_cash_holdings(date)

    def sell(self, instrument, date, quantity):
        """
        Defines a 'SELL' operation, handles cash and updates the holdings
        """

        # should handle shorts?
        if self.holdings.get(instrument.symbol) is not None and self.holdings.get(instrument.symbol) > 0:
            price = instrument.prices.loc[date].close
            self.trades.append(TradeAction(instrument.symbol,date, 'SELL', quantity, price))
            if self.holdings.get(instrument.symbol):
                self.holdings[instrument.symbol] -= quantity
            else:
                self.holdings.update({instrument.symbol: -quantity})
            self.cash += price * quantity
            self._update_cash_holdings(date)
        else:
            pass


    def _update_cash_holdings(self, date):
        self.cash_holdings.update({date: self.cash})

    def evaluate(self,date):
        """
        Applies the strategy to our market data on a day by day basis
        """
        print(f'_____________________ EVALUATION: {self.name} as of {date} ____________________')
        print('')
        print(f'Initial investment = {self.initial_capital:.2f}')
        print(f'Portfolio Gross value at {date}: {self.portfolio_gross_value_at(date):.2f}')
        print(f'Total Net Profit: {self.portfolio_gross_value_at(date) - self.initial_capital + self.cash :.2f}')

        print(f'Fractional contributions: {self.fractional_portfolio_gross_value_at(date)}')

    def fractional_portfolio_gross_value_at(self, date):
        """
        Returns a dictionary representing the portfolio gross value contributions of each instrument held
        """
        holdings_to_date = self._holdings_at(date)
        pgv = {}
        for symbol, quantity in holdings_to_date.items():
            pgv.update({symbol:self.market_data.close_at(symbol,date)*quantity})
        return pgv
    def portfolio_gross_value_at(self, date):
        """
        Returns the total portfolio gross value at a given date
        """
        pgv_dict = self.fractional_portfolio_gross_value_at(date)
        cash_holdings_at = self._cash_holdings_at(date)
        return sum(pgv_dict.values())+cash_holdings_at
    def _plot_PGV(self):
        """
        Returns data for plotting
        """
        pgv_over_time = []
        dates = self.market_data.dates
        for date in dates:
            pgv_over_time.append(self.portfolio_gross_value_at(date))
        x = dates
        y = pgv_over_time
        return x, y

    def _holdings_at(self, date):
        '''
        Reads trade records to return the positions held at a given date
        '''
        holdings_at = {}
        if type(date) == str:
            date = datetime.date.fromisoformat(date)
        relevant_trades = [trade_record for trade_record in self.trades if trade_record.date <= date]
        for trade in relevant_trades:
            if holdings_at.get(trade.symbol) is None:
                holdings_at.update({trade.symbol:trade.quantity})
            else:
                holdings_at[trade.symbol] += trade.quantity
        return holdings_at
    def _cash_holdings_at(self,date):
        """
        Reads the strategies cash_holdings variable and outputs the amount of cash at a given time
        """
        if type(date) == str:
            date = datetime.date.fromisoformat(date)
        cash_holdings_dates_to_date = [cash_record for cash_record in self.cash_holdings if cash_record <= date]
        if cash_holdings_dates_to_date:
            return self.cash_holdings.get(cash_holdings_dates_to_date[-1])
        else:
            return 0


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

class BuyOnTheUpSellOnTheDown(Strategy):
    """
    Dummy strategy that buys stocks that have gone up in the last 30 days and sells stocks that have gone down
    """
    def __init__(self,date_gap, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_gap = date_gap
    def execute(self):
            relevant_instruments = [instrument for symbol, instrument in self.market_data.instruments.items() if
                                    symbol in self.symbols]
            for date in self.market_data.dates:
                for instrument in relevant_instruments:
                    visible_instrument_prices = instrument.prices[date:]

                    if len(visible_instrument_prices) <self.date_gap:
                        continue
                    is_slope_positive = visible_instrument_prices.iloc[0] - visible_instrument_prices.iloc[-self.date_gap] > 0

                    if is_slope_positive['close']:
                        if self.cash > 10000:
                            quantity_to_buy = math.floor((self.cash//100) / instrument.prices.loc[date].close)
                            if quantity_to_buy <= 0:
                                break
                            self.buy(instrument, date, quantity_to_buy)
                    else:
                        quantity_to_sell = self.holdings.get(instrument.symbol)
                        self.sell(instrument, date, quantity_to_sell)

                else:
                    continue
                break

