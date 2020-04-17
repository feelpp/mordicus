
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase

from Mordicus.Modules.Mines.Containers.ZsetMesh import ZsetMesh, dict_elt
import pathlib
import numpy as np
import re



class ZsetMeshReader(MeshReaderBase):
    def __init__(self, fname):
        super(ZsetMeshReader, self).__init__()
        self._fname = fname

    
    def ReadMesh(self):
        if not pathlib.Path(self._fname).exists():
            raise Exception(f"The mesh file {self._fname} doesn't exists")

        nb_nodes = 0
        nb_dim   = 0
        nb_elems = 0
        nodes = None
        connectivity = []
        element_types = []
        gp_offset = [0]
        with open(self._fname, 'r') as fid:
            while True:
                line = fid.readline()
                if line == "***return" or line == "":
                    break
                if "***" in line:
                    continue
                if "**node" in line:
                    l = fid.readline()
                    tok = l.split(" ")
                    nb_nodes, nb_dim = int(tok[0]), int(tok[1])
                    nodes = np.zeros((nb_nodes, nb_dim)) 

                    for i in range(nb_nodes):
                        l = fid.readline()
                        l = l.strip()
                        nodes[i,:] = [ float(x) for x in l.split()[1:]]
                    continue

                if "**elem" in line:
                    l = fid.readline()
                    nb_elems = int(l)
                    for i in range(nb_elems):
                        l = fid.readline()
                        l = l.strip()
                        connectivity.append( [ int(x)-1 for x in l.split(" ")[2:] ])
                        etype = l.split(" ")[1]
                        element_types.append( etype )
                        gp_offset.append( gp_offset[i] + dict_elt[etype] )
                    continue

                break
        storage = {"nodes": nodes, "elements": connectivity, "element_types": element_types}
        ret = ZsetMesh(storage)
        return ret
