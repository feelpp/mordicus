# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.SolutionStructures import SolutionStructureBase as SSB

from Mordicus.Core.Containers.Meshes import MeshBase as MB


meshBase = MB.MeshBase()
solutionStructure = SSB.SolutionStructureBase(meshBase, 'node')

solutionStructure.SetInternalStorage("storage")
solutionStructure.SetInternalStorage("storage")
solutionStructure.GetInternalStorage()

