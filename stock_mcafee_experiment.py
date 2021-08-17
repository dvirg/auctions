#!python3

"""
The simulation experiment described by McAfee (1992), Table I (page 448).
With the real stock data prices.

Since:  2020-09

Author: Dvir Gilor
"""

from mcafee_protocol import mcafee_trade_reduction
from experiment_stock import experiment
from functools import partial

RESULT_FILE = "results/mcafee_experiment_stock.csv"

print("### Original McAfee: ")

experiment(RESULT_FILE, mcafee_trade_reduction, "McAfee", recipe=(1,1))

print("### McAfee without price-heuristic: ")
mcafee_without_heuristic = partial(mcafee_trade_reduction,price_heuristic=False)
experiment(RESULT_FILE, mcafee_without_heuristic, "McAfee Without Heuristic Stocks", recipe=(1,1))
