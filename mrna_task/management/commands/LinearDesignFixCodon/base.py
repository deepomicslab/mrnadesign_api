# base.py

from typing import Tuple, List, Any
import math
import numpy as np
import os
from . import settings

# Constants
LINEAR_DESIGN_CACHELINE = 64

# Utility Functions
def value_min() -> float:
    """Return the minimum possible value."""
    return -math.inf

def value_max() -> float:
    """Return the maximum possible value."""
    return math.inf

# Custom Hash Combine Function
def hash_combine(left_seed: int, right: Any) -> int:
    """Combine two hash values."""
    return left_seed ^ (hash(right) << 1)


def load_energy_params(path=str(settings.get_abs_home() / "original_parameters")):
    params = {
        "lam_cai":np.load(os.path.join(path, "lam_cai.npy")),
        "lxc37": np.load(os.path.join(path, "lxc37.npy")),
        "ML_intern37": np.load(os.path.join(path, "ML_intern37.npy")),
        "ML_closing37": np.load(os.path.join(path, "ML_closing37.npy")),
        "MAX_NINIO": np.load(os.path.join(path, "MAX_NINIO.npy")),
        "ninio37": np.load(os.path.join(path, "ninio37.npy")),
        "TerminalAU37": np.load(os.path.join(path, "TerminalAU37.npy")),
        "ML_BASE37": np.load(os.path.join(path, "ML_BASE37.npy")),
        "ML_BASEdH": np.load(os.path.join(path, "ML_BASEdH.npy")),
        "DuplexInit37": np.load(os.path.join(path, "DuplexInit37.npy")),
        "TripleC37": np.load(os.path.join(path, "TripleC37.npy")),
        "MultipleCA37": np.load(os.path.join(path, "MultipleCA37.npy")),
        "MultipleCB37": np.load(os.path.join(path, "MultipleCB37.npy")),
        "stack37": np.load(os.path.join(path, "stack37.npy")),
        "hairpin37": np.load(os.path.join(path, "hairpin37.npy")),
        "bulge37": np.load(os.path.join(path, "bulge37.npy")),
        "internal_loop37": np.load(os.path.join(path, "internal_loop37.npy")),
        "Tetraloop37": np.load(os.path.join(path, "Tetraloop37.npy")),
        "Hexaloop37": np.load(os.path.join(path, "Hexaloop37.npy")),
        "Triloop37": np.load(os.path.join(path, "Triloop37.npy")),
        "mismatchI37": np.load(os.path.join(path, "mismatchI37.npy")),
        "mismatchH37": np.load(os.path.join(path, "mismatchH37.npy")),
        "mismatchM37": np.load(os.path.join(path, "mismatchM37.npy")),
        "mismatch1nI37": np.load(os.path.join(path, "mismatch1nI37.npy")),
        "mismatch23I37": np.load(os.path.join(path, "mismatch23I37.npy")),
        "mismatchExt37": np.load(os.path.join(path, "mismatchExt37.npy")),
        "dangle5_37": np.load(os.path.join(path, "dangle5_37.npy")),
        "dangle3_37": np.load(os.path.join(path, "dangle3_37.npy")),
        "int11_37": np.load(os.path.join(path, "int11_37.npy")),
        "int21_37": np.load(os.path.join(path, "int21_37.npy")),
        "int22_37": np.load(os.path.join(path, "int22_37.npy")),
    }

    return params

