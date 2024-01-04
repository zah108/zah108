import datetime
import os.path
import sys
import backtrader as bt
import matplotlib.pyplot as plt

homepath = os.getenv('HOME')
datapath = os.path.join(homepath, 'github/backtrader/datas/orcl-1995-2014.txt')

data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    fromdate=datetime.datetime(2000,1,1),
    todate = datetime.datetime(2000,12,31),
    reverse=False)


class Strat2_BGTMA_SLSMA(bt.Strategy):
    params = (
        ('maperiod', 15),  # Tuple of tuples containing any variable settings required by the strategy.
    )

    def __init__(self):
        self.dataclose = self.datas[0].close  # Keep a reference to the "close" line in the data[0] dataseries
        self.order = None  # Property to keep track of pending orders.  There are no orders when the strategy is initialized.
        self.buyprice = None
        self.buycomm = None

        # Add SimpleMovingAverage indicator for use in the trading strategy
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # Add ExpMA, WtgMA, StocSlow, MACD, ATR, RSI indicators for plotting.
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def log(self, txt, dt=None):
        # Logging function for the strategy.  'txt' is the statement and 'dt' can be used to specify a specific datetime
        dt = dt or self.datas[0].datetime.date(0)
        print('{0},{1}'.format(dt.isoformat(), txt))

    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm: {3:8.2f}'.format(
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm{3:8.2f}'.format(
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm))

            self.bar_executed = len(self)  # when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(
            trade.pnl, trade.pnlcomm))

    def next(self):
        # Log the closing prices of the series from the reference
        self.log('Close, {0:8.2f}'.format(self.dataclose[0]))

        if self.order:  # check if order is pending, if so, then break out
            return

        # since there is no order pending, are we in the market?
        if not self.position:  # not in the market
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.buy()
        else:  # in the market
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.sell()

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(Strat2_BGTMA_SLSMA, maperiod=15)
cerebro.addsizer(bt.sizers.FixedSize,stake=10)
cerebro.broker.setcash(1000.0)
cerebro.broker.setcommission(commission=0.0)

print('Starting Portfolio Value: {0:8.2f}'.format(cerebro.broker.getvalue()))
cerebro.run()
print('Final Portfolio Value: {0:8.2f}'.format(cerebro.broker.getvalue()))