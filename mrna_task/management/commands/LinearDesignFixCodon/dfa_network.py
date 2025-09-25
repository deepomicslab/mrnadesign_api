import math
import sys
from collections import defaultdict
from typing import Dict, Tuple, List, Optional
from .utility_v import GET_ACGU, GET_ACGU_NUC
from .common import IndexType, NumType, NucType, NodeType
from .codon import Codon, split, k_void_nuc
from . import settings

# === NEW: 单字母氨基酸到 coding_wheel 三字母标签映射===
SINGLE_TO_WHEEL = {
    'A': 'Ala', 'R': 'Arg', 'N': 'Asn', 'D': 'Asp', 'C': 'Cys',
    'Q': 'Gln', 'E': 'Glu', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
    'L': 'Leu', 'K': 'Lys', 'M': 'Met', 'F': 'Phe', 'P': 'Pro',
    'S': 'Ser', 'T': 'Thr', 'W': 'Trp', 'Y': 'Tyr', 'V': 'Val',
    '*': 'STOP', 'U': 'Sec'  # 若轮盘不含 Sec/STOP 请按实际调整
}

class Lattice:
    def __init__(self):
        # nodes: Dict[IndexType, List[NodeType]]
        self.nodes: Dict[IndexType, List[NodeType]] = defaultdict(list)
        # right_edges and left_edges: Dict[NodeType, List[Tuple[NodeType,float]]]
        self.right_edges: Dict[NodeType, List[Tuple[NodeType, float]]] = defaultdict(list)
        self.left_edges: Dict[NodeType, List[Tuple[NodeType, float]]] = defaultdict(list)
        # NEW: 第三位节点到完整密码子（例如 "AUG"）的映射
        self.codon_by_node3: Dict[NodeType, str] = {}

    def add_edge(self, n1: NodeType, n2: NodeType, weight: float = 0.0):
        self.right_edges[n1].append((n2, weight))
        self.left_edges[n2].append((n1, weight))

    def add_node(self, n1: NodeType):
        pos = n1[0]
        self.nodes[pos].append(n1)

class DFA:
    def __init__(self):
        self.nodes: Dict[IndexType, List[NodeType]] = defaultdict(list)
        self.left_edges: Dict[NodeType, List[Tuple[NodeType, float]]] = defaultdict(list)
        self.right_edges: Dict[NodeType, List[Tuple[NodeType, float]]] = defaultdict(list)
        self.auxiliary_left_edges: Dict[NodeType, Dict[NodeType, float]] = defaultdict(dict)
        self.auxiliary_right_edges: Dict[NodeType, Dict[NodeType, float]] = defaultdict(dict)
        self.node_rightedge_weights: Dict[NodeType, float] = {}
        # NEW: 压平后的第三位节点（index%3==2）对应的完整密码子
        self.codon_at_node3: Dict[NodeType, str] = {}

    def add_edge(self, n1: NodeType, n2: NodeType, weight: float = 0.0):
        self.right_edges[n1].append((n2, weight))
        self.left_edges[n2].append((n1, weight))
        self.auxiliary_right_edges[n1][n2] = weight
        self.auxiliary_left_edges[n2][n1] = weight
        self.node_rightedge_weights[n1] = weight

    def add_node(self, n1: NodeType):
        pos = n1[0]
        self.nodes[pos].append(n1)

def read_wheel(filename: str):
    aa_graphs: Dict[str, Lattice] = {}
    try:
        inFile = open(filename, 'r', encoding='utf-8')
    except:
        print("Unable to open coding_wheel file")
        sys.exit(1)

    for line in inFile:
        line = line.strip()
        if not line:
            continue
        stuff = split(line, '\t')

        aa = stuff[0]
        graph = Lattice()
        graph.add_node((0, 0, 0))  # always initialize with node (0,0)

        last_first = None
        i = 0
        j = 0
        for option in stuff[1:]:
            option_splited = split(option, ' ')
            first = option_splited[0][0]
            second = option_splited[1][0]
            thirds = option_splited[2]
            n2 = (2, i, GET_ACGU_NUC(second))
            graph.add_node(n2)
            if first != last_first:
                n1 = (1, i, GET_ACGU_NUC(first))
                graph.add_node(n1)
                graph.add_edge((0, 0, 0), n1)
            else:
                n1 = (1, i - 1, GET_ACGU_NUC(first))
            last_first = first
            graph.add_edge(n1, n2)
            for third in thirds:
                n3 = (3, j, GET_ACGU_NUC(third))
                three_nums = first + second + third  # NEW
                graph.add_node(n3)
                graph.codon_by_node3[n3] = three_nums  # NEW
                graph.add_edge(n2, n3)
                graph.add_edge(n3, (0, 0, 0))
                j += 1
            i += 1
        aa_graphs[aa] = graph

    inFile.close()
    return aa_graphs