def init_structure_count_params():
    lam_cai_count = [0]
    lxc37_count = [0]
    ML_intern37_count = [0]
    ML_closing37_count = [0]
    ML_BASE37_count = [0]
    ML_BASEdH_count = [0]
    MAX_NINIO_count = [0]
    ninio37_count = [0]
    TerminalAU37_count = [0]
    DuplexInit37_count = [0]
    TripleC37_count = [0]
    MultipleCA37_count = [0]
    MultipleCB37_count = [0]

    stack37_count = [0] * 64
    hairpin37_count = [0] * 31
    bulge37_count = [0] * 31
    internal_loop37_count = [0] * 31
    Tetraloop37_count = [0] * 16
    Hexaloop37_count = [0] * 4
    Triloop37_count = [0] * 2
    mismatchI37_count = [0] * 200
    mismatchH37_count = [0] * 200
    mismatchM37_count = [0] * 200
    mismatch1nI37_count = [0] * 200
    mismatch23I37_count = [0] * 200
    mismatchExt37_count = [0] * 200
    dangle5_37_count = [0] * 40
    dangle3_37_count = [0] * 40
    int11_37_count = [0] * 1600
    int21_37_count = [0] * 8000
    int22_37_count = [0] * 40000

    count_params = {
        "lam_cai_count": lam_cai_count,
        "lxc37_count": lxc37_count,
        "ML_intern37_count": ML_intern37_count,
        "ML_closing37_count": ML_closing37_count,
        "MAX_NINIO_count": MAX_NINIO_count,
        "ninio37_count": ninio37_count,
        "TerminalAU37_count": TerminalAU37_count,
        "ML_BASE37_count":ML_BASE37_count,
        "ML_BASEdH_count": ML_BASEdH_count,
        "DuplexInit37_count": DuplexInit37_count,
        "TripleC37_count": TripleC37_count,
        "MultipleCA37_count": MultipleCA37_count,
        "MultipleCB37_count": MultipleCB37_count,
        "stack37_count": stack37_count,
        "hairpin37_count": hairpin37_count,
        "bulge37_count": bulge37_count,
        "internal_loop37_count": internal_loop37_count,
        "Tetraloop37_count":Tetraloop37_count,
        "Hexaloop37_count": Hexaloop37_count,
        "Triloop37_count": Triloop37_count,
        "mismatchI37_count": mismatchI37_count,
        "mismatchH37_count": mismatchH37_count,
        "mismatchM37_count": mismatchM37_count,
        "mismatch1nI37_count": mismatch1nI37_count,
        "mismatch23I37_count": mismatch23I37_count,
        "mismatchExt37_count": mismatchExt37_count,
        "dangle5_37_count": dangle5_37_count,
        "dangle3_37_count": dangle3_37_count,
        "int11_37_count": int11_37_count,
        "int21_37_count": int21_37_count,
        "int22_37_count": int22_37_count,
    }

    return count_params


# Custom Hash Functions
class HashFunctions:
    @staticmethod
    def hash_pair(pair: Tuple[Any, Any]) -> int:
        """Hash function for a pair (tuple of two elements)."""
        hash1 = hash(pair[0])
        hash2 = hash(pair[1])
        return hash1 ^ hash2

    @staticmethod
    def hash_tuple(triple: Tuple[Any, Any, Any]) -> int:
        """Hash function for a triple (tuple of three elements)."""
        hash1 = hash(triple[0])
        hash2 = hash(triple[1])
        hash3 = hash(triple[2])
        return hash1 ^ hash2 ^ hash3

    @staticmethod
    def hash_vector_of_pairs(vec: List[Tuple[Any, Any]]) -> int:
        """Hash function for a list of pairs."""
        seed = 0
        for pair in vec:
            seed = hash_combine(seed, HashFunctions.hash_pair(pair))
        return seed

    @staticmethod
    def hash_nested_pair(p: Tuple[Tuple[Any, Any], Any]) -> int:
        """Hash function for a nested pair (pair of a pair and another element)."""
        hash1 = HashFunctions.hash_pair(p[0])
        hash2 = hash(p[1])
        return hash1 ^ hash2

# Custom String Representations
def pair_str(pair: Tuple[Any, Any]) -> str:
    """String representation for a pair."""
    return f"({pair[0]}, {pair[1]})"

def tuple_str(tpl: Tuple[Any, Any, Any]) -> str:
    """String representation for a triple."""
    return f"({tpl[0]}, {tpl[1]}, {tpl[2]})"

def vector_of_pairs_str(vec: List[Tuple[Any, Any]]) -> str:
    """String representation for a list of pairs."""
    return "[" + ", ".join(pair_str(p) for p in vec) + "]"

# Example Usage
if __name__ == "__main__":
    load_energy_params()
    # Example pairs and triples
    # pair = (1, 2)
    # triple = (1, 2, 3)
    # nested_pair = ((1, 2), 3)
    # vector_of_pairs = [(1, 2), (3, 4), (5, 6)]
    #
    # # Print string representations
    # print("Pair:", pair_str(pair))
    # print("Triple:", tuple_str(triple))
    # print("Nested Pair:", pair_str(nested_pair))
    # print("Vector of Pairs:", vector_of_pairs_str(vector_of_pairs))
    #
    # # Compute and print hash values
    # print("Hash of Pair:", HashFunctions.hash_pair(pair))
    # print("Hash of Triple:", HashFunctions.hash_tuple(triple))
    # print("Hash of Nested Pair:", HashFunctions.hash_nested_pair(nested_pair))
    # print("Hash of Vector of Pairs:", HashFunctions.hash_vector_of_pairs(vector_of_pairs))
