# BinanceDCABot

The nonexistence of methods and projects that allow recurring buy on Binance prior to the start of this project, inspired the creation of this project. The code is by no means perfect as this was just a personal project with the intention for personal use. I tried to comment the code as well as possible so the parameters are easily understandable and adjustable for everyone.

## Getting Started

First You will need a Binance account. Next you will need to create a Binance API Key and Secret in order to access the Binance API. There are many Tutorials on how to create the Binance API Key and Secret I personally set the key and secret as enviroment variables. And besides money to place the orders everything you should have everything you need.

## Overview

This idea of the project was to allow a customizable recurring buy regarding the asset, price and a current calculated risk for the Binance platform. 

In Main.py the Binance API Key,  Secret, the wished for orders and other attributes are defined. After placing the orders a Excel file for all wanted trading pairs is created and orders that fit certain criterias (time, sell/buy, fulfilled, etc.) are written into the corresponding Excel sheet. Separetlely to the Binance-Python API get Requests are implemented to redeem the asset for paying from the flexible savings account. Therefore, the need manual interference or preparation should be none (besides having enough money to place the orders).
ExcelWriter.py opens an existing file (Orders.xlsx) and creates one sheet per asset and creates for each defined trading pair for the asset on dataframe.
RiskCalculator.py calculates a normalized risk for the current bitcoin price and adjusts the order amount to the risk. Therefore, a higher current risk results in a lower order amount.

## Deployment

I personally created a Batch File for the project and scheduled a task in the Windows Scheduler for every week. Running the Python File constantly in a cloud or scheduling a cron job are alternatives.

## Disclaimer

Use at your own risk. I am not liable for how you use the bot.







