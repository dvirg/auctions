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

from prices import *

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


class SimultaneousAscendingPriceVectors:
    """
    Represents a collection of tied price-vectors, corresponding to different PS recipes in the same market.
    All price-vectors must have the same number of categories.
    During price-increases, all price-vectors retain the same sum.

    >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
    >>> str(pv)
    "['[-5000.0, -5000.0, -2500.0, -2500.0]', '[-5000.0, -5000.0, -2500.0, -2500.0]'] None"
    """
    def __init__(self, ps_recipes: List[List[int]], initial_price_sum:float):
        if len(ps_recipes)==0:
            raise ValueError("Empty list of recipes")

        num_categories = len(ps_recipes[0])
        for ps_recipe in ps_recipes:
            if len(ps_recipe) != num_categories:
                raise ValueError("Different category counts: {} vs {}".format(num_categories, len(ps_recipe)))

        initial_prices = calculate_initial_prices(ps_recipes, initial_price_sum)
        vectors = []
        for ps_recipe in ps_recipes:
            vectors.append(AscendingPriceVector(ps_recipe, initial_prices))

        self.vectors = vectors
        self.num_categories = num_categories
        self.status = None  # status of the latest price-increase operation

    def price_sum(self):
        return self.vectors[0].price_sum()

    def map_category_index_to_price(self):
        """
        >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
        >>> pv.map_category_index_to_price()
        [-5000.0, -5000.0, -2500.0, -2500.0]
        >>> pv.increase_prices ([(1,10,"seller"), (2,10,"half-seller-A")])
        >>> pv.map_category_index_to_price()[2]
        10.0
        >>> pv.increase_prices ([(1,10,"seller"), (3,10,"half-seller-B")])
        >>> pv.map_category_index_to_price()[1]
        10.0
        """
        result = [None]*self.num_categories
        for vector in self.vectors:
            for category_index in range(self.num_categories):
                if vector.ps_recipe[category_index] > 0:
                    if result[category_index] is None:
                        result[category_index] = vector.prices[category_index]
                    elif result[category_index] != vector.prices[category_index]:
                        raise ValueError("Inconsistent prices for category {}: {} vs {}".format(category_index, result[category_index], vector.prices[category_index]))
                    else:
                        pass
        return result

    def __getitem__(self, vector_index:int):
        return self.vectors[vector_index]

    def increase_prices(self, increases:List[Tuple[int,float,str]]):
        """
        Simultaneously increase the prices of all vectors, keeping their sum equal.
        :param increases: a list of tuples; each tuple contains arguments to the increase_prices method of AscendingPriceVector:
            (category_index, new_price, description)

        >>> pv = SimultaneousAscendingPriceVectors([[1, 1, 0, 0], [1, 0, 1, 1]], -10000)
        >>> pv.increase_prices ([(0,10,"buyer"), (0,10,"buyer")])
        >>> str(pv)
        "['[10.0, -5000.0, -2500.0, -2500.0]', '[10.0, -5000.0, -2500.0, -2500.0]'] PriceStatus.STOPPED_AT_AGENT_VALUE"
        >>> pv.increase_prices ([(1,-80, "seller"), (2,-80,"halfseller-A")])
        >>> str(pv)
        "['[10.0, -2580.0, -80.0, -2500.0]', '[10.0, -2580.0, -80.0, -2500.0]'] PriceStatus.STOPPED_AT_AGENT_VALUE"
        >>> pv.increase_prices ([(1,-80, "seller"), (3,-80,"halfseller-B")])
        >>> str(pv)
        "['[10.0, -160.0, -80.0, -80.0]', '[10.0, -160.0, -80.0, -80.0]'] PriceStatus.STOPPED_AT_AGENT_VALUE"
        """
        if len(increases) != len(self.vectors):
            raise ValueError("There should be an increase-triplet per vector. increases={}, vectors={}".format(increases, self.vectors))
        logger.info("  Prices before increase: %s", self.map_category_index_to_price())
        logger.info("  Planned increase: %s", increases)
        new_sums = [0]*len(self.vectors)
        for vector_index, vector in enumerate(self.vectors):
            (category_index, new_price, _) = increases[vector_index]
            new_sums[vector_index] = vector.price_sum_after_increase(category_index, new_price)
        min_new_sum = min(0, min(new_sums))
        if -0.00000000001 < min_new_sum and min_new_sum < 0.00000000001:
            min_new_sum = 0
        logger.info("  Price-sums after increase: %s.  Min sum: %f", new_sums, min_new_sum)

        for vector_index, vector in enumerate(self.vectors):
            (category_index, new_price, description) = increases[vector_index]
            vector.increase_price_up_to_balance(category_index, new_price, description, sum_upper_bound=min_new_sum)

        self.status = PriceStatus.STOPPED_AT_ZERO_SUM if min_new_sum==0 else PriceStatus.STOPPED_AT_AGENT_VALUE


    def __str__(self):
        return str([str(v) for v in self.vectors]) + " " + str(self.status)



def calculate_initial_prices(ps_recipes:List[int], initial_price_sum:float)->List[float]:
    """
    :param ps_recipes:  A list of PS recipes.
    :param initial_price_sum: The sum that the price-vectors for all recipes should have.
    :return: A vector of initial prices.

    >>> p = calculate_initial_prices([[1,1,0,0],[1,0,1,1]], -10000)
    >>> p[0]
    -5000.0
    >>> p[1]
    -5000.0
    >>> p[2]
    -2500.0
    >>> p[3]
    -2500.0
    """
    num_recipes = len(ps_recipes)
    num_categories = len(ps_recipes[0])
    max_price = initial_price_sum/num_categories

    from scipy.optimize import linprog
    result = linprog(  # variables: price_heder, m, price_salon
        [-1]*num_categories,  # Minimize the sum of prices
        A_eq=ps_recipes,
        b_eq=[initial_price_sum]*num_recipes,  # The sum of every recipe must be the same
        bounds=[(None, max_price)]*num_categories,
        method="revised simplex"
    )
    if result.status==0:
        return list(result.x)
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
