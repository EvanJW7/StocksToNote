import asyncio, requests, stocks_list
import yfinance as yf
from bs4 import BeautifulSoup

def closest_number(close, high, low):
    if abs(close - high) < abs(close - low):
        return True

stocks = stocks_list.stocks

async def get_stock_data(stock, i):
    global stocks_in_play
    try:
        ticker = yf.Ticker(stock)
        p = str(i) + 'd'
        stock_data = await asyncio.to_thread(ticker.history, period=p)
        stock_data = stock_data.reset_index()
        gap = (stock_data['Open'][99] - stock_data['High'][98]) / stock_data['High'][98] * 100
        green_initial_day = stock_data['Close'][99] > stock_data['Open'][99]
        avg_vol = stock_data['Volume'][0:99].median()
        avg_price = stock_data['Open'][0:99].mean()
        equity_vol = round(avg_price * avg_vol, 2)
        if avg_vol > 0:
            vol_ratio = stock_data['Volume'][99] / avg_vol
        if green_initial_day and round(gap) >= 3 and equity_vol >= 500000 and vol_ratio > 4:
            date = stock_data['Date'][99]
            #Get Market Cap
            try:
                url = f'https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol'
                res = requests.get(url)
                if res.status_code != 200:
                    print(f"Error on market cap request: {res.status_code}")
                soup = BeautifulSoup(res.text, 'lxml')
                mc = soup.findAll('li', class_="kv__item")[3]
                mc = mc.text[11:].strip()
            except:
                mc = "No data"
            #Get short float
            try:
                url = f'https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol'
                res = requests.get(url)
                if res.status_code != 200:
                    print(f"Error on short float request: {res.status_code}")
                soup = BeautifulSoup(res.text, 'lxml')
                sf = soup.findAll('li', class_="kv__item")[14]
                sf = sf.text[19:].strip()
            except:
                sf = "No data"
            #Get volatility
            try:
                url = f'https://www.alphaquery.com/stock/{stock}/volatility-option-statistics/180-day/historical-volatility'
                res = requests.get(url)
                if res.status_code != 200:
                    print(f"Error on volaility request: {res.status_code}")
                soup = BeautifulSoup(res.content, 'lxml')
                volatility = soup.findAll('div', class_="indicator-figure-inner")[0]
                vol = float(volatility.text) * 100
                vol = round(vol, 2)
            except:
                vol = "No data"
            if round(vol) >= 60:
                print(f"{stock:>5}{date.strftime('%m/%d/%Y'):>14}{mc:>11}{format(round(equity_vol), ','):>14}{round(gap, 2):>9}%{round(vol_ratio, 2):>10}{sf:>11}{vol:>11}%")
                stocks_in_play += 1
    except:
        pass

async def main():
    tasks = []
    global stocks_in_play
    stocks_in_play = 0
    print("\n Stock      Date      MarketCap     EquityVol     Gap    VolRatio   ShortFloat   Vol180")
    for i in range(100, 111):
        print(f'{i}-------------------------------------------------------------------------------------')
        for stock in stocks:
            tasks.append(asyncio.create_task(get_stock_data(stock, i)))
        await asyncio.gather(*tasks)
        tasks.clear()

asyncio.run(main())

print(f"\nStocks in play: {stocks_in_play}\n")
