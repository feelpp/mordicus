import numpy as np
import math

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
        timeseq = self.ReadTimeSequenceFromSolutionFile()
        index = max(np.searchsorted(timeseq, time, side='left'), len(timeseq)-1)
        if index > 0 and math.fabs(timeseq[index-1] - time) < math.fabs(timeseq[index] - time):
            index = index-1
        snapshot = np.array(self.outputSample.getValueAtIndex(index)).flatten()
        return snapshot

    def ReadTimeSequenceFromSolutionFile(self):
        # here too
        return np.array(self.outputSample.getTimeGrid().getValues())
