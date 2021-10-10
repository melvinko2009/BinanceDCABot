"BinanceDCABot"

This idea of the project was to allow a customizable recurring buy regarding the assets, price and a current calculated risk for the Binance plattform. 

In Main.py the Binance ApiKey,  Binance Secret and the wished for orders are defineed. After placing the orders a Excel file for all wanted trading pairs is created and orders that fit certain criterias (time, sell/buy, fulfilled, etc.) are written into the coresponding Excel sheet.

ExcelWriter.py opens an existing file (Orders.xlsx) and creates one sheet per asset and creates for each defined trading pair for the asset on dataframe.

RiskCalculator.py calculates a normalized risk for the current bitcoin price and adjusts the order amount to the risk. Therefore a higher current risk results in a lower order amount.

I personally created a Batch File for the project and scheduled a task in the Windows Scheduler.

The code is by no means perfect as this was just a personal project with the intention for personal use. I tried to comment the code as well as possible so the paramters are easily understandable and adjustable for everyone.



