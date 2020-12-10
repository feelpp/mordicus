import sys
from feelpp.toolboxes.heat import *
from feelpp.mor import *
import feelpp

o=toolboxes_options("heat")
o.add(makeToolboxMorOptions())
e=feelpp.Environment(sys.argv,opts=o)