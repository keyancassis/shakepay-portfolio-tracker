import requests

EXCHANGE_RATE_API = 'https://api.shakepay.co/rates'
MARKET_API_PREFIX = 'https://shakepay.github.io/programming-exercise/web/'
BTC_CAD_HISTORY_API = MARKET_API_PREFIX + 'rates_CAD_BTC.json'
ETH_CAD_HISTORY_API = MARKET_API_PREFIX + 'rates_CAD_ETH.json'


class MarketData:
    """
    This class is used to fetch market data
    """
    def __init__(self):
        self.btc_cad_history = self.get_price_history('BTC')
        self.eth_cad_history = self.get_price_history('ETH')
        # the following are used when price on a given date is missing
        self.last_known_btc_cad = 0
        self.last_known_eth_cad = 0

    def get_price_on_date(self, currency, date):
        """
        Return the price of the given currency on date (YYYY-MM-DD)
        """
        if currency == 'BTC':
            price = self.btc_cad_history.get(date)
            if not price:
                price = self.last_known_btc_cad
            self.last_known_btc_cad = price
        elif currency == 'ETH':
            price = self.eth_cad_history.get(date)
            if not price:
                price = self.last_known_eth_cad
            self.last_known_eth_cad = price
        else:
            price = 0
        return float(price)

    @staticmethod
    def get_current_price(currency):
        """
        Get the current market price for the given currency
        """
        if currency == 'CAD':
            return 1
        try:
            response = requests.get(EXCHANGE_RATE_API)
            exchange_rates = response.json()
        except Exception as err:
            print('Error fetching daily exchange rates from '
                  f'{EXCHANGE_RATE_API}: {err}.')
            return 0
        return float(exchange_rates.get(currency + '_CAD', 0))

    @staticmethod
    def get_price_history(currency):
        """
        Get a list of the daily price of the given currency
        """
        try:
            url = BTC_CAD_HISTORY_API if currency == 'BTC' else \
                  ETH_CAD_HISTORY_API
            response = requests.get(url)
            price_history = response.json()
            # limit all timestamps to the day (YYYY-MM-DD)
            price_history = {data['createdAt'][:10]: data['midMarketRate']
                             for data in price_history}
        except Exception as err:
            print(f'Error fetching {currency} daily price history from '
                  f'{url}: {err}.')
            return []
        return price_history
