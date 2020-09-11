#!python3

"""
Demonstration of a multiple-clock strongly-budget-balanced ascending auction
for a multi-lateral market with one buyer per two sellers (recipe: 1,1)

Author: Dvir Gilor
Since:  2020-08
"""

from markets import Market
from agents import AgentCategory
import ascending_auction_protocol, prices
from ascending_auction_protocol import budget_balanced_ascending_auction
from experiment import experiment

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

print("\n\n###### RUNNING DEMO FOR TYPE (1,1)")

market = Market([
    AgentCategory("buyer", [1,1,1,1,1]),
    AgentCategory("seller", [-1,-1,-1,-1,-1]),
])
print(budget_balanced_ascending_auction(market, [1,1]))


print("\n\n###### RUNNING EXPERIMEENT FOR DEMO OF TYPE (1,1)")

results_file = "results/ascending_auction_demo_11.csv"
SBB_ASCENDING_STOCKS = "SBB Ascending Prices"

experiment(results_file, budget_balanced_ascending_auction, SBB_ASCENDING_STOCKS, (1, 1),
           value_ranges   = [(1,1),(-1,-1)],
           nums_of_agents = (5,5),
           num_of_iterations = 1
           )