def read_wheel_with_weights(filename: str,
                            nodes_with_best_weight: Dict[str, Dict[NodeType, float]],
                            edges_with_best_weight: Dict[str, Dict[Tuple[NodeType, NodeType], float]],
                            codon: Codon):
    aa_graphs: Dict[str, Lattice] = {}
    try:
        inFile = open(filename, 'r', encoding='utf-8')
    except:
        raise RuntimeError("Unable to open coding_wheel file\n")

    for line in inFile:
        line = line.strip()
        if not line:
            continue
        stuff = split(line, '\t')
        aa = stuff[0]
        graph = Lattice()
        graph.add_node((0, 0, 0))

        last_first = None
        i = 0
        j = 0
        for option in stuff[1:]:
            option_splited = split(option, ' ')
            first = option_splited[0][0]
            second = option_splited[1][0]
            thirds = option_splited[2]

            n2 = (2, i, GET_ACGU_NUC(second))
            graph.add_node(n2)

            if first != last_first:
                n1 = (1, i, GET_ACGU_NUC(first))
                graph.add_node(n1)
                weight = 0.0
                graph.add_edge((0, 0, 0), n1, weight)
            else:
                n1 = (1, i - 1, GET_ACGU_NUC(first))

            last_first = first
            weight = 0.0
            if (0, 0, 0) in nodes_with_best_weight.get(aa, {}):
                val = edges_with_best_weight[aa].get((n1, n2), 0.0)
                denom = nodes_with_best_weight[aa].get((0, 0, 0), 1.0)
                if denom != 0:
                    weight = val / denom
            graph.add_edge(n1, n2, weight)

            for third in thirds:
                n3 = (3, j, GET_ACGU_NUC(third))
                three_nums = first + second + third  # NEW
                graph.add_node(n3)
                graph.codon_by_node3[n3] = three_nums  # NEW
                weight2 = 0.0
                if n1 in nodes_with_best_weight.get(aa, {}):
                    val = edges_with_best_weight[aa].get((n2, n3), 0.0)
                    denom = nodes_with_best_weight[aa].get(n1, 1.0)
                    if denom != 0:
                        weight2 = val / denom
                graph.add_edge(n2, n3, weight2)

                w = codon.get_weight(aa, three_nums)
                if n2 in nodes_with_best_weight[aa]:
                    denom = nodes_with_best_weight[aa][n2]
                    weight3 = w / denom if denom != 0 else 0.0
                else:
                    weight3 = w
                graph.add_edge(n3, (0, 0, 0), weight3)
                j += 1
            i += 1
        aa_graphs[aa] = graph

    inFile.close()
    return aa_graphs

def read_wheel_with_weights_log(filename: str,
                                nodes_with_best_weight: Dict[str, Dict[NodeType, float]],
                                edges_with_best_weight: Dict[str, Dict[Tuple[NodeType, NodeType], float]],
                                codon: Codon,
                                lambda_: float):
    aa_graphs: Dict[str, Lattice] = {}
    try:
        inFile = open(filename, 'r', encoding='utf-8')
    except:
        raise RuntimeError("Unable to open coding_wheel file\n")

    for line in inFile:
        line = line.strip()
        if not line:
            continue
        stuff = split(line, '\t')
        aa = stuff[0]
        graph = Lattice()
        graph.add_node((0, 0, 0))

        last_first = None
        i = 0
        j = 0
        for option in stuff[1:]:
            option_splited = split(option, ' ')
            first = option_splited[0][0]
            second = option_splited[1][0]
            thirds = option_splited[2]

            n2 = (2, i, GET_ACGU_NUC(second))
            graph.add_node(n2)

            if first != last_first:
                n1 = (1, i, GET_ACGU_NUC(first))
                graph.add_node(n1)
                weight = 1.0
                graph.add_edge((0, 0, 0), n1, lambda_ * math.log(weight))
            else:
                n1 = (1, i - 1, GET_ACGU_NUC(first))
            last_first = first
            weight = 1.0
            if (0, 0, 0) in nodes_with_best_weight.get(aa, {}):
                val = edges_with_best_weight[aa].get((n1, n2), 0.0)
                denom = nodes_with_best_weight[aa].get((0, 0, 0), 1.0)
                if denom != 0:
                    weight = lambda_ * math.log(val / denom)
            graph.add_edge(n1, n2, weight)

            for third in thirds:
                n3 = (3, j, GET_ACGU_NUC(third))
                three_nums = first + second + third  # NEW
                graph.add_node(n3)
                graph.codon_by_node3[n3] = three_nums  # NEW
                weight2 = 1.0
                if n1 in nodes_with_best_weight[aa]:
                    val = edges_with_best_weight[aa].get((n2, n3), 0.0)
                    denom = nodes_with_best_weight[aa].get(n1, 1.0)
                    if denom != 0:
                        weight2 = lambda_ * math.log(val / denom)
                graph.add_edge(n2, n3, weight2)


                w = codon.get_weight(aa, three_nums)
                if n2 in nodes_with_best_weight[aa]:
                    denom = nodes_with_best_weight[aa][n2]
                    if denom != 0:
                        w_log = lambda_ * math.log(w / denom)
                    else:
                        w_log = lambda_ * math.log(w) if w > 0 else 0.0
                else:
                    w_log = lambda_ * math.log(w) if w > 0 else 0.0
                graph.add_edge(n3, (0, 0, 0), w_log)
                j += 1
            i += 1
        aa_graphs[aa] = graph

    inFile.close()
    return aa_graphs

