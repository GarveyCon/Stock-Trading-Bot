#Initial Stock Data Collection
#Connor Garvey - 9/7/2020
"""
This script does the initial data collection for all stocks in the S&P 500.
A year's worth of data is collected for each stock symbol. The close price is stored in the Master Data dataframe,
in which the short and long SMA's are calculated. Buy and Sell signals are generated off of a simple SMA crossover scheme.
Buy/Sell signals are saved in the Master Data dataframe and in a separate dataframe holding only the Buy/Sell signals.
Both the Master Data dataframe and the Buy/Sell Signal dataframe are saved off as .csv files
"""


import pandas as pd
import numpy as np
from pandas_datareader import data
import time


#import list of S&P 500 Stock symbols
stockSymbols = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\constituents.csv")

#Set our start and end dates - Currently set to collect the past year
start_date = '2019-09-04'
end_date = '2020-09-04'

#Do first Symbol to set up dataframe w/ date indexes
currentSym = stockSymbols['Symbol'][0]
print("Getting data for " + stockSymbols['Symbol'][0])
symbol_data = data.DataReader(currentSym, 'yahoo', start_date, end_date)
print("Complete")

#Create Master Data and Signals dataFrames with Date index
masterData = pd.DataFrame(index=symbol_data.index)
signals = pd.DataFrame(index=symbol_data.index)


#Download data from all symbols and add to master
#stockSymbols = stockSymbols.head(10)       #Use this line to do a smaller amount for testing
for i in range(0, len(stockSymbols)):
    currentSym = stockSymbols.iloc[i]['Symbol']

    #Get data from YahooFinance with Datareader
    print("Getting data for " + currentSym)
    symbol_data = data.DataReader(currentSym, 'yahoo', start_date, end_date)
    tempDF= symbol_data['Close']


    #Add close price to master, calculate SMAs and add to master
    print("Adding " + currentSym + " data to master repository")
    masterData = masterData.join(tempDF)
    masterData = masterData.rename(columns={"Close":currentSym})
    #Calculate SMAs - 20 Day and 100 Day
    masterData[currentSym + ' SMA20'] = masterData[currentSym].rolling(window=20).mean()
    masterData[currentSym + ' SMA100'] = masterData[currentSym].rolling(window=100).mean()


    #Find crossover points and mark as Buy or Sell
    signalBuySell = []
    flag = -1
    for i in range(len(masterData)):
        #Find where short SMA crosses above long SMA
        if masterData.iloc[i][currentSym + ' SMA20'] > masterData.iloc[i][currentSym + ' SMA100']:
            if flag != 1:
                signalBuySell.append('BUY')
                flag = 1
            else:
                signalBuySell.append(np.nan)
        #Find where short SMA crosses below long SMA
        elif masterData.iloc[i][currentSym + ' SMA20'] < masterData.iloc[i][currentSym + ' SMA100']:
            if flag != 0:
                signalBuySell.append('SELL')
                flag = 0
            else:
                signalBuySell.append(np.nan)
        else:
            signalBuySell.append(np.nan)
    #Add Buy/Sell signals to Master Data
    masterData[currentSym + ' Signal'] = signalBuySell
    signals[currentSym] = signalBuySell

    #Save into .csv files
    masterData.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv")
    signals.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv")
    print("Complete")
    #Wait 1 second to avoid the request limit on Yahoo Finance
    time.sleep(1)

#Save off Master Data and Signals as .csv files
masterData.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv")
signals.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv")