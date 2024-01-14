#+++Важно
# Основы mplfinance
# import pandas as pd

# data = pd.read_csv('Data/yahoofinance-SPY-20200901-20210113.csv')
# data.index.name = 'datetime'
# data.shape
# data.head(3)
# data.tail(3)
# print(data)

# # import matplotlib as plt
# import mplfinance as mpf
# mpf.plot(data)


import pandas as pd
import mplfinance as mpf

## infile = 'Data/yahoofinance-SPY-20200901-20210113.csv'
infile = 'Data/SBER_D1.csv'
strtitle = infile[5:12]

##df = pd.read_csv(infile, index_col=0, parse_dates=True).iloc[0:60]
df = pd.read_csv(infile, index_col = 0, parse_dates=True).tail(400) # Выводим в датафрейм последние 200 строк
# print(df)
# mpf.plot(df,figscale=1.5,type='candle',mav=(20,50))
#mpf.plot(df,type='candle',figscale=2)
#mpf.plot(df,type='renko',figscale=1.5)

chart_style = mpf.make_mpf_style(
    marketcolors = mpf.make_marketcolors(up = '#35a79b', down = '#ef3434', inherit = True),
    facecolor='#ffffff',
    edgecolor='#000000',
    figcolor='#ffffff',
    gridcolor='#eeeded',
    gridstyle='-',
    y_on_right=True
)

# addplot = mpf.make_addplot(relative_strength(rsi), panel=2)  #Передать RSI

mpf.plot(
    df,
    type = 'candle',
    volume = False,
    mav = [20,50],
    #figscale=2.0, 
    style = chart_style, 
    figsize = (25, 12),
    scale_padding = dict(left = 0.1, right = 0.3, top = 0.3, bottom = 0.5),
    axtitle = strtitle
    #addplot = addplot
) 


# Индикатор RSI
import numpy as np
def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """
    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


