import requests
from market_data import MARKET_API_PREFIX, MarketData

TRANSACTION_HISTORY_API = MARKET_API_PREFIX + 'transaction_history.json'

transaction_history = None
market_data = None


def get_transaction_history():
    """
    Get transaction history. If it's the first time, cache
    the results in 'transaction_history' global variable
    """
    global transaction_history
    if not transaction_history:
        try:
            response = requests.get(TRANSACTION_HISTORY_API)
            transaction_history = response.json()
        except Exception as err:
            print('Error fetching transaction history from '
                  f'{TRANSACTION_HISTORY_API}: {err}.')
            return []
    return transaction_history


def float_to_price_string(flt, num_decimals):
    """
    Convert a float to '100,000,000.00' format
    """
    format_str = '{:.' + str(num_decimals) + 'f}'
    main_number = format_str.format(flt)
    decimals_suffix = main_number[-num_decimals:]  # remove main number
    return f'{int(float(main_number)):,}.{decimals_suffix}'


def calculate_balances():
    """
    Calculate and return current and historical portfolio balances
    in the following format:
        {
            "CAD": (str),
            "BTC": (str),
            "ETH": (str),
            "networth": (str),
            "daily_networth": (dict)
        }
    """
    global market_data
    # Get and cache market_data if first time
    if not market_data:
        market_data = MarketData()

    tx_history = get_transaction_history()
    # sort transactions from oldest to newest to simplify daily
    # networth calculations
    tx_history.sort(key=lambda tx: tx['createdAt'])
    balances = {
        "CAD": 0,
        "BTC": 0,
        "ETH": 0,
        "networth": 0,
        "daily_networth": {}
    }
    daily_networth = balances['daily_networth']

    for tx in tx_history:
        # limit timestamps to the day (YYYY-MM-DD)
        date = tx['createdAt'][:10]
        if tx['type'] == 'conversion':
            balances[tx['from']['currency']] -= float(tx['amount'])
            balances[tx['to']['currency']] += float(tx['to']['amount'])
        elif tx['direction'] == 'credit':
            balances[tx['currency']] += float(tx['amount'])
        else:
            balances[tx['currency']] -= float(tx['amount'])
        btc_cad_on_date = market_data.get_price_on_date('BTC', date)
        eth_cad_on_date = market_data.get_price_on_date('ETH', date)

        # calculate networth at current date
        networth_on_date = (
            balances['CAD'] +
            balances['BTC'] * btc_cad_on_date +
            balances['ETH'] * eth_cad_on_date
        )
        # store daily networth in a map of date: networth
        daily_networth[date] = float_to_price_string(networth_on_date, 2)

    # reverse order of daily_networth map from newest to oldest
    # to display it in the UI
    daily_networth_desc = {}
    for date in sorted(daily_networth.keys(), reverse=True):
        daily_networth_desc[date] = daily_networth[date]
    balances['daily_networth'] = daily_networth_desc

    # use current market rate to calculate current networth
    networth = (
        balances['CAD'] +
        balances['BTC'] * market_data.get_current_price('BTC') +
        balances['ETH'] * market_data.get_current_price('ETH')
    )

    # convet balances to nicely formatted strings
    balances['networth'] = float_to_price_string(networth, 2)
    balances['CAD'] = float_to_price_string(balances['CAD'], 2)
    balances['BTC'] = float_to_price_string(balances['BTC'], 8)
    balances['ETH'] = float_to_price_string(balances['ETH'], 8)

    return balances
