import requests
from bs4 import BeautifulSoup
import yfinance as yf

def test_market_cap():
    url = 'https://www.marketwatch.com/investing/stock/aapl?mod=search_symbol'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    mc = soup.findAll('li', class_='kv__item')[3]
    mc = mc.text[11:].strip()
    assert mc

def test_short_float():
    url = 'https://www.marketwatch.com/investing/stock/xom?mod=search_symbol'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    sf = soup.findAll('li', class_='kv__item')[14]
    sf = sf.text[19:].strip()
    assert sf

def test_sector():
    url = f'https://www.marketwatch.com/investing/stock/zm/company-profile?mod=mw_quote_tab'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    industry = soup.findAll('span', class_="primary")[6].text
    sector = soup.findAll('span', class_="primary")[7].text
    assert industry and sector

def test_current_price():
    url = 'https://www.marketwatch.com/investing/stock/jpm?mod=search_symbol'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    cp = soup.findAll('td', class_="table__cell u-semi")[0].text
    cp = float(cp[1:])
    assert cp

def test_get_stock_data():
    stock = "TSLA"
    ticker = yf.Ticker(stock)
    data = ticker.history(period='100d')
    assert len(data == 100)

