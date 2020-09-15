#!python3

"""
class Market

Represents a multi-lateral market, that contains several agent categories.

See also: AgentCategory

Author: Erel Segal-Halevi
Since: 2019-08
"""

from agents import AgentCategory
from trade import TradeWithMaterialBalance

class Market:
    """
    Represents a market with several categories of traders,
    and several traders from each category.

    >>> market = Market([AgentCategory("buyer", [9, 7, 11, 5]), AgentCategory("seller",[-4,-6,-8,-2])])
    >>> str(market)
    'Traders: [buyer: [11, 9, 7, 5], seller: [-2, -4, -6, -8]]'
    """

    def __init__(self, categories:list):
        """
        :param categories: a list of k AgentCategory objects.
                           Each such object represents a set of traders
                           that belong to a single category.
        """
        self.categories = categories
        self.num_categories = len(categories)
        self.size_of_smallest_category =  min([len(c) for c in self.categories])


    def append_trader(self, category_index:int, value:float):
        """
        Append a trader to the given category in this market.
        The values in the category remain sorted.
        :param ps: a procurement-set - contains one value for each category.
        """
        self.categories[category_index].append(value)

    def append_PS(self, ps:list):
        """
        Append an entire procurement-set to the market.
        :param ps: a procurement-set - contains one value for each category.
        """
        if len(ps)!=len(self.categories):
            raise(ValueError("Market has {} categories but PS has {} values".format(len(self.categories),len(ps))))
        for i in range(len(ps)):
            self.append_trader(i, ps[i])

    def has_empty_category(self)->bool:
        return any([len(c)==0 for c in self.categories])

    def get_highest_agents(self, ps_recipe:list)->tuple:
        """
        Create a procurement-set from the r_i highest-value agents in each category i,
            where r_i = ps_recipe[i].

        :return a tuple with the values of the highest-valued agent/s in each category;
        if there are not enough agents in one of the categories, returns None.

        >>> market = Market([AgentCategory("buyer", [9, 7, 11, 5]), AgentCategory("seller",[-4,-6,-8,-2])])
        >>> market.get_highest_agents([1,1])
        (11, -2)
        >>> market.get_highest_agents([2,1])
        (11, 9, -2)
        >>> market.get_highest_agents([1,2])
        (11, -2, -4)
        >>> market.get_highest_agents([5,1])
        >>> market.get_highest_agents([1,5])
        """
        ps = []
        for i in range(self.num_categories):
            recipe_i = ps_recipe[i]
            category_i = self.categories[i]
            if len(category_i) < recipe_i:
                return None  # Category i is empty, so we cannot create any more procurement-sets.
            highest_i = category_i.highest_agent_values(recipe_i)
            ps += highest_i
        return tuple(ps)

    def remove_highest_agents(self, ps_recipe:list):
        """
        Remove, from each category i in the market,
        the r_i highest agents, where r_i = ps_recipe[i].
        """
        for i in range(self.num_categories):
            recipe_i = ps_recipe[i]
            category_i = self.categories[i]
            category_i.remove_highest_agents(recipe_i)


    # def remove_agents_below_prices(self, map_category_index_to_price:list):
    #     for category_index, category in enumerate(self.categories):
    #         if category.size()>0 and category.lowest_agent_value() <= map_category_index_to_price[category_index]:
    #             category.remove_lowest_agent()
    #             logger.info("{} after: {} agents remain,  {} PS supported".format(category.name, category.size(), integral_potential_ps(category_index)))



    def empty_agent_categories(self)->list:
        """
        Construct k empty categories, one for each category in the present market.
        :return:  a list of AgentCategory objects.
        """
        categories = [None] * self.num_categories
        for i in range(self.num_categories):
            categories[i] = AgentCategory(self.categories[i].name, [])
        return categories

    def optimal_trade(self, ps_recipe:list, max_iterations:int=2000, include_zero_gft_ps:bool=True)->tuple:
        """
        :param ps_recipe: a list that indicates the number of agents from each category that should be in each PS.
        For example: [1,2] means 1 agent from first category (e.g. one buyer) and 2 agents from second category (e.g. two sellers).
        :param include_zero_gft_ps: whether or not to include in the optimal trade procurement-sets with GFT = 0.

        :return: a list of procurement-sets, and a remaining market.
        Each PS should contain a single agent from each category.
        Each PS should have a positive gain-from-trade.
        The PS are ordered in ascending order of their GFT.

        >>> market2 = Market([AgentCategory("buyer", [9, 7, 11, 5]), AgentCategory("seller",[-4,-6,-8,-2])])
        >>> str(market2)
        'Traders: [buyer: [11, 9, 7, 5], seller: [-2, -4, -6, -8]]'

        >>> (trade,remaining_market)=market2.optimal_trade([1,1])
        >>> trade
        3 deals: [(7, -6), (9, -4), (11, -2)]
        >>> str(remaining_market)
        'Traders: [buyer: [5], seller: [-8]]'

        >>> (trade,remaining_market)=market2.optimal_trade([1,2])
        >>> trade
        1 deals: [(11, -2, -4)]
        >>> str(remaining_market)
        'Traders: [buyer: [9, 7, 5], seller: [-6, -8]]'

        >>> (trade,remaining_market)=market2.optimal_trade([2,1])
        >>> trade
        2 deals: [(7, 5, -4), (11, 9, -2)]
        >>> str(remaining_market)
        'Traders: [buyer: [], seller: [-6, -8]]'

        >>> market3 = Market([AgentCategory("buyer", [15, 12, 9, 6]),AgentCategory("seller",[-2,-5,-8,-11]),AgentCategory("mediator", [-1, -4, -7, -10])])
        >>> (trade,remaining_market)=market3.optimal_trade([1,1,1])
        >>> trade
        2 deals: [(12, -5, -4), (15, -2, -1)]

        >>> str(remaining_market)
        'Traders: [buyer: [9, 6], seller: [-8, -11], mediator: [-7, -10]]'
        """
        num_categories = self.num_categories
        if len(ps_recipe) != num_categories:
            raise ValueError(
                "There are {} categories but {} elements in the PS recipe".
                    format(num_categories, len(ps_recipe)))

        trade = []
        remaining_market = self.clone()
        for iteration in range(max_iterations):
            ps = remaining_market.get_highest_agents(ps_recipe)
            if ps is None:
                break      # Either there are not enough traders in one of the categories, or the GFT is negative, so we cannot create any more positive procurement-sets.
            gft = sum(ps)
            if gft < 0 or (gft == 0 and not include_zero_gft_ps):
                break

            trade.append(tuple(ps))
            remaining_market.remove_highest_agents(ps_recipe)
        trade.sort(key=lambda ps: sum(ps)) # sort in increasing order of GFT
        return (TradeWithMaterialBalance(trade), remaining_market)


    def best_containing_PS(self, category_index:int, value:float):
        """
        Find a procurement-set with the highest GFT that contains the given agent.
        :param category_index: the index of the category that this agent belongs to.
        :param value:          the value of this agent.
        :return:               a PS that contains the given agent plus agents from other categories
                                   (different than category_index),
                               such that the GFT of the given agent plus the other agents is highest.

        >>> market2 = Market([AgentCategory("buyer", [7, 5]), AgentCategory("seller", [-8, -10])])
        >>> market2.best_containing_PS(0, 9)
        (9, -8)
        >>> market2.best_containing_PS(1, -6)
        (7, -6)
        """
        best_PS = [None]*self.num_categories
        for i in range(self.num_categories):
            if i == category_index:
                best_PS[i] = value
            else:
                best_PS[i] = self.categories[i].highest_agent_value()
        return tuple(best_PS)


    def calculate_prices_by_external_competition(self, pivot_index:int, pivot_value:float, best_containing_PS:list)->list:
        """
        Determine the prices for the given procurement-set, based on the external competition found.
        :param ps: a procurement-set - contains one agent from each category.
        :return:   a list of prices - a price per agent. The sum of prices should be 0.
                   Returns None if no competition was found.
        """
        prices = [None]*self.num_categories
        for category_index in range(self.num_categories):
            if category_index==pivot_index:
                prices[category_index] = pivot_value - sum(best_containing_PS)
            else:
                prices[category_index] = best_containing_PS[category_index]
        prices = tuple(prices)
        return prices



    def __str__(self)->str:
        return "Traders: {}".format(self.categories)

    def clone(self):
        return Market([c.clone() for c in self.categories])



if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    market2 = Market([AgentCategory("buyer", [9, 7, 11, 5]), AgentCategory("seller", [-4, -6, -8, -2])])
    (trade, remaining_market) = market2.optimal_trade([1, 1])

