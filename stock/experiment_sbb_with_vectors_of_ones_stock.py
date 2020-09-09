#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.

Since:  2019-11
Author: Erel Segal-Halevi

"""

from experiment_stock import experiment

from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
import sys

results_file = "results/experiment_sbb_with_vectors_of_ones_stock.csv"

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", recipe=4*(1,))

