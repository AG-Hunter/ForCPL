
from datetime import datetime, timedelta
import sqlite3
from binance.client import Client
import api_keys


#def get_current_balance, a function to get the current balance of the users account:

def get_current_balances(key, secret, base, quote):
    ## connect to binance API with personal dict_keys
    client = Client(key, secret)
    acct = client.get_account()
    balances = acct['balances']

    for dict in balances:
        if quote in dict.values():
            free = float(dict['free'])
            locked = float(dict['locked'])
            quote_current_bal = free+locked
        else:
            continue
    for dict in balances:
        if base in dict.values():
            free = float(dict['free'])
            locked = float(dict['locked'])
            base_current_bal = free+locked
        else:
            continue
    balances = {'base':base_current_bal, 'quote':quote_current_bal}
    return balances

def fetch_price(base, quote, client):
    USDT = 'USDT'
    quote_US_ticker = quote + USDT
    base_US_ticker = base + USDT
    price_US = {}
    try:
        quote_price_US = client.get_avg_price(symbol=quote_US_ticker)
        price_US['quote_price_US'] = quote_price_US['price']
    except:
        print('Unable to retrieve current price of quote asset')
        quote_price_US = input('Enter current price of quote asset > ', )
        price_US['quote_price_US'] = quote_price_US
    try:
        base_price_US = client.get_avg_price(symbol=base_US_ticker)
        price_US['base_price_US'] = base_price_US['price']
    except:
        print('Unable to retrieve current price of base asset')
        base_price_US = input('Enter current price of base asset > ', )
        price_US['base_price_US'] = base_price_US
    return price_US

def fetch_price2(asset, client):

    USDT= 'USDT'
    ticker = asset+USDT
    asset_price_US = client.get_avg_price(symbol = ticker)
    price_US = {'asset_price_US': asset_price_US}
    return price_US

def calc_time():
    datestring = input('Over what period do you wish to calculate performance (in days): ')
    delta = timedelta(days=int(datestring))
    ## start_time is the furthest point back in time from which you want to select trades. Endtime is the end of the period
    ## from which you are selecting trades(i.e. the most recent time.)
    current_DTG = datetime.now()
    start_DTG = current_DTG - delta
    ## Convert DTG to timestamps.
    start_time = int(datetime.timestamp(start_DTG))*1000
    end_time = int(datetime.timestamp(current_DTG))*1000
    times = {'start_time': start_time, 'end_time': end_time, 'start_DTG': start_DTG, 'current_DTG': current_DTG, 'period': datestring}
    print(times['start_time'])
    return times

def fetch_trades(start_time, symbol, exchange):
    print(symbol)
    # connect to trade  database
    conn = sqlite3.connect('../Trades.sqlite')
    cur = conn.cursor()
    if exchange == 'All':
        query = 'SELECT timestamp, symbol, side, price, quantity, commission, commission_asset, exchange from Trades WHERE timestamp >= ? AND symbol = ?'
        params = (start_time, symbol)
        cur.execute(query, params)
        trades = cur.fetchall()
        cur.close()
    else:
        query = 'SELECT timestamp, symbol, side, price, quantity, commission, commission_asset, exchange from Trades WHERE timestamp >= ? AND symbol = ? AND exchange = ?'
        params = (start_time, symbol, exchange)
        cur.execute(query, params)
        trades = cur.fetchall()
        cur.close()

    return trades

def calc_trade_delta(trades):
    quote_acquired = 0
    quote_disposed = 0
    base_acquired = 0
    base_disposed = 0

    for trade in trades:
        if trade[2] == 'buy':
            base_acquired += trade[4]
            quote_disposed += (trade[3] * trade[4])
        else:
            quote_acquired += (trade[3] * trade[4])
            base_disposed += trade[4]

    quote_delta = quote_acquired - quote_disposed
    base_delta = base_acquired - base_disposed
    trade_delta = {'quote_delta': quote_delta, 'base_delta': base_delta}
    return trade_delta


def get_comms(trades, client):
    comms_BNB = 0
    comms_other = 0
    asset_list = []
    asset_totals = {}
    for trade in trades:
        comms_asset = trade[6]
        if comms_asset not in asset_list:
            asset_list.append(trade[6])
    for asset in asset_list:
        cum_asset = 0
        for trade in trades:
            if asset == trade[6]:
                cum_asset += float(trade[5])
        asset_totals[asset] = cum_asset

## There is a limitation in this part of the code as it is unable to handle comms assets that are not quoted against USDT
    asset_price_USD = {}
    for asset in asset_list:
        symbol = asset + "USDT"
        USD_price = client.get_avg_price(symbol=symbol)
        asset_price_USD[asset] = USD_price["price"]

    total_comms_paid = 0
    for asset in asset_list:
        total_comms_paid += float(asset_totals[asset]) * float(asset_price_USD[asset])

    return total_comms_paid



def choose_exchange(exchange):
    if exchange == '1':
        exchange = 'Binance'
    elif exchange == '2':
        exchange = 'Kucoin'
    elif exchange == '3':
        exchange = 'Ascendex'
    elif exchange == '4':
        exchange = 'Gate.io'
    else:
        exchange = 'All'
    return exchange


def calc_profit():
    ## Get input of required tokens
    base = input('Enter base asset: ')
    quote = input('Enter quote asset: ')
    symbol = base+ '-' + quote
    exchange = input('''If trades for a specific exchange are required, please follow the prompts, else just press enter.
    For Binance enter 1:
    For Kucoin enter 2:
    For Ascendex enter 3:
    For Gate.io enter 4: 
    >>: ''')

    exchange = choose_exchange(exchange)

    ## connect to binance API with personal dict_keys and fetch current account details

    key = api_keys.binance_keys()[0]
    secret = api_keys.binance_keys()[1]
    client = Client(key, secret)
    current_balances = get_current_balances(key, secret, base, quote)
    print(current_balances)

    # Calculate current and start times

    times = calc_time()

    #Fetch trades from "trades" database.

    trades = fetch_trades(times['start_time'], symbol, exchange)
    print('trades = ', trades)

    #Calculate total volume of assets acquired and disposed.

    trade_delta = calc_trade_delta(trades)
    print(trade_delta)

    ## Fetch USDT price for both base and quote and convert deltas to USDT.

    current_asset_price = fetch_price(base, quote, client)
    print(current_asset_price)

    ## calculate values of trade delta in constant currency terms.

    quote_delta_usd = float(current_asset_price['quote_price_US']) * trade_delta['quote_delta']
    base_delta_usd = float(current_asset_price['base_price_US']) * trade_delta['base_delta']

    # Calculate commissions paid

    try:
        comms = get_comms(trades, client)
    except:
        print('Commission could not be calculated')
        comms = 0

    ## Output results

    print(f'The trade delta for {base} is US$ {base_delta_usd}')
    print(f'The trade delta for {quote} is US$ {quote_delta_usd}')
    print(f'The total amount of commission paid is US$ {comms}')
    print(f'Your profitability for this market is US$ {base_delta_usd + quote_delta_usd - comms} over the past {times["period"]} days')


calc_profit()






