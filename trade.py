#!python3


"""
class TradeWithSinglePrice

Represents a set of deals done in a multi-lateral market.

See also: Market

Author: Erel Segal-Halevi
Since: 2019-08
"""


import math
from agents import AgentCategory
from typing import *

class Trade:
    """
    An abstract base class.
    Represents a set of deals done in a market.
    This may be the output of an auction mechanism, or an algorithm for computing optimal trade.
    """

    def num_of_deals(self) -> int:
        """
        :return: the number of deals done in this Trade.
        """
        pass

    def path_counters(self) -> Any:
        """
        :return: count of deals on each category (k_g).
        """
        pass

    def gain_from_trade(self)->float:
        """
        :return: the expected gain-from-trade resulting from doing the deals in this Trade.
        """
        pass




class TradeWithMaterialBalance (Trade):
    """
    A materially-balanced trade - a whole number of deals  done in the market.
    Represented by a list of tuples, where each tuple represents the valuations of agents in a particular deal.

    This is the output of an algorithm for finding the optimal trade.

    >>> t = TradeWithMaterialBalance([(7,-1),(6,-3),(5,-4)])
    >>> t
    3 deals: [(7, -1), (6, -3), (5, -4)]
    >>> t.num_of_deals()
    3
    >>> t.gain_from_trade()
    10
    """
    def __init__(self, procurement_sets:list):
        self.procurement_sets = procurement_sets

    def num_of_deals(self):
        return len(self.procurement_sets)

    def gain_from_trade(self):
        return sum([sum(ps) for ps in self.procurement_sets])

    def __repr__(self):
        return "{} deals: {}".format(self.num_of_deals(), self.procurement_sets)



class TradeWithSinglePrice (Trade):
    """
    Represents a set of agents trading in the market,
    assuming there is a single price-vector (one price per agent-category).

    This is the output of an auction mechanisms.

    self.categories: a vector of k AgentCategory objects.
    self.prices:     a vector of k floats - one  per category - representing the price paid by traders of that category.
    self.ps_recipe:  a vector of k integers - one per category - representing the number of traders from this category in each PS.

    >>> t = TradeWithSinglePrice([AgentCategory("buyer", [7,4,2]), AgentCategory("seller",[-1,-3,-5])], [1,1], [2,-1])
    >>> t
    buyer: [7, 4, 2]: all 3 agents trade and pay 2
    seller: [-1, -3, -5]: all 3 agents trade and pay -1
    >>> t.num_of_deals()
    3
    >>> t.gain_from_trade(including_auctioneer=True)
    4.0
    >>> t.gain_from_trade(including_auctioneer=False)
    1.0
    >>> t = TradeWithSinglePrice([AgentCategory("buyer", [7,4,3,2]), AgentCategory("seller",[-1,-3,-5])], [1,1], [1,-1])
    >>> t
    buyer: [7, 4, 3, 2]: random 3 out of 4 agents trade and pay 1
    seller: [-1, -3, -5]: all 3 agents trade and pay -1
    >>> t.gain_from_trade(including_auctioneer=True)
    3.0
    >>> t.gain_from_trade(including_auctioneer=False)
    3.0
    """
    def __init__(self, categories:List[AgentCategory], ps_recipe:List[int], prices:List[float]):
        self.categories = categories
        self.num_categories = len(categories)
        self.prices = prices
        self.ps_recipe = ps_recipe
        self.num_of_deals_cache = min([math.floor(category.size() / count)
             for (category, count) in zip(self.categories, self.ps_recipe)
             if count > 0])

    def num_of_deals(self):
        return self.num_of_deals_cache

    def gain_from_trade(self, including_auctioneer=True):
        """
        Calculate the total gain-from-trade.
        :param including_auctioneer:  If true, the result includes the profit of the auctioneer.
        If false, the result includes only the profit of the traders.
        This may be smaller when the auction has a surplus, or larger when the auction has a deficit.
        :return:
        """
        if self.num_of_deals_cache==0:
            return 0
        gft = 0
        for i in range(self.num_categories):
            category = self.categories[i]
            agents_per_deal = self.ps_recipe[i]
            participating_agents_in_category = agents_per_deal*self.num_of_deals_cache
            probability_to_participate_in_trade = participating_agents_in_category/len(category.values)
            price_per_agent_per_deal = self.prices[i]
            gft += sum(category.values)*probability_to_participate_in_trade
            if not including_auctioneer:
                gft -= price_per_agent_per_deal*participating_agents_in_category
        return gft

    def __repr__(self):
        if self.num_of_deals_cache==0:
            return "No trade"
        s = ""
        for category_index in range(self.num_categories):
            count_in_recipe = self.ps_recipe[category_index]
            if count_in_recipe>0:
                category = self.categories[category_index]
                price = self.prices[category_index]
                required_agents = count_in_recipe*self.num_of_deals_cache
                existing_agents = len(category)
                if existing_agents == required_agents:
                    s += "{}: all {} agents trade and pay {}\n".format(category, existing_agents, price)
                else:   # existing_agents > required_agents
                    s += "{}: random {} out of {} agents trade and pay {}\n".format(category, required_agents, existing_agents, price)
        return s.rstrip()



if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))