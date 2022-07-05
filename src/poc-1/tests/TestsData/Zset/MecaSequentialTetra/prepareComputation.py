import numpy as np


has_BasicTools = True

try:
  from BasicTools.IO import GeoReader as GR
except:
  has_BasicTools=False

def run():
    
    mesh = GR.ReadGeo('cube.geo')

    nNodes = mesh.GetNumberOfNodes()


    Tmin = 100.
    Tmax = 1900.



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


if __name__ == "__main__":

    run()



