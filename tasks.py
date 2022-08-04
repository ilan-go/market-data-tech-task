from re import search
import time
from prometheus_client import Gauge, start_http_server
import requests
from operator import itemgetter


class BinanceTask:

    def __init__(self):
        start_http_server(8080)
        self.g = Gauge('symbol_spread_delta', 'Value of symbol price spread absolute delta', ['asset'])

    def test_connection(self):
        try:
            r = requests.get('https://api.binance.com/api/v3/ping')
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(f'Error communicating with the Binanace API: {e}')
        return True

    def last24h_ticker_getter(self, asset='BTC'):
        r = requests.get('https://api.binance.com/api/v3/ticker/24hr').json()
        found_values = []
        [found_values.append(dictionary) for dictionary in r if search(asset, dictionary['symbol'])]
        [item.update({'volume': (float(item.get('volume')))}) for item in found_values]
        return found_values

    def highest_volume_getter(self, filtered_list):
        sorted_list = sorted(filtered_list, key=itemgetter('volume'), reverse=True)
        return list(map(itemgetter('symbol', 'volume'), sorted_list))[:5]

    def highest_number_of_trades_getter(self, filtered_list):
        sorted_list = sorted(filtered_list, key=itemgetter('count'), reverse=True)
        return list(map(itemgetter('symbol', 'count'), sorted_list))[:5]

    def top_200_bids_asks(self, filtered_list):
        for asset in filtered_list:
            r = requests.get('https://api.binance.com/api/v3/depth', params={'symbol': asset[0], 'limit': 200}).json()
            count_bids = self.notional_value_counter(r['bids'])
            count_asks = self.notional_value_counter(r['asks'])
            print(f"Notional value for {asset[0]} bids is: {count_bids}")
            print(f"Notional value for {asset[0]} asks is: {count_asks}")
        print()

    def notional_value_counter(self, order_book_list):
        count = 0
        for tuple in order_book_list:
            count += float(tuple[0])
        return count

    def price_spread_calculator_loop(self, q2_results):
        iteration_data = self.__price_spread_calculator(q2_results)
        while (True):
            print()
            iteration_data = self.__price_spread_calculator(q2_results, True, iteration_data)
            time.sleep(10)

    def __price_spread_calculator(self, q2_results, iterate=False, delta_list=[0, 0, 0, 0, 0]):
        i = 0
        for asset in q2_results:
            r = requests.get('https://api.binance.com/api/v3/depth', params={'symbol': asset[0], 'limit': 1}).json()
            price_spread = float(r['asks'][0][0]) - float(r['bids'][0][0])
            print(f"Symbol: {asset[0]}  Price spread: {price_spread}")
            if iterate:
                print(f"Absolute delta from the last value is: {abs(delta_list[i] - price_spread)}")
                self.g.labels(asset[0]).set(abs(delta_list[i] - price_spread))
            delta_list[i] = price_spread
            i += 1
        return delta_list

    def print_asset(self, asset_list, value):
        print(f"Asset symbol:       {value}:")
        for tuple in asset_list:
            print(f"{tuple[0]}            {tuple[1]}")
        print()


def main():
    session = BinanceTask()
    if session.test_connection():
        highest_volume = session.highest_volume_getter(session.last24h_ticker_getter('BTC'))
        session.print_asset(highest_volume, "Highest volume over last 24h")
        highest_trades = session.highest_number_of_trades_getter(session.last24h_ticker_getter('USDT'))
        session.print_asset(highest_trades, "Highest number of trades over last 24h")
        session.top_200_bids_asks(highest_volume)
        session.price_spread_calculator_loop(highest_trades)


if __name__ == "__main__":
    main()
