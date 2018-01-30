import pandas as pd
import numpy as np
import argparse
import logging
from   logging.handlers import RotatingFileHandler

# 1. Read coinmarketcap for volume signal
# 2. Pick the ones that have ridiculously increasing volumes
# 3. Use that as a signal for indication of public interest


# Separate: Find arbitrary opportunity by reading CMC

# Modules are from pip3.6 install coinmarketcap, pip3.6 install pymarketcap
# https://pypi.python.org/pypi/coinmarketcap/
# https://pypi.python.org/pypi/pymarketcap/
from coinmarketcap import Market
import pymarketcap


def get_all_coin_df(topn=0):
    '''
        Api: https://coinmarketcap.com/api/
        topn: the highest n capped coins. 0 => all coins.
        This method reads cmc and gets the coins now.
        Can print df to see what it looks like. API doesn't have historical data 
        This dataframe can have rough estimate on what coins are being pumped.
    '''
    cmc = Market()
    all_coins = cmc.ticker(limit=topn)
    df = pd.DataFrame(all_coins)
    df['last_updated'] = pd.to_datetime(df['last_updated'], unit='s').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df[['24h_volume_usd', 'available_supply', 'market_cap_usd', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']] = df[['24h_volume_usd', 'available_supply', 'market_cap_usd', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']].astype(float)
    df['Pump Rate'] = df['24h_volume_usd'] / df['market_cap_usd']* 100.0
    return df


def find_arb(coin, min_exchange_percentage_volume=1, filter_exchanges=[], notify_percentage=5, logger=logging.getLogger(__name__)):
    '''
        For each coin, look for coinmarketcap /#markets page to see if there is arb opportunity
        Parameters:
            coin: Name of coin in short: i.e. BTC
            min_exchange_percentage_volume: only look for exchange pairs with this much volume
            filter_exchanges: List of exchanges that you can access.
            notify_percentage: log percentage diff > x
    '''
    cmc = pymarketcap.Pymarketcap()
    df = pd.DataFrame(cmc.markets(coin))
    
    if len(filter_exchanges) > 0:
        df = df[df['exchange'].isin(filter_exchanges)]
    
    df = df[df['updated'] == True]
    df = df[df['percent_volume'] > min_exchange_percentage_volume]
    # if diff more than 3%, notify
    max_difference = float(df['price_usd'].max() - df['price_usd'].min()) / float(df['price_usd'].median()) * 100
    if max_difference > notify_percentage:
        print(f"{round(max_difference, 2)}% diff in {coin}")
        logger.info(f"{round(max_difference, 2)}% diff in {coin}")
        
        df = df.reset_index(drop=True)
        res = pd.DataFrame([df.iloc[df['price_usd'].idxmax()], df.iloc[df['price_usd'].idxmin()]])
        print(f"\n{res.to_string()}")
        logger.info(f"\n{res.to_string()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", help="File path to log results to", required=True)
    parser.add_argument("-topn", help="Look for coins within top n marketcap", required=False, default=0, type=int)
    parser.add_argument("-diff", help="notify if > x percent diff", required=False, default=10, type=int)
    parser.add_argument("-min_exchange_volume", help="include pairs if > x percent volume", required=False, default=1, type=int)
    parser.add_argument("-exchanges", nargs='+', default=['Bitfinex', 'Binance',
                'GDAX', 'Bittrex', 'Kraken', 'OKEx', 'Huobi', 'Poloniex', 'Bittrex', 'Kucoin'], required=False, help="Only find within these exchanges")
    
    args = parser.parse_args()
    

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(args.path)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    logger.info(args)

    
    while True:
        try:
            df = get_all_coin_df(topn=args.topn)
        except Exception as e:
            print(e)
            continue

        logger.info(f"Running arb finder on {df['symbol'].nunique()} symbols...")
        for coin in df['symbol'].unique():
            try:
                find_arb(coin, min_exchange_percentage_volume=args.min_exchange_volume, filter_exchanges=args.exchanges, notify_percentage=args.diff)
            except Exception as e:
                print(e)
                continue

