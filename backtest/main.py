from backtest.strategy import  BuyAndHoldEqualAllocation, BuyOnTheUpSellOnTheDown
import matplotlib.pyplot as plt



if __name__ == '__main__':

    a = BuyAndHoldEqualAllocation(relevant_symbols=('CSCO','IBM'))
    a.execute()
    a.evaluate('2022-03-01')
    a._plot_PGV()

    b = BuyOnTheUpSellOnTheDown(relevant_symbols=('CSCO','IBM'), date_gap=10)
    b.execute()
    b.evaluate('2022-03-01')

    x1, y1 = a._plot_PGV()
    x2, y2 = b._plot_PGV()

    plt.plot(x1,y1, label=a.name)
    plt.plot(x2,y2, label=b.name)
    plt.title(f'PGV over time')
    plt.xticks(rotation=90)
    plt.xlabel('Date')
    plt.ylabel('PGV')
    plt.legend()
    plt.savefig(f'Comparative Analysis of {a.name} and {b.name}.jpg', bbox_inches='tight')
