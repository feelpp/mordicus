import numpy as np

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase

class OTSolutionReader(SolutionReaderBase):
    """
    Solution reader for OpenTURNS fields

    Attributes
    ----------
    outputSample : :class:`openturns.ProcessSample`
        Snapshot
    """
    def __init__(self, outputSample):
        super(OTSolutionReader, self).__init__()
        self.outputSample = outputSample

    def ReadSnapshotComponent(self, fieldName, time, primality):
        # FIXME: indexing variable is not time, just the number of the realization
        i = int(time)
        snapshot = np.array(self.outputSample[i].getValues()).flatten()
        return snapshot

    def ReadTimeSequenceFromSolutionFile(self):
        # here too
        return [float(i) for i in range(self.outputSample.getSize())]
