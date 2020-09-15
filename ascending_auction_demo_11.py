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

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

print("\n\n###### EXAMPLE OF PS with GFT=0")

market = Market([
    AgentCategory("buyer", [1, 1, 1, 1, 1]),
    AgentCategory("seller", [-1, -1, -1, -1, -1]),
])

print(budget_balanced_ascending_auction(market, [1,1]))


