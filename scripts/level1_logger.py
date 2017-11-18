#!/usr/bin/env python

"""
Taken from gdax-python order_book.py, with small modifications
"""

from __future__ import absolute_import, division, print_function

from gdax import OrderBook
import sys
import time
import datetime as dt
import argparse


class OrderBookConsole(OrderBook):
    """
    Logs real-time changes to the bid-ask spread to the console.
    """
    def __init__(self, product_id=None):
        super(OrderBookConsole, self).__init__(product_id=product_id)

        # latest values of bid-ask spread
        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None

    def on_message(self, message):
        current_time = dt.datetime.now()

        super(OrderBookConsole, self).on_message(message)

        # Calculate newest bid-ask spread
        bid = self.get_bid()
        bids = self.get_bids(bid)
        bid_depth = sum([b['size'] for b in bids])
        ask = self.get_ask()
        asks = self.get_asks(ask)
        ask_depth = sum([a['size'] for a in asks])

        if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
            # If there are no changes to the bid-ask spread since the last update, no need to print
            pass
        else:
            # If there are differences, update the cache
            self._bid = bid
            self._ask = ask
            self._bid_depth = bid_depth
            self._ask_depth = ask_depth
            print('{},{:.3f},{:.2f},{:.3f},{:.2f}'.format(
                current_time, bid_depth, bid, ask_depth, ask))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("product", metavar="PRODUCT", help="e.g. BTC-USD")
    args = parser.parse_args()

    order_book = OrderBookConsole(args.product)
    order_book.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        order_book.close()

    if order_book.error:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
