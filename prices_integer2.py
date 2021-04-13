#!python3

"""
Defines classes related to price-vectors.

Author: Erel Segal-Halevi
Since:  2019-12
"""

import logging, sys
from typing import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
# To enable tracing, set logger.setLevel(logging.INFO)


def dot(xx:list,yy:list):
    """
    Dot product of two lists.
    >>> dot([1,2,3],[4,5,6])
    32
    """
    return sum([x*y for (x,y) in zip(xx,yy)])

from enum import Enum
class PriceStatus(Enum):
    STOPPED_AT_AGENT_VALUE = 1
    STOPPED_AT_ZERO_SUM = 2


class AscendingPriceVector:
    """
    Represents a vector of prices - one price for each category of agents.
    The vector is used in ascending-prices auctions: the price can be increased until the price-sum hits zero.
    """
    def __init__(self, ps_recipe:list, initial_price):
        self.num_categories = len(ps_recipe)
        self.ps_recipe = ps_recipe
        self.prices = initial_price if isinstance(initial_price,list) else [initial_price] * self.num_categories
        self.status = None  # status of the latest price-increase operation. Of type PriceStatus.

    def __getitem__(self, category_index:int):
        return self.prices[category_index]

    def __setitem__(self, category_index:int, new_price:float):
        self.prices[category_index] = new_price

    def price_sum(self):
        return dot(self.prices, self.ps_recipe)

    def price_sum_without_category(self, category_index:int):
        return self.price_sum() - self.ps_recipe[category_index]*self.prices[category_index]

    def price_sum_after_increase(self, category_index:int, new_price:float):
        """
        :return: the sum of prices after a hypothetical increase of the price in category_index to new_price.
        >>> p = AscendingPriceVector([1, 1, 0, 0], -1000)
        >>> p.price_sum_after_increase(0, 10)
        -990
        >>> p = AscendingPriceVector([1, 0, 1, 1], -1000)
        >>> p.price_sum_after_increase(0, 10)
        -1990
        """
        return self.price_sum_without_category(category_index) + self.ps_recipe[category_index]*new_price

    def increase_price_up_to_balance(self, category_index:int, new_price:float, description:str, sum_upper_bound:float=0):
        """
        Increase the price of the given agent-category to the given value.
        BUT, if the sum of prices crosses zero, the price will be increased only
        to the point where the sum is zero, and the status will be changed to STOPPED_AT_ZERO_SUM.
        :param category_index: index of price to increase.
        :param new_price: the target price.
        :param description: a textual description for logging (e.g. category name).
        :param sum_upper_bound: an upper bound to the price-sum; the increase stops when the sum hits this bound (default is 0).

        >>> # Simple recipe
        >>> p = AscendingPriceVector([1, 1], -1000)
        >>> p.increase_price_up_to_balance(0, 10., "buyer")
        >>> str(p.status)
        'PriceStatus.STOPPED_AT_AGENT_VALUE'
        >>> p.increase_price_up_to_balance(1, -100., "seller")
        >>> str(p.status), p.price_sum()
        ('PriceStatus.STOPPED_AT_AGENT_VALUE', -90.0)
        >>> p.increase_price_up_to_balance(0, 90., "buyer")
        >>> str(p.status), p.price_sum()
        ('PriceStatus.STOPPED_AT_AGENT_VALUE', -10.0)
        >>> p.increase_price_up_to_balance(1, -80., "seller")
        >>> str(p.status), p.price_sum(), p[1]
        ('PriceStatus.STOPPED_AT_ZERO_SUM', 0.0, -90.0)

        >>> # More complex recipe
        >>> p = AscendingPriceVector([2, 1, 0], -1000)
        >>> p.increase_price_up_to_balance(0, 10., "buyer")
        >>> p.status
        <PriceStatus.STOPPED_AT_AGENT_VALUE: 1>
        >>> p.increase_price_up_to_balance(1, -100., "seller")
        >>> str(p.status), p.price_sum()
        ('PriceStatus.STOPPED_AT_AGENT_VALUE', -80.0)
        >>> p.increase_price_up_to_balance(2, 1000., "watcher")
        >>> str(p.status), p.price_sum()
        ('PriceStatus.STOPPED_AT_AGENT_VALUE', -80.0)
        >>> p.increase_price_up_to_balance(0, 60., "buyer")
        >>> str(p.status), p.price_sum(), p[0]
        ('PriceStatus.STOPPED_AT_ZERO_SUM', 0.0, 50.0)

        """
        category_count_in_recipe = self.ps_recipe[category_index]
        sum_without_category = self.price_sum_without_category(category_index)
        new_sum = sum_without_category + category_count_in_recipe*new_price
        if new_sum >= sum_upper_bound:
            fixed_new_price = (sum_upper_bound - sum_without_category) / category_count_in_recipe
            logger.info("{}: while increasing price towards {}, stopped at {} where the price-sum crossed {}".format(description, new_price, fixed_new_price, sum_upper_bound))
            self.prices[category_index] = fixed_new_price
            self.status = PriceStatus.STOPPED_AT_ZERO_SUM
        else:
            logger.info("{}: price increases to {}".format(description, new_price))
            self.prices[category_index] = new_price
            self.status = PriceStatus.STOPPED_AT_AGENT_VALUE

    def __str__(self):
        return self.prices.__str__()


