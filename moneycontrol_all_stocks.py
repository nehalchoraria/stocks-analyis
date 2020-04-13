import pandas as pd
import mplfinance as mpf
from dateutil import parser
import requests,time
from bs4 import BeautifulSoup
import numpy as np
import math
import csv

# DOWNLOADS ALL THE STOCKS PRESENT IN NSE FROM MONEYCONTROL AND STORES IN STOCKS.CSV

main_url = 'https://www.moneycontrol.com'
base_url = main_url + '/stocks/marketinfo/marketcap/nse/index.html'

f =  open("stocks.csv", "w")
writer = csv.writer(f)
writer.writerow(['Company','Shortname','Link'])
def extract_sites(url):
    response = requests.get('https://www.moneycontrol.com'+url)
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find('table',{'class':'tbldata14 bdrtpg'})
    links = table.findAll('a',{'class':'bl_12'})
    for each in links:
        writer.writerow([each.text,each['href'].split("/")[-1], main_url + each['href']])

def build_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    li = soup.find('div', attrs = {'class':'lftmenu'}).findAll('li')
    websiteLinks = [ each.a['href'] for each in li ]
    for index,website in enumerate(websiteLinks):
        extract_sites(website)
        print(index)

build_list(base_url)