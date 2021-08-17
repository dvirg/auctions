#!python3

"""
Additional examples of a multiple-clock strongly-budget-balanced ascending auction.

Author: Dvir Gilor
Since:  2020-11
"""

from markets import Market
from agents import AgentCategory
import ascending_auction_protocol
from ascending_auction_protocol import budget_balanced_ascending_auction

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)

print("\n\n###### RUNNING EXAMPLE 3 FROM THE PAPER FOR TYPE (1,4)")


buyers = [33.375, 44.8, 52.72]
sellers = [-11.2, -11.2, -11.2, -11.2, -11.2, -3.1406, -2.6875, -0.1523, -0.1445]

buyers = [1, 44.4, 50]
sellers = [-11.1, -11.1, -11.1, -11.1, -11.1, -1, -1, -1, -1]

# buyers.sort()
# sellers.sort()
# print("buyers =", buyers)
# print("sellers =", sellers)

buyers = [price for price in buyers]
sellers = [price for price in sellers]

market = Market([
    AgentCategory("buyer", buyers),
    AgentCategory("seller",   sellers),
])
auction_trade = budget_balanced_ascending_auction(market, [1,4])
print(auction_trade)
(optimal_trade,_) = market.optimal_trade([1,4])
auction_trade_num_of_deals = auction_trade.num_of_deals()
optimal_trade_num_of_deals = optimal_trade.num_of_deals()
print("Actual:", auction_trade_num_of_deals)
print("Optimal:", optimal_trade_num_of_deals)
print(len(buyers), ",", len(sellers))
print("max buyer: ", max(buyers), ", min buyer: ", min(buyers), ", max seller: ", max(sellers), ", min seller: ", min(sellers))

# print("buyers =", buyers)
# print("sellers =", sellers)