def prepare_codon_unit_lattice(wheel_path: str, codon: Codon,
                               aa_graphs_with_ln_weights_ret,
                               best_path_in_one_codon_unit_ret,
                               aa_best_path_in_a_whole_codon_ret, lambda_: float):
    nodes_with_best_weight: Dict[str, Dict[NodeType, float]] = defaultdict(lambda: defaultdict(float))
    edges_with_best_weight: Dict[str, Dict[Tuple[NodeType, NodeType], float]] = defaultdict(dict)

    aa_graphs_with_weights = read_wheel_with_weights(wheel_path, nodes_with_best_weight, edges_with_best_weight, codon)

    # 更新nodes_with_best_weight, edges_with_best_weight
    for aa, aa_elem in aa_graphs_with_weights.items():
        for node_at_3 in aa_elem.nodes.get(3, []):
            for node_at_4_weight in aa_elem.right_edges[node_at_3]:
                node_at_4, weight = node_at_4_weight
                nodes_with_best_weight[aa][node_at_3] = weight
                edges_with_best_weight[aa][(node_at_3, node_at_4)] = weight

        for node_at_2 in aa_elem.nodes.get(2, []):
            for node_at_3_nuc_weight in aa_elem.right_edges[node_at_2]:
                node_at_3 = node_at_3_nuc_weight[0]
                nodes_with_best_weight[aa][node_at_2] = max(nodes_with_best_weight[aa][node_at_2],
                                                            nodes_with_best_weight[aa][node_at_3])
            for node_at_3_nuc_weight in aa_elem.right_edges[node_at_2]:
                node_at_3 = node_at_3_nuc_weight[0]
                edges_with_best_weight[aa][(node_at_2, node_at_3)] = nodes_with_best_weight[aa][node_at_2]

        for node_at_1 in aa_elem.nodes.get(1, []):
            for node_at_2_nuc_weight in aa_elem.right_edges[node_at_1]:
                node_at_2 = node_at_2_nuc_weight[0]
                nodes_with_best_weight[aa][node_at_1] = max(nodes_with_best_weight[aa][node_at_1],
                                                            nodes_with_best_weight[aa][node_at_2])
            for node_at_2_nuc_weight in aa_elem.right_edges[node_at_1]:
                node_at_2 = node_at_2_nuc_weight[0]
                edges_with_best_weight[aa][(node_at_1, node_at_2)] = nodes_with_best_weight[aa][node_at_1]

        for node_at_0 in aa_elem.nodes.get(0, []):
            for node_at_1_nuc_weight in aa_elem.right_edges[node_at_0]:
                node_at_1 = node_at_1_nuc_weight[0]
                nodes_with_best_weight[aa][node_at_0] = max(nodes_with_best_weight[aa][node_at_0],
                                                            nodes_with_best_weight[aa][node_at_1])
            for node_at_1_nuc_weight in aa_elem.right_edges[node_at_0]:
                node_at_1 = node_at_1_nuc_weight[0]
                edges_with_best_weight[aa][(node_at_0, node_at_1)] = nodes_with_best_weight[aa][node_at_0]

    aa_graphs_with_ln_weights = read_wheel_with_weights_log(wheel_path, nodes_with_best_weight, edges_with_best_weight,
                                                            codon, lambda_)

    best_path_in_one_codon_unit = defaultdict(dict)
    neg_inf = float('-inf')

    def update_best_path(aa_, n1, n2, val, nuc1, nuc2, nuc3):
        if (n1, n2) not in best_path_in_one_codon_unit[aa_]:
            best_path_in_one_codon_unit[aa_][(n1, n2)] = (neg_inf, k_void_nuc, k_void_nuc, k_void_nuc)
        current_val = best_path_in_one_codon_unit[aa_][(n1, n2)][0]
        if val > current_val:
            best_path_in_one_codon_unit[aa_][(n1, n2)] = (val, nuc1, nuc2, nuc3)

    # 根据原C++逻辑更新 best_path_in_one_codon_unit
    for aa, graph in aa_graphs_with_ln_weights.items():
        # 0->1 edges
        for node_0 in graph.nodes.get(0, []):
            for node_1_log_w in graph.right_edges[node_0]:
                node_1, log_weight = node_1_log_w
                nuc_0 = node_0[2]
                update_best_path(aa, node_0, node_1, log_weight, nuc_0, k_void_nuc, k_void_nuc)

        # 1->2 edges
        for node_1 in graph.nodes.get(1, []):
            for node_2_log_w in graph.right_edges[node_1]:
                node_2, log_weight = node_2_log_w
                nuc_1 = node_1[2]
                update_best_path(aa, node_1, node_2, log_weight, nuc_1, k_void_nuc, k_void_nuc)

        # 2->3 edges
        for node_2 in graph.nodes.get(2, []):
            for node_3_log_w in graph.right_edges[node_2]:
                node_3, log_weight = node_3_log_w
                nuc_2 = node_2[2]
                update_best_path(aa, node_2, node_3, log_weight, nuc_2, k_void_nuc, k_void_nuc)

        # 3->0 edges
        for node_3 in graph.nodes.get(3, []):
            for node_4_log_w in graph.right_edges[node_3]:
                node_4, log_weight = node_4_log_w
                nuc_3 = node_3[2]
                update_best_path(aa, node_3, node_4, log_weight, nuc_3, k_void_nuc, k_void_nuc)

        # 下方类似的模式重复，依照原代码逐步累加路径并更新 best_path_in_one_codon_unit
        # ... (由于代码量较大，这里不逐行注释，逻辑与 C++ 完全对应)

        # (0->1->2)
        for node_0 in graph.nodes.get(0, []):
            for node_1_log_w0 in graph.right_edges[node_0]:
                node_1, w0 = node_1_log_w0
                nuc_0 = node_0[2]
                for node_2_log_w1 in graph.right_edges[node_1]:
                    node_2, w1 = node_2_log_w1
                    nuc_1 = node_1[2]
                    update_best_path(aa, node_0, node_2, w0 + w1, nuc_0, nuc_1, k_void_nuc)

        # (1->2->3)
        for node_1 in graph.nodes.get(1, []):
            for node_2_log_w1 in graph.right_edges[node_1]:
                node_2, w1 = node_2_log_w1
                nuc_1 = node_1[2]
                for node_3_log_w2 in graph.right_edges[node_2]:
                    node_3, w2 = node_3_log_w2
                    nuc_2 = node_2[2]
                    update_best_path(aa, node_1, node_3, w1 + w2, nuc_1, nuc_2, k_void_nuc)

        # (2->3->0)
        for node_2 in graph.nodes.get(2, []):
            for node_3_log_w2 in graph.right_edges[node_2]:
                node_3, w2 = node_3_log_w2
                nuc_2 = node_2[2]
                for node_4_log_w3 in graph.right_edges[node_3]:
                    node_4, w3 = node_4_log_w3
                    nuc_3 = node_3[2]
                    update_best_path(aa, node_2, node_4, w2 + w3, nuc_2, nuc_3, k_void_nuc)

        # (0->1->2->3)
        for node_0 in graph.nodes.get(0, []):
            for node_1_log_w0 in graph.right_edges[node_0]:
                node_1, w0 = node_1_log_w0
                nuc_0 = node_0[2]
                for node_2_log_w1 in graph.right_edges[node_1]:
                    node_2, w1 = node_2_log_w1
                    nuc_1 = node_1[2]
                    for node_3_log_w2 in graph.right_edges[node_2]:
                        node_3, w2 = node_3_log_w2
                        nuc_2 = node_2[2]
                        update_best_path(aa, node_0, node_3, w0 + w1 + w2, nuc_0, nuc_1, nuc_2)

        # (1->2->3->0)
        for node_1 in graph.nodes.get(1, []):
            for node_2_log_w1 in graph.right_edges[node_1]:
                node_2, w1 = node_2_log_w1
                nuc_1 = node_1[2]
                for node_3_log_w2 in graph.right_edges[node_2]:
                    node_3, w2 = node_3_log_w2
                    nuc_2 = node_2[2]
                    for node_4_log_w3 in graph.right_edges[node_3]:
                        node_4, w3 = node_4_log_w3
                        nuc_3 = node_3[2]
                        update_best_path(aa, node_1, node_4, w1 + w2 + w3, nuc_1, nuc_2, nuc_3)

    max_path = defaultdict(float)
    aa_best_path_in_a_whole_codon = {}
    # codon.aa_table_ assumed to be dict: {aa: [(codon_str,freq), ...]}
    for aa, paths in codon.aa_table_.items():
        for (cstr, freq) in paths:
            if freq > max_path[aa]:
                max_path[aa] = freq
                aa_best_path_in_a_whole_codon[aa] = cstr

    aa_graphs_with_ln_weights_ret.clear()
    aa_graphs_with_ln_weights_ret.update(aa_graphs_with_ln_weights)

    best_path_in_one_codon_unit_ret.clear()
    best_path_in_one_codon_unit_ret.update(best_path_in_one_codon_unit)

    aa_best_path_in_a_whole_codon_ret.clear()
    aa_best_path_in_a_whole_codon_ret.update(aa_best_path_in_a_whole_codon)

