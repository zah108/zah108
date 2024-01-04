
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('Data/AAPL.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close'])])

fig.update_layout(
    title='AAPL',
    xaxis_title='Date',
    # shapes = [dict(
    #     x0='1970', x1='2015', y0=135, y1=135, xref='y', yref='paper',
    #     line_width=2)],
    # annotations=[dict(
    #     x='2016-12-09', y=0.05, xref='x', yref='paper',
    #     showarrow=False, xanchor='left', text='Increase Period Begins')]
)

fig.show()

