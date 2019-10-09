
import numpy as np
from BasicTools.IO import GeofReader as GR


mesh = GR.ReadGeof("cube.geof")

lenX0 = len(mesh.elements['quad4'].tags['x0'])
print("nbe of elements in tag X0 :", lenX0)


data_node = np.ones(lenX0)

nodeFile = open("pressure.node", "w")

data_node.astype(np.float32).byteswap().tofile(nodeFile)

nodeFile.close()
