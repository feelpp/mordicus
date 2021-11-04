#!/bin/bash
cat <<EOF > $(dirname ${BASH_SOURCE[0]})/generate_snapshots.py
#!/usr/bin/env python
import numpy as np
S = np.arange(20., dtype=np.double)
np.save("snapshot.npy", S, allow_pickle=False)
EOF
python $(dirname ${BASH_SOURCE[0]})/generate_snapshots.py
mv snapshot.npy $(dirname ${BASH_SOURCE[0]})/snapshot.npy
