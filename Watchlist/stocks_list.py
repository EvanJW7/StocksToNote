import pandas as pd
import matplotlib.pyplot as plt

path = '/Users/evanwright/Downloads/america_2023-08-17.csv'

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
