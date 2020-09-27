# Stock-Trading-Bot
Robotrader that trades the S&amp;P 500 on an SMA crossover strategy.

The purpose of this project is to implement a Simple Moving Average (SMA) crossover strategy to trade stocks on the S&P 500. The strategy uses two running averages of the stocks closing price to calculate when to buy or a sell a certain stock. In this case, I am using 20 and 100 day averages. When the 20 day average crosses above the 100 day average, it is a signal that the stock is gaining momentum and will therefore generate a Buy signal. When the 20 day averages drops below the 100 day average, it generates a Sell signal. These signals are generated for each of the 500 stock symbols in the S&P 500. Currently, when the buy or sell signal is generated, only 1 of that stock is bought or sold. In the future, more analysis could be implemented to optimize the size of the positions. 

The signals are used to generate API calls to the Alpaca trading API, which allows for paper trading ("Trading on paper" or, pretend trading to test a strategy's validity), letting us test out the strategy without losing real money. 


The two main files for this project are the getStockData.py and dailyDataDownload.py files. The getStockData.py file is used to download the backlog of data for each stock symbol and generate the Buy/Sell signals. I downloaded the last year's worth of data, however in order to start generating the averages, it is only necessary to download the last 100 trading days. The dailyDataDownload.py file is the file that will be run each trading day to download the latest data and generate the API calls to buy or sell stocks. This file should be scheduled to run daily, and takes about 20 minutes to collect all of the data. Stock symbols that are unable to be read will be stored in a .csv file. Currently, Yahoo Finance is used for the data downloading with the Pandas-Datareader library.

Note that a config.py file is necessary to store the Alpaca API keys in. 

Future Improvements:
- Visualization of portfolio value and buy/sell signals
- Usage of a different data source to improve speed of download
- Improve reliability of data downloading/failure handling
- Increase logging/debug capabilities
- Position sizing analysis
