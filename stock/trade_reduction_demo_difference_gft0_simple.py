#!python3

"""
Demonstration of a trade-reduction strongly-budget-balanced auction
for a multi-lateral market with buyers, mediators and sellers (recipe: 1,1,1)

Since:  2020-10

Author: Dvir Gilor
"""


from markets import Market
from agents import AgentCategory
import trade_reduction_protocol
from trade_reduction_protocol import budget_balanced_trade_reduction
import random
import logging
trade_reduction_protocol.logger.setLevel(logging.INFO)


def removeSeconds(prices, reduce_number):
    new_array = []
    for i in range(len(prices)):
        if i % reduce_number != 0:
            new_array.append(prices[i])
    return new_array

def randomArray(min, max, size):
    new_array = []
    for i in range(size):
        new_array.append(random.randint(min, max))
    print(new_array)
    return new_array

print("\n\n###### RUNNING EXAMPLE FROM THE PAPER FOR TYPE (1,2,3,4): buyers-sellers-mediators")
recipe = [1, 2]
with_count = 1
without_count = 1
with_gft = 1
without_gft = 1
reduce_number = 1
for reduce_number in range(2, 10000):

    buyers = randomArray(2, 20, 10)
    sellers = randomArray(-10, -1, 20)

    #
    # buyers = [135.9, 136.7999, 143.5499, 135.9, 136.7999, 143.5499, 144.0]
    # sellers = [-135.9, -136.7999, -143.5499, -18.95, -18.9, -17.95, -17.9, -17.7999, -17.7999, -17.2999, -17.0, -16.95, -16.7999, -15.15, -15.0, -15.0, -14.9, -14.2, -14.2, -14.1, -13.95]
    #
    # random.shuffle(buyers)
    # random.shuffle(sellers)
    #
    # buyers = removeSeconds(buyers, reduce_number)
    # sellers = removeSeconds(sellers, reduce_number)

    market = Market([
        AgentCategory("buyer",    buyers),
        AgentCategory("seller",   sellers),
    ])
    without_gft0 = budget_balanced_trade_reduction(market, recipe, False)
    with_gft0 = budget_balanced_trade_reduction(market, recipe, True)
    print(without_gft0)
    print(with_gft0)

    without_count = without_gft0.num_of_deals()
    with_count = with_gft0.num_of_deals()
    without_gft = without_gft0.gain_from_trade()
    with_gft = with_gft0.gain_from_trade()

    print('Compare: Without:', without_gft, "With:", with_gft)
    print('Compare: Without:', without_count, "With:", with_count)
    if without_count != with_count and with_gft != without_gft:
        print("Reached end")
        break
print("    buyers =", buyers)
print("    sellers =", sellers)


#
# print("\n\n###### SAME EXAMPLE WITH DIFFERENT ORDER: buyers-mediators-sellers")
# market = Market([
#     AgentCategory("buyer",    buyers),
#     AgentCategory("mediator", mediators),
#     AgentCategory("seller",   sellers),
# ])
# print(budget_balanced_trade_reduction(market, recipe))
#
#
# print("\n\n###### SAME EXAMPLE WITH DIFFERENT ORDER: sellers-buyers-mediators")
# market = Market([
#     AgentCategory("seller",   sellers),
#     AgentCategory("buyer",    buyers),
#     AgentCategory("mediator", mediators),
# ])
# print(budget_balanced_trade_reduction(market, recipe))
#
#
#
# print("\n\n###### SAME EXAMPLE WITH DIFFERENT ORDER: sellers-mediators-buyers")
# market = Market([
#     AgentCategory("seller",   sellers),
#     AgentCategory("mediator", mediators),
#     AgentCategory("buyer", buyers),
# ])
# print(budget_balanced_trade_reduction(market, recipe))
#
#
# print("\n\n###### SAME EXAMPLE WITH DIFFERENT ORDER: mediators-sellers-buyers")
# market = Market([
#     AgentCategory("mediator", mediators),
#     AgentCategory("seller",   sellers),
#     AgentCategory("buyer", buyers),
# ])
# print(budget_balanced_trade_reduction(market, recipe))
#
#
# print("\n\n###### SAME EXAMPLE WITH DIFFERENT ORDER: mediators-buyers-sellers")
# market = Market([
#     AgentCategory("mediator", mediators),
#     AgentCategory("buyer", buyers),
#     AgentCategory("seller",   sellers),
# ])
# print(budget_balanced_trade_reduction(market, recipe))
#
#
#
#
