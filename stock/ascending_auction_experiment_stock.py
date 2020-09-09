#!python3

"""
Perform a simulation experiment with the ascending auction, similar to the one described by McAfee (1992), Table I (page 448).

Since:  2019-11
Author: Erel Segal-Halevi
"""

from experiment_stock import  experiment

from ascending_auction_protocol import budget_balanced_ascending_auction
import sys

results_file = "results/ascending_auction_stock.csv"

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (1, 1))

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (1, 1, 1))

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (1, 1, 1, 1))

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (2, 1))

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (1, 2))

experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", (2, 1, 1))

