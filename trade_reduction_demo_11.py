#!python3

"""
Demonstration of a trade-reduction strongly-budget-balanced auction
for a multi-lateral market with buyers, mediators and sellers (recipe: 1,1,1)

Since:  2019-08

Author: Erel Segal-Halevi
"""


from markets import Market
from agents import AgentCategory
import trade_reduction_protocol
from trade_reduction_protocol import budget_balanced_trade_reduction

import logging
trade_reduction_protocol.logger.setLevel(logging.INFO)

print("\n\n###### EXAMPLE OF PS with GFT=0")

market = Market([
    AgentCategory("buyer", [1, 1, 1, 1, 1]),
    AgentCategory("seller", [-1, -1, -1, -1, -1]),
])

print(budget_balanced_trade_reduction(market, [1,1]))

