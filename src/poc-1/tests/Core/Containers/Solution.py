# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing
from Mordicus.Core.Containers import Solution
import collections
import pytest

def test():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot1 = np.ones(20)
    snapshot2 = np.ones(20)
    compressedSnapshots = collections.OrderedDict()
    compressedSnapshots[0.0] = np.ones(2)
    compressedSnapshots[1.0] = np.ones(2)
    solution.AddSnapshot(snapshot1, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)
    solution.AddSnapshot(snapshot1, 0.5)
    assert solution.GetNumberOfSnapshots() == 3, "Solution should have 3 snapshots at time 0., 0.5, 1."

    # Assert that callin constructor with wrong types fails
    with pytest.raises(TypeError):
        solution = Solution.Solution(1, 2, 10, True)

    solution.RemoveSnapshot(0.5)
    assert solution.GetNumberOfSnapshots() == 2, ("Solution should have 2 snapshots. "
                                                  "Maybe snapshot at time 0.5 was not removed")

    solution.RemoveSnapshot(0.7)
    assert solution.GetNumberOfSnapshots() == 2, ("Removing snapshot at a time where there is none "
                                                  "should do nothing silently.")

    solution.AddSnapshot(snapshot1, 0.5)
    assert solution.GetNumberOfSnapshots() == 3, "Solution should have 3 snapshots."

    solution.RemoveSnapshots([0.5, 0.])
    assert solution.GetNumberOfSnapshots() == 1, "Solution should have 1 snapshots."

    solution.AddSnapshot(snapshot1, 0.0)
    solution.AddCompressedSnapshots(np.ones(2), 1.)
    solution.AddCompressedSnapshots(np.ones(2), 0.)
    numpy.testing.assert_almost_equal(solution.GetSnapshot(1.0), np.ones(20))

    solution.ConvertCompressedSnapshotReducedOrderBasis(np.arange(6.0).reshape((3,2)))
    numpy.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(0.), np.array([1., 5., 9.]))

    solution.ConvertCompressedSnapshotReducedOrderBasisAtTime(np.arange(12.0).reshape((4,3)), 0.)
    numpy.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(0.), 
                                      np.array([ 23.,  68., 113., 158.]))
    
    assert solution.GetPrimality(), "Primality should be True as set at the beginning."

    assert solution.GetTimeSequenceFromSnapshots() == pytest.approx([0., 1.]), "Time sequence should be [0, 1]"
    slist = solution.GetSnapshotsList()
    numpy.testing.assert_almost_equal(slist[0], np.ones(20))
    numpy.testing.assert_almost_equal(slist[1], np.ones(20))

    assert solution.GetNbeOfComponents() == 2  , "Solution has the wrong number of components"
    assert solution.GetNumberOfDofs() == 20    , "Solution has the wrong number of Dofs"
    assert solution.GetNumberOfSnapshots() == 2, "Solution has the wrong number of snapshots"
    numpy.testing.assert_almost_equal(solution.GetSnapshotAtTime(0.5), np.ones(20))

    snapshots = collections.OrderedDict()
    snapshots[0.0] = np.ones(20)
    snapshots[1.0] = np.ones(20)
    solution.SetSnapshots(snapshots)
    solution.SetCompressedSnapshots(compressedSnapshots)
    assert solution.GetCompressedSnapshots() is compressedSnapshots, "Compressed snapshots were not properly set"
    cslist = solution.GetCompressedSnapshotsList()
    numpy.testing.assert_almost_equal(cslist[0], np.ones(2))
    numpy.testing.assert_almost_equal(cslist[1], np.ones(2))

    assert solution.GetTimeSequenceFromCompressedSnapshots() == pytest.approx([0., 1.])
    numpy.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(0.5), np.ones(2))
    cslist = solution.GetCompressedSnapshotsAtTimes([0.5, 0.6])
    numpy.testing.assert_almost_equal(cslist[0], np.ones(2))
    numpy.testing.assert_almost_equal(cslist[1], np.ones(2))

    solution.UncompressSnapshots(np.arange(40.).reshape((2,20)))
    numpy.testing.assert_almost_equal(solution.GetSnapshot(1.0), np.arange(20.) + np.arange(20., 40.))
    solution.CompressSnapshots(np.eye(20), np.arange(40.).reshape((2,20)))
    numpy.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(1.0), np.array([ 8740., 24340.]))

    print(solution)
    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
