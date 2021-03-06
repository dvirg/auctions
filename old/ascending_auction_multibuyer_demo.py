#!python3

"""
Demonstration of a multiple-clock strongly-budget-balanced ascending auction
for a multi-lateral market with one buyer per two sellers (recipe: 1,2)

Author: Erel Segal-Halevi
Since:  2019-08
"""

from markets import Market
from agents import AgentCategory
from old import ascending_auction_multibuyer_protocol
from old.ascending_auction_multibuyer_protocol import budget_balanced_ascending_auction
import prices

import logging
ascending_auction_multibuyer_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

print("\n\n###### TEST MULTI RECIPE AUCTION WITH A SINGLE RECIPE (1,2)")

market = Market([
    AgentCategory("buyer", [17, 14, 13, 9, 6]),
    AgentCategory("seller", [-1, -2, -3, -4, -5, -7, -8, -10, -11]),
])

print(budget_balanced_ascending_auction(market, [[1, 2]]))


print("\n\n###### TEST TWO RECIPES: (1,0,1) and (0,1,2)")

market = Market([
    AgentCategory("onebuyer", [12, 13, 15, 17, 19]),
    AgentCategory("twobuyer", [16, 18, 25, 27, 31]),
    AgentCategory("seller", [-1, -2, -3, -4, -5, -7, -8, -10, -11]),
])

print(budget_balanced_ascending_auction(market, [[1, 0, 1], [0, 1, 2]]))

#print(budget_balanced_ascending_auction(market,[[1,1,0],[1,0,2]]))



print("\n\n###### TEST THREE RECIPES: (1,0,0,1) and (0,1,0,2) and  (0,0,1,3)")

market = Market([
    AgentCategory("onebuyer",   [13, 15, 17, 19]),
    AgentCategory("twobuyer",   [16, 18, 25, 27, 31]),
    AgentCategory("threebuyer", [30, 40, 50, 60]),
    AgentCategory("seller", [-1, -2, -3, -4, -5, -7, -8, -10, -11, -12, -13, -14]),
])

print(budget_balanced_ascending_auction(market, [[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3]]))