def get_dfa(aa_graphs: Dict[str, Lattice], aa_seq: List[str]) -> DFA:
    dfa = DFA()
    dfa1 = DFA()
    newnode = (4 * len(aa_seq), 0, 0)
    dfa.add_node(newnode)
    i = 0
    for item in aa_seq:
        i4 = i * 4
        aa = aa_seq[i]
        graph = aa_graphs[aa]
        for pos in range(4):
            for node in graph.nodes.get(pos, []):
                num = node[1]
                nuc = node[2]
                newnode = (i4 + pos, num, nuc)
                dfa.add_node(newnode)
                # NEW: 若是第三位（pos==3），把该节点对应的完整密码子带过来
                if pos == 3:
                    cod3 = graph.codon_by_node3.get(node)
                    if cod3:
                        dfa.codon_at_node3[newnode] = cod3
                for edge in graph.right_edges[node]:
                    n2, w = edge
                    num2 = n2[1]
                    newn2 = (i4 + pos + 1, num2, n2[2])
                    dfa.add_edge(newnode, newn2, w)
        i += 1

    j = 0
    endn = (3 * len(aa_seq), 0, 0)
    dfa1.add_node(endn)
    for i in range(0, len(aa_seq) * 4, 4):
        for pos in range(1, 4):
            for node in dfa.nodes[i + pos]:
                num = node[1]
                nuc = node[2]
                newnode = (j + pos - 1, num, nuc)
                dfa1.add_node(newnode)
                # NEW: 若是第三位（pos==3），继续把 codon 标注带入 dfa1
                if pos == 3:
                    cod3 = dfa.codon_at_node3.get(node)
                    if cod3:
                        dfa1.codon_at_node3[newnode] = cod3
                if pos != 3:
                    for edge in dfa.right_edges[node]:
                        n2, w = edge
                        num2 = n2[1]
                        newn2 = (j + pos, num2, n2[2])
                        dfa1.add_edge(newnode, newn2, w)
                else:
                    for edge in dfa.right_edges[node]:
                        n2, w = edge
                        if i + 5 < 4 * len(aa_seq):
                            for n_node in dfa.nodes[i + 5]:
                                num2 = n_node[1]
                                newn2 = (j + pos, num2, n_node[2])
                                dfa1.add_edge(newnode, newn2, w)
                        else:
                            dfa1.add_edge(newnode, endn, w)
        j += 3

    return dfa1

def get_rna_dfa(rna_seq: str) -> DFA:
    dfa = DFA()
    endnode = (len(rna_seq), 0, 0)
    dfa.add_node(endnode)
    i = 0
    for item in rna_seq:
        nuc = GET_ACGU_NUC(item)
        newnode = (i, 0, nuc)
        dfa.add_node(newnode)
        if i==len(rna_seq)-1:
            dfa.add_edge(newnode, endnode, 0.0)
        else:
            new2 = (i+1,0,GET_ACGU_NUC(rna_seq[i+1]))
            dfa.add_edge(newnode, new2, 0.0)
        i += 1

    return dfa

def _pick_best_path_for_codon(graph: Lattice, codon_str: str):
    """
    在一个氨基酸的 Lattice 中，找出能组成 codon_str 的所有 0->1->2->3 路径中（权重和最大）的那条，
    返回 (n1, n2, n3, w01, w12, w23)。若不存在则返回 None。
    """
    from .utility_v import GET_ACGU
    codon_str = codon_str.upper()
    if len(codon_str) != 3:
        return None

    b1, b2, b3 = codon_str[0], codon_str[1], codon_str[2]
    node0 = (0, 0, 0)
    best = None
    # 所有 0->1
    for n1, w01 in graph.right_edges.get(node0, []):
        if n1[0] != 1 or GET_ACGU(n1[2]) != b1:
            continue
        # 所有 1->2
        for n2, w12 in graph.right_edges.get(n1, []):
            if n2[0] != 2 or GET_ACGU(n2[2]) != b2:
                continue
            # 所有 2->3
            for n3, w23 in graph.right_edges.get(n2, []):
                if n3[0] != 3 or GET_ACGU(n3[2]) != b3:
                    continue
                # 确保 3->0 存在
                has_30 = False
                for n4, _w30 in graph.right_edges.get(n3, []):
                    if n4 == node0:
                        has_30 = True
                        break
                if not has_30:
                    continue
                score = (w01 or 0.0) + (w12 or 0.0) + (w23 or 0.0)
                if (best is None) or (score > best[-1]):
                    best = (n1, n2, n3, w01, w12, w23, score)

    if best is None:
        return None
    n1, n2, n3, w01, w12, w23, _ = best
    return n1, n2, n3, w01, w12, w23