class SimultaneousAscendingPriceVectors:
    """
    Represents a price-vector that can increase several prices simultaneously.

    >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
    >>> str(pv)
    '[-10000.0, -20000.0, -10000.0, -10000.0] None'
    """
    def __init__(self, ps_recipes: List[List[int]], initial_price_sum:float):
        if len(ps_recipes)==0:
            raise ValueError("Empty list of recipes")

        num_categories = len(ps_recipes[0])
        for ps_recipe in ps_recipes:
            if len(ps_recipe) != num_categories:
                raise ValueError("Different category counts: {} vs {}".format(num_categories, len(ps_recipe)))
        self.num_categories = num_categories

        initial_prices = calculate_initial_prices(ps_recipes, initial_price_sum)

        self.ps_recipes = ps_recipes
        self.vector = AscendingPriceVector(ps_recipes[0], initial_prices)
        # vectors = []
        # for ps_recipe in ps_recipes:
        #     vectors.append(AscendingPriceVector(ps_recipe, initial_prices))
        # self.vectors = vectors
        # self.vector  = vectors[0]
        self.status = None  # status of the latest price-increase operation

    def price_sum(self):
        return self.vector.price_sum()

    def map_category_index_to_price(self):
        """
        >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
        >>> pv.map_category_index_to_price()
        [-10000.0, -20000.0, -10000.0, -10000.0]
        >>> pv.increase_prices ([(1,10,"seller"), (2,10,"half-seller-A")])
        >>> pv.map_category_index_to_price()[2]
        10.0
        >>> pv.increase_prices ([(1,10,"seller"), (3,10,"half-seller-B")])
        >>> pv.map_category_index_to_price()[1]
        10.0
        """
        return self.vector.prices

    # def __getitem__(self, vector_index:int):
    #     return self.vectors[vector_index]

    def increase_prices(self, increases:List[Tuple[int,float,str]], sum_upper_bound:float=0):
        """
        Simultaneously increase the prices of all vectors, keeping their sum equal.
        :param increases: a list of tuples; each tuple contains arguments to the increase_prices method of AscendingPriceVector:
            (category_index, target_price, description)

        There must be exactly one increase per recipe.
        This guarantees that the sum in all recipes remains equal.

        >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
        >>> str(pv)
        '[-10000.0, -20000.0, -10000.0, -10000.0] None'
        >>> pv.increase_prices ([(1,-80, "seller"), (2,-80,"halfseller-A")])
        >>> str(pv)
        '[-10000.0, -10080.0, -80.0, -10000.0] PriceStatus.STOPPED_AT_AGENT_VALUE'
        >>> pv.increase_prices ([(1,-80, "seller"), (3,-80,"halfseller-B")])
        >>> str(pv)
        '[-10000.0, -160.0, -80.0, -80.0] PriceStatus.STOPPED_AT_AGENT_VALUE'
        >>> pv.increase_prices ([(0,100, "buyer")])
        >>> str(pv)
        '[100.0, -160.0, -80.0, -80.0] PriceStatus.STOPPED_AT_AGENT_VALUE'
        >>> pv.increase_prices ([(1,-80, "seller"), (3,-10,"halfseller-B")])
        >>> str(pv)
        '[100.0, -100.0, -80.0, -20.0] PriceStatus.STOPPED_AT_ZERO_SUM'
        """
        logger.info("  Prices before increase: %s", self.map_category_index_to_price())
        logger.info("  Planned increase: %s", increases)

        # Verify that there is exactly one increase per recipe
        increases_per_recipe = [0]*len(self.ps_recipes)
        for (recipe_index,recipe) in enumerate(self.ps_recipes):
            for (category_index, new_price, description) in increases:
                if recipe[category_index]==1:
                    increases_per_recipe[recipe_index] += 1
        logger.info("  Increases per recipe: %s", increases_per_recipe)
        if any([ipr!=1 for ipr in increases_per_recipe]):
            raise ValueError("There must be exactly one increase per recipe!")

        increase_to_upper_bound = sum_upper_bound - self.price_sum()
        increases_to_new_prices = [new_price - self.vector[category_index]
                                   for (category_index,new_price,_) in increases]
        min_increase_to_new_price = min(increases_to_new_prices)
        min_increase = min(min_increase_to_new_price, increase_to_upper_bound)
        if min_increase == increase_to_upper_bound:
            self.status = PriceStatus.STOPPED_AT_ZERO_SUM
            for (category_index, new_price, description) in increases:
                fixed_new_price = self.vector[category_index] + min_increase
                logger.info("{}: while increasing price towards {}, stopped at {} where the price-sum crossed {}".format(description, new_price, fixed_new_price, sum_upper_bound))
                self.vector[category_index] = fixed_new_price

        else: # min_increase == min_increase_to_new_price:
            self.status = PriceStatus.STOPPED_AT_AGENT_VALUE
            for (category_index, new_price, description) in increases:
                fixed_new_price = self.vector[category_index] + min_increase
                if fixed_new_price == new_price:
                    logger.info("{}: price increases to {}".format(description, new_price))
                else:
                    logger.info("{}: while increasing price towards {}, stopped at {} where an agent from another category left".format(description, new_price, fixed_new_price, sum_upper_bound))
                self.vector[category_index] = fixed_new_price


    def __str__(self):
        return str(self.vector) + " " + str(self.status)



