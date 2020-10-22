# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.InitialConditions import InitialConditionBase as ICB


def test():

    initialCondition = ICB.InitialConditionBase()

    print(initialCondition)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
