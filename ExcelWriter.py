from binance.client import Client
import pandas as pd
from datetime import datetime
import numpy as np


def updateExcel(client: Client):
    # Initialize the Excel Writer to create the Excel File
    # Orders.xlsx is the name of the Excel File.
    writer = pd.ExcelWriter("Orders.xlsx", engine='xlsxwriter')

    # Set all relevant tickers
    # key := Name for the Excel sheet
    # value:= Trading Pairs to search for and add to the Excel file
    tickers = {'Bitcoin': ['BTCEUR', 'BTCUSDT'],
               'Ethereum': ['ETHEUR', 'ETHUSDT'],
               'Cardano': ['ADAEUR', 'ADAUSDT'],
               'Polkadot': ['DOTEUR', 'DOTUSDT'],
               'Elrond': ['EGLDEUR', 'EGLDUSDT'],
               'VeChain': ['VETEUR', 'VETUSDT'],
               'Theta': ['THETAEUR', 'THETAUSDT'],
               'Chainlink': ['LINKEUR', 'LINKUSDT'],
               'Avalanche': ['AVAXEUR', 'AVAXUSDT']}

    # Iterate through every ticker and check if orders exist(ed)
    for key, value in tickers.items():
        bigDf = pd.DataFrame()
        for ticker in value:
            # Get all Orders for current ticker
            orders = client.get_all_orders(symbol=ticker)

            filteredOrders = []

            # Remove old orders, Sell orders and not filled orders
            for order in orders:
                if order['side'] == 'BUY' and order['status'] == 'FILLED' and \
                        (orderIsInAllowedTimeframe(order['time']) or orderIsInAllowedTimeframe(order['updateTime'])):
                    filteredOrders.append(order)

            # If there are no orders go to the next ticker
            if len(filteredOrders) == 0:
                continue

            # Create the dataframe with the valid orders
            df = pd.DataFrame(filteredOrders)

            # Drop the unnecessary columns
            columnsToDrop = ['orderListId', 'clientOrderId', 'timeInForce', 'type', 'side', 'stopPrice',
                             'icebergQty', 'time', 'isWorking', 'executedQty', 'origQuoteOrderQty', 'status', 'orderId']
            # Rename the columns left
            newColumnsNames = ['Symbol', 'Kaufkurs', 'Anzahl', 'Kaufwert', 'Zeitpunkt']
            df.drop(columnsToDrop, axis=1, inplace=True)
            df.columns = newColumnsNames

            # Convert the rows to the correct type
            df['Zeitpunkt'] = df['Zeitpunkt'].map(
                lambda x: datetime.fromtimestamp(x / 1000).strftime('%d-%m-%Y %H:%M:%S'))
            df['Kaufkurs'] = df['Kaufkurs'].map(lambda x: float(x))
            df['Anzahl'] = df['Anzahl'].map(lambda x: float(x))
            df['Kaufwert'] = df['Kaufwert'].map(lambda x: float(x))

            # Remove the Index Column
            df.reset_index(drop=True, inplace=True)

            # Create and add Total Column Row (also empty for visual purposes)
            emptyRow = {'Symbol': np.nan, 'Kaufkurs': np.nan, 'Anzahl': np.nan, 'Kaufwert': np.nan,
                        'Zeitpunkt': np.nan}

            totalRow = {'Symbol': 'Total',
                        'Kaufkurs': df['Kaufwert'].sum() / df['Anzahl'].sum(),
                        'Anzahl': df['Anzahl'].sum(),
                        'Kaufwert': df['Kaufwert'].sum(),
                        'Zeitpunkt': np.nan}

            df = df.append([emptyRow, totalRow, emptyRow], ignore_index=True)
            bigDf = bigDf.append(df)

        # Write the dataframe to Excel file
        bigDf.to_excel(writer, sheet_name=key, index=False)

    # Save the excel file
    writer.save()


# Returns true if order is after earliest allowed date
def orderIsInAllowedTimeframe(timestamp) -> bool:
    orderDate = datetime.fromtimestamp(timestamp / 1000)
    # YYYY MM DD HH MM
    earliestAllowedDate = datetime(2021, 8, 1, 00, 00)

    # If orderDate is before the earliest allowed then return false
    if orderDate < earliestAllowedDate:
        return False
    return True
