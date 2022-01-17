# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.IO import MeshReaderBase as MRB


def test():

    meshReaderBase = MRB.MeshReaderBase()
    print(meshReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
