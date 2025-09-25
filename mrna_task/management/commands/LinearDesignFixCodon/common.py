from typing import Tuple, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

# 在原C++中：
# using SizeType = size_t;
# using ScoreType = int32_t;
# using IndexType = int32_t;
# using NucType = int8_t;
# using NumType = int32_t;
# using NucPairType = int8_t;
# using PairType = int8_t;
# using FinalScoreType = double;
#
# Python中无需严格类型定义，可用注释标明。

ScoreType = int   # 对应int32_t
IndexType = int   # 对应int32_t
NucType = int     # 对应int8_t
NumType = int     # 对应int32_t
NucPairType = int # 对应int8_t
PairType = int    # 对应int8_t
FinalScoreType = float
INT_MIN = -2**31

# NodeType = tuple<IndexType, NumType, NucType>
NodeType = Tuple[IndexType, NumType, NucType]

# NodeNucType = std::pair<NodeType, NucType>
NodeNucType = Tuple[NodeType, NucType]

# NodeNucWType = std::tuple<NodeType, NucType, double>
NodeNucWType = Tuple[NodeType, NucType, float]

# 定义枚举 Manner, Beam_type 对应 C++ 的 enum class
class Manner(Enum):
    NONE = 0
    H = 1
    HAIRPIN = 2
    SINGLE = 3
    HELIX = 4
    MULTI = 5
    MULTI_eq_MULTI_plus_U = 6
    P_eq_MULTI = 7
    M2_eq_M_plus_P = 8
    M_eq_M2 = 9
    M_eq_M_plus_U = 10
    M_eq_P = 11
    C_eq_C_plus_U = 12
    C_eq_C_plus_P = 13

class BeamType(Enum):
    BEAM_C = 0
    BEAM_P = 1
    BEAM_MULTI = 2
    BEAM_M2 = 3
    BEAM_M1 = 4

@dataclass
class State:
    score: ScoreType
    cai_score: float
    pre_node: NodeType
    pre_left_cai: float
    pre_left_ctx: Optional[Any] = None

@dataclass
class BacktraceResult:
    seq: str
    structure: str

@dataclass
class DecoderResult:
    sequence: str
    structure: str
    score: ScoreType
    cai: ScoreType
    old_cai: ScoreType
    num_states: IndexType

@dataclass
class ScoreInnerDate:
    newscore: ScoreType
    j_node: Tuple[IndexType, IndexType, NucType]  # 这里的NodeType在C++中为std::tuple<IndexType,IndexType,NucType>
    i_node: Tuple[IndexType, IndexType, NucType]
    nuc_pair: int

@dataclass(frozen=True)
class NodeNucpair:
    node_first: IndexType
    node_second: NumType
    nucpair: NucPairType

@dataclass
class QNodeNucs:
    q_1_node: NodeType
    q_node: NodeType
    nucq_1: int
    nucq: int
    nucj_2: int
    right_seq: List[Tuple[int, int]]
    right_start: int
    right_end: int
    right_start_node: NodeType
    right_end_node: NodeType
    weight_nucq_1: float
    weight_nucq: float
    weight_nucj_2: float
    weight_nucj_1: float
    q_equ_j_1: bool
    j_1_node: NodeType


