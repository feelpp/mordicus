# -*- coding: utf-8 -*-
from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase


dict_elt = {}
#2D linear
dict_elt["c2d3r"]   = 1
dict_elt["cax3r"]   = 1
dict_elt["c2d3"]    = 3
dict_elt["cax3"]    = 3
dict_elt["c2d4r"]   = 1
dict_elt["cax4r"]   = 1
dict_elt["c2d4"]    = 4
dict_elt["cax4"]    = 4
#2D quadratic
dict_elt["c2d6r"]   = 3
dict_elt["cax6r"]   = 3
dict_elt["c2d6"]    = 6
dict_elt["cax6"]    = 6
dict_elt["c2d8r"]   = 4
dict_elt["cax8r"]   = 4
dict_elt["c2d8"]    = 9
dict_elt["cax8"]    = 9
#3D linear
dict_elt["c3d6r"]   = 2
dict_elt["c3d6"]    = 6
dict_elt["c3d8r"]   = 1
dict_elt["c3d8"]    = 8
dict_elt["c3d4"]    = 1
#3D quadratic
dict_elt["c3d15r"]  = 6
dict_elt["c3d15_9"] = 9
dict_elt["c3d15"]   = 18
dict_elt["c3d20r"]  = 8
dict_elt["c3d20"]   = 27
dict_elt["c3d10r"]  = 1
dict_elt["c3d10_4"] = 4
dict_elt["c3d10"]   = 5



class ZsetMesh(MeshBase):
    def __init__(self, storage):
        super(ZsetMesh, self).__init__()
        self.SetInternalStorage( storage )
        self.__buildInverseTables()

    def GetNodes(self):
        return self.GetInternalStorage()["nodes"]

    def GetElement(self, e_rk):
        return self.GetInternalStorage()["elements"][e_rk]

    def AllElementsIterator(self):
        return self.GetInternalStorage()["elements"]

    def GetElemAttach(self, node_rk: int) -> list:
        """[summary]
        
        Arguments:
            node_rk {int} -- [description]
        
        Returns:
            list -- [description]
        """

        return self.GetInternalStorage()["node2elem"][node_rk]

    def GetElemContaining(self, ip_rk: int) -> int:
        """[summary]
        
        Arguments:
            ip_rk {int} -- [description]
        
        Returns:
            int -- [description]
        """
        return self.GetInternalStorage()["ip2elem"][ip_rk]

    def GetNumberOfIntegrationPoint(self):
        ret = 0
        for e in self.GetInternalStorage()["element_types"]:
            ret += dict_elt[e]
        return ret 

    def __buildInverseTables(self):
        # Node to elem connectivity 
        node2elem = [ [] for _ in range(self.GetNumberOfNodes()) ]
        for i, elem in enumerate(self.AllElementsIterator()):
            for node in elem:
                node2elem[node].append( i )

        self.GetInternalStorage()["node2elem"] = node2elem
        # IP to elem connectivity
        ip2elem = [None]*self.GetNumberOfIntegrationPoint()
        count = 0
        for i, e_type in enumerate(self.GetInternalStorage()["element_types"]):
            for k in range(dict_elt[e_type]):
                ip2elem[count] = i
                count += 1
        self.GetInternalStorage()["ip2elem"] = ip2elem


    