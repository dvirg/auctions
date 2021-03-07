#!python3

"""
function budget_balanced_trade_reduction_fixed
Implementation of a budget-balanced trade-reduction protocol for a multi-lateral market.

Author: Erel Segal-Halevi
Since:  2019-08
"""


from agents import AgentCategory
from markets import Market
from trade import TradeWithSinglePrice

import logging, sys
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.INFO)
# To enable tracing, set logger.setLevel(logging.INFO)

MAX_VALUE=100000000    # an upper bound (not necessarily tight) on the agents' values.


def convert_category_index(ps_recipe:list, pivot_index:int):
    for i in range(len(ps_recipe)):
        if pivot_index < ps_recipe[i]:
            return i
        else:
            pivot_index -= ps_recipe[i]
    return len(ps_recipe)-1


def budget_balanced_trade_reduction(market:Market, ps_recipe:list, including_gft_0:bool = True):
    """
    Calculate the trade and prices using generalized-trade-reduction.
    :param market:   contains a list of k categories, each containing several agents.
    :param ps_recipe:  a list of integers, one integer per category.
                       Each integer i represents the number of agents of category i
                       that should be in each procurement-set.
    :return: Trade object, representing the trade and prices.

    >>> market = Market([AgentCategory("seller", [-1, -2, -3, -4, -5, -7, -8, -10, -11]),AgentCategory("buyer", [17, 14, 13, 9, 6])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [2, 1]))
    Traders: [seller: [-1, -2, -3, -4, -5, -7, -8, -10, -11], buyer: [17, 14, 13, 9, 6]]
    seller: [-1, -2, -3, -4]: all 4 agents trade and pay -5
    buyer: [17, 14, 13]: random 2 out of 3 agents trade and pay 10.0

    >>> market = Market([AgentCategory("mediator", [-3, -4, -5, -6, -7, -8, -9, -10]),AgentCategory("seller", [-1, -2, -3, -4, -5, -6, -7, -8]),AgentCategory("buyer", [17, 16, 15, 14, 13, 12, 10, 6])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [2,3,2]))
    Traders: [mediator: [-3, -4, -5, -6, -7, -8, -9, -10], seller: [-1, -2, -3, -4, -5, -6, -7, -8], buyer: [17, 16, 15, 14, 13, 12, 10, 6]]
    mediator: [-3, -4]: all 2 agents trade and pay -5
    seller: [-1, -2, -3, -4, -5]: random 3 out of 5 agents trade and pay -5.333333333333333
    buyer: [17, 16, 15, 14]: random 2 out of 4 agents trade and pay 13


    >>> market = Market([AgentCategory("seller", [-2, -4, -6, -8, -10, -12, -14]),AgentCategory("buyer", [20, 18, 16, 9, 2, 1])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [2,3]))
    Traders: [seller: [-2, -4, -6, -8, -10, -12, -14], buyer: [20, 18, 16, 9, 2, 1]]
    seller: [-2, -4]: all 2 agents trade and pay -6
    buyer: [20, 18, 16, 9]: random 3 out of 4 agents trade and pay 4.0

    >>> # Multi trade
    >>> market = Market([AgentCategory("buyer", [17, 14, 13, 9, 6]),AgentCategory("seller", [-1, -2, -3, -4, -5, -7, -8, -10, -11])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1, 2]))
    Traders: [buyer: [17, 14, 13, 9, 6], seller: [-1, -2, -3, -4, -5, -7, -8, -10, -11]]
    buyer: [17, 14]: all 2 agents trade and pay 13
    seller: [-1, -2, -3, -4, -5]: random 4 out of 5 agents trade and pay -6.5

    >>> market = Market([AgentCategory("buyer", [17, 16, 15, 14, 13, 12, 10, 6]),AgentCategory("mediator", [-3, -4, -5, -6, -7, -8, -9, -10]),AgentCategory("seller", [-1, -2, -3, -4, -5, -6, -7, -8])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [2,2,3]))
    Traders: [buyer: [17, 16, 15, 14, 13, 12, 10, 6], mediator: [-3, -4, -5, -6, -7, -8, -9, -10], seller: [-1, -2, -3, -4, -5, -6, -7, -8]]
    buyer: [17, 16]: all 2 agents trade and pay 15
    mediator: [-3, -4]: all 2 agents trade and pay -5
    seller: [-1, -2, -3, -4, -5, -6]: random 3 out of 6 agents trade and pay -6.666666666666667

    >>> market = Market([AgentCategory("buyer", [20, 18, 16, 9, 2, 1]),AgentCategory("seller", [-2, -4, -6, -8, -10, -12, -14])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [3,2]))
    Traders: [buyer: [20, 18, 16, 9, 2, 1], seller: [-2, -4, -6, -8, -10, -12, -14]]
    buyer: [20, 18, 16, 9]: random 3 out of 4 agents trade and pay 6.666666666666667
    seller: [-2, -4, -6, -8]: random 2 out of 4 agents trade and pay -10

    >>> # Multi trade
    >>> market = Market([AgentCategory("seller", [-1, -2, -2, -3]),AgentCategory("buyer", [2, 2, 2, 3])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1, 1]))
    Traders: [seller: [-1, -2, -2, -3], buyer: [3, 2, 2, 2]]
    seller: [-1, -2, -2]: all 3 agents trade and pay -2.0
    buyer: [3, 2, 2]: all 3 agents trade and pay 2

    >>> # Multi trade
    >>> market = Market([AgentCategory("buyer", [2, 2, 2, 3]),AgentCategory("seller", [-1, -2, -2, -3])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1, 1]))
    Traders: [buyer: [3, 2, 2, 2], seller: [-1, -2, -2, -3]]
    buyer: [3, 2]: all 2 agents trade and pay 2
    seller: [-1, -2, -2]: random 2 out of 3 agents trade and pay -2.0

    >>> market = Market([AgentCategory("buyer", [17, 16, 15, 14, 13, 12, 10, 6]),AgentCategory("mediator", [-3, -4, -5, -6, -7, -8, -9, -10]),AgentCategory("seller", [-1, -2, -3, -4, -5, -6, -7, -8])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [2,2,3]))
    Traders: [buyer: [17, 16, 15, 14, 13, 12, 10, 6], mediator: [-3, -4, -5, -6, -7, -8, -9, -10], seller: [-1, -2, -3, -4, -5, -6, -7, -8]]
    buyer: [17, 16]: all 2 agents trade and pay 15
    mediator: [-3, -4]: all 2 agents trade and pay -5
    seller: [-1, -2, -3, -4, -5, -6]: random 3 out of 6 agents trade and pay -6.666666666666667

    >>> # ONE BUYER, ONE SELLER
    >>> market = Market([AgentCategory("buyer", [9.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("seller", [-4.]), AgentCategory("buyer", [9.,8.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [seller: [-4.0], buyer: [9.0, 8.0]]
    seller: [-4.0]: all 1 agents trade and pay -8.0
    buyer: [9.0]: all 1 agents trade and pay 8.0

    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [seller: [-3.0, -4.0], buyer: [9.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.]), AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0], seller: [-3.0, -4.0]]
    buyer: [9.0]: all 1 agents trade and pay 4.0
    seller: [-3.0]: all 1 agents trade and pay -4.0

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-3.0, -4.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -8.0

    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.,8.])])
    >>> print(budget_balanced_trade_reduction(market, [1,1]))
    seller: [-3.0]: all 1 agents trade and pay -4.0
    buyer: [9.0, 8.0]: random 1 out of 2 agents trade and pay 4.0

    >>> # ALL POSITIVE VALUES
    >>> market = Market([AgentCategory("buyer1", [4.,3.]), AgentCategory("buyer2", [9.,8.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [buyer1: [4.0, 3.0], buyer2: [9.0, 8.0]]
    buyer1: [4.0]: all 1 agents trade and pay 3.0
    buyer2: [9.0, 8.0]: random 1 out of 2 agents trade and pay -3.0

    >>> # ALL NEGATIVE VALUES
    >>> market = Market([AgentCategory("seller1", [-4.,-3.]), AgentCategory("seller2", [-9.,-8.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1]))
    Traders: [seller1: [-3.0, -4.0], seller2: [-8.0, -9.0]]
    No trade

    >>>
    >>> # ONE BUYER, ONE SELLER, ONE MEDIATOR
    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [seller: [-3.0, -4.0], buyer: [9.0, 8.0], mediator: [-1.0, -2.0]]
    seller: [-3.0]: all 1 agents trade and pay -4.0
    buyer: [9.0]: all 1 agents trade and pay 8.0
    mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -4.0

    >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-10.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-3.0, -4.0, -10.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    mediator: [-1.0]: all 1 agents trade and pay -2.0
    seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -6.0

    >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-5.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-3.0, -4.0, -5.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -3.0
    seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -5.0

    >>> market = Market([AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.]), AgentCategory("seller", [-4.,-3.,-2.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0], mediator: [-1.0, -2.0], seller: [-2.0, -3.0, -4.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -4.0
    seller: [-2.0, -3.0]: random 1 out of 2 agents trade and pay -4.0

    >>> market = Market([AgentCategory("buyer", [9.,8.,7.]), AgentCategory("mediator", [-1.,-2.,-3.]), AgentCategory("seller", [-4.,-3.,-2.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0, 7.0], mediator: [-1.0, -2.0, -3.0], seller: [-2.0, -3.0, -4.0]]
    buyer: [9.0, 8.0]: all 2 agents trade and pay 7.0
    mediator: [-1.0, -2.0]: all 2 agents trade and pay -3.0
    seller: [-2.0, -3.0, -4.0]: random 2 out of 3 agents trade and pay -4.0

    >>> market = Market([AgentCategory("buyer", [9.,8.,4.]), AgentCategory("mediator", [-1.,-2.,-3.]), AgentCategory("seller", [-4.,-3.,-2.])])
    >>> print(market); print(budget_balanced_trade_reduction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0, 4.0], mediator: [-1.0, -2.0, -3.0], seller: [-2.0, -3.0, -4.0]]
    buyer: [9.0, 8.0]: all 2 agents trade and pay 7.0
    mediator: [-1.0, -2.0]: all 2 agents trade and pay -3.0
    seller: [-2.0, -3.0]: all 2 agents trade and pay -4.0

    """
    if len(ps_recipe) != market.num_categories:
        raise ValueError(
            "There are {} categories but {} elements in the PS recipe".
                format(market.num_categories, len(ps_recipe)))

    logger.info("\n#### Budget-Balanced Trade Reduction\n")
    logger.info(market)
    (optimal_trade, remaining_market) = market.optimal_trade(ps_recipe)
    if len(optimal_trade.procurement_sets) == 0:
        return TradeWithSinglePrice(market.empty_agent_categories(), ps_recipe, [0] * len(ps_recipe))

    highest_negative_ps = remaining_market.get_highest_agents(ps_recipe)
    list_ps_to_compete = optimal_trade.procurement_sets
    if highest_negative_ps:
        list_ps_to_compete = [highest_negative_ps] + list_ps_to_compete
        remaining_market.remove_highest_agents(ps_recipe)

    for category in remaining_market.categories:
        if len(category)==0:
            category.append(-MAX_VALUE)
    logger.info("Optimal trade including one highest non-positive trade, by increasing GFT: {}".format(optimal_trade))
    logger.info("Remaining market: {}".format(remaining_market))

    actual_traders = market.empty_agent_categories()

    # Preparing the order of pivot index for trade_reduction
    pivot_indexes = []
    pivot_index_to_category_index = []
    total = 0
    index = 0
    for agent in ps_recipe:
        pivot_indexes += [total+i for i in range(agent-1, -1, -1)]
        pivot_index_to_category_index += [index for _ in range(agent)]
        total += agent
        index += 1
    found_external = False

    latest_prices = None
    for ps in list_ps_to_compete:
        ps = list(ps)
        if latest_prices is None:
            logger.info("\nCalculating prices for PS {}:".format(ps))
            for pivot_index in pivot_indexes:
                pivot_value = ps[pivot_index]
                if found_external:
                    actual_traders[pivot_index_to_category_index[pivot_index]].append(pivot_value)
                    continue
                pivot_category_index = convert_category_index(ps_recipe, pivot_index)
                pivot_category = market.categories[pivot_category_index]
                logger.info("  Looking for external competition to {} with value {}:".
                            format(pivot_category.name, pivot_value))
                best_containing_PS = remaining_market.best_containing_PS(pivot_category_index, pivot_value)
                best_containing_GFT = sum([best_containing_PS[i]*ps_recipe[i] for i in range(len(best_containing_PS))])
                if best_containing_GFT > 0 or (including_gft_0 and best_containing_GFT == 0):  # EXTERNAL COMPETITION - KEEP TRADER
                    found_external = True
                    logger.info("    best PS is {},{} with GFT {}. It is positive so it is an external competition.".
                                format(best_containing_PS, ps_recipe, best_containing_GFT))
                    prices = market.calculate_prices_by_external_competition(pivot_category_index, pivot_value, best_containing_PS, ps_recipe)
                    logger.info("    Prices are {}".format(prices))
                    latest_prices = prices
                    actual_traders[pivot_index_to_category_index[pivot_index]].append(pivot_value)
                    #for i in range(len(prices)):
                    #    agent_prices = market.categories[i].values
                    #    for value in agent_prices:
                    #        #TODO: should we check if value is greater or equal?
                    #        if value >= prices[i]:
                    #            actual_traders[i].append(value)
                    #break  # done with current PS - move to next PS
                else:  # NO EXTERNAL COMPETITION - REMOVE TRADER
                    logger.info("    Best PS is {},{} with GFT {}. It is negative so it is not an external competition.".
                                format(best_containing_PS, ps_recipe, best_containing_GFT))
                    logger.info("    Remove {} {} from trade and add to remaining market".
                                format(pivot_category.name, pivot_value))
                    ps[pivot_index] = None
                    remaining_market.append_trader(pivot_category_index, pivot_value)
                    logger.info("    Remaining market is now: {}".format(remaining_market))
        else:
            logger.info("\nPrices for PS {} are {}".format(ps, latest_prices))
            #print(pivot_index_to_category_index)
            for pivot_index in pivot_indexes:
                pivot_value = ps[pivot_index]
                actual_traders[pivot_index_to_category_index[pivot_index]].append(pivot_value)
    logger.info("\n")
    result = TradeWithSinglePrice(actual_traders, ps_recipe, latest_prices)
    logger.info(result)
    return result


if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
