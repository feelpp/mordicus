# coding: utf-8

import numpy as np
mu1 = 0.0
mu2 = 0.0

a = np.linspace(mu1, mu2+19., 20)
np.save("snapshot.npy", a, allow_pickle=False)
