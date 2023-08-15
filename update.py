import asyncio
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import stocks_list
import logging
import warnings

logging.basicConfig(
    filename='watchlist.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s - line %(lineno)d'
)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=RuntimeWarning, message="divide by zero")

class Watchlist:
    def __init__(self):
        self.stocks = stocks_list.stocks_filtered_lots
        self.stocks_in_play = 0
        self.sizzlers = 0

    def get_market_cap(self, stock):
        try:
            url = f'https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol'
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            mc = soup.findAll('li', class_='kv__item')[3]
            mc = mc.text[11:].strip()
            return mc
        except Exception as e:
            logger.error(f"Unexpected error on get_market_cap request for {stock}: {e}")
            return "No data"

    def get_short_float(self, stock):
        try:
            url = f'https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol'
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            sf = soup.findAll('li', class_='kv__item')[14]
            sf = sf.text[19:].strip()
            return sf
        except Exception as e:
            logger.error(f"Unexpected error on get_short_float request for {stock}: {e}")
            return "No data"

    def get_volatility(self, stock):
        try:
            url = f'https://www.alphaquery.com/stock/{stock}/volatility-option-statistics/180-day/historical-volatility'
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            volatility = soup.findAll('div', class_='indicator-figure-inner')[0]
            vol = float(volatility.text) * 100
            vol = round(vol, 2)
            return vol
        except Exception as e:
            logger.error(f"Unexpected error on get_volatility request for {stock}: {e}")
            return 0

    def get_sector(self, stock):
        try:
            url = f'https://www.marketwatch.com/investing/stock/{stock}/company-profile?mod=mw_quote_tab'
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            industry = soup.findAll('span', class_="primary")[6].text
            sector = soup.findAll('span', class_="primary")[7].text
            if len(industry) <= len(sector):
                return industry
            else:
                return sector
        except Exception as e:
            logger.error(f"Unexpected error on get_sector request for {stock}: {e}")
            return "N/A"

    def closest_number(self, close, high, low):
        dist1 = abs(close - high)
        dist2 = abs(close - low)
        if dist1 < dist2:
            return True
        else:
            return False

    def get_current_price(self, stock):
        try:
            url = f'https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol'
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            cp = soup.findAll('td', class_ = "table__cell u-semi")[0].text
            cp = float(cp[1:])
            logger.info(f"Close price of {stock}: {cp}")
            return cp
        except Exception as e:
            logger.critical(f"Unable to get current price of {stock} due to {e}")
            return 999

    #Get yahoo finance stock data and screen for unusually bullish stocks along with their data
    async def get_stock_data(self, stock, i):
        try:
            ticker = yf.Ticker(stock)
            p = str(i) + 'd'
            stock_data = await asyncio.to_thread(ticker.history, period=p)
            stock_data = stock_data.reset_index()
            #Since we are grabbing 100 days of data, [99] is the most recent day and [98] is the day before, etc.
            gap = (stock_data['Open'][99] - stock_data['Close'][98]) / stock_data['Close'][98] * 100
            green_initial_day = stock_data['Close'][99] > stock_data['Open'][99]
            median_vol = stock_data['Volume'][0:99].median()
            if median_vol == 0:
                logger.warning(f"Median volume is 0 for {stock}")
            equity_vol = stock_data['Close'][0:99].mean() * median_vol
            vol_ratio = stock_data['Volume'][99] / median_vol
            if green_initial_day and round(gap) >= 3 and equity_vol >= 500000 and round(vol_ratio) > 5:
                date = stock_data['Date'][99]
                mc = self.get_market_cap(stock)
                sf = self.get_short_float(stock)
                vol = self.get_volatility(stock)
                sector = self.get_sector(stock)
                current_price = self.get_current_price(stock)
                momentum = self.closest_number(current_price, stock_data['High'][99], stock_data['Open'][98])
                if vol > 60 and momentum:
                    print(
                        f"{stock:>5}{date.strftime('%m/%d/%Y'):>14}{sector:^30}{mc:>8}{format(round(equity_vol), ','):>15}"
                        f"{round(gap, 2):>11}%{round(vol_ratio, 2):>11}{sf:>12}{vol:>12}%")
                    self.stocks_in_play += 1
                    if vol > 100:
                        self.sizzlers += 1
        except KeyError:
            logger.warning(f"KeyError on get_stock_data request for {stock}")

    async def main(self):
        tasks = []
        print("\n Stock      Date              Sector             MarketCap     EquityVol        Gap      VolRatio   "
              "ShortFloat    Vol180")
        #Grab 100 days of stock data and stop after doing that for the previous 10 days
        days = 1
        for i in range(100, 110):
            print(
                f'{days}--------------------------------------------------------------------------------------------'
                f'---------------------------')
            days += 1
            for stock in self.stocks:
                tasks.append(asyncio.create_task(self.get_stock_data(stock, i)))
            await asyncio.gather(*tasks)
            tasks.clear()
        print(f"\nStocks in play: {self.stocks_in_play}")
        print(f"Sizzlers: {self.sizzlers}\n")


if __name__ == '__main__':
    my_watchlist = Watchlist()
    asyncio.run(my_watchlist.main())





