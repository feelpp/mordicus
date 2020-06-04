# -*- coding: utf-8 -*-


from Mordicus.Modules.Phimeca.IO.OTSolutionReader import OTSolutionReader
import openturns as ot

def test():

    # generate some fields
    mesh = ot.IntervalMesher([10, 5]).build(ot.Interval([0.0, 0.0], [2.0, 1.0]))
    model = ot.ExponentialModel([3.0, 3.0], [5.0])
    processSample = ot.GaussianProcess(model, mesh).getSample(10)

    # run reader
    field = ot.Field(mesh, processSample[0])
    reader = OTSolutionReader(field)
    snapshot = reader.ReadSnapshotComponent("U1", 0.0, True)
    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