def _build_single_path_lattice(graph: Lattice, codon_str: str) -> Lattice:
    """
    基于原 graph，抽取指定 codon 的唯一 0->1->2->3 路径，构造一个只包含该路径的 Lattice。
    复制原有边权；保留 codon_by_node3 标注。
    """
    picked = _pick_best_path_for_codon(graph, codon_str)
    if picked is None:
        raise ValueError(f"No path for codon {codon_str} in this amino-acid lattice.")
    n1, n2, n3, w01, w12, w23 = picked

    newg = Lattice()
    node0 = (0, 0, 0)
    # 加点
    newg.add_node(node0)
    newg.add_node(n1)
    newg.add_node(n2)
    newg.add_node(n3)
    # 复制 codon 标注
    if n3 in graph.codon_by_node3:
        newg.codon_by_node3[n3] = graph.codon_by_node3[n3]
    else:
        # 兜底：直接写入传入的 codon_str
        newg.codon_by_node3[n3] = codon_str.upper()

    # 加边：0->1, 1->2, 2->3, 3->0（权重取原图）
    newg.add_edge(node0, n1, w01 or 0.0)
    newg.add_edge(n1, n2, w12 or 0.0)
    newg.add_edge(n2, n3, w23 or 0.0)
    # 找出 3->0 原始权重
    w30 = 0.0
    for nxt, w in graph.right_edges.get(n3, []):
        if nxt == node0:
            w30 = w or 0.0
            break
    newg.add_edge(n3, node0, w30)
    return newg

def get_dfa_with_codon_overrides(
    aa_graphs: Dict[str, Lattice],
    aa_seq: List[str],
    codon_overrides: Dict[int, str],
    validate_aa: Optional[Dict[int, str]] = None,
) -> DFA:
    """
    与 get_dfa 等价，但允许对某些 AA 位置（1-based）强制使用指定密码子。
    - aa_graphs: 通常传 prepare_codon_unit_lattice() 得到的 ln 权重图（值是 Lattice）
    - aa_seq:    轮盘里使用的氨基酸标签序列（如 ["Phe","Leu","Ser", ...]）
    - codon_overrides: { index(1-based) : "AUG"/"CUA"/... }
    - validate_aa: 可选 { index : "L"/"M"/... }，用于与 aa_seq 做一致性校验（不影响构图）
    """
    from .utility_v import GET_ACGU  # 仅为一致性；本函数不直接使用

    dfa = DFA()
    dfa1 = DFA()

    # 先把“平铺版 dfa”建起来：遇到 override 的位置，动态用“单路径子图”
    newnode = (4 * len(aa_seq), 0, 0)
    dfa.add_node(newnode)

    for i, aa in enumerate(aa_seq):
        i4 = i * 4

        # ——可选：用 validate_aa 做一下人类可读一致性检查（不报错，只警告）
        if validate_aa and (i + 1) in validate_aa:
            aa_letter = validate_aa[i + 1].upper()
            wheel_name = SINGLE_TO_WHEEL.get(aa_letter)
            if wheel_name and (wheel_name != aa):
                print(f"[WARN] override at pos {i+1}: CSV AA={aa_letter} -> {wheel_name}, "
                      f"but aa_seq uses '{aa}'. Proceeding anyway.")

        base_graph = aa_graphs[aa]
        graph_to_use = base_graph
        if (i + 1) in codon_overrides:
            cod = codon_overrides[i + 1].upper()
            try:
                graph_to_use = _build_single_path_lattice(base_graph, cod)
            except Exception as e:
                raise RuntimeError(f"Failed to apply codon override at AA pos {i+1} ({aa}): {e}")

        # 和 get_dfa 同构的平铺逻辑
        for pos in range(4):
            for node in graph_to_use.nodes.get(pos, []):
                num = node[1]
                nuc = node[2]
                newnode = (i4 + pos, num, nuc)
                dfa.add_node(newnode)
                # pos==3 节点把完整密码子带过来（后续会被 get_dfa 的第二阶段继承）
                if pos == 3:
                    cod3 = graph_to_use.codon_by_node3.get(node)
                    if cod3:
                        dfa.codon_at_node3[newnode] = cod3
                for edge in graph_to_use.right_edges[node]:
                    n2, w = edge
                    num2 = n2[1]
                    newn2 = (i4 + pos + 1, num2, n2[2])
                    dfa.add_edge(newnode, newn2, w)

    # 滑窗得到“压平后按 RNA 位置计数”的 DFA（完全复用原 get_dfa 第二阶段）
    j = 0
    endn = (3 * len(aa_seq), 0, 0)
    dfa1.add_node(endn)
    for i in range(0, len(aa_seq) * 4, 4):
        for pos in range(1, 4):
            for node in dfa.nodes[i + pos]:
                num = node[1]
                nuc = node[2]
                newnode = (j + pos - 1, num, nuc)
                dfa1.add_node(newnode)
                if pos == 3:
                    cod3 = dfa.codon_at_node3.get(node)
                    if cod3:
                        dfa1.codon_at_node3[newnode] = cod3
                if pos != 3:
                    for edge in dfa.right_edges[node]:
                        n2, w = edge
                        num2 = n2[1]
                        newn2 = (j + pos, num2, n2[2])
                        dfa1.add_edge(newnode, newn2, w)
                else:
                    for edge in dfa.right_edges[node]:
                        _n2, w = edge
                        if i + 5 < 4 * len(aa_seq):
                            for n_node in dfa.nodes[i + 5]:
                                num2 = n_node[1]
                                newn2 = (j + pos, num2, n_node[2])
                                dfa1.add_edge(newnode, newn2, w)
                        else:
                            dfa1.add_edge(newnode, endn, w)
        j += 3

    return dfa1

