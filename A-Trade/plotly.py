import plotly as go
# import plotly.graph_objects as go
# import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close'])])

fig.show()

# import pandas as pd

# df = pd.DataFrame({
#   "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#   "Contestant": ["Alex", "Alex", "Alex", "Jordan", "Jordan", "Jordan"],
#   "Number Eaten": [2, 1, 3, 1, 3, 2],
# })


# # Plotly Express

# import plotly.express as px

# fig = px.bar(df, x="Fruit", y="Number Eaten", color="Contestant", barmode="group")
# fig.show()