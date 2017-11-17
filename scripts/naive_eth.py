#!/usr/bin/env python

import gdax
import json

import random
import argparse
from   pikachu.credentials import auth_client_from_json

import time
import datetime as dtime

def get_eth_funds(auth_client):
	dicts = auth_client.get_accounts()
	for item in dicts:
		if item['currency'] == 'ETH':
			eth = item
		elif item['currency'] == 'USD':
			usd = item
	return eth['available'], usd['available']

def limit_buy_lowest(auth_client, usd_balance, live=0):
	daily_stats = public_client.get_product_24hr_stats('ETH-USD')

	currentTime = dtime.datetime.now().isoformat()

	array = public_client.get_product_historic_rates('ETH-USD', end=currentTime, granularity=300)

	time_value, five_min_low, five_min_high, open_p, close_p, volume = sorted(array, reverse=True)[1]

	# data not recent
	if int(time.time()) - time_value > 1200:
		print("time too far")
		return

	# not enough liq
	if volume < 5:
		return
	# not enough money
	if usd_balance < five_min_low * 0.1:
		return

	# not enough volatility
	if (five_min_high - five_min_low) / five_min_low < 0.0005:
		print("volatility low")
		return

	price = round(five_min_low * 0.9995, 2)

	# sanity check on price
	if price > 350:
		print("insane price @ {}".format(price))
		return

	if live == 1:
		returns = auth_client.buy(product_id='ETH-USD', size=0.01, price=price, type='limit', side='buy')
		order_id = returns.get('id', None)

		if order_id:
			my_orders.append(order_id)

def limit_sell_highest(auth_client, eth_balance, live=0):
	daily_stats = public_client.get_product_24hr_stats('ETH-USD')

	currentTime = dtime.datetime.now().isoformat()

	array = public_client.get_product_historic_rates('ETH-USD', end=currentTime, granularity=300)

	time_value, five_min_low, five_min_high, open_p, close_p, volume = sorted(array, reverse=True)[1]

	# check time recent
	if int(time.time()) - time_value > 1200:
		print("time too far")
		return

	# not enough liq
	if volume < 5:
		return

	# not enough eth
	if eth_balance < 0.1:
		return

	#  not enough volatility
	if (five_min_high - five_min_low) / five_min_low < 0.0005:
		print("volatility low")
		return

	price = round(five_min_high * 1.0005, 2)

	# sanity check
	if price < 250:
		print("insane price @ {}".format(price))
		return


	if live == 1:
		returns = auth_client.sell(product_id='ETH-USD', size=0.01, price=price, type='limit', side='sell')
		order_id = returns.get('id', None)

		if order_id:
			my_orders.append(order_id)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-l', '--live', type=int, required=True, help='1 to trade')
	parser.add_argument(
		'-c', '--cred_file', metavar="JSON_FILE", required=True,
		help="path to credential file"
	)
	args = parser.parse_args()

	public_client = gdax.PublicClient()

	daily_stats = public_client.get_product_24hr_stats('ETH-USD')
	currencies = public_client.get_currencies()
	# print(currencies)
	print(daily_stats)

	# print(public_client.get_product_historic_rates('ETH-USD', start=None, end=None,
    # granularity=3600))

	today_low = daily_stats['low']
	my_orders = []

	auth_client = auth_client_from_json(args.cred_file)

	request = auth_client.get_fills(limit=100)

	# print(request[0])

	# print auth_client.get_position()
	while True:
		try:
			for id in my_orders:
					res = auth_client.get_order(id)
					if float(res['filled_size']) > 0:
						print(res)

			eth, usd = get_eth_funds(auth_client)
			eth = float(eth)
			usd = float(usd)


			# the other thing got sold. Finish.
			# print(eth, usd)
			if float(usd) > 500:
				exit()

			limit_buy_lowest(auth_client, usd, live=args.live)
			limit_sell_highest(auth_client, eth, live=args.live)
		finally:
			pass
		# except Exception as e:
		# 		print(e)
