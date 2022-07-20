import datetime
import sqlite3
from binance.client import Client
import api_keys # api_keys file name to be updated once personal keys inserted.
from time import sleep

def download_trades(symbol, sub):

    #connect to DB
    conn = sqlite3.connect('..\Trades.sqlite')
    cur = conn.cursor()

    key = api_keys.binance_keys(sub)[0]
    secret = api_keys.binance_keys(sub)[1]


    ## connect to binance API with personal dict_keys
    client = Client(key, secret)

    base, quote = symbol.split('-')
    pair = base+quote
    exchange = "Binance"
    ##datestring = input('Enter date of earliest trade in format mm/dd/YYYY:')
    datestring = "01/07/2021" ##overriding input with default date for start of FY
    date = datetime.datetime.strptime(datestring, '%m/%d/%Y')
    starttime = int(datetime.datetime.timestamp(date))*1000

    # Establish counters to track program execution and control loops. Count = 500 to commence while loop.
    count = 500
    cumsum = 0

    while count>499:
        orders = client.get_my_trades(symbol=pair, requests_params={'timeout': 5}, startTime=starttime)
        count = 0
        for entry in orders:
            timestamp = entry["time"]
            time = datetime.datetime.fromtimestamp(timestamp/1000)
            trade_id = entry['id']
            if entry['isBuyer'] is True:
                side = "buy"
            else:
                side = "sell"
            price = entry['price']
            quantity = entry['qty']
            orderid = entry['orderId']
            commission = entry['commission']
            commission_asset = entry['commissionAsset']
            params = (trade_id, exchange, orderid, timestamp, time, symbol, side, price, quantity, commission, commission_asset)
            cur.execute('INSERT or IGNORE INTO Trades VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?)', params)
            conn.commit()
            count = count +1
            cumsum = cumsum +1

        params = (symbol, exchange)
        cur.execute('SELECT max(timestamp) FROM Trades WHERE symbol = ? and exchange = ?', params)
        starttime = cur.fetchone()
        starttime = starttime[0]
        #insert pause to manage API rate limits
        sleep(1.5)


    cur.close()

    print(f'Total number of trades retrieved for {pair} in Sub account {sub} is:  {cumsum}')

    print('#################################################')


def import_trades():
    print('working')
    # Create database to store trade data
    conn = sqlite3.connect('..\Trades.sqlite')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Trades
            (id INTEGER PRIMARY KEY UNIQUE, exchange TEXT,orderid INTEGER, timestamp INTEGER, datetime INTEGER, symbol TEXT, side TEXT,
            price REAL, quantity REAL, commission REAL, commission_asset TEXT)
            ''')
    cur.close()
    print('working again')

    # binance only allows download by trade pair so each pair that you have traded must be entered manually into this list
    # in all caps.

    token_list =['PHB-TUSD', 'AVAX-USDT', 'AVAX-TRY', 'STRAX-BUSD', "BTC-USDT", 'ETH-USDT', 'FRONT-BUSD', 'FRONT-USDT',
                 'MFT-ETH', 'MFT-BNB', 'PIVX-ETH','NANO-USDT', 'LINK-USDT', 'USDC-USDT', 'AVAX-BNB', 'STRAX-USDT',
                 'FRONT-BTC', 'RLC-ETH', 'EXRD-USDT', 'BNB-USDT', "MANA-USDT", 'MATIC-USDT', 'ALGO-USDT', 'ALGO-BTC', 'LRC-USDC', 'ETH-USDC']

    # the number of sub accounts you wish to iterate through
    sub_num = 4

    fail_tkn = []
    fail_acct = []

    for sub in range(1, sub_num + 1):
        for token in token_list:

            try:
                download_trades(token, sub)
            except:
                fail_tkn.append(token)
                fail_acct.append(sub)

    new_lst = [list(x) for x in zip(fail_tkn, fail_acct)]
    print("Downloading failed for the following tokens and sub accounts")
    print(new_lst)

import_trades()


