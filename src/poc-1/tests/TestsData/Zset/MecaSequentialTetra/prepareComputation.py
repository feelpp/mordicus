import numpy as np


f = open('cube2.geof')
string = ""
for line in f:
  line = line.split()
  try:
    index = line.index("c3d10_4")
    line[index] = "c3d10"
  except ValueError:
    True
  line = ' '.join(line)
  string += str(line)+'\n'
f.close()

f = open('cube2.geof', 'w')
f.write(string)
f.close()





from BasicTools.IO import GeofReader as GR

mesh = GR.ReadGeof('cube2.geof')

nNodes = mesh.GetNumberOfNodes()


Tmin = 100.
Tmax = 400.



temperature1 = Tmin*np.ones(nNodes)

xMin = np.min(mesh.nodes[:,0])
xMax = np.max(mesh.nodes[:,0])
yMin = np.min(mesh.nodes[:,1])
yMax = np.max(mesh.nodes[:,1])
zMin = np.min(mesh.nodes[:,2])
zMax = np.max(mesh.nodes[:,2])

center = [(xMin+xMax)/2,(yMin+yMax)/2,(zMin+zMax)/2]

sigma6 = 1.

x = mesh.nodes[:,0]
y = mesh.nodes[:,1]
z = mesh.nodes[:,2]
r2 = ((x-center[0])**2+(y-center[1])**2+(z-center[2])**2)
temperature2 = Tmin+(Tmax-Tmin)*np.exp(-r2/sigma6)

assert temperature2.shape[0] == nNodes

f = open('temperature12.node','wb')
temperature1.astype(np.float32).byteswap().tofile(f)
f.close()

f = open('temperature22.node','wb')
temperature2.astype(np.float32).byteswap().tofile(f)
f.close()


pressure = []
for name, data in mesh.elements.items():
  if 'x1' in data.tags:
    idstotreat = data.tags['x1'].GetIds()
    for el in idstotreat:
      xcoor = mesh.nodes[data.connectivity[el],:]
      barycenter = (1./xcoor.shape[0])*np.sum(xcoor, axis=0)
      r2 = ((barycenter[0]-center[0])**2+(barycenter[1]-yMax)**2+(barycenter[2]-center[2])**2)
      pressure.append(1.*np.exp(-r2/sigma6))
pressure = np.array(pressure)


f = open('pressure.node','wb')
pressure.astype(np.float32).byteswap().tofile(f)
f.close()


print("nNodes =", nNodes)


