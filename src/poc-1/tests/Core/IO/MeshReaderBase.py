# -*- coding: utf-8 -*-

from Mordicus.Core.IO import MeshReaderBase as MRB


def test():

    meshReaderBase = MRB.MeshReaderBase()
    print(meshReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
