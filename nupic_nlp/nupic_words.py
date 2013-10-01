import numpy
# This is the class correspondingn to the C++ optimized Temporal Pooler (default)
from nupic.research.TP10X2 import TP10X2 as TP

class Client(object):

  def __init__(self):
    self.tp = TP(numberOfCols=16384, cellsPerColumn=8,
                initialPerm=0.5, connectedPerm=0.5,
                minThreshold=164, newSynapseCount=164,
                permanenceInc=0.1, permanenceDec=0.0,
                activationThreshold=164, # 1/2 of the on bits = (16384 * .02) / 2
                globalDecay=0, burnIn=1,
                checkSynapseConsistency=False,
                pamLength=10)


  def feed(self, sdr):
    tp = self.tp
    narr = numpy.ndarray((len(sdr),), buffer=numpy.array(sdr), dtype="uint32")
    return tp.compute(numpy.array(narr), enableLearn = True, computeInfOutput = True)


  def reset(self):
    self.tp.reset()