def calculate_initial_prices(ps_recipes:List[int], max_price_per_category:float)->List[float]:
    """
    Calculate a vector of initial prices such that
       (a) the sum of prices in all recipes is the same
       (b) the price in each category is at most max_price_per_category (a negative number).
    :param ps_recipes:  A list of PS recipes.
    :param max_price_per_category: a negative number indicating the maximum price per category
           (should be smaller than all valuations of traders in this category).
    :return: A vector of initial prices.

    >>> p = calculate_initial_prices([[1,1,0,0],[1,0,1,1]], -100)
    >>> p[0]
    -100.0
    >>> p[1]
    -200.0
    >>> p[2]
    -100.0
    >>> p[3]
    -100.0
    """
    num_recipes = len(ps_recipes)
    num_categories = len(ps_recipes[0])

    from scipy.optimize import linprog
    # variables: 0 (the sum);  1, ..., num_categories-1 [the prices)
    result = linprog(
        [-1] + [0]*num_categories,  # Maximize the (negative) sum of prices
        A_eq=[ [-1] + recipe for recipe in ps_recipes],  # The sum of prices should equal the sum in each recipe
        b_eq=[0]*num_recipes,  # The sum of every recipe minus the sum-variable must be 0
        bounds=[(None, max_price_per_category)]*(num_categories+1),
        method="revised simplex"
    )
    if result.status==0:
        return list(result.x[1:])
    else:
        raise ValueError("Cannot determine initial prices: "+result.message)



if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
    # ps_recipes = [
    #     [1, 1, 0, 0],
    #     [1, 0, 1, 1]]
    # sum_prices = -10000
    # print(calculate_initial_prices(ps_recipes,sum_prices))
