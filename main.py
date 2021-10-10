from binance.client import Client as BinanceClient
from decimal import *
from datetime import datetime
import os
import ExcelWriter
import RiskCalculator
import requests
import hmac
import hashlib
import time


# Creates a Limit Order for the symbol trading pair with quantity as the amount and the given price
def createBuyOrder(symbol: str, quantity: float, price: float):
    try:
        buy_limit = binanceClient.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
        addToMessageBody(buy_limit['orderId'], symbol, quantity, price,
                         datetime.fromtimestamp(buy_limit['transactTime'] / 1000).strftime('%d-%m-%Y %H:%M:%S'))
    except Exception as e:
        print(e)


# Iterates through the pairs and places a spot order for each
def placeDCAOrders():
    # create Message body
    global body
    body = 'Total of *' + str(len(assets)) + '* orders for a total of *' + str(totalSum) + ' $* spent. \n\n'

    # Checks if Balance is sufficient
    currentBalance = float(binanceClient.get_asset_balance(asset=assetForPaying)['free'])
    if currentBalance < totalSum:
        missingBalance = totalSum - currentBalance + 0.5
        redeemFromSavings(asset=assetForPaying, redeem_amount=missingBalance, redeem_type='FAST')

    # Iterates through every order
    for key in assets.values():
        # Get Amount and Price stepSize (decimals)
        for filt in binanceClient.get_symbol_info(key[0])['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                ticks[key[0]] = Decimal(filt['stepSize']).normalize()
            if filt['filterType'] == 'PRICE_FILTER':
                steps[key[0]] = Decimal(filt['tickSize']).normalize()

        moneySpent = key[1]

        # Calculate/set price and amount for the order
        try:
            currPrice = round(float(binanceClient.get_symbol_ticker(symbol=key[0])['price']) * factor,
                              len(str(steps[key[0]]).split(".")[1]))
            amount = round(moneySpent / currPrice, len(str(ticks[key[0]]).split(".")[1]))
        except IndexError:
            currPrice = round(binanceClient.get_symbol_ticker(symbol=key)['price'] * factor)
            amount = round(moneySpent / currPrice)

        # Try to place the order
        try:
            createBuyOrder(key[0], amount, currPrice)
        except Exception as e:
            print(e)


# Sends WhatsAppMessage with the order details
def addToMessageBody(orderId, symbol: str, quantity: float, price: float, time):
    global body
    body += 'Successfully placed order ' + str(orderId) \
            + ':\nTrading Pair: *' + symbol + '*' \
            + '\nAmount: ' + str(quantity) + ' ' + symbol.replace('USDT', '') \
            + '\nPrice: ' + str(price) + ' $' \
            + '\nTotal Amount: ' + str(round(price * quantity, 2)) + ' $' \
            + '\nTimestamp: ' + str(time) + '\n\n' \
            + '------------------------------------- \n\n'


# Cancels all Open Spot Orders for the account
def cancelAllOpenOrders():
    try:
        for key in assets.values():
            orders = binanceClient.get_open_orders(symbol=key[0])
            for order in orders:
                binanceClient.cancel_order(symbol=key, orderId=order['orderId'])
    except Exception as e:
        print(e)


# Hashes he signature for the request
def hashing(query_string):
    return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()


def redeemFromSavings(asset: str, redeem_amount, redeem_type):
    # Obtain all needed data
    headers = {'X-MBX-APIKEY': api_key}
    timestamp = int(time.time() * 1000)
    productId = asset + '001'
    queryString = 'timestamp=' + str(
        timestamp) + '&productId=' + productId + '&type=' + redeem_type + '&amount=' + str(redeem_amount)
    urlPath = '/sapi/v1/lending/daily/redeem'

    # Construct URL and send Request
    url = BASE_URL + urlPath + '?' + queryString + '&signature=' + hashing(queryString)
    req = requests.post(url=url, headers=headers)


# Main
if __name__ == "__main__":

    # Dictionary for what you want to buy
    # key := Name of the Asset (only relevant for RiskCalcuator)
    # value := trading pair and the amount you want to spend
    assets = {'Bitcoin': ['BTCEUR', 50],
              'Ethereum': ['ETHEUR', 50],
              'Cardano': ['ADAEUR', 50],
              'Chainlink': ['LINKEUR', 30],
              'Polkadot': ['DOTEUR', 30],
              'VeChain': ['VETEUR', 20],
              'Delta-Theta': ['THETAEUR', 20],
              'Solana': ['SOLEUR', 20],
              'Avalanche-2': ['AVAXEUR', 15],
              'Elrond-erd-2': ['EGLDEUR', 15]
              }

    # Calculates the current Risk for Bitcoin and adjust the amount to the current risk level
    risk = RiskCalculator.getRiskForAsset('Bitcoin', True)
    for key, value in assets.items():
        value[1] *= (1.4 - (2 * risk))

    # Calculates the sum of money to spent
    totalSum = sum([x[1] for x in list(assets.values())])

    # The Fiat currency used for paying (if multiple are wanted, then the code needs to be adjusted)
    assetForPaying = 'EUR'

    # Factor by which the current price is dropped (for example: current price is 10,000 and factor 0.95 ->
    # 10,000 * 0.95 => Order is set at price 9,500
    factor = 0.95

    # So that the amount I want to buy has the right number of decimals
    ticks = dict()
    # So that the price has the right number of decimals
    steps = dict()

    # Connect to Binance API
    api_key = 'xxx'  # yourApiKey
    api_secret = 'xxx'  # yourApiSecret

    binanceClient = BinanceClient(api_key, api_secret)
    BASE_URL = 'https://api.binance.com'

    if api_key is not None and api_secret is not None:
        # Place all the defined orders
        placeDCAOrders()

        # Updates Excel Sheet
        ExcelWriter.updateExcel(binanceClient)
