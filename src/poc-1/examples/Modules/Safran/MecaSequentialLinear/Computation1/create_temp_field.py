
import numpy as np
import BasicTools.IO.GeofReader as GR

import os

import pytest


@pytest.mark.skip
def compute():

    mesh = GR.ReadGeof(fileName=os.path.dirname(os.path.abspath(__file__))+os.sep+"cube.geof")

    xmin = np.min(mesh.nodes[:,0])
    xmax = np.max(mesh.nodes[:,0])
    dx = xmax - xmin

    ymin = np.min(mesh.nodes[:,1])
    ymax = np.max(mesh.nodes[:,1])
    dy = ymax - ymin

    zmin = np.min(mesh.nodes[:,2])
    zmax = np.max(mesh.nodes[:,2])
    dz = zmax - zmin

    d = [dx, dy, dz]
    mmax = [xmax, ymax, zmax]
    mmin = [xmin, ymin, zmin]

    sd = np.argsort(np.array([dx, dy, dz]))[1]
    cd = np.argsort(np.array([dx, dy, dz]))[2]

    center = [(xmax+xmin)/2., (ymax+ymin)/2., (zmax+zmin)/2.]
    sigma6 = (d[cd]/2)**2


    nbNodes = mesh.nodes.shape[0]
    temperature2 = np.zeros(nbNodes)
    print("nbNodes = ", nbNodes)
    print("center = ", center)

    Tmax = 400.

    for i in range(nbNodes):
        x = mesh.nodes[i,0]; y = mesh.nodes[i,1]; z = mesh.nodes[i,2]
        r2 = ((x-center[0])**2+(y-center[1])**2+(z-center[2])**2)
        temperature2[i] = 20.+(Tmax-20.)*np.exp(-r2/sigma6)

    print("temperature2 =", temperature2)

    f = open('temperature2.node','wb')
    temperature2.astype(np.float32).byteswap().tofile(f)
    f.close()


if __name__ == "__main__":
    compute()

