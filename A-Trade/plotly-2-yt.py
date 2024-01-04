# https://www.youtube.com/watch?v=IfoZaCGTJ_Q&t=9s
# Maximize Trading Profits with Python Optimize Your Strategy Using EMA, Bollinger Bands & Backtesting
# pandas_ta Pandas TA - A Technical Analysis Library in Python 3 https://github.com/twopirllc/pandas-ta

import pandas as pd
import pandas_ta as ta

df = pd.read_csv("Data/EURUSD_Candlestick_5_M_ASK_30.09.2019-30.09.2022.csv")
df["Gmt time"]=df["Gmt time"].str.replace(".000","")
df['Gmt time']=pd.to_datetime(df['Gmt time'],format='%d.%m.%Y %H:%M:%S')
df=df[df.High!=df.Low]
df.set_index("Gmt time", inplace=True)

df["EMA"]=ta.ema(df.Close, length=30)
df['RSI']=ta.rsi(df.Close, length=10)
my_bbands = ta.bbands(df.Close, length=15, std=1.5)
df['ATR']=ta.atr(df.High, df.Low, df.Close, length=7)
df=df.join(my_bbands)
df

def ema_signal(df, current_candle, backcandles):
    df_slice = df.reset_index().copy()

    df_slice = df_slice.loc[current_candle-backcandles:current_candle, ["Open", "Close", "EMA"]]
    dnt = 0 if (df_slice[["Open", "Close"]].max(axis=1) >= df_slice["EMA"]).any() else 1
    upt = 0 if (df_slice[["Open", "Close"]].min(axis=1) <= df_slice["EMA"]).any() else 1

    if upt==1 and dnt==1:
        return 3
    elif upt==1:
        return 2
    elif dnt==1:
        return 1
    else:
        return 0

df=df[-10000:-1]
#ema_signal(df, 1313, 5)
from tqdm import tqdm
tqdm.pandas()
df.reset_index(inplace=True)
#df['EMASignal'] = df.progress_apply(lambda row: ema_signal(df, row.name, 5) if row.name >= 20 else 0, axis=1)

def total_signal(df, current_candle, backcandles):
    if (ema_signal(df, current_candle, backcandles) == 2
            and df.Close[current_candle] <= df['BBL_15_1.5'][current_candle]
            # and df.RSI[current_candle]<60
    ):
        return 2
    if (ema_signal(df, current_candle, backcandles) == 1
            and df.Close[current_candle] >= df['BBU_15_1.5'][current_candle]
            # and df.RSI[current_candle]>40
    ):
        return 1
    return 0


df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name, 7), axis=1)

df[df.TotalSignal != 0].head(10)

# print(df)

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
st=100
dfpl = df[st:st+350]
#dfpl.reset_index(inplace=True)
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close']),

                go.Scatter(x=dfpl.index, y=dfpl['BBL_15_1.5'],
                           line=dict(color='green', width=1),
                           name="BBL"),
                go.Scatter(x=dfpl.index, y=dfpl['BBU_15_1.5'],
                           line=dict(color='green', width=1),
                           name="BBU"),
                go.Scatter(x=dfpl.index, y=dfpl['EMA'],
                           line=dict(color='black', width=1),
                           name="EMA")           ])

fig.show()

def SIGNAL():
    return df.TotalSignal


from backtesting import Strategy
from backtesting import Backtest


class MyStrat(Strategy):
    mysize = 0.99
    slcoef = 1.2  # 1.3
    TPSLRatio = 2  # 1.8

    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        slatr = self.slcoef * self.data.ATR[-1]
        TPSLRatio = self.TPSLRatio

        if len(self.trades) > 0:
            if self.trades[-1].is_long and self.data.RSI[-1] >= 90:
                self.trades[-1].close()
            elif self.trades[-1].is_short and self.data.RSI[-1] <= 10:
                self.trades[-1].close()

        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr * TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)

        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr * TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


bt = Backtest(df, MyStrat, cash=250, margin=1 / 30, commission=0.00)
stats, heatmap = bt.optimize(slcoef=[i / 10 for i in range(10, 21)],
                             TPSLRatio=[i / 10 for i in range(10, 21)],
                             maximize='Return [%]', max_tries=300,
                             random_state=0,
                             return_heatmap=True)
stats

stats["_strategy"]

bt.run()
bt.plot()

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Convert multiindex series to dataframe
heatmap_df = heatmap.unstack()
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_df, annot=True, cmap='viridis', fmt='.0f')
plt.show()