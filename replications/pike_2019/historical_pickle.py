"""Restricted constructors used by the hash-pinned author data archives."""

from collections import defaultdict
import pickle

import numpy as np


class ArchiveReader(pickle.Unpickler):
    def find_class(self, module, name):
        return {
            ("collections", "defaultdict"): defaultdict,
            ("builtins", "list"): list,
            ("numpy.core.multiarray", "scalar"): np.core.multiarray.scalar,
            ("numpy", "dtype"): np.dtype,
        }[module, name]