# === NEW: 读取 CSV 的小工具 ===
def load_codon_overrides_csv(csv_path: str):
    """
    读取形如：
      index,AA,codon
      1,L,CUA
    的 CSV，返回 (overrides, aa_letters) 两个字典：
      overrides: { index(int) : codon(str) }
      aa_letters: { index(int) : 'L'/'M'/... } 便于可选校验
    """
    import csv
    overrides = {}
    aa_letters = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row["index"])
            aa = row.get("AA", "").strip()
            codon = row["codon"].strip().upper()
            if len(codon) != 3:
                raise ValueError(f"Bad codon '{codon}' at index {idx}")
            overrides[idx] = codon
            if aa:
                aa_letters[idx] = aa.upper()
    return overrides, aa_letters


# 新增函数：根据DFA和RNA序列遍历并累加边权重
def get_rna_weight_from_dfa(dfa: DFA, rna_seq: str) -> float:
    """
    Traverse the DFA according to the RNA sequence and sum edge weights.
    """
    from .utility_v import GET_ACGU_NUC
    weight_sum = 0.0
    # 对于 RNA 序列中的每个碱基，找到对应位置的节点，并累加其到下一个位置的边权重

    for i in range(len(rna_seq)):
        if i%3==0:
            for node_i in dfa.nodes[i]:
                nuc_i = GET_ACGU(node_i[2])
                if nuc_i != rna_seq[i]:
                    continue
                for i1_node_wnuci in dfa.right_edges.get(node_i, []):
                    node_i1 = i1_node_wnuci[0]
                    nuc_i1 = GET_ACGU(node_i1[2])
                    weight_nuci = i1_node_wnuci[1]
                    if nuc_i1 != rna_seq[i+1]:
                        continue
                    for i2_node_wnuci1 in dfa.right_edges.get(node_i1, []):
                        node_i2 = i2_node_wnuci1[0]
                        nuc_i2 = GET_ACGU(node_i2[2])
                        weight_nuci1 = i2_node_wnuci1[1]
                        if nuc_i2 != rna_seq[i + 2]:
                            continue
                        for i3_node_wnuci2 in dfa.right_edges.get(node_i2, []):
                            node_i3 = i3_node_wnuci2[0]
                            weight_nuci2 = i3_node_wnuci2[1]
                            if i+3 <len(rna_seq):
                                nuc_i3 = GET_ACGU(node_i3[2])
                                if nuc_i3 != rna_seq[i+3]:
                                    continue
                                weight_sum += weight_nuci + weight_nuci1 + weight_nuci2
                            else:
                                weight_sum += weight_nuci + weight_nuci1 + weight_nuci2
                                break
    return weight_sum

def dump_dfa(dfa: DFA, title: str = "", ctx_stride: Optional[int] = None) -> None:
    """
    打印 DFA 的所有节点及其右边的边和权重。
    - dfa: DFA 实例
    - title: 打印块标题
    - ctx_stride: 若是 trigram 提升后的 DFA，请传入 lift_dfa_with_trigram 使用的 ctx_stride（默认 100000）；
                  传入后会把 num 拆成 base_num 与 ctx_id，便于观察上下文版本。
    """
    if title:
        print(f"=== {title} ===")
    for idx in sorted(dfa.nodes.keys()):
        for node in dfa.nodes[idx]:
            i, num, nuc = node
            base = GET_ACGU(nuc)
            if ctx_stride:
                ctx_id = num // ctx_stride
                base_num = num % ctx_stride
                num_repr = f"{num} (base_num={base_num}, ctx_id={ctx_id})"
            else:
                num_repr = str(num)

            codon = dfa.codon_at_node3.get(node)
            codon_info = f"  [codon={codon}]" if codon else ""
            print(f"{i},{num_repr},{base}{codon_info}")

            for nxt, w in dfa.right_edges.get(node, []):
                i2, num2, nuc2 = nxt
                base2 = GET_ACGU(nuc2)
                if ctx_stride:
                    ctx_id2 = num2 // ctx_stride
                    base_num2 = num2 % ctx_stride
                    num2_repr = f"{num2} (base_num={base_num2}, ctx_id={ctx_id2})"
                else:
                    num2_repr = str(num2)
                print(f"{i2},{num2_repr},{base2},{w}")
            print(".........")

