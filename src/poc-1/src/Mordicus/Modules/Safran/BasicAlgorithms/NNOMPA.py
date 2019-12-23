 # -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import nnls as nnls
from scipy.optimize import lsq_linear as lsq_linear
from BasicTools.Helpers.TextFormatHelper import TFormat


def ComputeReducedIntegrationScheme(diag, Phi, tolerance, imposedIndices = [], reducedIntegrationPointsInitSet = []):

      y = np.dot(Phi, diag)
      normy = np.linalg.norm(y)
      
      NGaussOrEl = Phi.shape[1]

      if len(reducedIntegrationPointsInitSet) == 0:
        s = np.empty(0, dtype = int)
      else:
        s = reducedIntegrationPointsInitSet
      k = 0
      x = 0
      r = y

      err = 1.1
      oldErr = 1.
      count0 = 0
      lenx = 0
      while err > tolerance:

        nRandom = 1#NGaussOrElToSelect - len(s)
        notSelectedIndices = np.array(list((set(np.arange(NGaussOrEl))-set(s))))

        count = 0

        while err >= oldErr:
          ind = np.array(notSelectedIndices.shape[0]*np.random.rand(nRandom), dtype = int)
          addIndices = notSelectedIndices[ind]
          tau = np.argmax(np.dot(Phi.T,r))
          sTemp = np.array(list(s) + list(set(addIndices) - set(s)))
          sTemp = np.array(list(sTemp) + list(set([tau]) - set(sTemp)))
          Phi_s = Phi[:,sTemp]

          algo = lsq_linear(Phi_s, y, bounds=(0.,np.inf), method = 'bvls', lsmr_tol='auto', verbose = 0, lsq_solver = 'exact', max_iter = 500); xTemp = algo['x']
          count0 += 1

          index = list(np.nonzero(xTemp)[0])
          xTemp = xTemp[index]
          sTemp = sTemp[index]
          Phi_s = Phi[:,sTemp]

          r = y - np.dot(Phi_s, xTemp)
          err = np.linalg.norm(r)/normy
          count += 1


        s = sTemp
        x = xTemp
        oldErr = err

        
        print(TFormat.InBlue("Relative error = "+str(err)+" obtained with "+str(len(s))+" integration points (corresponding to "+str(round(100*len(s)/NGaussOrEl, 5))+"% of the total) ("+str(count)+" sample(s) to decrease interpolation error)"))


      #add imposed indices
      l1 = s.shape[0]
      s = np.array(list(s) + list(set(imposedIndices) - set(s)))
      dlength = s.shape[0] - l1
      x = np.hstack((x,np.zeros(dlength)))

      Phi_s = Phi[:,s]
      r = y - np.dot(Phi_s, x)
      err = np.linalg.norm(r)/normy
      
      print(TFormat.InRed("Reduced Integration Scheme Constructed:"))
      print(TFormat.InRed("Relative error = "+str(err)+" obtained with "+str(len(s))+" integration points (corresponding to "+str(round(100*len(s)/NGaussOrEl, 5))+"% of the total)"))
        
      return s, x



