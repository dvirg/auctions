#!python3

"""
Demonstration of a multiple-clock strongly-budget-balanced ascending auction
for a multi-lateral market with one buyer per two sellers (recipe: 1,2)

Author: Erel Segal-Halevi
Since:  2019-08
"""

from markets import Market
from agents import AgentCategory
import ascending_auction_protocol, prices
from ascending_auction_protocol import budget_balanced_ascending_auction
from get_stock_data import getPrices

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

#stock prices
att = getPrices('stocks\T.csv',(1,2))

print("\n\n###### RUNNING EXAMPLE FROM THE PAPER FOR TYPE (1,2)")

market = Market([
    AgentCategory("buyer", att[0]),
    AgentCategory("seller", att[1]),
])

print(budget_balanced_ascending_auction(market, [1,2]))


print("\n\n###### RUNNING EXAMPLE FROM THE PAPER, WITH DIFFERENT CATEGORY ORDER")

market = Market([
    AgentCategory("seller", att[1]),
    AgentCategory("buyer", att[0]),
])

print(budget_balanced_ascending_auction(market, [2,1]))
