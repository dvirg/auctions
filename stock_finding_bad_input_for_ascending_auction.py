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
import random

import logging
ascending_auction_protocol.logger.setLevel(logging.INFO)

def removeSeconds(prices, reduce_number):
    new_array = []
    for i in range(len(prices)):
        if i % reduce_number != 0:
            new_array.append(prices[i])
    return new_array

print("\n\n###### RUNNING EXAMPLE 3 FROM THE PAPER FOR TYPE (1,4)")



auction_trade_num_of_deals = 1
optimal_trade_num_of_deals = 2
reduce_number = 1
while auction_trade_num_of_deals <= optimal_trade_num_of_deals and reduce_number < 10:
    buyers = [52.72, 44.8, 33.375]
    sellers = [-0.1523, -0.1445, -11.2, -11.2, -3.1406, -11.2, -11.2, -2.6875, -11.2]


    random.shuffle(buyers)
    random.shuffle(sellers)

    reduce_number += 1
    print(reduce_number)
    buyers = removeSeconds(buyers, reduce_number)
    sellers = removeSeconds(sellers, reduce_number)


    # buyers1 = [4]*10 + [8]*20 + [12]*30
    # sellers1 = [-2]*40 + [-2]*80 + [-3]*120

    market = Market([
        AgentCategory("buyer", buyers),
        AgentCategory("seller",   sellers),
    ])
    auction_trade = budget_balanced_ascending_auction(market, [1,4])
    (optimal_trade,_) = market.optimal_trade([1,4])
    auction_trade_num_of_deals = auction_trade.num_of_deals()
    optimal_trade_num_of_deals = optimal_trade.num_of_deals()
    print(auction_trade_num_of_deals)
    print("Optimal:", optimal_trade_num_of_deals)
    # print(len(buyers), ",", len(sellers))
    # print("max buyer: ", max(buyers), ", min buyer: ", min(buyers), ", max seller: ", max(sellers), ", min seller: ", min(sellers))
# buyers.sort()
# sellers.sort()
print("buyers =", buyers)
print("sellers =", sellers)
