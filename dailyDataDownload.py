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
import time

# Data downloading function
def getTodaysData(symbols, masterData, buySellSignals, todays_date):
    # Download todays data for each stock and add to Master Data .csv
    failed_reads = []

    for i in range(0, len(symbols)):
        currentSym = symbols.iloc[i]['Symbol']
        print('Getting data for ' + currentSym)

        # Attempt 5 times before adding symbol to array to try later.
        attempts = 1
        while attempts < 5:
            try:
                symbol_data = data.DataReader(currentSym, 'yahoo', todays_date, todays_date)
                break
            except:
                attempts += 1
                print('Attempt number ' + str(attempts))
                time.sleep(0.5)

        if attempts == 5:
            print("No data returned. Attempting again later.")
            failed_reads.append(currentSym)
            symbol_data = []
        else:
            tempDF = symbol_data.iloc[0]['Close']

            # Get yestedays SMAs to check for crossovers
            yesterdaySMA20 = masterData[currentSym + ' SMA20'].iloc[-1]
            yesterdaySMA100 = masterData[currentSym + ' SMA100'].iloc[-1]

            # Add new value to Master Data and calculate SMAs
            masterData.at[todays_date, currentSym] = tempDF
            masterData.at[todays_date, currentSym + ' SMA20'] = masterData[currentSym].tail(20).mean()
            masterData.at[todays_date, currentSym + ' SMA100'] = masterData[currentSym].tail(100).mean()

            # Add Buy/Sell Signals
            if (masterData.at[todays_date, currentSym + ' SMA20'] < masterData.at[
                todays_date, currentSym + ' SMA100'] and
                    yesterdaySMA20 > yesterdaySMA100):
                masterData.at[todays_date, currentSym + ' Signal'] = "SELL"
                buySellSignals.at[todays_date, currentSym + ' Signal'] = "SELL"
            elif (masterData.at[todays_date, currentSym + ' SMA20'] > masterData.at[
                todays_date, currentSym + ' SMA100'] and
                  yesterdaySMA20 < yesterdaySMA100):
                masterData.at[todays_date, currentSym + ' Signal'] = "BUY"
                buySellSignals.at[todays_date, currentSym + ' Signal'] = "BUY"
            else:
                masterData.at[todays_date, currentSym + ' Signal'] = np.nan
                buySellSignals.at[todays_date, currentSym + ' Signal'] = np.nan
                print('No changes here')
            print("Complete")
            time.sleep(1)
            symbol_data = []

    failed_reads_df = pd.DataFrame(failed_reads, columns=['Symbol'])

    return masterData, buySellSignals, failed_reads_df


#######################################################################################################################

# Open .csv files containing Stock Symbols, Stock Data, and Buy/Sell Signals as dataFrames
stockSymbols = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\constituents.csv")
masterData = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv",
                         index_col="Date")
buySellSignals = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv",
                             index_col="Date")
# Get todays date
todays_date = str(date.today())

day = date.today().weekday()
# print(todays_date)

# Only runs if it is a weekday - this should be handled by the scheduler anyways
if day in range(6, 8):
    print('Not a weekday')
    exit()

# Run data download
masterData, buySellSignals, failed_symbols = getTodaysData(stockSymbols, masterData, buySellSignals, todays_date)

# Retry failed symbols once, and then save off any symbols that still fail.
if len(failed_symbols) != 0:
    print('Attempting Failed Reads:')
    print(failed_symbols)
    time.sleep(60)
    masterData, buySellSignals, failed_symbols = getTodaysData(failed_symbols, masterData, buySellSignals, todays_date)
    if len(failed_symbols) != 0:
        print('Symbols still failing will be saved off into failedReads.csv')
        failed_symbols.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\failedReads.csv")

# Save off data and signals
masterData.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv")
buySellSignals.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv")
