#!python3

"""
The direct implementation of the McAfee (1992) trade-reduction protocol for a bi-lateral market.
This protocol may have a budget surplus.

Author: Erel Segal-Halevi
Since:  2019-11
"""


from agents import AgentCategory
from markets import Market
from trade import TradeWithSinglePrice

import logging, sys
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
# To enable tracing, set logger.setLevel(logging.INFO)

MAX_VALUE=100000000    # an upper bound (not necessarily tight) on the agents' values.


def is_price_good_for_ps(price:float, ps:list)->bool:
    """
    Decides if the given price can be used as the trading price for the given PS.

    >>> is_price_good_for_ps(5, [9, -3])
    True
    >>> is_price_good_for_ps(5, [9, -7])
    False
    >>> is_price_good_for_ps(5, [4, -3])
    False
    """
    for i in range(len(ps)):
        if ps[i] >= 0 and price > ps[i]:
            return False   # price too high for a buyer
        elif ps[i] <= 0 and -price > ps[i]:
            return False   # price too low for a seller
    return True



def mcafee_trade_reduction(market:Market, ps_recipe:list, price_heuristic=True):
    """
    Calculate the trade and prices using generalized-trade-reduction.
    :param market:   contains a list of k categories, each containing several agents.
    :param ps_recipe:  a list of integers, one integer per category.
                       Each integer i represents the number of agents of category i
                       that should be in each procurement-set.
    :param price_heuristic: whether to use the heuristic of setting the price to (s_{k+1)+b_{k+1})/2.
                            Default is true, as in the original paper.
    :return: Trade object, representing the trade and prices.

    >>> # ONE BUYER, ONE SELLER
    >>> market = Market([AgentCategory("buyer", [9.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("seller", [-4.]), AgentCategory("buyer", [9.,8.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [seller: [-4.0], buyer: [9.0, 8.0]]
    No trade

    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [seller: [-3.0, -4.0], buyer: [9.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.]), AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0], seller: [-3.0, -4.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(mcafee_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-3.0, -4.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    seller: [-3.0]: all 1 agents trade and pay -4.0

    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.,8.])])
    >>> print(mcafee_trade_reduction(market, [1,1]))
    seller: [-3.0]: all 1 agents trade and pay -4.0
    buyer: [9.0]: all 1 agents trade and pay 8.0

    >>> market = Market([AgentCategory("seller", [-8.,-3.]), AgentCategory("buyer", [9.,4.])])
    >>> print(mcafee_trade_reduction(market, [1,1]))
    seller: [-3.0]: all 1 agents trade and pay -6.0
    buyer: [9.0]: all 1 agents trade and pay 6.0

    #
    # >>>
    # >>> # ONE BUYER, ONE SELLER, ONE MEDIATOR
    # >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [seller: [-3.0, -4.0], buyer: [9.0, 8.0], mediator: [-1.0, -2.0]]
    # seller: [-3.0]: all 1 agents trade and pay -4.0
    # buyer: [9.0]: all 1 agents trade and pay 8.0
    # mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -4.0
    #
    # >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-10.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-3.0, -4.0, -10.0]]
    # buyer: [9.0]: all 1 agents trade and pay 8.0
    # mediator: [-1.0]: all 1 agents trade and pay -2.0
    # seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -6.0
    #
    # >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-5.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-3.0, -4.0, -5.0]]
    # buyer: [9.0]: all 1 agents trade and pay 8.0
    # mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -3.0
    # seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -5.0
    #
    # >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-2.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-2.0, -3.0, -4.0]]
    # buyer: [9.0]: all 1 agents trade and pay 8.0
    # mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -4.0
    # seller: [-2.0, -3.0]: random 1 out of 2 agents trade and pay -4.0
    #
    # >>> market = Market([AgentCategory("buyer", [9.,8.,7.]), AgentCategory("mediator", [-1.,-2.,-3.]), AgentCategory("seller", [-4.,-3.,-2.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [buyer: [9.0, 8.0, 7.0], mediator: [-1.0, -2.0, -3.0], seller: [-2.0, -3.0, -4.0]]
    # buyer: [9.0, 8.0]: all 2 agents trade and pay 7.0
    # mediator: [-1.0, -2.0]: all 2 agents trade and pay -3.0
    # seller: [-2.0, -3.0]: all 2 agents trade and pay -4.0
    #
    # >>> market = Market([AgentCategory("buyer", [9.,8.,4.]), AgentCategory("mediator", [-1.,-2.,-3.]), AgentCategory("seller", [-4.,-3.,-2.])])
    # >>> print(market); print(mcafee_trade_reduction(market, [1,1,1]))
    # Traders: [buyer: [9.0, 8.0, 4.0], mediator: [-1.0, -2.0, -3.0], seller: [-2.0, -3.0, -4.0]]
    # buyer: [9.0, 8.0]: all 2 agents trade and pay 7.0
    # mediator: [-1.0, -2.0]: all 2 agents trade and pay -3.0
    # seller: [-2.0, -3.0]: all 2 agents trade and pay -4.0

    """
    if len(ps_recipe) != market.num_categories:
        raise ValueError(
            "There are {} categories but {} elements in the PS recipe".
                format(market.num_categories, len(ps_recipe)))

    if any(r!=1 for r in ps_recipe):
        raise ValueError("Currently, the trade-reduction protocol supports only recipes of ones; {} was given".format(ps_recipe))

    logger.info("\n#### McAfee Trade Reduction\n")
    logger.info(market)
    (optimal_trade, remaining_market) = market.optimal_trade(ps_recipe)
    for category in remaining_market.categories:
        if len(category)==0:
            category.append(-MAX_VALUE)
    logger.info("Optimal trade, by increasing GFT: {}".format(optimal_trade))
    first_negative_ps = remaining_market.get_highest_agents(ps_recipe)
    if price_heuristic:
        price_candidate = sum([abs(x) for x in first_negative_ps]) / len(first_negative_ps)
        logger.info("First negative PS: {}, candidate price: {}".format(first_negative_ps, price_candidate))
    actual_traders = market.empty_agent_categories()

    if optimal_trade.num_of_deals()>0:
        last_positive_ps = optimal_trade.procurement_sets[0]

        if price_heuristic and is_price_good_for_ps(price_candidate, last_positive_ps):
            # All optimal traders trade in the candidate price - no reduction
            prices = [price_candidate * (-1 if last_positive_ps[i]<0 else +1)
                      for i in range(market.num_categories)]

        else:
            # Trade reduction
            del optimal_trade.procurement_sets[0]
            prices = last_positive_ps

        for ps in optimal_trade.procurement_sets:
            for i in range(market.num_categories):
                if ps[i] is not None:
                    actual_traders[i].append(ps[i])
    else:
        prices = [0 for i in range(market.num_categories)]

    logger.info("\n")
    return TradeWithSinglePrice(actual_traders, ps_recipe, prices)


if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
