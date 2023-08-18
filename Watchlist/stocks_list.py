import pandas as pd

path = '/Users/evanwright/Downloads/stocks.csv'

df = pd.read_csv(path)
df = df.reset_index(drop=True)
stocks = []

x = 0
while x < len(df):
    if '.' in str(df['Ticker'][x]) or '/' in str(df['Ticker'][x]):
        pass
    else:
        stocks.append((str(df['Ticker'][x])).strip())
    x += 1

