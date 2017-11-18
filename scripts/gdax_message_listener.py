#!/usr/bin/env python

"""
Logs all messages from gdax in rotating logs.

The messages are in JSON.

The Socket does not look very reliable though.
"""

import gdax
import argparse
import logging
import time
from   pikachu.lib import rotation_logger

MKTDATA_PATH = "../../btc/mktdata/gdax/{}/mktdata.json" # FIXME: customize
MEGA = 2 ** 20

def setup_logging(product):
    path = MKTDATA_PATH.format(product)
    # TODO: tweak params
    rotation_logger.set_root_logger(path, maxBytes=50 * MEGA, backupCount=100)

def log_msg(msg):
    logging.info(str(msg))

def continuous_logging(product):
    setup_logging(product)
    wsClient = gdax.WebsocketClient(url="wss://ws-feed.gdax.com",
                                    products=[product])
    wsClient.on_message = log_msg
    wsClient.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        wsClient.close()
        logging.info('{"shutdown" : 1}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("product", metavar="PRODUCT", help="e.g. BTC-USD")
    args = parser.parse_args()
    continuous_logging(args.product)

if __name__ == "__main__":
    main()
