#!python3

"""
class AgentCategory

Represents a category of traders in a multi-lateral market,
such as "buyers", "sellers", etc.

Author: Erel Segal-Halevi
Since: 2019-08
"""


MAX_VALUE=100000000    # an upper bound (not necessarily tight) on the agents' values.

class AgentCategory:
    """
    Represents a category of single-parametric agents in a market, for example: "buyers".
    The agents are sorted in descending order of their value.

    >>> a = AgentCategory("buyer", [1,6,3,7,4,9])
    >>> str(a)
    'buyer: [9, 7, 6, 4, 3, 1]'
    >>> a.remove_highest_agent()
    >>> str(a)
    'buyer: [7, 6, 4, 3, 1]'
    >>> a.remove_highest_agents(2)
    >>> str(a)
    'buyer: [4, 3, 1]'
    >>> a.remove_lowest_agent()
    >>> str(a)
    'buyer: [4, 3]'
    >>> a.append(3.5)
    >>> str(a)
    'buyer: [4, 3.5, 3]'
    >>> a.append([3.2,3.8])
    >>> str(a)
    'buyer: [4, 3.8, 3.5, 3.2, 3]'
    """
    def __init__(self, name:str, values:list):
        self.name = name
        self.values = list(values)
        self.values.sort(reverse=True)

    def size(self):
        return len(self.values)

    def __len__(self):
        return len(self.values)

    def __str__(self)->str:
        return "{}: {}".format(self.name, self.values)

    def __repr__(self)->str:
        return self.__str__()

    def append(self, value:float):
        """
        Adds an agent with the given value to the category.
        Keeps the values sorted in descending order.
        :param value: the value of the new agent.
        """
        if isinstance(value, list):
            self.values += value
        else:
            self.values.append(value)
        self.values.sort(reverse=True)


    def highest_agent_value(self)->float:
        """
        :return: the highest value of an agent in this category.
        """
        return self.values[0]  # Assumes the values are sorted

    def highest_agent_values(self, count:int)->list:
        """
        :return: the highest 'count' value of agents in this category.
        """
        return self.values[0:count]  # Assumes the values are sorted

    def lowest_agent_value(self)->float:
        """
        :return: the lowest value of an agent in this category.
        """
        return self.values[-1]  # Assumes the values are sorted

    def remove_highest_agent(self):
        """
        Removes the highest-valued agent from this category.
        :return:
        """
        self.values.pop(0)

    def remove_highest_agents(self, count:int):
        """
        Removes the 'count' highest-valued agents from this category.
        """
        # del self.values[0:count]
        for i in range(count):
            self.values.pop(0)

    def remove_lowest_agent(self):
        """
        Removes the lowest-valued agent from this category.
        :return:
        """
        self.values.pop(-1)

    def clone(self):
        return AgentCategory(self.name, self.values)



    @staticmethod
    def uniformly_random(name:str, num_of_agents:int, min_value:float, max_value:float):
        import random
        values = [random.uniform(min_value,max_value) for _ in range(num_of_agents)]
        return AgentCategory(name, values)



class EmptyCategoryException(Exception):
    pass


if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
