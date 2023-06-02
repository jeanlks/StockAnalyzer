import requests
import yfinance as yf
import bs4 as bs
import pickle
import requests
from yahoo_fin import stock_info as si
import pandas as pd

def getSymbols():
    df1 = pd.DataFrame( si.tickers_sp500() )
    df2 = pd.DataFrame( si.tickers_nasdaq() )
    df3 = pd.DataFrame( si.tickers_dow() )
    df4 = pd.DataFrame( si.tickers_other() )

    sym1 = set( symbol for symbol in df1[0].values.tolist() )
    sym2 = set( symbol for symbol in df2[0].values.tolist() )
    sym3 = set( symbol for symbol in df3[0].values.tolist() )
    sym4 = set( symbol for symbol in df4[0].values.tolist() )

    del_set = set()
    sav_set = set()
    symbols = set.union( sym1, sym2, sym3, sym4 )
    my_list = ['W', 'R', 'P', 'Q']

    for symbol in symbols:
        if len( symbol ) > 4 and symbol[-1] in my_list:
            del_set.add( symbol )
        else:
            sav_set.add( symbol )
    return sav_set


def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker.strip())

    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers,f)

    return tickers

def filter_stocks(stocks, pe_ratio, dividend_rate, debt_ratio, roe):
    print("stock len: {}".format(len(stocks)))
    filtered_stocks = []
    i = 0
    for stock in stocks:
        i=i+1
        print("running: {}".format(i))
        try:
            if "pegRatio" in stock.info and float(stock.info["pegRatio"]) <= pe_ratio:
                if "trailingAnnualDividendYield" in stock.info and float(stock.info["trailingAnnualDividendYield"]) >= dividend_rate:
                    if "debtToEquity" in stock.info and float(stock.info["debtToEquity"]) <= debt_ratio:
                        if "returnOnEquity" in stock.info and float(stock.info["returnOnEquity"]) >= roe:
                            filtered_stocks.append(stock)
        except Exception as e:
            pass
        # else:
        #     print("Sem pegRatio {}".format(stock.info["symbol"]))
        #     print(stock.info)
    return filtered_stocks


def main():
    # List of stock symbols to filter
    #print(getSymbols())
    #symbols = ["MSFT", "AAPL", "AMZN", "GOOGL", "META", "JNJ", "PG", "V", "KO", "DIS", "JPM", "WMT", "HD", "IBM", "VZ", "MA", "UNH", "T", "PYPL", "INTC", "CMCSA", "PEP", "NFLX", "NKE", "MRK", "CSCO", "ABT", "COST", "BAC", "XOM", "PFE"]

    # Parameters for filtering

    peg_ratio_threshold = 1.0
    dividend_rate_threshold = 0.05
    debt_ratio_threshold = 10000000.0
    roe = 0.10

    stocks = []
    for symbol in getSymbols():
        try:
            stock = yf.Ticker(symbol)
            stocks.append(stock)
        except Exception as e:
            # Handle or ignore the exception as per your requirement
            pass

    filtered_stocks = filter_stocks(stocks, peg_ratio_threshold, dividend_rate_threshold, debt_ratio_threshold, roe)
    print("Filtered len: {}".format(len(filtered_stocks)))
    for stock in filtered_stocks:
        symbol = stock.info["symbol"]
        peg_ratio = stock.info["pegRatio"]
        dividend_rate = stock.info["trailingAnnualDividendYield"]
        debt_ratio = stock.info["debtToEquity"]
        roe = stock.info["returnOnEquity"]

        print(f"Symbol: {symbol}")
        print(f"PEG Ratio: {peg_ratio}")
        print(f"Dividend Rate: {dividend_rate}")
        print(f"Debt Ratio: {debt_ratio}")
        print(f"ReturnOnEquity: {roe}")
        print("-------------")

if __name__ == "__main__":
    main()
