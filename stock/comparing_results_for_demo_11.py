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
from experiment import experiment
from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

print("\n\n###### RUNNING DEMO FOR TYPE (1,1)")

market = Market([
    AgentCategory("buyer", [1,1,1,1,1]),
    AgentCategory("seller", [-1,-1,-1,-1,-0.5]),
])
print(budget_balanced_ascending_auction(market, [1,1]))


print("\n\n###### RUNNING EXPERIMENT FOR DEMO OF TYPE (1,1)")

ascending_auction_protocol.logger.setLevel(logging.ERROR)
prices.logger.setLevel(logging.ERROR)

results_file = "results/ascending_auction_demo_11.csv"
SBB_ASCENDING_STOCKS = "SBB Ascending Prices"

experiment(results_file,mcafee_trade_reduction, "McAfee Stock", (1, 1),
           value_ranges   = [(1,1),(-1,-1)],
           nums_of_agents = (5,5),
           num_of_iterations = 1
           )


experiment(results_file,budget_balanced_trade_reduction, "SBB External Competition Stock", (1, 1),
           value_ranges   = [(1,1),(-1,-1)],
           nums_of_agents = (5,5),
           num_of_iterations = 1
           )


experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices Stock", (1, 1),
           value_ranges   = [(1,1),(-1,-1)],
           nums_of_agents = (5,5),
           num_of_iterations = 1
           )


from functools import partial
mcafee_without_heuristic = partial(mcafee_trade_reduction,price_heuristic=False)

experiment(results_file,mcafee_without_heuristic, "McAfee Without Heuristic Stock", (1, 1),
           value_ranges   = [(1,1),(-1,-1)],
           nums_of_agents = (5,5),
           num_of_iterations = 1
           )