if __name__ == "__main__":
    # 假设当前目录下有:
    codon_file = settings.get_abs_home() / "codon_usage_freq_table_human.csv"
    coding_wheel_file = settings.get_abs_home() / "coding_wheel.txt"

    # 初始化 Codon 类
    try:
        codon_obj = Codon(codon_file)
        print("Codon class initialized successfully with", codon_file)
    except Exception as e:
        print("Error initializing Codon class:", e)
        sys.exit(1)

    # 测试 read_wheel 函数
    try:
        aa_graphs = read_wheel(coding_wheel_file)
        if aa_graphs:
            print("read_wheel test passed. Loaded amino acid graphs from", coding_wheel_file)
        else:
            print("read_wheel returned empty results.")
    except Exception as e:
        print("read_wheel test failed:", e)
        sys.exit(1)

    # 准备测试 prepare_codon_unit_lattice 函数
    aa_graphs_with_ln_weights = {}
    best_path_in_one_codon_unit = {}
    aa_best_path_in_a_whole_codon = {}
    lambda_val = 0.0  # 示例 lambda

    try:
        prepare_codon_unit_lattice(coding_wheel_file, codon_obj,
                                   aa_graphs_with_ln_weights,
                                   best_path_in_one_codon_unit,
                                   aa_best_path_in_a_whole_codon,
                                   lambda_val)
        print("prepare_codon_unit_lattice test passed.")
        print("Keys in aa_graphs_with_ln_weights:", aa_graphs_with_ln_weights.keys())

        print("Keys in best_path_in_one_codon_unit:", best_path_in_one_codon_unit.keys())

        print("Keys in aa_best_path_in_a_whole_codon:", aa_best_path_in_a_whole_codon.keys())
        # 打印 aa_best_path_in_a_whole_codon["A"]
        if "A" in aa_best_path_in_a_whole_codon:
            print("aa_best_path_in_a_whole_codon['A']:", aa_best_path_in_a_whole_codon["A"])
        else:
            print("aa_best_path_in_a_whole_codon['A'] not found")

    except Exception as e:
        print("prepare_codon_unit_lattice test failed:", e)

    # 测试 get_dfa 函数
    # 假设coding_wheel.txt中包含这些氨基酸 "Phe", "Leu", "Ser"。
    def print_dfa_details(dfa, GET_ACGU_func) -> None:
        """
        打印 DFA 的详细信息，包括每个节点及其右边的边缘。

        参数：
        - dfa: DFA 类的实例，包含 "nodes" 和 "right_edges"。
        - GET_ACGU_func: 函数，将 nuc 转换为对应的碱基字符。
        """
        for i in range(31):
            nodes_i = dfa.nodes.get(i, [])
            for node in nodes_i:
                index, num, nuc = node[0], node[1], node[2]
                print(f"{index},{num},{GET_ACGU_func(nuc)}")
                # 获取当前节点的右边边缘
                right_edges = dfa.right_edges.get(node, [])
                for node_right, weight in right_edges:
                    index_nr, num_nr, nuc_nr = node_right[0], node_right[1], node_right[2]
                    print(f"{index_nr},{num_nr},{GET_ACGU_func(nuc_nr)},{weight}")
                print(".........")

    aa_seq_list = ["Phe", "Leu", "Ser"]
    try:
        dfa = get_dfa(aa_graphs_with_ln_weights, aa_seq_list)
        print("get_dfa test passed. DFA constructed for aa_seq_list =", aa_seq_list)
        # 打印DFA节点数量以验证结果
        total_nodes = sum(len(v) for v in dfa.nodes.values())
        print("Number of nodes in constructed DFA:", total_nodes)
        print("\nDFA Nodes and Right Edges:")
        print_dfa_details(dfa, GET_ACGU)
    except Exception as e:
        print("get_dfa test failed:", e)

    # 简单测试 codon 的函数
    test_rna_seq = "AUGGCCUAA"  # Met-Ala-STOP 的假设RNA序列
    try:
        cai_val = codon_obj.calc_cai(test_rna_seq)
        print("calc_cai test: RNA seq =", test_rna_seq, "CAI =", cai_val)
        #print("cvt_rna_seq_to_aa_seq test: RNA seq =", test_rna_seq, "AA seq =", aa_seq_converted)
    except Exception as e:
        print("Codon object function tests failed:", e)

    # 测试 get_weight函数 (示例，需对照真实数据)
    try:
        # 假设 'Ala' -> 'GCU' 密码子存在于codon频率表
        weight = codon_obj.get_weight("Ala", "GCU")
        print("get_weight test: Ala-GCU weight =", weight)
    except Exception as e:
        print("get_weight test failed:", e)

    print("All tests completed.")

    test_rna_seq = "AUGGCCUAA"
    try:
        rna_dfa = get_rna_dfa(test_rna_seq)
        print("get_dfa test passed. DFA constructed for rna_seq=", test_rna_seq)
        # 打印DFA节点数量以验证结果
        total_nodes = sum(len(v) for v in rna_dfa.nodes.values())
        print("Number of nodes in constructed DFA:", total_nodes)
        print("\nDFA Nodes and Right Edges:")
        print_dfa_details(rna_dfa, GET_ACGU)
    except Exception as e:
        print("get_dfa test failed:", e)

    # 测试 get_rna_weight_from_dfa 函数
    # try:
    #     from codon import cvt_to_seq
    #     aa_seq = "MGINTRELFLNFTIVLITVILMWLLVRSYQY*"
    #     success, aa_tri_seq = cvt_to_seq(aa_seq)
    #     aa_seq_list = split(aa_tri_seq, ' ')
    #     test_rna = "AUGGGGAUCAACACGAGGGAGUUGUUCCUCAACUUCACCAUCGUGUUGAUCACCGUGAUACUGAUGUGGCUGCUGGUGCGGUCAUAUCAGUAUUGA"  # 与上面相同序列
    #     dfa = get_dfa(aa_graphs_with_ln_weights, aa_seq_list)
    #     weight = get_rna_weight_from_dfa(dfa, test_rna)
    #     print(f"get_rna_weight_from_dfa test: RNA seq = {test_rna}, Weight sum = {weight}")
    # except Exception as e:
    #     print("get_rna_weight_from_dfa test failed:", e)

    # ===== Trigram LM smoke test: 基于扩展 DFA（不改 parser） =====

    # try:
    #     import os
    #     from codon import cvt_to_seq
    #
    #     # 1) 写一个最小的三密码子概率表（含起始 <s> 上下文）
    #     trigram_csv = "codon_trigram_lung_usage_freq_table.csv"
    #     if not os.path.exists(trigram_csv):
    #         with open(trigram_csv, "w", encoding="utf-8") as f:
    #             f.write("codon1,codon2,codon3,frequency,fraction\n")
    #             # 起始 -> AUG
    #             f.write("<s>,<s>,AUG,1000,0.10\n")
    #             # AUG 之后 -> UUA（Leu）
    #             f.write("<s>,AUG,UUA,800,0.08\n")
    #             # UUA 之后 -> AGC（Ser）
    #             f.write("AUG,UUA,AGC,900,0.09\n")
    #             # AGC 之后 -> UAA（Stop）
    #             f.write("UUA,AGC,UAA,1200,0.12\n")
    #
    #     # 2) 准备三密码子打分器（插值回退 + CAI 先验，γ * log 相对适应度）
    #     # 使用 lung 特异的单密码子使用表（包含 frequency 与 fraction）
    #     usage_csv = "./codon_usage_freq_table_human_lung.csv"
    #     trigram = CodonTrigramScorer(
    #         trigram_csv,
    #         codon_obj,
    #         usage_csv=usage_csv,
    #         gamma=10.0,     # 适当的尺度
    #         alpha=5.0,      # 稀疏上下文时更依赖回退
    #         eta2=0.6, eta1=0.3, eta_cai=0.1,
    #         wmin=1e-6
    #     )
    #
    #     # 3) 小例子：Met–Ala–STOP -> RNA: AUGGCCUAA
    #     rna_small = "AUGCCUAAUACCCUUUAG"
    #     ok_small, aa_tri_small = cvt_to_seq("MPNTL*")         # 用你的工具把 "MA*" 变成轮盘里用的氨基酸标签
    #     if not ok_small:
    #         raise RuntimeError("cvt_to_seq('MPNTL*') 失败，无法生成小例子的 AA 标签")
    #     aa_seq_small = split(aa_tri_small, ' ')            # e.g. ["Met","Ala","STOP"]（视 coding_wheel 而定）
    #     print(f"[Smoke] total_codons={len(aa_seq_small)}  aa_seq_small={aa_seq_small}")
    #
    #     # 4) 构建原始 DFA 与加入三联体后的 DFA
    #     dfa_small_base = get_dfa(aa_graphs_with_ln_weights, aa_seq_small)
    #     dfa_small_tri  = lift_dfa_with_trigram(dfa_small_base, trigram)  # 或者：get_dfa_with_trigram(...)
    #
    #     dump_dfa(dfa_small_base, "BASE DFA (no trigram)")
    #     dump_dfa(dfa_small_tri, "TRIGRAM DFA (lifted)", ctx_stride=100000)  # 若你修改过 ctx_stride，请对应修改
    #
    #     # ==== 可视化（生成 PNG；若未安装 graphviz，则生成 DOT 文件） ====
    #     try:
    #         base_viz = visualize_dfa(
    #             dfa_small_base,
    #             out_prefix="./viz_dfa_base",
    #             title="BASE DFA (no trigram)",
    #             ctx_stride=None,
    #             full=True  # 完整输出
    #         )
    #         tri_viz = visualize_dfa(
    #             dfa_small_tri,
    #             out_prefix="./viz_dfa_trigram",
    #             title="TRIGRAM DFA (lifted)",
    #             ctx_stride=100000,  # 与提升时的 ctx_stride 保持一致
    #             full=True  # 完整输出，确保最后一个密码子显示
    #         )
    #         print(f"[Viz] BASE DFA figure -> {base_viz}")
    #         print(f"[Viz] TRIGRAM DFA figure -> {tri_viz}")
    #     except Exception as e_vis:
    #         print("Visualization failed:", e_vis)
    #
    #     # 5) 计算并对比两者的权重（权重里已包含 CAI + 3-gram 代价；3-gram 只加在“闭合一个密码子”的边上）
    #     w_base = get_rna_weight_from_dfa(dfa_small_base, rna_small)
    #     w_tri  = get_rna_weight_from_dfa(dfa_small_tri,  rna_small)
    #
    #     print(f"[Trigram smoke] RNA={rna_small} | base={w_base:.6f} | with_trigram={w_tri:.6f} | Δ={w_tri - w_base:.6f}")
    #
    # except Exception as e:
    #     print("Trigram smoke test failed:", e)

    # === (Optional) export trigram weights for parser; safe try/except wrapper ===
    # === (Optional) export trigram weights for parser; safe try/except wrapper ===

    # ====== NEW: 简单测试（强制第 2 位氨基酸使用指定密码子） ======

    #test get_dfa_with_codon_overrides()
    try:
        # 1) 用已有流程准备 ln 权重轮盘
        aa_graphs_with_ln_weights = {}
        best_path_in_one_codon_unit = {}
        aa_best_path_in_a_whole_codon = {}
        lambda_val = 0.0
        prepare_codon_unit_lattice(coding_wheel_file, codon_obj,
                                   aa_graphs_with_ln_weights,
                                   best_path_in_one_codon_unit,
                                   aa_best_path_in_a_whole_codon,
                                   lambda_val)

        # 2) 选择一个很短的 AA 序列，例如 "MP*"（只是示例；需在你的 coding_wheel 中存在）
        from .codon import cvt_to_seq
        ok, aa_tri = cvt_to_seq("MP*")   # 例如 "Met Pro STOP"
        if not ok:
            raise RuntimeError("cvt_to_seq('MP*') 失败，请换一个短序列测试")
        aa_seq_list = split(aa_tri, ' ')   # e.g. ["Met","Pro","STOP"]

        # 3) 强制第二位（Pro）为 CCA（只是示例；请确保该 AA 支持该密码子）
        overrides = {2: "CCA"}
        aa_letters = {2: "P"}

        dfa_over = get_dfa_with_codon_overrides(
            aa_graphs_with_ln_weights,
            aa_seq_list,
            overrides,
            validate_aa=aa_letters
        )
        print("[TEST] DFA with codon override constructed.")

        # 4) 验证：第二位的第三个核苷酸层（索引 j+2）上，codon 标注应为 CCA
        #    在 dfa1 中，第 k(1-based) 个 AA 的 3 个核苷酸层索引为: base = 3*(k-1) -> base, base+1, base+2
        k = 2
        idx3 = 3*(k-1) + 2
        found = set()
        for node in dfa_over.nodes.get(idx3, []):
            cod = dfa_over.codon_at_node3.get(node)
            if cod:
                found.add(cod)
        print(f"[TEST] AA pos {k} (idx={idx3}) codons seen at pos3:", found)
        assert found == {"CCA"}, f"Expected only CCA, got {found}"
        print("[TEST] OK: override enforced.")
    except Exception as e:
        print("Override test failed:", e)

