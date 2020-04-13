import pandas as pd
import mplfinance as mpf
from dateutil import parser
import requests,time
from bs4 import BeautifulSoup
import numpy as np
import math
from datetime import date

url = 'https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol={}'
moneycontrolAPI = 'https://www.moneycontrol.com/tech_charts/nse/his/{}.csv'

#from nse data dump
def read_csv(filename,seperator=','):
    data = pd.read_csv(filename,sep=seperator,index_col=0,parse_dates=True) 
    data.index.name = 'Date'

    data['Open'] = data['Open'].str.replace(',', '')
    data['High'] = data['High'].str.replace(',', '')
    data['Low'] = data['Low'].str.replace(',', '')
    data['Close'] = data['Close'].str.replace(',', '')
    data['Volume'] = data['Volume'].str.replace(',', '')
    data.sort_values(by=['Date'], inplace=True, ascending=True)
    # data['newDate'] = data['Date'].apply(lambda x: parser.parse(x))
    # df = df.rename(columns={'newDate': 'Date'})
    # df['Date'] = pd.DatetimeIndex(df['Date'])     
    mpf.plot(data,type='candle',mav=4)


def check_marubuzo(df,variance = 1,body_cover=75):
    import numpy as np
    signal   = []
    def marubuzo(open,high,low,close):
        if ( (abs(float(open) - float(low))*100)/float(open) ) < variance and  \
           ( (abs(float(high) - float(close))*100)/float(high) < variance ) and \
              abs(open-close) != 0 and (abs(high-low)/abs(open-close)) < body_cover  :
            return True
        else:
            return False

    for index,value in df.iterrows():
        if marubuzo(value['Open'],value['High'],value['Low'],value['Close']):
            signal.append(1)
        else:
            signal.append(np.nan)
    return signal

# from moneycontrol api
def read_live_stock(shortname,stockname):
    requestUrl = moneycontrolAPI.format(shortname)
    print(requestUrl)
    data = requests.get(requestUrl,headers={'Cache-Control': 'no-cache'})
    data =  data.text.splitlines()
    df = pd.DataFrame([sub.split(",") for sub in data])
    df.columns = ["Date", "Open", "High", "Low","Close","Volume","A","B","C","D"]

    df['Date'] = df['Date'].apply(lambda x: parser.parse(x))
    df = df[["Date", "Open", "High", "Low","Close","Volume"]]
    df.set_index('Date', inplace=True)

    # df['Marubuzo'] = [ check_marubuzo(row['Open'],row['High'],row['Low'],row['Close']) for index, row in df.iterrows() ]
    df['Open'] = df['Open'].apply(lambda x: float(x))
    df['High'] = df['High'].apply(lambda x: float(x))
    df['Low'] = df['Low'].apply(lambda x: float(x))
    df['Close'] = df['Close'].apply(lambda x: float(x))
    df['Volume'] = df['Volume'].apply(lambda x: float(x))
    df = df.tail(30)  

    if date.today() not in df.iloc[[-1]].index:
        print('Ignoring '+stockname+' as last date was - '+str(df.iloc[[-1]].index))
        return
 
    marubuzo = mpf.make_addplot(check_marubuzo(df),markersize=5)
    mpf.plot(df,volume=True,addplot=marubuzo,type='candle',mav=4,title=stockname)

stocks = pd.read_csv('stocks.csv')
for index, row in stocks.iterrows():
    shortname = row['Shortname'].lower()
    stockname = row['Company']
    read_live_stock(shortname,stockname)

