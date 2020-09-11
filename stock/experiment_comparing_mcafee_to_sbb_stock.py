#!python3

"""
Simulation experiment for our AAAI 2020 paper, recipe (1,1).
Comparing McAfee's double auction to our SBB auctions.
With using stock market real data.

Since:  2020-08
Author: Dvir Gilor

"""

from experiment import experiment

from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
from experiment_stock import experiment

from functools import partial
mcafee_without_heuristic = partial(mcafee_trade_reduction,price_heuristic=False)

recipe = (1,1)

results_file = "results/experiment_comparing_mcafee_to_sbb_stock.csv"

experiment(results_file,mcafee_trade_reduction, "McAfee Stock", recipe=recipe)

experiment(results_file,budget_balanced_trade_reduction, "SBB External Competition Stock", recipe=recipe)

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices Stock", recipe=recipe)

experiment(results_file,mcafee_without_heuristic, "McAfee Without Heuristic Stock", recipe=recipe)
