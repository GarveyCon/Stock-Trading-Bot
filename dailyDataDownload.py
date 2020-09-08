"""
Daily Data Download
Connor Garvey
9/7/2020

Download daily data for each stock in the S&P 500 and add it to the Master Data .csv file.
Calculates SMAs and generates Buy/Sell signals.
"""

import pandas as pd
import numpy as np
from pandas_datareader import data
from datetime import date

stockSymbols = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\constituents.csv")
masterData = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv", index_col= "Date")
buySellSignals = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv", index_col= "Date")


todays_date = str(date.today())
day = date.today().weekday()
#print(todays_date)

#Only runs if it is a weekday
if day in range(0,5):
    #Download todays data for each stock and add to Master Data .csv
    for i in range(0, len(stockSymbols)):
        currentSym = stockSymbols.iloc[i]['Symbol']
        print('Getting data for ' + currentSym)
        #Try to check for market holidays
        try:
            symbol_data = data.DataReader(currentSym, 'yahoo', todays_date, todays_date)
        except:
            print('No data returned from Yahoo Finance. Market holiday.')
            exit()

        tempDF = symbol_data.iloc[0]['Close']

        #Get yestedays SMAs to check for crossovers
        yesterdaySMA20 = masterData[currentSym + ' SMA20'].iloc[-1]
        yesterdaySMA100 = masterData[currentSym + ' SMA100'].iloc[-1]

        #Add new value to Master Data and calculate SMAs
        masterData.at[todays_date, currentSym] = tempDF
        masterData.at[todays_date, currentSym + ' SMA20'] = masterData[currentSym].tail(20).mean()
        masterData.at[todays_date, currentSym + ' SMA100'] = masterData[currentSym].tail(100).mean()

        #Add Buy/Sell Signals
        if (masterData.at[todays_date, currentSym + ' SMA20'] < masterData.at[todays_date, currentSym + ' SMA100'] and
                    yesterdaySMA20 > yesterdaySMA100):
            masterData.at[todays_date, currentSym + ' Signal'] = "SELL"
            buySellSignals.at[todays_date, currentSym + ' Signal'] = "SELL"
        elif (masterData.at[todays_date, currentSym + ' SMA20'] > masterData.at[todays_date, currentSym + ' SMA100'] and
                yesterdaySMA20 < yesterdaySMA100):
            masterData.at[todays_date, currentSym + ' Signal'] = "BUY"
            buySellSignals.at[todays_date, currentSym + ' Signal'] = "BUY"
        else:
            masterData.at[todays_date, currentSym + ' Signal'] = np.nan
            buySellSignals.at[todays_date, currentSym + ' Signal'] = np.nan
            print('No changes here')
        print("Complete")

    masterData.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv")
    buySellSignals.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv")
