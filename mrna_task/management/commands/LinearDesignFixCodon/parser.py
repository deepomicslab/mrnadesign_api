from typing import Tuple, Dict, List, Set
from collections import defaultdict
from .utility_v_op import *
from .common import IndexType, NucType, BeamType, QNodeNucs, NodeType, BacktraceResult, NodeNucpair, State, ScoreType,FinalScoreType
from .codon import Codon, split, k_void_nuc, k_map_3_1
from . import struct_parser
import time
import os

INT_MIN = -2 ** 31
NextPair_t = List[Dict[NodeType, List[Tuple[NodeType, NucType, float]]]]
NextPairSet_t = List[Dict[NodeType, Set[Tuple[NodeType, NucType, float]]]]
_allowed_pairs = [[False for _ in range(NOTON)] for _ in range(NOTON)]
_allowed_pairs[0] = [0, 0, 0, 0, 0]
_allowed_pairs[1] = [0, 0, 0, 0, 1]
_allowed_pairs[2] = [0, 0, 0, 1, 0]
_allowed_pairs[3] = [0, 0, 1, 0, 1]
_allowed_pairs[4] = [0, 1, 0, 1, 0]

class BeamCKYParser:
    def __init__(self, lambda_value: float, verbose: bool, best_path_in_one_codon, aa_best_path_in_a_whole_codon, params):
        self.lambda_value = lambda_value
        self.verbose = verbose
        self.seq_length = 0
        self.protein: List[str] = []
        self.NOTON = NOTON
        #self._allowed_pairs = [[1 for _ in range(NOTON)] for _ in range(NOTON)]
        # 初始化各类最佳路径字典
        self.bestH = struct_parser.BestX_t_CAI()
        self.bestP = struct_parser.BestX_t_CAI()
        self.bestMulti = struct_parser.BestX_t_CAI()
        self.bestM = struct_parser.BestM_t_CAI()
        self.bestM2 = struct_parser.BestM_t_CAI()
        self.bestM_P = struct_parser.BestM_t_CAI()
        self.bestC = struct_parser.BestC_t_CAI()

        self.best_path_in_one_codon_unit = best_path_in_one_codon
        self.aa_best_path_in_a_whole_codon = aa_best_path_in_a_whole_codon

        # 初始化 next_pair 和 prev_pair
        self.next_pair: NextPair_t = [defaultdict(list) for _ in range(5)]  # 索引0未使用
        self.next_pair_set: NextPairSet_t = [defaultdict(set) for _ in range(5)]
        self.prev_pair: NextPair_t = [defaultdict(list) for _ in range(5)]
        self.prev_pair_set: NextPairSet_t = [defaultdict(set) for _ in range(5)]
        self.prev_list: NextPair_t = [defaultdict(list) for _ in range(5)]
        self.next_list: NextPair_t = [defaultdict(list) for _ in range(5)]

        # 初始化 hairpin_seq_score_cai
        # self.hairpin_seq_score_cai = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  #修改
        self.hairpin_seq_score_cai: Dict[
            NodeType,
            Dict[
                NodeType,
                Dict[int, List[Tuple[str, ScoreType, FinalScoreType]]]
            ]
        ] = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )

        self.get_broken_codon_score_map = defaultdict(lambda: defaultdict(float))

        # 初始化 stacking_score 和 bulge_score
        self.stacking_score = [[0 for _ in range(6)] for _ in range(6)]
        self.bulge_score = [[[0 for _ in range(SINGLE_MAX_LEN + 1)] for _ in range(6)] for _ in range(6)]
        # self.bulge_score: List[List[List[int]]] = []

        # 初始化其他必要的变量
        self.tetra_hex_tri = -1  # 根据实际情况初始化

        self.func9 = func9(0, 0)
        self.params = params

        # —— 与上下文有关的小工具：与 dfa_network 的 lift_dfa_with_trigram(ctx_stride=100000) 保持一致 ——
        self.ctx_stride = 100000  # 如果你在 dfa_network 里改了，这里也要一致

        def base_num_fn(num: int, stride: int = None) -> int:
            return num % (stride or self.ctx_stride)

        self.base_num = lambda n: base_num_fn(n)
        self.same_num = lambda a, b: (self.base_num(a) == self.base_num(b))

        # —— “活跃键”索引：只遍历真的存在的状态 ——

        self.alive_H = defaultdict(set)  # key = j_node,   val = set of temppair
        self.alive_P = defaultdict(set)  # key = j_node,   val = set of temppair
        self.alive_Multi = defaultdict(set)  # key = j_node,   val = set of temppair
        self.alive_M = defaultdict(set)  # key = j_node,   val = set of temppair
        self.alive_M2 = defaultdict(set)  # key = j_node,   val = set of temppair
        self.alive_M_P = defaultdict(set)  # key = j_node,   val = set of temppair
        # 如果 C 也需要（一般 C 只按单 key 存，不用 pair），可选：
        self.alive_C = set()

    def preprocess(self, dfa):
        """
        初始化解析所需的存储结构，并完成 `self.next_list` 和 `prev_list` 的构建。
        """
        # 假设 self.protein 已被设置
        # 计算序列长度
        self.seq_length = len(self.protein) * 3  # 每个氨基酸对应3个核苷酸

        # 获取 next_pair 和 prev_pair 连接关系
        self.get_next_pair(dfa)
        self.get_next_pair_set()
        self.get_prev_pair(dfa)
        self.get_prev_pair_set()

        # Dump next/prev pair tables for inspection
        #self.dump_pairs()  # writes to logs/dfa_pairs_*.txt

        # 更新 self.get_broken_codon_score_map
        for i in range(self.seq_length + 1):
            for node_i in dfa.nodes.get(i, []):  # 遍历每个节点
                for l in range(SINGLE_MAX_LEN + 1):  # 遍历可能的距离
                    j = i + l
                    if j > self.seq_length:
                        break
                    for node_j in dfa.nodes.get(j, []):  # 遍历节点j
                        self.get_broken_codon_score_map[node_i][node_j] = self.get_broken_codon_score(node_i, node_j)

        # 构建 self.next_list 和 prev_list
        self.build_next_list(dfa)
        self.build_prev_list(dfa)
        # self.write_pairs_file("./logs/pairs.txt")
        self.write_pairs_file()

        # 计算 stacking energy
        for outer_pair in range(1, 7):
            nuci_1 = PTLN(outer_pair)
            nucq = PTRN(outer_pair)
            for inner_pair in range(1, 7):
                nuci = PTLN(inner_pair)
                nucj_1 = PTRN(inner_pair)
                # print(nuci_1,nucq,nuci,nucj_1)
                self.stacking_score[outer_pair - 1][inner_pair - 1] = -func14(
                    0, 1, 1, 0, nuci_1, nuci, nucj_1,
                    nucq, nuci_1, nuci, nucj_1, nucq, self.params)
                for l in range(SINGLE_MAX_LEN + 1):
                    self.bulge_score[outer_pair - 1][inner_pair - 1][l] = -func14(
                        0, l + 2, 1, 0,
                        nuci_1, nuci, nucj_1, nucq,
                        nuci_1, nuci, nucj_1, nucq, self.params)

        if SPECIAL_HP:
            # Triloops
            self.special_hp(dfa, 5)
            # Tetraloop37
            self.special_hp(dfa, 6)
            # Hexaloops
            self.special_hp(dfa, 8)

    # 构建 self.next_list
    def build_next_list(self, dfa):
        # 获取初始节点
        init_node = dfa.nodes[0][0]

        # 遍历所有核苷酸编号 (1-4)
        for nuci in range(1, 5):
            visited = set()
            q_list = self.next_pair[nuci].get(init_node, [])
            while q_list:
                new_q_list = []
                for q_node_nucq in q_list:
                    q_node = q_node_nucq[0]
                    self.next_list[nuci].setdefault(q_node, []).append(q_node_nucq)

                    # q-1 是特殊处理部分
                    for q_1_node_dict in dfa.auxiliary_left_edges.get(q_node, {}).items():
                        q_1_node = q_1_node_dict[0]  # 获取 q_1_node
                        self.next_list[nuci].setdefault(q_1_node, []).append(q_node_nucq)
                        # 递归处理 q_2_node
                        for q_2_node_dict in dfa.auxiliary_left_edges.get(q_1_node, {}).items():
                            q_2_node = q_2_node_dict[0]  # 获取 q_2_node
                            self.next_list[nuci].setdefault(q_2_node, []).append(q_node_nucq)

                    # 遍历 q_node 前面的节点，范围为 q_node[0]-3 到 q_node[0]-SINGLE_MAX_LEN
                    for j in range(q_node[0] - 3, max(0, q_node[0] - SINGLE_MAX_LEN - 1), -1):
                        for j_node in dfa.nodes[j]:
                            self.next_list[nuci].setdefault(j_node, []).append(q_node_nucq)

                    # 遍历 q_node 的辅助右边界节点
                    for q1_node in dfa.auxiliary_right_edges.get(q_node, {}).keys():
                        if q1_node not in visited:
                            visited.add(q1_node)
                            # 将新的配对节点加入到新的查询列表中
                            new_q_list.extend(self.next_pair[nuci].get(q1_node, []))
                q_list = new_q_list

    # 构建 prev_list
    def build_prev_list(self, dfa):
        """
        构建 prev_list，存储每个核苷酸编号和节点对应的前驱节点列表。

        参数：
        - dfa: DFA 实例，包含节点和边的信息。
        """
        # 初始化结束节点
        init_node = (self.seq_length, 0, 0)

        # 遍历所有核苷酸编号 (1-4)
        for nucj in range(1, 5):
            visited = set()
            p_list = self.prev_pair[nucj].get(init_node, [])

            while p_list:
                new_p_list = []
                for p_node_nucp_1 in p_list:
                    p_node = p_node_nucp_1[0]
                    # 将当前配对节点添加到 prev_list
                    self.prev_list[nucj].setdefault(p_node, []).append(p_node_nucp_1)

                    # p+1 是特殊处理部分
                    for p1_node, _ in dfa.auxiliary_right_edges.get(p_node, {}).items():
                        self.prev_list[nucj].setdefault(p1_node, []).append(p_node_nucp_1)
                        # 处理 p2_node，递归加入
                        for p2_node, _ in dfa.auxiliary_right_edges.get(p1_node, {}).items():
                            self.prev_list[nucj].setdefault(p2_node, []).append(p_node_nucp_1)

                    # 遍历 p_node 后面的节点，范围为 p_node[0]+3 到 p_node[0]+SINGLE_MAX_LEN
                    for i in range(p_node[0] + 3, min(self.seq_length, p_node[0] + SINGLE_MAX_LEN + 1) + 1):
                        for i_node in dfa.nodes.get(i, []):
                            self.prev_list[nucj].setdefault(i_node, []).append(p_node_nucp_1)

                    # 遍历 p_node 的辅助左边界节点
                    for p_1_node, weight in dfa.left_edges.get(p_node, []):
                        if p_1_node not in visited:
                            visited.add(p_1_node)
                            # 将新的配对节点加入到新的查询列表中
                            new_p_list.extend(self.prev_pair[nucj].get(p_1_node, []))

                p_list = new_p_list

    def get_next_pair(self, dfa):
        """
        将C++中的get_next_pair函数转换为Python。

        Args:
            dfa (DFA_t): 包含节点和辅助边缘的确定性有限自动机。
        """
        temp_vector = []
        for nuci in range(self.NOTON):
            for j in range(self.seq_length, 0, -1):
                for j_node in dfa.nodes[j]:
                    # 获取j_node对应的所有辅助左边缘
                    auxiliary_edges = dfa.auxiliary_left_edges.get(j_node, []).items()
                    for item in auxiliary_edges:
                        j_1_node, weight = item
                        temp_vector.clear()
                        nuc = j_1_node[2]  # 从j_1_node中获取NucType
                        # 检查是否允许当前nuci和nuc的配对
                        if _allowed_pairs[nuci][nuc]:
                            # 如果允许，则将(j_1_node, nuc, weight)添加到next_pair
                            temp_vector.append((j_1_node, nuc, weight))
                            # self.next_pair[nuci][j_1_node].append((j_1_node, nuc, weight))

                        if len(temp_vector) == 0:
                            # 如果不允许，进行合并操作
                            next_pair_j_1 = self.next_pair[nuci].get(j_1_node, [])
                            next_pair_j = self.next_pair[nuci].get(j_node, [])
                            if next_pair_j_1 and next_pair_j:
                                # 获取index1和index2
                                index1 = next_pair_j_1[0][0][0]  # j_1_node的第一个元素的第一个索引
                                index2 = next_pair_j[0][0][0]  # j_node的第一个元素的第一个索引
                                if index1 // 3 == index2 // 3:
                                    # 如果index1和index2同属于一个三联体，则合并
                                    self.next_pair[nuci][j_1_node].extend(next_pair_j)
                                elif index1 > index2:
                                    # 如果index1大于index2，则清空并合并
                                    self.next_pair[nuci][j_1_node].clear()
                                    self.next_pair[nuci][j_1_node].extend(next_pair_j)
                            elif next_pair_j:
                                # 如果只有next_pair_j存在，则直接合并
                                self.next_pair[nuci][j_1_node].extend(next_pair_j)

                            # if len(self.next_pair[nuci][j_1_node]) > 0 and len(self.next_pair[nuci][j_node]) > 0:
                            #     # 如果 temp_vector 为空，尝试合并节点对
                            #     index1 = self.next_pair[nuci][j_1_node][0][0][0]  # 获取 index1
                            #     index2 = self.next_pair[nuci][j_node][0][0][0]  # 获取 index2
                            #     if index1 // 3 == index2 // 3:
                            #         self.next_pair[nuci][j_1_node].extend(self.next_pair[nuci][j_node])
                            #     elif index1 > index2:
                            #         self.next_pair[nuci][j_1_node].clear()
                            #         self.next_pair[nuci][j_1_node].extend(self.next_pair[nuci][j_node])
                            # elif len(self.next_pair[nuci][j_node]) > 0:
                            #     self.next_pair[nuci][j_1_node].extend(self.next_pair[nuci][j_node])
                        else:
                            self.next_pair[nuci][j_1_node].extend(temp_vector)

    def get_prev_pair(self, dfa):
        temp_vector = []
        for nuci in range(self.NOTON):
            for j in range(self.seq_length):
                for j_node in dfa.nodes[j]:
                    auxiliary_edges = dfa.auxiliary_right_edges.get(j_node, []).items()
                    for item in auxiliary_edges:
                        j1_node, weight = item
                        temp_vector.clear()
                        nuc = j_node[2]  # 假设 `j_node` 是一个元组，获取其中的NucType
                        if _allowed_pairs[nuci][nuc]:
                            temp_vector.append((j1_node, nuc, weight))

                        if len(temp_vector) == 0:
                            if len(self.prev_pair[nuci][j_node]) > 0 and len(self.prev_pair[nuci][j1_node]) > 0:
                                # merge
                                index1 = self.prev_pair[nuci][j1_node][0][0][0] - 1
                                index2 = self.prev_pair[nuci][j_node][0][0][0] - 1
                                if index1 // 3 == index2 // 3:
                                    self.prev_pair[nuci][j1_node].extend(self.prev_pair[nuci][j_node])
                                elif index1 < index2:
                                    self.prev_pair[nuci][j1_node].clear()
                                    self.prev_pair[nuci][j1_node].extend(self.prev_pair[nuci][j_node])
                            elif len(self.prev_pair[nuci][j_node]) > 0:
                                self.prev_pair[nuci][j1_node].extend(self.prev_pair[nuci][j_node])
                        else:
                            self.prev_pair[nuci][j1_node].extend(temp_vector)

    def get_next_pair_set(self):
        """
        对 next_pair 去重，转化为集合形式。
        """
        for nuci in range(self.NOTON):
            for node, pairs in self.next_pair[nuci].items():
                self.next_pair_set[nuci][node] = set(pairs)

        for nuci in range(self.NOTON):
            for node, pairs in self.next_pair_set[nuci].items():
                # 清空 next_pair 的 j_node 对应的列表
                self.next_pair[nuci][node] = []
                for item in pairs:
                    self.next_pair[nuci][node].append(item)

    def get_prev_pair_set(self):
        """
        对 prev_pair 去重，转化为集合形式。
        """
        for nuci in range(self.NOTON):
            for node, pairs in self.prev_pair[nuci].items():
                self.prev_pair_set[nuci][node] = set(pairs)

        for nuci in range(self.NOTON):
            for node, pairs in self.prev_pair_set[nuci].items():
                # 清空 next_pair 的 j_node 对应的列表
                self.prev_pair[nuci][node] = []
                for item in pairs:
                    self.prev_pair[nuci][node].append(item)

    def get_nuc_from_dfa_cai(self, dfa: Dict, start_node: Tuple[int, int, int], end_node: Tuple[int, int, int],
                             protein: List[str],
                             best_path_in_one_codon_unit: Dict[str, Dict[
                                 Tuple[Tuple[int, int, int], Tuple[int, int, int]], Tuple[float, int, int, int]]],
                             aa_best_path_in_a_whole_codon: Dict[str, str]) -> str:
        """
        转换两个节点之间的核苷酸序列。
        """
        s_index = start_node[0]
        t_index = end_node[0]

        if s_index >= t_index:
            return ""

        aa_left = protein[s_index // 3]  # tri letter
        aa_right = protein[t_index // 3] if t_index // 3 < len(protein) else aa_left

        # start_node_re_index = (s_index % 3 + 1, start_node[1], start_node[2])
        # end_node_re_index = (t_index % 3 + 1, end_node[1], end_node[2])
        # === 关键：把 num 还原为 base_num，避免查表 miss ===
        b_start_num = self.base_num(start_node[1])
        b_end_num = self.base_num(end_node[1])

        start_node_re_index = (s_index % 3 + 1, b_start_num, start_node[2])
        end_node_re_index = (t_index % 3 + 1, b_end_num, end_node[2])

        if t_index - s_index < 3:
            if s_index // 3 == t_index // 3:
                temp_seq = ""
                #print("aa",aa_left)
                #print(start_node_re_index,end_node_re_index)
                nucs = best_path_in_one_codon_unit.get(aa_left, {}).get((start_node_re_index, end_node_re_index))
                #print(nucs[1])

                temp_seq += GET_ACGU(nucs[1])
                if nucs[2] != k_void_nuc:  # 假设k_void_nuc = 0
                    temp_seq += GET_ACGU(nucs[2])
                #print('temp_seq', len(temp_seq))
                assert len(temp_seq) == end_node[0] - start_node[0], "Sequence length mismatch."
                return temp_seq
            else:
                temp_left = ""
                temp_right = ""
                if s_index % 3 != 0:
                    nucs = best_path_in_one_codon_unit.get(aa_left, {}).get((start_node_re_index, (0, 0, 0)))
                    temp_left += GET_ACGU(nucs[1])
                    if nucs[2] != k_void_nuc:
                        temp_left += GET_ACGU(nucs[2])

                if t_index % 3 != 0:
                    nucs = best_path_in_one_codon_unit.get(aa_right, {}).get(((0, 0, 0), end_node_re_index))
                    if GET_ACGU(nucs[1]) != 'X':  # 假设 'X' 是无效核苷酸
                        temp_right += GET_ACGU(nucs[1])
                    if nucs[2] != k_void_nuc:
                        temp_right += GET_ACGU(nucs[2])
                temp = len(temp_left + temp_right)
                #print('temp', temp)
                assert len(temp_left + temp_right) == end_node[0] - start_node[0], "Sequence length mismatch."

                return temp_left + temp_right
        else:
            temp_left = ""
            temp_mid = ""
            temp_right = ""

            if s_index % 3 != 0:
                nucs = best_path_in_one_codon_unit.get(aa_left, {}).get((start_node_re_index, (0, 0, 0)))
                temp_left += GET_ACGU(nucs[1])
                if nucs[2] != k_void_nuc:
                    temp_left += GET_ACGU(nucs[2])

            protein_start_index = s_index // 3
            if s_index % 3 != 0:
                protein_start_index += 1

            protein_end_index = t_index // 3

            if protein_start_index != protein_end_index:
                for protein_index in range(protein_start_index, protein_end_index):
                    aa_tri = protein[protein_index]
                    if aa_tri in k_map_3_1:
                        nucs = aa_best_path_in_a_whole_codon[k_map_3_1[aa_tri]]
                    elif aa_tri in aa_best_path_in_a_whole_codon:
                        nucs = aa_best_path_in_a_whole_codon[aa_tri]
                    else:
                        raise ValueError(f"No best path found for amino acid: {aa_tri}")

                    temp_mid += nucs

            if t_index % 3 != 0:
                nucs = best_path_in_one_codon_unit.get(aa_right, {}).get(((0, 0, 0), end_node_re_index))
                temp_right += GET_ACGU(nucs[2])
                if nucs[3] != k_void_nuc:
                    temp_right += GET_ACGU(nucs[3])
            temp = len(temp_left + temp_mid + temp_right)

            assert len(temp_left + temp_mid + temp_right) == end_node[0] - start_node[0], "Sequence length mismatch."

            return temp_left + temp_mid + temp_right

    def get_broken_codon_score(self, start_node, end_node):
        """
        计算两个节点之间的破损编码分数。

        参数：
        - start_node: 起始节点 (tuple)
        - end_node: 结束节点 (tuple)

        返回：
        - ret: 两个节点之间的破损编码分数 (float)
        """
        s_index = start_node[0]
        t_index = end_node[0]

        # 如果起始节点索引大于等于结束节点索引，返回 0
        if s_index >= t_index:
            return 0.0

        # 获取起始节点和结束节点所在的氨基酸三字母
        aa_left = self.protein[s_index // 3]  # 起始三字母
        aa_right = self.protein[s_index // 3]
        if t_index // 3 < len(self.protein):
            aa_right = self.protein[t_index // 3]

        # 计算起始节点和结束节点的重新索引
        # start_node_re_index = (s_index % 3 + 1, start_node[1], start_node[2])
        # end_node_re_index = (t_index % 3 + 1, end_node[1], end_node[2])
        # === 关键：去上下文偏移 ===
        b_start_num = self.base_num(start_node[1])
        b_end_num = self.base_num(end_node[1])

        start_node_re_index = (s_index % 3 + 1, b_start_num, start_node[2])
        end_node_re_index = (t_index % 3 + 1, b_end_num, end_node[2])

        ret = 0.0

        # 如果索引间距小于 3
        if t_index - s_index < 3:
            if s_index // 3 == t_index // 3:  # 同一个氨基酸内
                ret = self.best_path_in_one_codon_unit[aa_left].get((start_node_re_index, end_node_re_index), (0.0,))[0]
            else:
                left_ln_cai, right_ln_cai = 0.0, 0.0
                if s_index % 3 != 0:  # 计算左侧片段的 ln(CAI)
                    left_ln_cai = self.best_path_in_one_codon_unit[aa_left].get(
                        (start_node_re_index, (0, 0, 0)), (0.0,)
                    )[0]
                if t_index % 3 != 0:  # 计算右侧片段的 ln(CAI)
                    right_ln_cai = self.best_path_in_one_codon_unit[aa_right].get(
                        ((0, 0, 0), end_node_re_index), (0.0,)
                    )[0]
                ret = left_ln_cai + right_ln_cai
        else:
            # 如果索引间距大于等于 3
            left_ln_cai, right_ln_cai = 0.0, 0.0
            if s_index % 3 != 0:
                left_ln_cai = self.best_path_in_one_codon_unit[aa_left].get(
                    (start_node_re_index, (0, 0, 0)), (0.0,)
                )[0]
            if t_index % 3 != 0:
                right_ln_cai = self.best_path_in_one_codon_unit[aa_right].get(
                    ((0, 0, 0), end_node_re_index), (0.0,)
                )[0]
            ret = left_ln_cai + right_ln_cai

        return ret

    def update_if_better(self, state, new_score, new_cai_score, best=None, i=0, j=-99999):
        if state.score + state.cai_score < new_score + new_cai_score:
            if best is not None:
                if j != -99999:
                    tempstate = best.get_state(i, j)
                    tempstate.score = new_score
                    tempstate.cai_score = new_cai_score
                    best.set_state(i, j, tempstate)
                    # === 新增：登记活跃键 ===
                    if best is self.bestH:
                        self.alive_H[i].add(j)
                    elif best is self.bestP:
                        self.alive_P[i].add(j)
                    elif best is self.bestMulti:
                        self.alive_Multi[i].add(j)
                    elif best is self.bestM:
                        self.alive_M[i].add(j)
                    elif best is self.bestM2:
                        self.alive_M2[i].add(j)
                    elif best is self.bestM_P:
                        self.alive_M_P[i].add(j)
                else:
                    tempstate = best.get_state(i)
                    tempstate.score = new_score
                    tempstate.cai_score = new_cai_score
                    best.set_state(i, tempstate)
                    # C 如果也需要登记，可选：
                    if best is self.bestC:
                        self.alive_C.add(i)

    def update_if_better_T(self, state, new_score, cai_score, pre_node,
                           pre_left_cait, best=None, i=0, j=0):
        if state.score + state.cai_score < new_score + cai_score:
            if best is not None:
                tempstate = best.get_state(i, j)
                tempstate.score = new_score
                tempstate.cai_score = cai_score
                tempstate.pre_node = pre_node
                tempstate.pre_left_cai = pre_left_cait
                best.set_state(i, j, tempstate)
                # === 新增：登记活跃键 ===
                if best is self.bestH:
                    self.alive_H[i].add(j)
                elif best is self.bestP:
                    self.alive_P[i].add(j)
                elif best is self.bestMulti:
                    self.alive_Multi[i].add(j)
                elif best is self.bestM:
                    self.alive_M[i].add(j)
                elif best is self.bestM2:
                    self.alive_M2[i].add(j)
                elif best is self.bestM_P:
                    self.alive_M_P[i].add(j)

    def _format_node(self, node):
        """Format a DFA node tuple (i, num, nuc) into a readable string with base letter."""
        try:
            i, num, nuc = node
        except Exception:
            return str(node)
        try:
            base = GET_ACGU(nuc)
        except Exception:
            base = str(nuc)
        return f"(i={i}, num={num}, base={base}, nuc={nuc})"

    def dump_pairs(self, filepath: str = None, limit_per_key: int = None):
        """
        Dump self.next_pair and self.prev_pair into a human-readable txt file.

        Args:
            filepath: Target txt path. If None, write to logs/pairs_{timestamp}.txt
            limit_per_key: If set, limit the number of items shown per key for readability.
        """
        os.makedirs("logs", exist_ok=True)
        if filepath is None:
            ts = time.strftime("%Y%m%d-%H%M%S")
            filepath = f"logs/dfa_pairs_{ts}.txt"

        def _dump_one(title, pair_table, f):
            f.write(f"\n===== {title} =====\n")
            totals = 0
            for nuci in range(self.NOTON):
                d = pair_table[nuci]
                keys = list(d.keys())
                f.write(f"\n-- nuci={nuci} | keys={len(keys)} --\n")
                for key_node in keys:
                    lst = d.get(key_node, [])
                    totals += len(lst)
                    f.write(f"  key {self._format_node(key_node)} -> {len(lst)} items\n")
                    to_show = lst if (limit_per_key is None) else lst[:limit_per_key]
                    for (dst_node, pair_nuc, weight) in to_show:
                        try:
                            pair_base = GET_ACGU(pair_nuc)
                        except Exception:
                            pair_base = str(pair_nuc)
                        f.write(
                            "    - to "
                            + self._format_node(dst_node)
                            + f", pair_nuc={pair_nuc}({pair_base}), weight={weight:.6f}\n"
                        )
            f.write(f"\n[Summary for {title}] total_items={totals}\n")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Dump of DFA pair tables\n")
            f.write(f"# time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# NOTON={self.NOTON}, seq_length={self.seq_length}\n")

            _dump_one("NEXT_PAIR", self.next_pair, f)
            _dump_one("PREV_PAIR", self.prev_pair, f)

        # Also print the path so it's visible in console/logs
        # print(f"[dump_pairs] Wrote next/prev pair tables to: {filepath}")

    # === Debug dump for prev_pair / next_pair / next_pair_list ===
    def write_pairs_file(self, filepath: str = 'pairs.txt') -> None:
        """Dump prev_pair, next_pair and next_pair_list to a text file."""
        def _fmt_node(n):
            try:
                return f"({int(n[0])}, {int(n[1])}, {int(n[2])})"
            except Exception:
                return str(n)

        def _dump_table(fh, title, table):
            fh.write(f"\n## {title} ##\n")
            # 约定结构: table[nuc][src_node] = [(dst_node, pair_nuc, weight), ...]
            for nuc in range(1, 5):
                mapping = table.get(nuc, {}) if hasattr(table, 'get') else table[nuc]
                if not mapping:
                    continue
                fh.write(f"[nuc={nuc}]\n")
                for src_node, lst in mapping.items():
                    fh.write(f"  {_fmt_node(src_node)} -> ")
                    if not lst:
                        fh.write("[]\n")
                        continue
                    parts = []
                    for item in lst:
                        # item: (dst_node, pair_nuc, weight) 或兼容已有格式
                        try:
                            dst_node, pair_nuc, weight = item
                            parts.append(f"{_fmt_node(dst_node)}|pair={int(pair_nuc)}|w={float(weight):.6f}")
                        except Exception:
                            parts.append(str(item))
                    fh.write("[ " + ", ".join(parts) + " ]\n")

        try:
            with open(filepath, 'w', encoding='utf-8') as fh:
                # prev_pair
                if hasattr(self, 'prev_pair') and self.prev_pair is not None:
                    _dump_table(fh, 'PREV_PAIR', self.prev_pair)
                else:
                    fh.write("\n## PREV_PAIR ##\n<none>\n")

                # next_pair
                if hasattr(self, 'next_pair') and self.next_pair is not None:
                    _dump_table(fh, 'NEXT_PAIR', self.next_pair)
                else:
                    fh.write("\n## NEXT_PAIR ##\n<none>\n")

                # next_pair_list —— 本次新增
                if hasattr(self, 'next_pair_list') and self.next_pair_list is not None:
                    _dump_table(fh, 'NEXT_PAIR_LIST', self.next_pair_list)
                else:
                    fh.write("\n## NEXT_PAIR_LIST ##\n<none>\n")
        except Exception as e:
             print(f"[pairs debug] failed to write '{filepath}': {e}")

    def reverse_index(self, idx: int) -> NodeNucpair:
        """根据索引反向映射到NodeNucpair。"""
        node_first = idx >> 6
        node_second = (idx & 0x3F) >> 3
        nucpair = (idx & 0x7)  # 修改
        return NodeNucpair(node_first, node_second, nucpair)

    def parse(self, dfa, codon, aa_seq, protein, aa_best_in_codon, best_path_in_one_codon,
              aa_graphs_with_ln_weights):
        """
        主解析逻辑，包括初始化、处理 DFA 和运行动态规划。
        改动要点：对每个 j，不再固定遍历 `range(6)`，而是遍历 `dfa.nodes[j]` 中实际存在的所有节点，
        将各节点的 `num` 作为 `j_num` 传入各个 beam 函数，以覆盖被 trigram-lift 后的全部上下文编号。
        """
        # 记录蛋白序列并预处理（将构建 next/prev list，calc broken_codon 等）
        self.protein = protein
        self.preprocess(dfa)

        # 初始化起始节点 bestC（要求 dfa.nodes[0] 只有一个初始节点）
        start_node = dfa.nodes[0][0]
        self.update_if_better(
            self.bestC.get_state(start_node),
            0,
            0.0,
            self.bestC,
            start_node
        )
        # 同步起点的直接右邻节点
        for node1_nuc0 in dfa.right_edges.get(start_node, []):
            node1 = node1_nuc0[0]
            self.update_if_better(
                self.bestC.get_state(node1),
                0,
                0.0,
                self.bestC,
                node1
            )

        # 主循环：遍历 j 索引（0..seq_length），并对该 j 下 **所有存在的节点** 分别执行各 beam
        for j in range(self.seq_length + 1):
            # Hairpin Beam：遍历 j 位点所有节点 num
            # print("j=",j,"-----------------------------------------------------------------------------")
            # print("j=",j, "-----hairpin_beam--------------------------------------")
            for j_node in dfa.nodes.get(j, []):
                j_num = j_node[1]
                # print("j=", j, "--j_num=", j_num, "--hairpin_beam-------------------")
                self.hairpin_beam(j, dfa, j_num)

            if j > 0:
                # Multi Beam：遍历 j 位点所有节点 num
                # print("j=",j, "-----multi_beam------------------------------------------")
                for j_node in dfa.nodes.get(j, []):
                    j_num = j_node[1]
                    # print("j=", j, "--j_num=", j_num, "-----multi_beam-------------------")
                    self.multi_beam(j, dfa, j_num)

                # P Beam：遍历 j 位点所有节点 num
                # print("j=", j, "-----p_beam------------------------------------------------")
                for j_node in dfa.nodes.get(j, []):
                    j_num = j_node[1]
                    # print("j=", j, "--j_num=", j_num, "-----p_beam-------------------------")
                    self.p_beam(j, dfa, j_num)

                # M2 Beam：遍历 j 位点所有节点 num
                # print("j=", j, "-----m2_beam----------------------------------------------")
                for j_node in dfa.nodes.get(j, []):
                    j_num = j_node[1]
                    # print("j=", j, "--j_num=", j_num, "-----m2_beam------------------")
                    self.m2_beam(j, dfa, j_num)

                if j < self.seq_length:
                    # M Beam：遍历 j 位点所有节点 num
                    # print("j=", j, "-----m_beam---------------------------------------------")
                    for j_node in dfa.nodes.get(j, []):
                        j_num = j_node[1]
                        # print("j=", j, "--j_num=", j_num, "-----m_beam------------------")
                        self.m_beam(j, dfa, j_num)

                    # C Beam：遍历 j 位点所有节点 num
                    # print("j=",j, "-----c_beam--------------------------------------------")
                    for j_node in dfa.nodes.get(j, []):
                        j_num = j_node[1]
                        # print("j=", j, "--j_num=", j_num, "-----c_beam------------------")
                        self.c_beam(j, dfa, j_num)

        # 结束节点与回溯（TRIGRAM 提升后，最后一位存在多个“结束 X 节点”）
        # 我们在所有 j==self.seq_length 的真实结束节点中，选择得分最高的那个再回溯。
        best_end_node = None
        best_viterbi = None
        best_total = float('-inf')

        # 这些都是形如 (self.seq_length, num, nuc=X) 的真实结束节点
        end_nodes = dfa.nodes.get(self.seq_length, [])
        for cand in end_nodes:
            st = self.bestC.get_state(cand)
            if st is None or getattr(st, 'score', None) is None:
                continue
            if st.score == INT_MIN:
                continue
            total = float(st.score) + float(getattr(st, 'cai_score', 0.0))
            if total > best_total:
                best_total = total
                best_end_node = cand
                best_viterbi = st

        # 回退方案：如果没有在 bestC 里找到合法的结束节点，就退回到旧的单一 (seq_length,0,0)
        if best_end_node is None:
            fallback_end = (self.seq_length, 0, 0)
            best_end_node = fallback_end
            best_viterbi = self.bestC.get_state(fallback_end)

        # print("[parse] chosen end node:", best_end_node, " total=", best_total)
        # print("backtrace-------------------------------------------------------------")
        backtrace_result = self.backtrace(dfa, best_viterbi, best_end_node)

        # 返回最终结果
        return {
            "sequence": backtrace_result.seq,
            "structure": backtrace_result.structure,
            "score": best_viterbi.score / -100.0,
            "cai_score": best_viterbi.cai_score
        }

    # Beam 处理函数（框架）
    def hairpin_beam(self, j, dfa, j_num):
        """
        处理 Hairpin Beam 的逻辑。
        j: 当前节点索引
        dfa: DFA 实例，包含节点和边信息
        j_num: 当前核苷酸索引
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        if nuc_j is None:
            return

        j_node = (j, j_num, nuc_j)

        # 遍历 j_node 的右边界
        # print("...h(j,jnext)............")
        for j1_node_nucj in dfa.right_edges.get(j_node, []):
            j1_node = j1_node_nucj[0]
            nucj = j_node[2]
            weight_nucj = j1_node_nucj[1]

            # 遍历 j+4 的节点
            if j + 4 >= len(dfa.nodes):
                continue

            for j4_node in dfa.nodes[j + 4]:
                jnext_list = self.next_pair[nucj].get(j4_node, [])
                # print("nucj", nucj)
                # print("j4_node", j4_node)
                # print("jnext_list", jnext_list)
                if not jnext_list:
                    continue

                for jnext_node_nucjnext in jnext_list:
                    jnext_node = jnext_node_nucjnext[0]
                    nucjnext = jnext_node_nucjnext[1]
                    weight_nucjnext = jnext_node_nucjnext[2]
                    jnext = jnext_node[0]
                    # jnext_num = jnext_node[1]

                    # hairpin_length = jnext + 1 - j
                    temp = (j, j_num, NTP(nucj, nucjnext))

                    # 遍历 j1_node 的右边界
                    for j2_node_nucj1 in dfa.right_edges.get(j1_node, []):
                        j2_node = j2_node_nucj1[0]
                        j2_num = j2_node[1]
                        nucj1 = j1_node[2]
                        weight_nucj1 = j2_node_nucj1[1]

                        # 遍历 jnext_node 的左边界
                        for jnext_1_node_list in dfa.auxiliary_left_edges.get(jnext_node, {}).items():

                            jnext_1_node = jnext_1_node_list[0]
                            jnext_1_num = jnext_1_node[1]

                            # if jnext - j == 4 and jnext_1_num != j2_num:
                            #     continue

                            for j3_node_nucj2 in dfa.right_edges.get(j2_node, []):
                                j3_node = j3_node_nucj2[0]
                                j3_num = j3_node[1]
                                if j3_num != jnext_1_num:
                                    continue

                                nucjnext_1 = jnext_1_node[2]
                                weight_nucjnext_1 = jnext_1_node_list[1]
                                # print(j, jnext, nucj, nucj1, nucjnext_1, nucjnext, self.tetra_hex_tri)

                                newscore = -func12(j, jnext, nucj, nucj1, nucjnext_1, nucjnext, self.tetra_hex_tri, self.params)

                                cai_score = weight_nucj + weight_nucj1 + weight_nucjnext_1 + weight_nucjnext

                                if (jnext_1_node[0] - j2_node[0]) <= SINGLE_MAX_LEN:
                                    cai_score += self.get_broken_codon_score_map[j2_node][jnext_1_node]
                                else:
                                    cai_score += self.get_broken_codon_score(j2_node, jnext_1_node)

                                # state = self.bestH.get_state(jnext_node, temp)
                                # print('state', state)
                                # self.update_if_better(state, newscore, cai_score)

                                # print("jnext_node", jnext_node)
                                # print("temp", temp)
                                # print("newscore", newscore)
                                # print(self.bestH.get_state(jnext_node, temp))

                                self.update_if_better(
                                    self.bestH.get_state(jnext_node, temp),
                                    newscore,
                                    cai_score,
                                    self.bestH,
                                    jnext_node,
                                    temp
                                )

                                # print("after_update",self.bestH.get_state(jnext_node, temp))
                                # print("........")

        # print(self.bestH)
        # Extend h(i, j) to h(i, jnext) 或生成 p(i, j)
        # print("...h(i, j) to h(i, jnext)/p(i, j)............")
        # for i_node_nucpair_idx in range(64 * j):
        #     i_node_nucpair = self.reverse_index(i_node_nucpair_idx)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
        #
        #     state = self.bestH.get_state(j_node, temppair)
        #     # print('state:', state)
        #     if state is not None and state.score == INT_MIN:
        #         continue
        #     # print('Achieve!')
        #     # i_node_nucpair = self.reverse_index(i_node_nucpair_idx)
        #     i = i_node_nucpair.node_first
        #     i_num = i_node_nucpair.node_second
        #     pair_nuc = i_node_nucpair.nucpair
        for temppair in self.alive_H.get(j_node, ()):
            state = self.bestH.get_state(j_node, temppair)
            if state is None or state.score == INT_MIN:
                continue

            i, i_num, pair_nuc = int(temppair[0]), int(temppair[1]), int(temppair[2])

            nuci = PTLN(pair_nuc)
            nucj = PTRN(pair_nuc)
            i_node = (i, i_num, nuci)
            # print("temppair", temppair)
            # print("i_node", i_node)

            # for item in dfa.auxiliary_right_edges.get(j_node, {}).values():
            # print("..h(i, j) to h(i, jnext)............")
            for j1_node, weight in dfa.auxiliary_right_edges[j_node].items():
                jnext_list = self.next_pair[nuci].get(j1_node, [])
                if not jnext_list:
                    continue

                # print("nuci", nuci)
                # print("j1_node", j1_node)
                # print("jnext_list", jnext_list)
                for jnext_node_nucjnext in jnext_list:
                    jnext_node = jnext_node_nucjnext[0]
                    nucjnext = jnext_node_nucjnext[1]
                    jnext = jnext_node[0]
                    weight_nucjnext = jnext_node_nucjnext[2]
                    hairpin_length = jnext + 1 - i

                    temp = (i, i_num, NTP(nuci, nucjnext))

                    for i1_node_newnuci in dfa.right_edges.get(i_node, []):
                        newnuci = i_node[2]
                        if nuci != newnuci:
                            continue
                        i1_node = i1_node_newnuci[0]
                        weight_newnuci = i1_node_newnuci[1]

                        for i2_node_nuci1 in dfa.right_edges.get(i1_node, []):
                            i2_node = i2_node_nuci1[0]
                            nuci1 = i1_node[2]
                            weight_nuci1 = i2_node_nuci1[1]

                            for jnext_1_node_nucjnext_1 in dfa.left_edges.get(jnext_node, []):
                                jnext_1_node = jnext_1_node_nucjnext_1[0]
                                nucjnext_1 = jnext_1_node[2]
                                weight_nucjnext_1 = jnext_1_node_nucjnext_1[1]

                                newscore = -func12(i, jnext, nuci, nuci1, nucjnext_1, nucjnext, self.tetra_hex_tri, self.params)

                                cai_score = weight_newnuci + weight_nuci1 + weight_nucjnext_1 + weight_nucjnext

                                if (jnext_1_node[0] - i2_node[0]) <= SINGLE_MAX_LEN:
                                    cai_score += self.get_broken_codon_score_map[i2_node][jnext_1_node]
                                else:
                                    cai_score += self.get_broken_codon_score(i2_node, jnext_1_node)

                                # print("jnext_node", jnext_node)
                                # print("temp", temp)
                                # print("newscore", newscore)
                                # print(self.bestH.get_state(jnext_node, temp))

                                self.update_if_better(
                                    self.bestH.get_state(jnext_node, temp),
                                    newscore,
                                    cai_score,
                                    self.bestH,
                                    jnext_node,
                                    temp
                                )

                                # print("after_update",self.bestH.get_state(jnext_node, temp))
                                # print("........")

            # "H->P-------------"
            # print("..h(i, j) to p(i, j)............")
            for j1_node_newnucj in dfa.right_edges.get(j_node, []):
                newnucj = j_node[2]
                if nucj != newnucj:
                    continue
                j1_node = j1_node_newnucj[0]

                # print("j1_node", j1_node)
                # print("temppair", temppair)
                # print(self.bestP.get_state(j1_node, temppair))
                self.update_if_better(
                    self.bestP.get_state(j1_node, temppair),
                    state.score,
                    state.cai_score,
                    self.bestP,
                    j1_node,
                    temppair
                )
                # print("after_update",self.bestP.get_state(j1_node, temppair))
                # print("........")

    def multi_beam(self, j, dfa, j_num):
        """
        处理 Multi Beam 的逻辑。

        参数：
        - j: 当前节点的索引
        - dfa: DFA 实例，包含节点和边信息
        - j_num: 当前节点的核苷酸编号
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        if nuc_j is None:
            return

        j_node = (j, j_num, nuc_j)

        # 遍历 i_node_nucpair
        # for i_node_nucpair_idx in range(64 * j):
        #     # 获取对应的分数
        #     i_node_nucpair = self.reverse_index(i_node_nucpair_idx)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
        #
        #     new_state_score = self.bestMulti.get_state(j_node, temppair)
        #
        #     if new_state_score.score == INT_MIN:
        #         continue
        #
        #     # 解析 i_node_nucpair
        #     i_node_nucpair = self.reverse_index(i_node_nucpair_idx)
        #     i = i_node_nucpair.node_first
        #     i_num = i_node_nucpair.node_second
        #     pair_nuc = i_node_nucpair.nucpair
        for temppair in self.alive_Multi.get(j_node, ()):
            new_state_score = self.bestMulti.get_state(j_node, temppair)
            if new_state_score.score == INT_MIN:
                continue
            i, i_num, pair_nuc = int(temppair[0]), int(temppair[1]), int(temppair[2])
            nuci = PTLN(pair_nuc)
            nucj_1 = PTRN(pair_nuc)

            # 获取与 j_node 配对的 self.next_list
            jnext_list = self.next_pair[nuci].get(j_node, [])
            if jnext_list:
                # 遍历 jnext_list
                for jnext_node_nucjnext in jnext_list:
                    jnext_node = jnext_node_nucjnext[0]
                    nucjnext = jnext_node_nucjnext[1]
                    weight_nucjnext = jnext_node_nucjnext[2]
                    jnext = jnext_node[0]

                    # 遍历 jnext_node 的右边界
                    for jnext1_node_newnucjnext in dfa.right_edges.get(jnext_node, []):
                        jnext1_node = jnext1_node_newnucjnext[0]
                        newnucjnext = jnext_node[2]

                        if newnucjnext == nucjnext:
                            # 计算 CAI 分数
                            if (jnext_node[0] - new_state_score.pre_node[0]) <= SINGLE_MAX_LEN:
                                cai_score = (
                                        new_state_score.pre_left_cai +
                                        (self.get_broken_codon_score_map[new_state_score.pre_node][
                                             jnext_node] + weight_nucjnext)
                                )
                            else:
                                cai_score = (
                                        new_state_score.pre_left_cai +
                                        (self.get_broken_codon_score_map[new_state_score.pre_node][
                                             jnext_node] + weight_nucjnext)
                                )

                            temp = (i, i_num, NTP(nuci, nucjnext))

                            # print("multi--j->jnext")
                            # print("cai_score", cai_score)
                            # print("newscore", new_state_score.score)
                            # print("bestMulti_jnext1_before", self.bestMulti.get_state(jnext1_node, temp))
                            # 更新 bestMulti
                            self.update_if_better_T(
                                self.bestMulti.get_state(jnext1_node, temp),
                                new_state_score.score,
                                cai_score,
                                new_state_score.pre_node,
                                new_state_score.pre_left_cai,
                                self.bestMulti,
                                jnext1_node,
                                temp
                            )
                            # print("bestMulti_jnext1_after", self.bestMulti.get_state(jnext1_node, temp))

            # 生成 multi(i, j) -> p(i, j)
            # print("multi(i, j) -> p(i, j)")
            newscore = new_state_score.score - func15(
                i, j, nuci, -1, -1, nucj_1, self.seq_length, self.params
            )
            # print("cai_score", new_state_score.cai_score)
            # print("funcscore", - func15(
            #     i, j, nuci, -1, -1, nucj_1, self.seq_length, self.params
            # ))
            # print("state.score", new_state_score.score)
            # print("newscore", newscore)
            # print("bestP_j_before", self.bestMulti.get_state(j_node, temppair))
            self.update_if_better(
                self.bestP.get_state(j_node, temppair),
                newscore,
                new_state_score.cai_score,
                self.bestP,
                j_node,
                temppair
            )
            # print("bestP_j_after", self.bestMulti.get_state(j_node, temppair))


    def p_beam(self, j, dfa, j_num):
        """
        处理 P Beam 的逻辑。

        参数：
        - j: 当前节点的索引
        - dfa: DFA 实例，包含节点和边信息
        - j_num: 当前节点的核苷酸编号
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        if nuc_j is None:
            return

        j_node = (j, j_num, nuc_j)
        # print('j_range', 64 * j)
        # 处理 j < self.seq_length 的情况
        # print(f"p_beam-j={j}")
        if j < self.seq_length:
            # for i_node_nucpair_idx in range(64 * j):
            #     # 获取当前状态
            #     i_node_nucpair = self.reverse_index(i_node_nucpair_idx)
            #     # print('i_node_nucpair:', i_node_nucpair)
            #     temppair1 = (
            #     int(i_node_nucpair.node_fi1rst), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
            for temppair1 in self.alive_P.get(j_node, ()):
                state = self.bestP.get_state(j_node, temppair1)
                if state.score == INT_MIN:
                    continue

                # 解析 i_node_nucpair
                i, i_num, pair_nuc = int(temppair1[0]), int(temppair1[1]), int(temppair1[2])
                # i = i_node_nucpair.node_first
                if i <= 0:
                    continue
                # i_num = i_node_nucpair.node_second
                # pair_nuc = i_node_nucpair.nucpair
                nuci = PTLN(pair_nuc)
                nucj_1 = PTRN(pair_nuc)
                i_node = (i, i_num, nuci)
                #print("..i_node", i_node)

                # 处理 stacking (堆叠)
                # print("..stacking................")
                for j1_node_nucj in dfa.right_edges.get(j_node, []):
                    j1_node = j1_node_nucj[0]
                    # print("j1_node", j1_node)
                    # print("j_node", j_node)
                    nucj = j_node[2]
                    weight_nucj = j1_node_nucj[1]

                    for i_1_node_nuci_1 in dfa.left_edges.get(i_node, []):
                        i_1_node = i_1_node_nuci_1[0]
                        # print("i_1_node", i_1_node)
                        nuci_1 = i_1_node[2]
                        weight_nuci_1 = i_1_node_nuci_1[1]
                        outer_pair = NTP(nuci_1, nuc_j)

                        if _allowed_pairs[nuci_1][nuc_j]:
                            newscore = self.stacking_score[outer_pair - 1][pair_nuc - 1] + state.score
                            cai_score = state.cai_score + (weight_nuci_1 + weight_nucj)
                            temp = (i_1_node[0], i_1_node[1], outer_pair)

                            # print("cai_score", cai_score)
                            # print("outer_pair",outer_pair)
                            # print("stacking_score",self.stacking_score[outer_pair - 1][pair_nuc - 1])
                            # print("state.score",state.score)
                            # print("newscore",newscore)
                            # print("bestP_j1_before",self.bestP.get_state(j1_node, temp))
                            self.update_if_better(
                                self.bestP.get_state(j1_node, temp),
                                newscore, cai_score, self.bestP, j1_node, temp
                            )
                            # print("bestP_j1_after", self.bestP.get_state(j1_node, temp))

                system_start1 = time.time()
                # 处理右侧 bulge: ((...)..)
                # print("..right_bulge: ((...)..) -------")
                for j1_node, _ in dfa.auxiliary_right_edges.get(j_node, {}).items():
                    for i_1_node_nuci_1 in dfa.left_edges.get(i_node, []):
                        i_1_node = i_1_node_nuci_1[0]
                        nuci_1 = i_1_node[2]
                        weight_nuci_1 = i_1_node_nuci_1[1]

                        q_list = self.next_list[nuci_1].get(j1_node, [])
                        # print("nuci_1", nuci_1)
                        # print("j1_node", j1_node)
                        # print("q_list", q_list)
                        for q_node_nucq in q_list:
                            q_node = q_node_nucq[0]
                            q = q_node[0]
                            if q - j > SINGLE_MAX_LEN:
                                break
                            nucq = q_node_nucq[1]
                            weight_nucq = q_node_nucq[2]
                            outer_pair = NTP(nuci_1, nucq)

                            for q1_node, _ in dfa.auxiliary_right_edges.get(q_node, {}).items():
                                if nucq != q_node[2]:
                                    continue
                                newscore = self.bulge_score[outer_pair - 1][pair_nuc - 1][q - j - 1] + state.score

                                if (q - j) <= SINGLE_MAX_LEN:
                                    cai_score = state.cai_score + (
                                            weight_nuci_1 + weight_nucq +
                                            self.get_broken_codon_score_map[j_node][q_node]
                                    )
                                else:
                                    cai_score = state.cai_score + (
                                            weight_nuci_1 + weight_nucq +
                                            self.get_broken_codon_score(j_node, q_node)
                                    )

                                temp = (i_1_node[0], i_1_node[1], outer_pair)

                                # print("cai_score", cai_score)
                                # print("bulge_score", self.bulge_score[outer_pair - 1][pair_nuc - 1][q - j - 1])
                                # print("state.score", state.score)
                                # print("newscore", newscore)
                                # print("bestP_q1_before", self.bestP.get_state(q1_node, temp))
                                self.update_if_better(
                                    self.bestP.get_state(q1_node, temp),
                                    newscore, cai_score, self.bestP, q1_node, temp
                                )
                                # print("bestP_q1_after", self.bestP.get_state(q1_node, temp))

                system_duration = time.time() - system_start1
                # if j > 30:
                #     print('right bulge time :', system_duration)
                #     print('\n')
                # 处理左侧 bulge: (..(...))
                # print("..left_bulge: (..(...)) -------")
                system_start1 = time.time()
                for j1_node_nucj in dfa.right_edges.get(j_node, []):
                    j1_node = j1_node_nucj[0]
                    weight_nucj = j1_node_nucj[1]

                    for i_1_node_nuci_1 in dfa.auxiliary_left_edges.get(i_node, {}).keys():
                        i_1_node = i_1_node_nuci_1
                        p_list = self.prev_list[nucj].get(i_1_node, [])
                        # print("nucj", nucj)
                        # print("i_1_node", i_1_node)
                        # print("p_list", p_list)
                        for p_node_nucp_1 in p_list:
                            p_node = p_node_nucp_1[0]
                            p = p_node[0]
                            if i - p > SINGLE_MAX_LEN:
                                break
                            nucp_1 = p_node_nucp_1[1]
                            outer_pair = NTP(nucp_1, nucj)
                            for p_1_node_nucp_1 in dfa.left_edges.get(p_node, []):
                                p_1_node = p_1_node_nucp_1[0]
                                weight_nucp_1 = p_1_node_nucp_1[1]
                                if nucp_1 != p_1_node[2]:
                                    continue
                                newscore = self.bulge_score[outer_pair - 1][pair_nuc - 1][i - p - 1] + state.score

                                if (i - p) <= SINGLE_MAX_LEN:
                                    cai_score = state.cai_score + (
                                            weight_nucp_1 + weight_nucj +
                                            self.get_broken_codon_score_map[p_node][i_node]
                                    )
                                else:
                                    cai_score = state.cai_score + (
                                            weight_nucp_1 + weight_nucj +
                                            self.get_broken_codon_score(p_node, i_node)
                                    )

                                temp = (p_1_node[0], p_1_node[1], outer_pair)
                                # print("cai_score", cai_score)
                                # print("bulge_score", self.bulge_score[outer_pair - 1][pair_nuc - 1][i - p - 1])
                                # print("state.score", state.score)
                                # print("newscore", newscore)
                                # print("bestP_j1_before", self.bestP.get_state(j1_node, temp))
                                self.update_if_better(
                                    self.bestP.get_state(j1_node, temp),
                                    newscore, cai_score, self.bestP, j1_node, temp
                                )
                                # print("bestP_j1_after", self.bestP.get_state(j1_node, temp))

                system_duration = time.time() - system_start1
                # if j > 30:
                #     print('left bulge time :', system_duration)
                #     print('\n')
                # 处理 internal loop
                # print("..internal_loop: (..(...)..) -------")
                system_start1 = time.time()
                for j1_node, weight_nucj in dfa.auxiliary_right_edges[j_node].items():
                    # j1_node 是 (index, num, nuc)，因此
                    j1_num = j1_node[1]

                    # 遍历 left_edges[i_node] -> List[ (NodeType, float) ]
                    for i_1_node, weight_nuci_1 in dfa.left_edges[i_node]:
                        i_1_num = i_1_node[1]
                        nuci_1 = i_1_node[2]
                        # p 从 i-1 遍历到 max(i - SINGLE_MAX_LEN, 0) (递减)
                        for p in range(i - 1, max(i - SINGLE_MAX_LEN, 0), -1):
                            p_node_list = []

                            if p == i - 1:
                                # 直接把 i_1_node 加进来
                                p_node_list.append(i_1_node)

                            elif p == i - 2:
                                # auxiliary_left_edges[i_1_node] 是 dict[NodeType -> float]
                                # 只要 key (p_node) 就好
                                for p_node_in_dict, _ in dfa.auxiliary_left_edges[i_1_node].items():
                                    p_node_list.append(p_node_in_dict)

                            else:
                                # p < i - 2, 直接用 dfa.nodes[p] (List[NodeType])
                                p_node_list = dfa.nodes[p]

                            # 遍历 p_node_list
                            for p_node in p_node_list:
                                # dfa.right_edges[p_node] 是 List[ (NodeType, float) ]
                                for p1_node, weight_nucp in dfa.right_edges[p_node]:
                                    p1_num = p1_node[1]
                                    nucp = p_node[2]  # 与C++一致: nucp = std::get<2>(p_node);
                                    # 分支判断
                                    if p == i - 1 and (p1_num != i_num):
                                        continue
                                    elif p == i - 2 and (p1_num != i_1_num):
                                        continue
                                    elif p == i - 3:
                                        # p == i-3 需要二次校验 p2_node
                                        for p2_node, _ in dfa.right_edges[p1_node]:
                                            p2_num = p2_node[1]
                                            if p2_num != i_1_num:
                                                continue
                                            else:
                                                # 再遍历 left_edges[p_node]
                                                for p_1_node, weight_nucp_1 in dfa.left_edges[p_node]:
                                                    nucp_1 = p_1_node[2]
                                                    # 获取 self.next_list[nucp_1][j1_node]
                                                    q_list = self.next_list[nucp_1].get(j1_node, [])

                                                    for q_node_nucq in q_list:
                                                        q_node = q_node_nucq[0]
                                                        q_num = q_node[1]
                                                        q = q_node[0]
                                                        nucq = q_node_nucq[1]
                                                        weight_nucq = q_node_nucq[2]

                                                        if (i - p + q - j) > SINGLE_MAX_LEN:
                                                            break

                                                        # 遍历 auxiliary_right_edges[q_node]
                                                        for q1_node, _ in dfa.auxiliary_right_edges[q_node].items():
                                                            # 组装 self.bestP 索引
                                                            p_1 = p_1_node[0]
                                                            nump_1 = p_1_node[1]
                                                            temp = (p_1, nump_1, NTP(nucp_1, nucq))
                                                            BestP_val = self.bestP.get_state(q1_node, temp)

                                                            nucj = j_node[2]  # (j, j_num, nuc_j)
                                                            # 这里 weight_nucj 就来自外层 for j1_node, weight_nucj in ...
                                                            # q 与 j 的差值判断
                                                            if q == j + 1:
                                                                # q == j+1
                                                                newscore = -func14(
                                                                    p - 1, q, i, j - 1,
                                                                    nucp_1, nucp, nucj, nucq,
                                                                    nuci_1, nuci, nucj_1, nucj, self.params
                                                                ) + state.score
                                                                if p == i - 1:
                                                                    weight_left = weight_nucp_1 + weight_nucp
                                                                else:
                                                                    if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                        weight_left = (weight_nucp_1 + weight_nucp +
                                                                                       self.get_broken_codon_score_map[
                                                                                           p1_node][i_1_node]
                                                                                       + weight_nuci_1)
                                                                    else:
                                                                        weight_left = (weight_nucp_1 + weight_nucp
                                                                                       + self.get_broken_codon_score(
                                                                                    p1_node, i_1_node)
                                                                                       + weight_nuci_1)

                                                                cai_score = state.cai_score + (
                                                                        weight_left + weight_nucj + weight_nucq)

                                                                # print("cai_score", cai_score)
                                                                # print("func_score",-func14(
                                                                #     p - 1, q, i, j - 1,
                                                                #     nucp_1, nucp, nucj, nucq,
                                                                #     nuci_1, nuci, nucj_1, nucj, self.params
                                                                # ))
                                                                # print("state.score", state.score)
                                                                # print("newscore", newscore)
                                                                # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))

                                                                self.update_if_better(BestP_val, newscore, cai_score,
                                                                                      self.bestP, q1_node, temp)
                                                                # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))


                                                            elif q == j + 2:
                                                                # q == j+2
                                                                # 遍历 auxiliary_left_edges[q_node]
                                                                for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                                    q_node].items():
                                                                    q_1_num = q_1_node[1]
                                                                    if q_1_num != j1_num:
                                                                        continue

                                                                    nucq_1 = q_1_node[2]
                                                                    newscore = -func14(
                                                                        p - 1, q, i, j - 1,
                                                                        nucp_1, nucp, nucq_1, nucq,
                                                                        nuci_1, nuci, nucj_1, nucj, self.params
                                                                    ) + state.score

                                                                    if p == i - 1:
                                                                        weight_left = weight_nucp_1 + weight_nucp
                                                                    else:
                                                                        if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                            weight_left = (
                                                                                    weight_nucp_1 + weight_nucp +
                                                                                    self.get_broken_codon_score_map[
                                                                                        p1_node][i_1_node]
                                                                                    + weight_nuci_1
                                                                            )
                                                                        else:
                                                                            weight_left = (
                                                                                    weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                                p1_node, i_1_node)
                                                                                    + weight_nuci_1
                                                                            )
                                                                    cai_score = state.cai_score + (
                                                                            weight_left + weight_nucj + weight_nucq_1 + weight_nucq)

                                                                    # print("cai_score", cai_score)
                                                                    # print("func_score", -func14(
                                                                    #     p - 1, q, i, j - 1,
                                                                    #     nucp_1, nucp, nucq_1, nucq,
                                                                    #     nuci_1, nuci, nucj_1, nucj, self.params
                                                                    # ))
                                                                    # print("state.score", state.score)
                                                                    # print("newscore", newscore)
                                                                    # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))

                                                                    self.update_if_better(BestP_val, newscore,
                                                                                          cai_score, self.bestP,
                                                                                          q1_node, temp)

                                                                    # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                                                            elif q == j + 3:
                                                                # q == j+3
                                                                # 遍历 auxiliary_left_edges[q_node]
                                                                for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                                    q_node].items():
                                                                    # q_1_num = q_1_node[1]
                                                                    # 再遍历 left_edges[q_1_node]
                                                                    for q_2_node, _ in dfa.left_edges[q_1_node]:
                                                                        q_2_num = q_2_node[1]
                                                                        if q_2_num != j1_num:
                                                                            continue
                                                                        nucq_1 = q_1_node[2]

                                                                        newscore = -func14(
                                                                            p - 1, q, i, j - 1,
                                                                            nucp_1, nucp, nucq_1, nucq,
                                                                            nuci_1, nuci, nucj_1, nucj, self.params
                                                                        ) + state.score

                                                                        if p == i - 1:
                                                                            weight_left = weight_nucp_1 + weight_nucp
                                                                        else:
                                                                            if (i_1_node[0] - p1_node[
                                                                                0]) <= SINGLE_MAX_LEN:
                                                                                weight_left = (
                                                                                        weight_nucp_1 + weight_nucp +
                                                                                        self.get_broken_codon_score_map[
                                                                                            p1_node][i_1_node]
                                                                                        + weight_nuci_1
                                                                                )
                                                                            else:
                                                                                weight_left = (
                                                                                        weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                                    p1_node, i_1_node)
                                                                                        + weight_nuci_1
                                                                                )

                                                                        if (q_1_node[0] - j1_node[0]) <= SINGLE_MAX_LEN:
                                                                            cai_score = state.cai_score + (
                                                                                    weight_left + weight_nucj +
                                                                                    self.get_broken_codon_score_map[
                                                                                        j1_node][q_1_node]
                                                                                    + weight_nucq_1 + weight_nucq)
                                                                        else:
                                                                            cai_score = state.cai_score + (
                                                                                    weight_left + weight_nucj
                                                                                    + self.get_broken_codon_score(
                                                                                j1_node, q_1_node)
                                                                                    + weight_nucq_1 + weight_nucq
                                                                            )

                                                                        # print("cai_score", cai_score)
                                                                        # print("func_score", -func14(
                                                                        #     p - 1, q, i, j - 1,
                                                                        #     nucp_1, nucp, nucq_1, nucq,
                                                                        #     nuci_1, nuci, nucj_1, nucj, self.params
                                                                        # ))
                                                                        # print("state.score", state.score)
                                                                        # print("newscore", newscore)
                                                                        # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))

                                                                        self.update_if_better(BestP_val, newscore,
                                                                                              cai_score, self.bestP,
                                                                                              q1_node, temp)
                                                                        # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                                                            else:
                                                                # q > j+3 或其他
                                                                for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                                    q_node].items():
                                                                    nucq_1 = q_1_node[2]
                                                                    newscore = -func14(
                                                                        p - 1, q, i, j - 1,
                                                                        nucp_1, nucp, nucq_1, nucq,
                                                                        nuci_1, nuci, nucj_1, nucj, self.params
                                                                    ) + state.score

                                                                    if p == i - 1:
                                                                        weight_left = weight_nucp_1 + weight_nucp
                                                                    else:
                                                                        if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                            weight_left = (weight_nucp_1 + weight_nucp
                                                                                           +
                                                                                           self.get_broken_codon_score_map[
                                                                                               p1_node][i_1_node]
                                                                                           + weight_nuci_1
                                                                                           )
                                                                        else:
                                                                            weight_left = (weight_nucp_1 + weight_nucp
                                                                                           + self.get_broken_codon_score(
                                                                                        p1_node, i_1_node)
                                                                                           + weight_nuci_1
                                                                                           )
                                                                    if (q_1_node[0] - j1_node[0]) <= SINGLE_MAX_LEN:
                                                                        cai_score = state.cai_score + (
                                                                                weight_left + weight_nucj
                                                                                + self.get_broken_codon_score_map[
                                                                                    j1_node][q_1_node]
                                                                                + weight_nucq_1 + weight_nucq
                                                                        )
                                                                    else:
                                                                        cai_score = state.cai_score + (
                                                                                weight_left + weight_nucj
                                                                                + self.get_broken_codon_score(j1_node,
                                                                                                              q_1_node)
                                                                                + weight_nucq_1 + weight_nucq
                                                                        )
                                                                    # print("cai_score", cai_score)
                                                                    # print("func_score", -func14(
                                                                    #     p - 1, q, i, j - 1,
                                                                    #     nucp_1, nucp, nucq_1, nucq,
                                                                    #     nuci_1, nuci, nucj_1, nucj, self.params
                                                                    # ))
                                                                    # print("state.score", state.score)
                                                                    # print("newscore", newscore)
                                                                    # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))

                                                                    self.update_if_better(BestP_val, newscore,
                                                                                          cai_score, self.bestP,
                                                                                          q1_node, temp)

                                                                    # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))
                                        # 处理完 p == i-3 的情况后 continue
                                        continue

                                    else:
                                        # 处理 p < i-3 (或不满足上述条件时) 的 else 分支
                                        for p_1_node, weight_nucp_1 in dfa.left_edges[p_node]:
                                            nucp_1 = p_1_node[2]
                                            q_list = self.next_list[nucp_1].get(j1_node, [])

                                            for q_node_nucq in q_list:
                                                q_node = q_node_nucq[0]
                                                # q_num = q_node[1]
                                                q = q_node[0]
                                                if i - p + q - j > SINGLE_MAX_LEN:
                                                    break
                                                nucq = q_node_nucq[1]
                                                weight_nucq = q_node_nucq[2]

                                                for q1_node, _ in dfa.auxiliary_right_edges[q_node].items():
                                                    p_1 = p_1_node[0]
                                                    nump_1 = p_1_node[1]
                                                    temp = (p_1, nump_1, NTP(nucp_1, nucq))
                                                    BestP_val = self.bestP.get_state(q1_node, temp)

                                                    nucj = j_node[2]

                                                    if q == j + 1:
                                                        newscore = -func14(
                                                            p - 1, q, i, j - 1,
                                                            nucp_1, nucp, nucj, nucq,
                                                            nuci_1, nuci, nucj_1, nucj, self.params
                                                        ) + state.score
                                                        if p == i - 1:
                                                            weight_left = weight_nucp_1 + weight_nucp
                                                        else:
                                                            if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                weight_left = weight_nucp_1 + weight_nucp + \
                                                                              self.get_broken_codon_score_map[p1_node][
                                                                                  i_1_node] + weight_nuci_1

                                                            else:
                                                                weight_left = weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                    p1_node, i_1_node) + weight_nuci_1

                                                        cai_score = state.cai_score + (
                                                                weight_left + weight_nucj + weight_nucq)

                                                        # print("cai_score", cai_score)
                                                        # print("func_score", -func14(
                                                        #     p - 1, q, i, j - 1,
                                                        #     nucp_1, nucp, nucj, nucq,
                                                        #     nuci_1, nuci, nucj_1, nucj, self.params
                                                        # ))
                                                        # print("state.score", state.score)
                                                        # print("newscore", newscore)
                                                        # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))

                                                        self.update_if_better(BestP_val, newscore, cai_score,
                                                                              self.bestP, q1_node, temp)
                                                        # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                                                    elif q == j + 2:
                                                        for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                            q_node].items():
                                                            q_1_num = q_1_node[1]
                                                            if q_1_num != j1_num:
                                                                continue

                                                            nucq_1 = q_1_node[2]
                                                            newscore = -func14(
                                                                p - 1, q, i, j - 1,
                                                                nucp_1, nucp, nucq_1, nucq,
                                                                nuci_1, nuci, nucj_1, nucj, self.params
                                                            ) + state.score

                                                            if p == i - 1:
                                                                weight_left = weight_nucp_1 + weight_nucp
                                                            else:
                                                                if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                    weight_left = weight_nucp_1 + weight_nucp + \
                                                                                  self.get_broken_codon_score_map[
                                                                                      p1_node][i_1_node] + weight_nuci_1
                                                                else:
                                                                    weight_left = weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                        p1_node, i_1_node) + weight_nuci_1

                                                            cai_score = state.cai_score + (
                                                                    weight_left + weight_nucj + weight_nucq_1 + weight_nucq)
                                                            # print("cai_score", cai_score)
                                                            # print("func_score", -func14(
                                                            #     p - 1, q, i, j - 1,
                                                            #     nucp_1, nucp, nucq_1, nucq,
                                                            #     nuci_1, nuci, nucj_1, nucj, self.params
                                                            # ))
                                                            # print("state.score", state.score)
                                                            # print("newscore", newscore)
                                                            # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))
                                                            self.update_if_better(BestP_val, newscore, cai_score,
                                                                                  self.bestP, q1_node, temp)
                                                            # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                                                    elif q == j + 3:
                                                        for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                            q_node].items():
                                                            # q_1_num = q_1_node[1]
                                                            for q_2_node, _ in dfa.left_edges[q_1_node]:
                                                                q_2_num = q_2_node[1]
                                                                if q_2_num != j1_num:
                                                                    continue

                                                                nucq_1 = q_1_node[2]
                                                                newscore = -func14(
                                                                    p - 1, q, i, j - 1,
                                                                    nucp_1, nucp, nucq_1, nucq,
                                                                    nuci_1, nuci, nucj_1, nucj, self.params
                                                                ) + state.score
                                                                if p == i - 1:
                                                                    weight_left = weight_nucp_1 + weight_nucp
                                                                else:
                                                                    if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                        weight_left = weight_nucp_1 + weight_nucp + \
                                                                                      self.get_broken_codon_score_map[
                                                                                          p1_node][
                                                                                          i_1_node] + weight_nuci_1

                                                                    else:
                                                                        weight_left = weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                            p1_node, i_1_node) + weight_nuci_1

                                                                if (q_1_node[0] - j1_node[0]) <= SINGLE_MAX_LEN:
                                                                    cai_score = state.cai_score + (
                                                                            weight_left
                                                                            + weight_nucj
                                                                            + self.get_broken_codon_score_map[j1_node][
                                                                                q_1_node]
                                                                            + weight_nucq_1
                                                                            + weight_nucq
                                                                    )
                                                                else:
                                                                    cai_score = state.cai_score + (
                                                                            weight_left
                                                                            + weight_nucj
                                                                            + self.get_broken_codon_score(j1_node,
                                                                                                          q_1_node)
                                                                            + weight_nucq_1
                                                                            + weight_nucq
                                                                    )
                                                                # print("cai_score", cai_score)
                                                                # print("func_score", -func14(
                                                                #     p - 1, q, i, j - 1,
                                                                #     nucp_1, nucp, nucq_1, nucq,
                                                                #     nuci_1, nuci, nucj_1, nucj, self.params
                                                                # ))
                                                                # print("state.score", state.score)
                                                                # print("newscore", newscore)
                                                                # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))
                                                                self.update_if_better(BestP_val, newscore, cai_score,
                                                                                      self.bestP, q1_node, temp)
                                                                # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                                                    else:
                                                        # q > j+3 或其他
                                                        for q_1_node, weight_nucq_1 in dfa.auxiliary_left_edges[
                                                            q_node].items():
                                                            nucq_1 = q_1_node[2]
                                                            newscore = -func14(
                                                                p - 1, q, i, j - 1,
                                                                nucp_1, nucp, nucq_1, nucq,
                                                                nuci_1, nuci, nucj_1, nucj, self.params
                                                            ) + state.score

                                                            if p == i - 1:
                                                                weight_left = weight_nucp_1 + weight_nucp
                                                            else:
                                                                if (i_1_node[0] - p1_node[0]) <= SINGLE_MAX_LEN:
                                                                    weight_left = weight_nucp_1 + weight_nucp + \
                                                                                  self.get_broken_codon_score_map[
                                                                                      p1_node][i_1_node] + weight_nuci_1

                                                                else:
                                                                    weight_left = weight_nucp_1 + weight_nucp + self.get_broken_codon_score(
                                                                        p1_node, i_1_node) + weight_nuci_1

                                                            if (q_1_node[0] - j1_node[0]) <= SINGLE_MAX_LEN:
                                                                cai_score = state.cai_score + (
                                                                        weight_left
                                                                        + weight_nucj
                                                                        + self.get_broken_codon_score_map[j1_node][
                                                                            q_1_node]
                                                                        + weight_nucq_1
                                                                        + weight_nucq
                                                                )
                                                            else:
                                                                cai_score = state.cai_score + (
                                                                        weight_left
                                                                        + weight_nucj
                                                                        + self.get_broken_codon_score(j1_node, q_1_node)
                                                                        + weight_nucq_1
                                                                        + weight_nucq
                                                                )
                                                            # print("cai_score", cai_score)
                                                            # print("func_score", -func14(
                                                            #     p - 1, q, i, j - 1,
                                                            #     nucp_1, nucp, nucq_1, nucq,
                                                            #     nuci_1, nuci, nucj_1, nucj, self.params
                                                            # ))
                                                            # print("state.score", state.score)
                                                            # print("newscore", newscore)
                                                            # print("bestP_q1_before",self.bestP.get_state(q1_node, temp))
                                                            self.update_if_better(BestP_val, newscore, cai_score,
                                                                                  self.bestP, q1_node, temp)
                                                            # print("bestP_q1_after",self.bestP.get_state(q1_node, temp))

                system_duration = time.time() - system_start1
                # if j > 30:
                #     print('internal loop time :', system_duration)
                #     print('\n')

        # 3) M = P, M_P = P
        system_start1 = time.time()
        # print("..M = P,M_P = P.........")
        # for i_node_nucpair_ in range(64 * j):
        #     i_node_nucpair = self.reverse_index(i_node_nucpair_)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair2 = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
        for temppair2 in self.alive_P.get(j_node, ()):
            state = self.bestP.get_state(j_node, temppair2)
            if state.score == INT_MIN:
                continue
            # i_node_nucpair = self.reverse_index(i_node_nucpair_)
            # i = i_node_nucpair.node_first
            # i_num = i_node_nucpair.node_second
            # pair_nuc = i_node_nucpair.nucpair
            i, i_num, pair_nuc = int(temppair2[0]), int(temppair2[1]), int(temppair2[2])
            nuci = PTLN(pair_nuc)
            nucj_1 = PTRN(pair_nuc)
            i_node = (i, i_num, nuci)

            if (i > 0) and (j < self.seq_length):
                M1_score = -func6(i, j - 1, j - 1, -1, nuci, nucj_1, -1, self.seq_length, self.params) + state.score
                # print("i_node",i_node)
                # print("nucj_1", nucj_1)
                # print("state.score",state.score)
                # print("fun6_score", -func6(i, j - 1, j - 1, -1, nuci, nucj_1, -1, self.seq_length,self.params))
                # print("M1_score",M1_score)
                # print("before_bestM", self.bestM.get_state(j_node, i_node))
                # print("before_bestM_P", self.bestM_P.get_state(j_node, i_node))
                self.update_if_better(self.bestM.get_state(j_node, i_node), M1_score, state.cai_score, self.bestM,
                                      j_node, i_node)
                self.update_if_better(self.bestM_P.get_state(j_node, i_node), M1_score, state.cai_score, self.bestM_P,
                                      j_node, i_node)
                # print("after_bestM", self.bestM.get_state(j_node, i_node))
                # print("after_bestM_P", self.bestM_P.get_state(j_node, i_node))

        system_duration = time.time() - system_start1
        # if j > 30:
        #     print('case3 loop time :', system_duration)
        #     print('\n')

        # 4) M2 = M + M_P
        system_start1 = time.time()
        # print("..M2 = M + M_P.........")
        # for i_node_ in range(64 * j):
        #     i_node_nucpair = self.reverse_index(i_node_)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair3 = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))

        for i_node in self.alive_M_P.get(j_node, ()):
            state = self.bestM_P.get_state(j_node, i_node)
            if state.score == INT_MIN:
                continue
            # node_nuc = self.reverse_index(i_node_)
            # i_node = (node_nuc.node_first, node_nuc.node_second, node_nuc.nucpair)
            i = i_node[0]

            if i > 0 and j < self.seq_length:
                # for m_node_ in range(64 * i):
                #     m_node_nucpair = self.reverse_index(m_node_)
                #     # print('i_node_nucpair:', i_node_nucpair)
                #     temppair4 = (
                #         int(m_node_nucpair.node_first), int(m_node_nucpair.node_second), int(m_node_nucpair.nucpair))
                for temppair4 in self.alive_M.get(j_node, ()):
                    m_new_state_score = self.bestM.get_state(i_node, temppair4)
                    if m_new_state_score.score == INT_MIN:
                        continue

                    newscore = m_new_state_score.score + state.score
                    cai_score = m_new_state_score.cai_score + state.cai_score

                    # print("i_node",i_node)
                    # print("temppair4", temppair4)
                    # print("m_new_state_score",m_new_state_score.score)
                    # print("state.score",state.score)
                    # print("newscore",newscore)
                    # print("before_bestM2", self.bestM2.get_state(j_node, temppair4))
                    self.update_if_better(self.bestM2.get_state(j_node, temppair4), newscore, cai_score, self.bestM2,
                                          j_node, temppair4)
                    # print("after_bestM2", self.bestM2.get_state(j_node, temppair4))

        system_duration = time.time() - system_start1
        # if j > 30:
        #     print('case4 loop time :', system_duration)
        #     print('\n')

        # 5) C = C + P
        system_start1 = time.time()
        # print("..C = C + P................")
        # for i_node_nucpair_ in range(64 * j):
        #     i_node_nucpair = self.reverse_index(i_node_nucpair_)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair5 = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
        for temppair5 in self.alive_P.get(j_node, ()):
            state = self.bestP.get_state(j_node, temppair5)
            if state.score == INT_MIN:
                continue

            # i_node_nucpair = self.reverse_index(i_node_nucpair_)
            # i = i_node_nucpair.node_first
            # i_num = i_node_nucpair.node_second
            # pair_nuc = i_node_nucpair.nucpair
            i, i_num, pair_nuc = int(temppair5[0]), int(temppair5[1]), int(temppair5[2])
            nuci = PTLN(pair_nuc)
            nucj_1 = PTRN(pair_nuc)
            i_node = (i, i_num, nuci)

            # print("i_node",i_node)
            # print("p_state.score", state.score)

            if i > 0:
                # prefix_C = self.bestC.get_state(i_node)
                # #print("prefix_C ", prefix_C)
                # if prefix_C.score != INT_MIN:
                #     newscore = -func3(i, j - 1, nuci, nucj_1, self.seq_length) \
                #                + prefix_C.score + state.score
                #     cai_score = prefix_C.cai_score + state.cai_score
                #     # print("newscore",newscore)
                #     # print(self.bestC.get_state(j_node))
                #     self.update_if_better(self.bestC.get_state(j_node), newscore, cai_score, self.bestC, j_node)
                #     # print(self.bestC.get_state(j_node))
                # else:
                #     # print("prefix_C = 0 ")
                #     newscore = -func3(i, j - 1, nuci, nucj_1, self.seq_length)  \
                #                + 0 + state.score
                #     cai_score = 0 + state.cai_score
                #     print("newscore", newscore)
                #     print("before",self.bestC.get_state(j_node))
                #     self.update_if_better(self.bestC.get_state(j_node), newscore, cai_score, self.bestC, j_node)
                #     print("after",self.bestC.get_state(j_node))

                prefix_C = self.bestC.get_state(i_node)
                # print("prefix_C ", prefix_C)
                # if prefix_C.score != INT_MIN:
                newscore = -func3(i, j - 1, nuci, nucj_1, self.seq_length, self.params) \
                           + prefix_C.score + state.score
                cai_score = prefix_C.cai_score + state.cai_score
                # print("newscore", newscore)
                # print(self.bestC.get_state(j_node))
                self.update_if_better(self.bestC.get_state(j_node), newscore, cai_score, self.bestC, j_node)
                # print(self.bestC.get_state(j_node))

            else:
                newscore = -func3(0, j - 1, nuci, nucj_1, self.seq_length, self.params) + state.score
                # print("newscore", newscore)
                # print(self.bestC.get_state(j_node))
                self.update_if_better(self.bestC.get_state(j_node), newscore, state.cai_score, self.bestC, j_node)
                # print(self.bestC.get_state(j_node))

        system_duration = time.time() - system_start1
        # if j > 30:
        #     print('case5 loop time :', system_duration)
        #     print('\n\n\n')

    def m2_beam(self, j, dfa, j_num):
        """
        处理 M2 Beam 的逻辑。

        参数：
        - j: 当前节点的索引
        - dfa: DFA 实例，包含节点和边信息
        - j_num: 当前节点的核苷酸编号
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        if nuc_j is None:
            return

        j_node = (j, j_num, nuc_j)

        # 遍历所有 i_node_nucpair
        # for i_node_idx in range(64 * j):
        for i_node in self.alive_M2.get(j_node, ()):
            # print(self.bestM2)
            state = self.bestM2.get_state(j_node, i_node)
            if state.score == INT_MIN:
                continue

            # 解析 i_node_nucpair
            # node_nuc = self.reverse_index(i_node_idx)
            # i_node = (node_nuc.node_first, node_nuc.node_second, node_nuc.nucpair)
            i = i_node[0]

            # 处理 multi-loop
            # print("-multi-")
            for p in range(i - 1, max(i - SINGLE_MAX_LEN, 0), -1):
                if p == i - 1:
                    # 从 auxiliary_left_edges 获取 p_node_list
                    p_node_list = [node[0] for node in dfa.auxiliary_left_edges.get(i_node, {}).keys()]
                else:
                    # 从 nodes 获取 p_node_list
                    p_node_list = dfa.nodes.get(p, [])

                for p_node in p_node_list:
                    for p1_node_nucp in dfa.right_edges.get(p_node, []):
                        p1_node = p1_node_nucp[0]
                        nucp = p_node[2]
                        weight_nucp = p1_node_nucp[1]

                        if p == i - 1 and p1_node != i_node:
                            continue

                        if p == i - 2:
                            for p2_node_nucp1 in dfa.right_edges.get(p1_node, []):
                                p2_node = p2_node_nucp1[0]
                                if p2_node != i_node:
                                    continue

                                # 遍历可能的 q
                                q_list = self.next_pair[nucp].get(j_node, [])
                                for q_node_nucq in q_list:
                                    q_node = q_node_nucq[0]
                                    nucq = q_node_nucq[1]
                                    weight_nucq = q_node_nucq[2]
                                    q = q_node[0]

                                    if i - p + q - j - 1 > SINGLE_MAX_LEN:
                                        continue

                                    outer_pair = NTP(nucp, nucq)

                                    for q1_node_newnucq in dfa.right_edges.get(q_node, []):
                                        q1_node = q1_node_newnucq[0]
                                        newnucq = q_node[2]

                                        if newnucq != nucq:
                                            continue
                                        # 计算 CAI 分数
                                        cai_score = state.cai_score + (
                                                weight_nucp +
                                                self.get_broken_codon_score_map.get(p1_node, {}).get(i_node, 0) +
                                                self.get_broken_codon_score_map.get(j_node, {}).get(q_node, 0) +
                                                weight_nucq
                                        )
                                        temp_left_cai = state.cai_score + (
                                                weight_nucp +
                                                self.get_broken_codon_score_map.get(p1_node, {}).get(i_node, 0)
                                        )
                                        temp = (p_node[0], p_node[1], outer_pair)

                                        # 更新 bestMulti

                                        # print("cai_score", cai_score)
                                        # print("state.score", state.score)
                                        # print("newscore", state.score)
                                        # print("before_bestMulti", self.bestMulti.get_state(q1_node, temp))
                                        self.update_if_better_T(
                                            self.bestMulti.get_state(q1_node, temp),
                                            state.score,
                                            cai_score,
                                            j_node,
                                            temp_left_cai,
                                            self.bestMulti,
                                            q1_node,
                                            temp
                                        )
                                        # print("after_bestMulti", self.bestMulti.get_state(q1_node, temp))
                        else:
                            q_list = self.next_pair[nucp].get(j_node, [])
                            for q_node_nucq in q_list:
                                q_node = q_node_nucq[0]
                                nucq = q_node_nucq[1]
                                weight_nucq = q_node_nucq[2]
                                q = q_node[0]

                                if i - p + q - j - 1 > SINGLE_MAX_LEN:
                                    continue

                                outer_pair = NTP(nucp, nucq)

                                for q1_node_newnucq in dfa.right_edges.get(q_node, []):
                                    q1_node = q1_node_newnucq[0]
                                    newnucq = q_node[2]

                                    if newnucq != nucq:
                                        continue
                                    # 计算 CAI 分数
                                    cai_score = state.cai_score + (
                                            weight_nucp +
                                            self.get_broken_codon_score_map.get(p1_node, {}).get(i_node, 0) +
                                            self.get_broken_codon_score_map.get(j_node, {}).get(q_node, 0) +
                                            weight_nucq
                                    )
                                    temp_left_cai = state.cai_score + (
                                            weight_nucp +
                                            self.get_broken_codon_score_map.get(p1_node, {}).get(i_node, 0)
                                    )
                                    temp = (p_node[0], p_node[1], outer_pair)

                                    # print("cai_score", cai_score)
                                    # print("state.score", state.score)
                                    # print("newscore", state.score)
                                    # print("before_bestMulti", self.bestMulti.get_state(q1_node, temp))
                                    # 更新 bestMulti
                                    self.update_if_better_T(
                                        self.bestMulti.get_state(q1_node, temp),
                                        state.score,
                                        cai_score,
                                        j_node,
                                        temp_left_cai,
                                        self.bestMulti,
                                        q1_node,
                                        temp
                                    )
                                    # print("after_bestMulti", self.bestMulti.get_state(q1_node, temp))

            # 更新 M = M2
            # print("-M = M2-")
            # print("before_bestM", self.bestM.get_state(j_node, i_node))
            self.update_if_better(
                self.bestM.get_state(j_node, i_node),
                state.score,
                state.cai_score,
                self.bestM,
                j_node,
                i_node
            )
            # print("after_bestM", self.bestM.get_state(j_node, i_node))

    def m_beam(self, j, dfa, j_num):
        """
        处理 M Beam 的逻辑。

        参数：
        - j: 当前节点的索引
        - dfa: DFA 实例，包含节点和边信息
        - j_num: 当前节点的核苷酸编号
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        if nuc_j is None:
            return

        j_node = (j, j_num, nuc_j)

        # 遍历 i_node_nucpair
        # for i_node_idx in range(64 * j):
        #     # 获取当前状态
        #     i_node_nucpair = self.reverse_index(i_node_idx)
        #     # print('i_node_nucpair:', i_node_nucpair)
        #     temppair = (int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
        for i_node in self.alive_M.get(j_node, ()):
            state = self.bestM.get_state(j_node, i_node)
            if state.score == INT_MIN:
                continue

            # 解析 i_node_nucpair
            # node_nuc = self.reverse_index(i_node_idx)
            # i_node = (int(node_nuc.node_first), int(node_nuc.node_second), int(node_nuc.nucpair))

            # 遍历 j_node 的右边界
            for j1_node_nucj in dfa.right_edges.get(j_node, []):
                j1_node = j1_node_nucj[0]
                weight_nucj = j1_node_nucj[1]

                # 计算新的 CAI 分数
                cai_score = state.cai_score + weight_nucj

                # 更新 self.bestM
                # print("-m_beam-")
                # print("state.score", state.score)
                # print("cai_score", cai_score)

                # print("before_bestM", self.bestM.get_state(j_node, i_node))
                self.update_if_better(
                    self.bestM.get_state(j1_node, i_node),
                    state.score,
                    cai_score,
                    self.bestM,
                    j1_node,
                    i_node
                )
                # print("after_bestM", self.bestM.get_state(j_node, i_node))

    def c_beam(self, j, dfa, j_num):
        """
        处理 C Beam 的逻辑。

        参数：
        - j: 当前节点的索引
        - dfa: DFA 实例，包含节点和边信息
        - j_num: 当前节点的核苷酸编号
        """
        # 获取核苷酸 nuc_j
        nuc_j = None
        for j_at_node in dfa.nodes[j]:
            j_at_num = j_at_node[1]
            if j_num == j_at_num:
                nuc_j = j_at_node[2]
                break

        # if nuc_j is None:
        #     return

        j_node = (j, j_num, nuc_j)

        # 获取当前节点的状态
        state = self.bestC.get_state(j_node)

        # 遍历 j_node 的右边界
        # print(f"j={j},c_beam->j+1")
        for j1_node_nucj in dfa.right_edges.get(j_node, []):
            j1_node = j1_node_nucj[0]
            weight_nucj = j1_node_nucj[1]

            # 更新 CAI 分数
            cai_score = state.cai_score + weight_nucj

            #更新 self.bestC
            # print("j1_node", j1_node)
            # print("state_score", state.score)
            # print("before_c_beam", self.bestC.get_state(j1_node))
            self.update_if_better(
                self.bestC.get_state(j1_node),
                state.score,
                cai_score,
                self.bestC,
                j1_node
            )
            # print("after_c_beam", self.bestC.get_state(j1_node))

    def special_hp(self, dfa, hairpin_length):
        """
        处理特殊发卡环的逻辑。

        参数：
        - dfa: DFA 实例，包含节点和边信息。
        - hairpin_length: 发卡环的长度。
        """
        if self.verbose:
             print(f"Processing special_hp with hairpin_length={hairpin_length}")

        hairpin_type = HAIRPINTYPE(hairpin_length)  # 假设 HAIRPINTYPE 已定义
        queue: List[Tuple[NodeType, str, float, NodeType]] = []
        frontier: List[Tuple[NodeType, str, float, NodeType]] = []

        for i in range(0, self.seq_length - hairpin_length + 1):
            for i_node in dfa.nodes.get(i, []):
                count = hairpin_length
                queue.clear()
                queue.append((i_node, "", 0.0, i_node))
                while count > 0:
                    count -= 1
                    frontier.clear()
                    for node_str in queue:
                        cur_node = node_str[0]
                        cur_str = node_str[1]
                        cur_lncai = node_str[2]
                        for node_nuc in dfa.right_edges.get(cur_node, []):
                            new_node = node_nuc[0]
                            # 假设 GET_ACGU 返回的是字符
                            new_str = cur_str + GET_ACGU(cur_node[2])  # 假设 GET_ACGU 已定义
                            new_total_lncai = cur_lncai + node_nuc[1]
                            frontier.append((new_node, new_str, new_total_lncai, cur_node))
                    queue, frontier = frontier, queue  # 交换队列

                for node_str in queue:
                    j_node = node_str[3]
                    temp_seq = node_str[1]
                    cai_score = node_str[2]
                    current_hairpin_length = len(temp_seq)
                    current_hairpin_type = HAIRPINTYPE(current_hairpin_length)  # 假设 HAIRPINTYPE 已定义

                    if current_hairpin_length == 0:
                        continue  # 避免空序列

                    nuci = GET_ACGU_NUC(temp_seq[0])  # 假设 GET_ACGU_NUC 已定义
                    nucj = GET_ACGU_NUC(temp_seq[-1])  # 假设 GET_ACGU_NUC 已定义
                    temp_nucpair = NTP(nuci, nucj)  # 假设 NTP 已定义
                    special_hairpin_score = func1(temp_seq, current_hairpin_type, self.params)  # 假设 func1 已定义

                    if special_hairpin_score == SPECIAL_HAIRPIN_SCORE_BASELINE:  # 假设 SPECIAL_HAIRPIN_SCORE_BASELINE 已定义
                        if current_hairpin_length < 2:
                            continue  # 避免索引错误
                        newscore = -func12(  # 假设 func12 已定义
                            0,
                            current_hairpin_length - 1,
                            GET_ACGU_NUC(temp_seq[0]),
                            GET_ACGU_NUC(temp_seq[1]),
                            GET_ACGU_NUC(temp_seq[current_hairpin_length - 2]),
                            GET_ACGU_NUC(temp_seq[current_hairpin_length - 1]),
                            self.tetra_hex_tri,  # 请确保 self.tetra_hex_tri 已在类中定义
                            self.params
                        )
                        self.hairpin_seq_score_cai[i_node][j_node][temp_nucpair].append(
                            (temp_seq, newscore, cai_score)
                        )
                        if self.verbose:
                             print(f"Added baseline hairpin: {temp_seq}, score: {newscore}, cai_score: {cai_score}")
                    else:
                        self.hairpin_seq_score_cai[i_node][j_node][temp_nucpair].append(
                            (temp_seq, special_hairpin_score, cai_score)
                        )
                        if self.verbose:
                             print(
                                f"Added special hairpin: {temp_seq}, score: {special_hairpin_score}, cai_score: {cai_score}"
                            )

    def backtrace(
            self,
            dfa,
            state: State,
            end_node: NodeType
    ) -> BacktraceResult:
        """
        执行回溯以生成序列和结构。

        参数：
        - dfa: DFA 实例，包含节点和边信息。
        - state: 终止状态。
        - end_node: 结束节点。

        返回：
        - BacktraceResult: 包含序列和结构的结果。
        """
        sequence = ['.'] * self.seq_length
        structure = ['.'] * self.seq_length

        stk = []
        # 假设 dfa.nodes[0][0] 对应 start_node
        start_node = dfa.nodes[0][0]
        stk.append((start_node, end_node, state, BeamType.BEAM_C, -1))

        epsilon = 1e-6

        while stk:
            top = stk.pop()
            i_node, j_node, state, beam_type, curr_pair_nuc = top
            i = i_node[0]
            j = j_node[0]
            nuci = PTLN(curr_pair_nuc)
            nucj_1 = PTRN(curr_pair_nuc)
            no_backpointer = True

            if beam_type == BeamType.BEAM_C:
                # print(f"........BEAM_C_j={j}....................")
                # print("i_node", i_node)

                if j <= 0:
                    continue
                # 遍历左边的边

                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                    c_state = self.bestC.get_state(j_1_node)
                    cai_score = c_state.cai_score + weight_nucj_1

                    if (state.score == c_state.score and
                            abs(state.cai_score - cai_score) < epsilon):
                        # print("bestC(j)=bestC(j-1)")
                        # print("state.score", state.score)
                        # print("c_state.score", c_state.score)
                        # print("state.cai_score", state.cai_score)
                        # print("cai_score", cai_score)
                        nucj_1 = j_1_node[2]  # 修改
                        stk.append((i_node, j_1_node, c_state, BeamType.BEAM_C, curr_pair_nuc))
                        sequence[j - 1] = GET_ACGU(nucj_1)
                        no_backpointer = False
                        break

                if no_backpointer:
                    #C = C + P
                    # print("....C = C + P..........")
                    # print("state.score", state.score)
                    # for c_node_nucpair_ in range(64 * self.seq_length):
                    #     i_node_nucpair = self.reverse_index(c_node_nucpair_)
                    #     # print('i_node_nucpair:', i_node_nucpair)
                    #     temppair = (
                    #     int(i_node_nucpair.node_first), int(i_node_nucpair.node_second), int(i_node_nucpair.nucpair))
                    #     p_state = self.bestP.get_state(j_node, temppair)
                    #     if p_state.score == INT_MIN:
                    #         continue
                    for temppair in self.alive_P.get(j_node, ()):
                        # c_node_nucpair = self.reverse_index(c_node_nucpair_)
                        # temppair = (
                        #     int(c_node_nucpair.node_first), int(c_node_nucpair.node_second),
                        #     int(c_node_nucpair.nucpair))
                        p_state = self.bestP.get_state(j_node, temppair)
                        if p_state.score == INT_MIN:
                            continue

                        # c, c_num, pair_nuc = (
                        #     c_node_nucpair.node_first,
                        #     c_node_nucpair.node_second,
                        #     c_node_nucpair.nucpair
                        # )
                        c, c_num, pair_nuc = temppair
                        nucc = PTLN(pair_nuc)
                        nucj_1 = PTRN(pair_nuc)
                        c_node = (c, c_num, nucc)

                        newscore = -func3(c, j - 1, nucc, nucj_1, self.seq_length, self.params) + p_state.score
                        # print("...c_node", c_node)
                        # print("p_state.score", p_state.score)
                        # print("func3_score", -func3(c, j - 1, nucc, nucj_1, self.seq_length,self.params))
                        # print("newscore", newscore)

                        if c > 0:
                            # print("..c>0..")
                            c_state = self.bestC.get_state(c_node)
                            # print("c_state.score", c_state.score)
                            # print("c_state.score + newscore",c_state.score + newscore)
                            cai_score = c_state.cai_score + p_state.cai_score
                            if state.score == c_state.score + newscore and abs(state.cai_score - cai_score) < epsilon:
                                #print("update_stk", i, c, j)
                                stk.append((i_node, c_node, c_state, BeamType.BEAM_C, curr_pair_nuc))
                                stk.append((c_node, j_node, p_state, BeamType.BEAM_P, pair_nuc))
                                no_backpointer = False
                                break
                        else:
                            # print("..c=0..")
                            if (state.score == newscore and
                                    abs(state.cai_score - p_state.cai_score) < epsilon):
                                # print("update_stk", c, j)
                                stk.append((c_node, j_node, p_state, BeamType.BEAM_P, pair_nuc))
                                no_backpointer = False
                                break
                    assert not no_backpointer, "No path matches for BeamType.BEAM_C"

            elif beam_type == BeamType.BEAM_P:
                # print("...........BEAM_P...........")
                hairpin_length = j - i
                # 遍历 j_node 的左边边
                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                    new_nucj_1 = j_1_node[2]
                    if new_nucj_1 != nucj_1:
                        continue

                    # 处理 SPECIAL_HP
                    if SPECIAL_HP and hairpin_length in [5, 6, 8]:
                        key = NTP(nuci, nucj_1)
                        hairpin_seq_scores = self.hairpin_seq_score_cai.get(i_node, {}).get(j_1_node, {}).get(key, [])
                        for seq_score_weight in hairpin_seq_scores:
                            seq, pre_cal_score, pre_cal_cai_score = seq_score_weight
                            if (state.score == pre_cal_score and
                                    abs(state.cai_score - pre_cal_cai_score) < epsilon):
                                for c, nuc in enumerate(seq):
                                    sequence[i + c] = nuc
                                structure[i] = '('
                                structure[j - 1] = ')'
                                no_backpointer = False
                                break
                        if not no_backpointer:
                            break  # 退出当前循环
                    if not no_backpointer:
                        break  # 退出当前循环

                    # 遍历 i_node 的右边边
                    for i1_node, weight_nuci in dfa.right_edges.get(i_node, []):
                        new_nuci = i_node[2]  # 修改i_node[2]->i_node[2]
                        if new_nuci != nuci:
                            continue

                        # helix/ stacking

                        for j_2_node, _ in dfa.left_edges.get(j_1_node, []):
                            nucj_2 = j_2_node[2]
                            # 遍历 i1_node 的右边边
                            for i2_node, _ in dfa.right_edges.get(i1_node, []):
                                nuci1 = i1_node[2]
                                pair_nuc = NTP(nuci1, nucj_2)  # i1_node[2] -> i1_node[2]
                                temp = (i1_node[0], i1_node[1], pair_nuc)

                                p_state = self.bestP.get_state(j_1_node, temp)

                                newscore = -func14(
                                    i, j - 1, i + 1, j - 2,
                                    nuci, nuci1, nucj_2, nucj_1,
                                    nuci, nuci1, nucj_2, nucj_1, self.params
                                ) + p_state.score

                                cai_score = p_state.cai_score + (weight_nuci + weight_nucj_1)

                                if (state.score == newscore and
                                        abs(state.cai_score - cai_score) < epsilon):
                                    # print("...stacking.....")
                                    # print("i_node",i_node)
                                    # print("j_1_node", j_1_node)
                                    stk.append((i1_node, j_1_node, p_state, BeamType.BEAM_P, pair_nuc))
                                    sequence[i] = GET_ACGU(nuci)
                                    sequence[j - 1] = GET_ACGU(nucj_1)
                                    structure[i] = '('
                                    structure[j - 1] = ')'
                                    no_backpointer = False
                                    break

                            if not no_backpointer:
                                break
                        if not no_backpointer:
                            break

                        # 处理 hairpin after main loops
                        temp = (i_node[0], i_node[1], curr_pair_nuc)
                        bestH_state = self.bestH.get_state(j_1_node, temp)
                        if state.score == bestH_state.score:
                            for j_2_node, weight_nucj_2 in dfa.left_edges.get(j_1_node, []):
                                nucj_2 = j_2_node[2]  # 假设 NodeType 有属性 `nuc`
                                j_2 = j_2_node[0]

                                for i1_node, weight_nuci in dfa.right_edges.get(i_node, []):
                                    new_nuci = i_node[2]
                                    if new_nuci != nuci:
                                        continue
                                    for i2_node, weight_nuci1 in dfa.right_edges.get(i1_node, []):
                                        nuci1 = i1_node[2]
                                        if j - 1 - i == 4:
                                            # Special condition when j - 1 - i == 4
                                            for i3_node, _ in dfa.right_edges.get(i2_node, []):
                                                i3_num = i3_node[1]
                                                if i3_num != j_2_node[1]:
                                                    continue
                                                else:
                                                    newscore = -func12(
                                                        i, j - 1, nuci, nuci1, nucj_2, nucj_1,
                                                        self.tetra_hex_tri, self.params
                                                    )
                                                    cai_score = weight_nuci + weight_nuci1 + self.get_broken_codon_score(
                                                        i2_node, j_2_node) + weight_nucj_2 + weight_nucj_1

                                                    if (state.score == newscore and
                                                            abs(state.cai_score - cai_score) < epsilon):
                                                        # print("...hairpin_l=4.....")
                                                        # print("i_node", i_node)
                                                        # print("j_1_node", j_1_node)
                                                        sequence[i] = GET_ACGU(nuci)
                                                        sequence[i + 1] = GET_ACGU(nuci1)
                                                        sequence[j - 2] = GET_ACGU(nucj_2)
                                                        sequence[j - 1] = GET_ACGU(nucj_1)
                                                        structure[i] = '('
                                                        structure[j - 1] = ')'

                                                        # print("i_2_node",i2_node, ", j_2_node", j_2_node)
                                                        temp_string = self.get_nuc_from_dfa_cai(
                                                            dfa, i2_node, j_2_node, self.protein,
                                                            self.best_path_in_one_codon_unit,
                                                            self.aa_best_path_in_a_whole_codon
                                                        )

                                                        count = i2_node[0]  # Assuming i2_node[0] is the start
                                                        for nuc in temp_string:
                                                            sequence[count] = nuc
                                                            count += 1

                                                        assert count == j_2, "Sequence count mismatch in hairpin loop."

                                                        no_backpointer = False
                                                        break
                                        elif j - 1 - i == 5:
                                            # Special condition when j - 1 - i == 4
                                            for i3_node, _ in dfa.right_edges.get(i2_node, []):
                                                i3_num = i3_node[1]
                                                for j_3_node, _ in dfa.left_edges.get(j_2_node, []):
                                                    j_3_num = j_3_node[1]
                                                    if i3_num != j_3_num:
                                                        continue
                                                    else:
                                                        newscore = -func12(
                                                            i, j - 1, nuci, nuci1, nucj_2, nucj_1,
                                                            self.tetra_hex_tri, self.params
                                                        )
                                                        cai_score = weight_nuci + weight_nuci1 + self.get_broken_codon_score(
                                                            i2_node, j_2_node) + weight_nucj_2 + weight_nucj_1

                                                        if (state.score == newscore and
                                                                abs(state.cai_score - cai_score) < epsilon):
                                                            # print("...hairpin_l=5.....")
                                                            # print("i_node", i_node)
                                                            # print("j_1_node", j_1_node)
                                                            sequence[i] = GET_ACGU(nuci)
                                                            sequence[i + 1] = GET_ACGU(nuci1)
                                                            sequence[j - 2] = GET_ACGU(nucj_2)
                                                            sequence[j - 1] = GET_ACGU(nucj_1)
                                                            structure[i] = '('
                                                            structure[j - 1] = ')'

                                                            # print("i_2_node",i2_node, ", j_2_node", j_2_node)
                                                            temp_string = self.get_nuc_from_dfa_cai(
                                                                dfa, i2_node, j_2_node, self.protein,
                                                                self.best_path_in_one_codon_unit,
                                                                self.aa_best_path_in_a_whole_codon
                                                            )

                                                            count = i2_node[0]  # Assuming i2_node[0] is the start
                                                            for nuc in temp_string:
                                                                sequence[count] = nuc
                                                                count += 1

                                                            assert count == j_2, "Sequence count mismatch in hairpin loop."

                                                            no_backpointer = False
                                                            break
                                        else:
                                            # General hairpin condition
                                            newscore = -func12(
                                                i, j - 1, nuci, nuci1, nucj_2, nucj_1,
                                                self.tetra_hex_tri, self.params
                                            )

                                            cai_score = weight_nuci + weight_nuci1 + self.get_broken_codon_score(
                                                i2_node, j_2_node) + weight_nucj_2 + weight_nucj_1

                                            if (state.score == newscore and
                                                    abs(state.cai_score - cai_score) < epsilon):
                                                # print("...hairpin.....")
                                                # print("i_node", i_node)
                                                # print("j_1_node", j_1_node)
                                                sequence[i] = GET_ACGU(nuci)
                                                sequence[i + 1] = GET_ACGU(nuci1)
                                                sequence[j - 2] = GET_ACGU(nucj_2)
                                                sequence[j - 1] = GET_ACGU(nucj_1)
                                                structure[i] = '('
                                                structure[j - 1] = ')'

                                                temp_string = self.get_nuc_from_dfa_cai(
                                                    dfa, i2_node, j_2_node, self.protein,
                                                    self.best_path_in_one_codon_unit,
                                                    self.aa_best_path_in_a_whole_codon
                                                )
                                                count = i2_node[0]
                                                for nuc in temp_string:
                                                    sequence[count] = nuc
                                                    count += 1

                                                assert count == j_2_node[0], "Sequence count mismatch in hairpin loop."

                                                no_backpointer = False
                                                break

                                    if not no_backpointer:
                                        break
                    # 处理 single branch if no backpointer has been found
                    if no_backpointer:
                        right_seq: List[Tuple[int, int]] = []
                        q_node_nucs_list: List[QNodeNucs] = []
                        for q in range(j - 1, max(j - SINGLE_MAX_LEN - 1, i + 5) - 1, -1):
                            right_start = -1
                            right_end = -1
                            q_node_nucs_list.clear()

                            if q == j - 1:
                                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                                    if j_1_node[2] != nucj_1:
                                        continue
                                    q_node = j_1_node
                                    for q_1_node, weight_nucq_1 in dfa.left_edges.get(q_node, []):
                                        nucq_1 = q_1_node[2]
                                        right_seq.append((j - 1, nucj_1))
                                        q_node_nucs_list.append(QNodeNucs(
                                            q_1_node=q_1_node,
                                            q_node=q_node,
                                            nucq_1=nucq_1,
                                            nucq=nucj_1,
                                            nucj_2=nucq_1,
                                            right_seq=right_seq.copy(),
                                            right_start=right_start,
                                            right_end=right_end,
                                            right_start_node=(-1, 0, 0),  # Placeholder
                                            right_end_node=(-1, 0, 0),  # Placeholder
                                            weight_nucq_1=weight_nucq_1,
                                            weight_nucq=0.0,
                                            weight_nucj_2=0.0,
                                            weight_nucj_1=weight_nucj_1,
                                            q_equ_j_1=True,
                                            j_1_node=(-1, 0, 0)
                                        ))
                                        right_seq.clear()

                            elif q == j - 2:
                                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                                    if j_1_node[2] != nucj_1:
                                        continue
                                    for q_node, weight_nucq in dfa.left_edges.get(j_1_node, []):
                                        nucq = q_node[2]
                                        for q_1_node, weight_nucq_1 in dfa.left_edges.get(q_node, []):
                                            nucq_1 = q_1_node[2]
                                            right_seq.extend([
                                                (q, nucq),
                                                (j - 1, nucj_1)
                                            ])
                                            q_node_nucs_list.append(QNodeNucs(
                                                q_1_node=q_1_node,
                                                q_node=q_node,
                                                nucq_1=nucq_1,
                                                nucq=nucq,
                                                nucj_2=nucq,
                                                right_seq=right_seq.copy(),
                                                right_start=right_start,
                                                right_end=right_end,
                                                right_start_node=(-1, 0, 0),  # Placeholder
                                                right_end_node=(-1, 0, 0),  # Placeholder
                                                weight_nucq_1=weight_nucq_1,
                                                weight_nucq=weight_nucq,
                                                weight_nucj_2=0.0,
                                                weight_nucj_1=weight_nucj_1,
                                                q_equ_j_1=False,
                                                j_1_node=j_1_node
                                            ))
                                            right_seq.clear()

                            elif q == j - 3:
                                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                                    if j_1_node[2] != nucj_1:
                                        continue
                                    for j_2_node, weight_nucj_2 in dfa.left_edges.get(j_1_node, []):
                                        nucj_2 = j_2_node[2]  # 假设 NodeType 有属性 `nuc`
                                        for q_node, weight_nucq in dfa.left_edges.get(j_2_node, []):
                                            nucq = q_node[2]
                                            for q_1_node, weight_nucq_1 in dfa.left_edges.get(q_node, []):
                                                nucq_1 = q_1_node[2]
                                                right_seq.extend([
                                                    (q, nucq),
                                                    (j - 2, nucj_2),
                                                    (j - 1, nucj_1)
                                                ])
                                                q_node_nucs_list.append(QNodeNucs(
                                                    q_1_node=q_1_node,
                                                    q_node=q_node,
                                                    nucq_1=nucq_1,
                                                    nucq=nucq,
                                                    nucj_2=nucj_2,
                                                    right_seq=right_seq.copy(),
                                                    right_start=right_start,
                                                    right_end=right_end,
                                                    right_start_node=(-1, 0, 0),
                                                    right_end_node=(-1, 0, 0),
                                                    weight_nucq_1=weight_nucq_1,
                                                    weight_nucq=weight_nucq,
                                                    weight_nucj_2=weight_nucj_2,
                                                    weight_nucj_1=weight_nucj_1,
                                                    q_equ_j_1=False,
                                                    j_1_node=j_1_node
                                                ))
                                                right_seq.clear()

                            elif q == j - 4:
                                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                                    if j_1_node[2] != nucj_1:
                                        continue
                                    for j_2_node, weight_nucj_2 in dfa.left_edges.get(j_1_node, []):
                                        nucj_2 = j_2_node[2]  # 假设 NodeType 有属性 `nuc`
                                        for j_3_node, weight_nucj_3 in dfa.left_edges.get(j_2_node, []):
                                            for q_node, weight_nucq in dfa.left_edges.get(j_3_node, []):
                                                nucq = q_node[2]
                                                for q_1_node, weight_nucq_1 in dfa.left_edges.get(q_node, []):
                                                    nucq_1 = q_1_node[2]
                                                    right_seq.extend([
                                                        (q, nucq),
                                                        (j - 2, nucj_2),
                                                        (j - 1, nucj_1)
                                                    ])
                                                    q_node_nucs_list.append(QNodeNucs(
                                                        q_1_node=q_1_node,
                                                        q_node=q_node,
                                                        nucq_1=nucq_1,
                                                        nucq=nucq,
                                                        nucj_2=nucj_2,
                                                        right_seq=right_seq.copy(),
                                                        right_start=q + 1,
                                                        right_end=j - 2,
                                                        right_start_node=j_3_node,
                                                        right_end_node=j_2_node,
                                                        weight_nucq_1=weight_nucq_1,
                                                        weight_nucq=weight_nucq,
                                                        weight_nucj_2=weight_nucj_2,
                                                        weight_nucj_1=weight_nucj_1,
                                                        q_equ_j_1=False,
                                                        j_1_node=j_1_node
                                                    ))
                                                    right_seq.clear()

                            else:
                                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                                    if j_1_node[2] != nucj_1:
                                        continue
                                    for j_2_node, weight_nucj_2 in dfa.left_edges.get(j_1_node, []):
                                        nucj_2 = j_2_node[2]  # 假设 NodeType 有属性 `nuc`
                                        for q_node in dfa.nodes.get(q, []):
                                            for q1_node, weight_nucq in dfa.right_edges.get(q_node, []):
                                                nucq = q_node[2]
                                                for q_1_node, weight_nucq_1 in dfa.left_edges.get(q_node, []):
                                                    nucq_1 = q_1_node[2]
                                                    right_seq.extend([
                                                        (q, nucq),
                                                        (j - 2, nucj_2),
                                                        (j - 1, nucj_1)
                                                    ])
                                                    q_node_nucs_list.append(QNodeNucs(
                                                        q_1_node=q_1_node,
                                                        q_node=q_node,
                                                        nucq_1=nucq_1,
                                                        nucq=nucq,
                                                        nucj_2=nucj_2,
                                                        right_seq=right_seq.copy(),
                                                        right_start=q + 1,
                                                        right_end=j - 2,
                                                        right_start_node=q1_node,
                                                        right_end_node=j_2_node,
                                                        weight_nucq_1=weight_nucq_1,
                                                        weight_nucq=weight_nucq,
                                                        weight_nucj_2=weight_nucj_2,
                                                        weight_nucj_1=weight_nucj_1,
                                                        q_equ_j_1=False,
                                                        j_1_node=j_1_node
                                                    ))
                                                    right_seq.clear()

                            # 遍历 q_node_nucs_list
                            for q_node_nucs in q_node_nucs_list:
                                q_1_node = q_node_nucs.q_1_node
                                q_node = q_node_nucs.q_node
                                nucq_1 = q_node_nucs.nucq_1
                                nucq = q_node_nucs.nucq
                                nucj_2 = q_node_nucs.nucj_2
                                right_seq = q_node_nucs.right_seq
                                right_start = q_node_nucs.right_start
                                right_end = q_node_nucs.right_end
                                right_start_node = q_node_nucs.right_start_node
                                right_end_node = q_node_nucs.right_end_node
                                weight_nucq_1 = q_node_nucs.weight_nucq_1
                                weight_nucq = q_node_nucs.weight_nucq
                                weight_nucj_2 = q_node_nucs.weight_nucj_2
                                weight_nucj_1 = q_node_nucs.weight_nucj_1
                                q_equ_j_1 = q_node_nucs.q_equ_j_1
                                j_1_node = q_node_nucs.j_1_node

                                weight_right = 0.0
                                weight_left = 0.0

                                if q_equ_j_1:
                                    for i1_node, weight_nuci in dfa.right_edges.get(i_node, []):
                                        new_nuci = i_node[2]
                                        if new_nuci != nuci:
                                            continue

                                        p_list = self.next_list[nucq_1].get(i1_node, [])
                                        for p_node_nucp in p_list:
                                            p_node = p_node_nucp[0]  # 假设 p_node_nucp[0] 是 NodeType 实例
                                            nucp = p_node[2]
                                            p = p_node[0]
                                            pair_nuc = NTP(nucp, nucq_1)

                                            if p == i + 1:
                                                continue  # stack
                                            if (p - i) + (j - q) - 2 > SINGLE_MAX_LEN:
                                                continue

                                            temp = (
                                                p_node[0],
                                                p_node[1],
                                                pair_nuc
                                            )

                                            p_state = self.bestP.get_state(q_node, temp)
                                            newscore = -func14(
                                                i, j - 1, p, q - 1,
                                                nuci, nucp, nucq_1, nucj_1,
                                                nuci, nucp, nucq_1, nucj_1, self.params
                                            ) + p_state.score
                                            weight_left = weight_nuci + self.get_broken_codon_score(i1_node, p_node)
                                            cai_score = p_state.cai_score + (weight_left + weight_nucj_1)

                                            if (state.score == newscore and
                                                    abs(state.cai_score - cai_score) < epsilon):
                                                # print("...left_bulge.....")
                                                # print("i_node", i_node)
                                                # print("j_1_node", j_1_node)
                                                # print("p_node", p_node)
                                                # print("q_1_node", q_1_node)
                                                stk.append(
                                                    (p_node, q_node, p_state, BeamType.BEAM_P, pair_nuc))
                                                sequence[i] = GET_ACGU(nuci)

                                                temp_i1_to_p_nucs = self.get_nuc_from_dfa_cai(
                                                    dfa, i1_node, p_node, self.protein,
                                                    self.best_path_in_one_codon_unit,
                                                    self.aa_best_path_in_a_whole_codon
                                                )
                                                assert len(temp_i1_to_p_nucs) == p - (
                                                        i + 1), "Sequence length mismatch in left bulge."

                                                count = i + 1
                                                for nuc in temp_i1_to_p_nucs:
                                                    sequence[count] = nuc
                                                    count += 1
                                                assert count == p, "Sequence count mismatch after left bulge."

                                                assert len(
                                                    right_seq) == 1, "Right sequence should have exactly one element."
                                                sequence[j - 1] = GET_ACGU(right_seq[0][1])

                                                structure[i] = '('
                                                structure[j - 1] = ')'

                                                no_backpointer = False
                                                break
                                    if not no_backpointer:
                                        break
                                else:
                                    for i1_node, weight_nuci in dfa.right_edges.get(i_node, []):
                                        new_nuci = i_node[2]
                                        if new_nuci != nuci:
                                            continue

                                        p_list = self.next_list[nucq_1].get(i1_node, [])
                                        for p_node_nucp in p_list:
                                            p_node = p_node_nucp[0]  # 假设 p_node_nucp[0] 是 NodeType 实例
                                            weight_nucp = p_node_nucp[2]
                                            nucp = p_node[2]
                                            p = p_node[0]
                                            pair_nuc = NTP(nucp, nucq_1)

                                            if (p - i) + (j - q) - 2 > SINGLE_MAX_LEN:
                                                continue

                                            temp = (
                                                p_node[0],
                                                p_node[1],
                                                pair_nuc
                                            )

                                            p_state = self.bestP.get_state(q_node, temp)

                                            newscore = 0.0
                                            if p == i + 1:
                                                newscore = -func14(
                                                    i, j - 1, p, q - 1,
                                                    nuci, nucp, nucj_2, nucj_1,
                                                    nuci, nucp, nucq_1, nucq, self.params
                                                ) + p_state.score

                                                weight_right = self.get_broken_codon_score(q_node,
                                                                                           j_1_node) + weight_nucj_1

                                                cai_score = p_state.cai_score + (weight_nuci + weight_right)

                                                if (state.score == newscore and
                                                        abs(state.cai_score - cai_score) < epsilon):
                                                    # print("...right_bulge.....")
                                                    # print("i_node", i_node)
                                                    # print("j_1_node", j_1_node)
                                                    # print("p_node", p_node)
                                                    # print("q_1_node", q_1_node)
                                                    stk.append((p_node, q_node, p_state, BeamType.BEAM_P, pair_nuc))
                                                    sequence[i] = GET_ACGU(nuci)
                                                    for idx, nucidx in right_seq:
                                                        sequence[idx] = GET_ACGU(nucidx)

                                                    structure[i] = '('
                                                    structure[j - 1] = ')'

                                                    temp_string = self.get_nuc_from_dfa_cai(
                                                        dfa, q_node, j_1_node, self.protein,
                                                        self.best_path_in_one_codon_unit,
                                                        self.aa_best_path_in_a_whole_codon
                                                    )
                                                    count = q
                                                    for nuc in temp_string:
                                                        sequence[count] = nuc
                                                        count += 1

                                                    assert count == j - 1, "Sequence count mismatch in right bulge."
                                                    no_backpointer = False
                                                    break

                                            elif p == i + 2:
                                                for i2_node, weight_nuci1 in dfa.right_edges.get(i1_node, []):
                                                    if p_node != i2_node:
                                                        continue
                                                    nuci1 = i1_node[2]
                                                    newscore = -func14(
                                                        i, j - 1, p, q - 1,
                                                        nuci, nuci1,
                                                        nucj_2, nucj_1,
                                                        nuci1, nucp, nucq_1, nucq, self.params
                                                    ) + p_state.score

                                                    weight_left = weight_nuci + weight_nuci1
                                                    weight_right = weight_nucq + self.get_broken_codon_score(
                                                        right_start_node,
                                                        right_end_node
                                                    ) + weight_nucj_2 + weight_nucj_1

                                                    cai_score = p_state.cai_score + weight_left + weight_right

                                                    if (state.score == newscore and
                                                            abs(state.cai_score - cai_score) < epsilon):
                                                        # print("...internal_loop.....")
                                                        # print("i_node", i_node)
                                                        # print("j_1_node", j_1_node)
                                                        # print("p_node", p_node)
                                                        # print("q_1_node", q_1_node)
                                                        # print("state.score",state.score)
                                                        # print("p_state.score",p_state.score)
                                                        # print("func_score",-func14(
                                                    #     i, j - 1, p, q - 1,
                                                    #     nuci, nuci1,
                                                    #     nucj_2, nucj_1,
                                                    #     nuci1, nucp, nucq_1, nucq
                                                    # ))
                                                        # print("newscore",newscore)

                                                        stk.append((
                                                            p_node, q_node, p_state, BeamType.BEAM_P,
                                                            pair_nuc))
                                                        sequence[i] = GET_ACGU(nuci)
                                                        sequence[i + 1] = GET_ACGU(nuci1)
                                                        for idx, nucidx in right_seq:
                                                            sequence[idx] = GET_ACGU(nucidx)

                                                        structure[i] = '('
                                                        structure[j - 1] = ')'

                                                        temp_string = self.get_nuc_from_dfa_cai(
                                                            dfa, right_start_node, right_end_node,
                                                            self.protein,
                                                            self.best_path_in_one_codon_unit,
                                                            self.aa_best_path_in_a_whole_codon
                                                        )
                                                        count = right_start
                                                        for nuc in temp_string:
                                                            sequence[count] = nuc
                                                            count += 1

                                                        assert count == right_end, "Sequence count mismatch in internal loop."
                                                        no_backpointer = False
                                                        break

                                            elif p == i + 3:
                                                for p_1_node, weight_nucp_1 in dfa.left_edges.get(p_node, []):
                                                    nucp_1 = p_1_node[2]  # 假设 NodeType 有属性 `nuc`
                                                    for i2_node, weight_nuci1 in dfa.right_edges.get(i1_node, []):
                                                        if p_1_node != i2_node:
                                                            continue
                                                        nuci1 = i1_node[2]
                                                        newscore = -func14(
                                                            i, j - 1, p, q - 1,
                                                            nuci, nuci1,
                                                            nucj_2, nucj_1,
                                                            nucp_1, nucp, nucq_1, nucq, self.params
                                                        ) + p_state.score

                                                        weight_left = weight_nuci + weight_nuci1 + weight_nucp_1
                                                        weight_right = weight_nucq + self.get_broken_codon_score(
                                                            right_start_node,
                                                            right_end_node
                                                        ) + weight_nucj_2 + weight_nucj_1

                                                        cai_score = p_state.cai_score + (
                                                                weight_left + weight_right
                                                        )

                                                        if (state.score == newscore and
                                                                abs(state.cai_score - cai_score) < epsilon):
                                                            # print("...internal_loop.....")
                                                            # print("i_node", i_node)
                                                            # print("j_1_node", j_1_node)
                                                            # print("p_node", p_node)
                                                            # print("q_1_node", q_1_node)
                                                            # print("state.score", state.score)
                                                            # print("p_state.score", p_state.score)
                                                            # print("func_score", -func14(
                                                            #     i, j - 1, p, q - 1,
                                                            #     nuci, nuci1,
                                                            #     nucj_2, nucj_1,
                                                            #     nuci1, nucp, nucq_1, nucq
                                                            # ))
                                                            # print("newscore", newscore)

                                                            stk.append((p_node, q_node, p_state,
                                                                        BeamType.BEAM_P, pair_nuc))
                                                            sequence[i] = GET_ACGU(nuci)
                                                            sequence[i + 1] = GET_ACGU(nuci1)
                                                            sequence[p - 1] = GET_ACGU(nucp_1)
                                                            for idx, nucidx in right_seq:
                                                                sequence[idx] = GET_ACGU(nucidx)

                                                            structure[i] = '('
                                                            structure[j - 1] = ')'

                                                            temp_string = self.get_nuc_from_dfa_cai(
                                                                dfa, right_start_node, right_end_node,
                                                                self.protein,
                                                                self.best_path_in_one_codon_unit,
                                                                self.aa_best_path_in_a_whole_codon
                                                            )
                                                            count = right_start
                                                            for nuc in temp_string:
                                                                sequence[count] = nuc
                                                                count += 1

                                                            assert count == right_end, "Sequence count mismatch in internal loop."
                                                            no_backpointer = False
                                                            break

                                            elif p == i + 4:
                                                for p_1_node, weight_nucp_1 in dfa.left_edges.get(p_node, []):
                                                    nucp_1 = p_1_node[2]  # 假设 NodeType 有属性 `nuc`
                                                    for i2_node, weight_nuci1 in dfa.right_edges.get(i1_node, []):
                                                        nuci1 = i1_node[2]
                                                        for i3_node, weight_nuci2 in dfa.right_edges.get(i2_node, []):
                                                            if i3_node != p_1_node:
                                                                continue
                                                            nuci2 = i2_node[2]

                                                            newscore = -func14(
                                                                i, j - 1, p, q - 1,
                                                                nuci, nuci1,
                                                                nucj_2, nucj_1,
                                                                nucp_1, nucp, nucq_1, nucq, self.params
                                                            ) + p_state.score

                                                            weight_left = weight_nuci + weight_nuci1 + weight_nuci2 + weight_nucp_1
                                                            weight_right = weight_nucq + self.get_broken_codon_score(
                                                                right_start_node,
                                                                right_end_node
                                                            ) + weight_nucj_2 + weight_nucj_1

                                                            cai_score = p_state.cai_score + (
                                                                    weight_left + weight_right
                                                            )

                                                            if (state.score == newscore and abs(
                                                                    state.cai_score - cai_score) < epsilon):
                                                                # print("...internal_loop.....")
                                                                # print("i_node", i_node)
                                                                # print("j_1_node", j_1_node)
                                                                # print("p_node", p_node)
                                                                # print("q_1_node", q_1_node)
                                                                # print("state.score", state.score)
                                                                # print("p_state.score", p_state.score)
                                                                # print("func_score", -func14(
                                                                #     i, j - 1, p, q - 1,
                                                                #     nuci, nuci1,
                                                                #     nucj_2, nucj_1,
                                                                #     nuci1, nucp, nucq_1, nucq
                                                                # ))
                                                                # print("newscore", newscore)
                                                                stk.append((p_node, q_node, p_state, BeamType.BEAM_P,
                                                                            pair_nuc))
                                                                sequence[i] = GET_ACGU(nuci)
                                                                sequence[i + 1] = GET_ACGU(nuci1)
                                                                sequence[i + 2] = GET_ACGU(nuci2)
                                                                sequence[p - 1] = GET_ACGU(nucp_1)
                                                                for idx, nucidx in right_seq:
                                                                    sequence[idx] = GET_ACGU(nucidx)

                                                                structure[i] = '('
                                                                structure[j - 1] = ')'

                                                                temp_string = self.get_nuc_from_dfa_cai(
                                                                    dfa, right_start_node, right_end_node,
                                                                    self.protein,
                                                                    self.best_path_in_one_codon_unit,
                                                                    self.aa_best_path_in_a_whole_codon
                                                                )
                                                                count = right_start
                                                                for nuc in temp_string:
                                                                    sequence[count] = nuc
                                                                    count += 1

                                                                assert count == right_end, "Sequence count mismatch in internal loop."
                                                                no_backpointer = False
                                                                break

                                            else:
                                                for i2_node, weight_nuci1 in dfa.right_edges.get(i1_node, []):
                                                    nuci1 = i1_node[2]
                                                    for p_1_node, weight_nucp_1 in dfa.left_edges.get(p_node, []):
                                                        nucp_1 = p_1_node[2]  # 假设 NodeType 有属性 `nuc`

                                                        newscore = -func14(
                                                            i, j - 1, p, q - 1,
                                                            nuci, nuci1,
                                                            nucj_2, nucj_1,
                                                            nucp_1, nucp, nucq_1, nucq, self.params
                                                        ) + p_state.score

                                                        weight_left = weight_nuci + weight_nuci1 + self.get_broken_codon_score(
                                                            i2_node, p_1_node) + weight_nucp_1
                                                        weight_right = weight_nucq + self.get_broken_codon_score(
                                                            right_start_node,
                                                            right_end_node
                                                        ) + weight_nucj_2 + weight_nucj_1

                                                        cai_score = p_state.cai_score + (weight_left + weight_right)

                                                        if (state.score == newscore and
                                                                abs(state.cai_score - cai_score) < epsilon):
                                                            # print("...internal_loop.....")
                                                            # print("i_node", i_node)
                                                            # print("j_1_node", j_1_node)
                                                            # print("p_node", p_node)
                                                            # print("q_1_node", q_1_node)
                                                            # print("state.score", state.score)
                                                            # print("p_state.score", p_state.score)
                                                            # print("func_score", -func14(
                                                            #     i, j - 1, p, q - 1,
                                                            #     nuci, nuci1,
                                                            #     nucj_2, nucj_1,
                                                            #     nuci1, nucp, nucq_1, nucq
                                                            # ))
                                                            # print("newscore", newscore)
                                                            stk.append((p_node, q_node, p_state,
                                                                        BeamType.BEAM_P, pair_nuc))
                                                            sequence[i] = GET_ACGU(nuci)
                                                            sequence[i + 1] = GET_ACGU(nuci1)
                                                            sequence[p - 1] = GET_ACGU(nucp_1)
                                                            temp_string = self.get_nuc_from_dfa_cai(
                                                                dfa, i2_node, p_1_node, self.protein,
                                                                self.best_path_in_one_codon_unit,
                                                                self.aa_best_path_in_a_whole_codon
                                                            )
                                                            count = i + 2
                                                            for nuc in temp_string:
                                                                sequence[count] = nuc
                                                                count += 1
                                                            assert count == p - 1, "Sequence count mismatch after internal loop."

                                                            for idx, nucidx in right_seq:
                                                                sequence[idx] = GET_ACGU(nucidx)
                                                            structure[i] = '('
                                                            structure[j - 1] = ')'

                                                            temp_string = self.get_nuc_from_dfa_cai(
                                                                dfa, right_start_node, right_end_node,
                                                                self.protein, self.best_path_in_one_codon_unit,
                                                                self.aa_best_path_in_a_whole_codon
                                                            )
                                                            count = right_start
                                                            for nuc in temp_string:
                                                                sequence[count] = nuc
                                                                count += 1
                                                            assert count == right_end, "Sequence count mismatch in right bulge."
                                                            no_backpointer = False
                                                            break
                                                if not no_backpointer:
                                                    break
                                            if not no_backpointer:
                                                break
                                    if not no_backpointer:
                                        break
                            if not no_backpointer:
                                break

                    # 处理 multi after all conditions
                    if no_backpointer:
                        temp = (i_node[0], i_node[1], curr_pair_nuc)
                        multi_state = self.bestMulti.get_state(j_node, temp)

                        newscore = multi_state.score - func15(i, j, nuci, -1, -1, nucj_1, self.seq_length, self.params)

                        if (state.score == newscore and
                                abs(state.cai_score - multi_state.cai_score) < epsilon):
                            stk.append((i_node, j_node, multi_state, BeamType.BEAM_MULTI, curr_pair_nuc))
                            sequence[i] = GET_ACGU(nuci)
                            sequence[j - 1] = GET_ACGU(nucj_1)
                            structure[i] = '('
                            structure[j - 1] = ')'
                            no_backpointer = False

            elif beam_type == BeamType.BEAM_MULTI:
                # 处理 BeamType.BEAM_MULTI
                nuci = PTLN(curr_pair_nuc)
                nucj_1 = PTRN(curr_pair_nuc)
                j = j_node[0]
                i = i_node[0]

                no_backpointer = True

                for j_1_node_nucj_1 in dfa.left_edges.get(j_node, []):
                    j_1_node = j_1_node_nucj_1[0]
                    weight_nucj_1 = j_1_node_nucj_1[1]
                    q_node = state.pre_node
                    q = q_node[0]

                    if q == j - 1 and q_node != j_1_node:
                        continue

                    if q == j - 2:
                        for q1_node_nucq in dfa.right_edges.get(q_node, []):
                            q1_node = q1_node_nucq[0]
                            q1_num = q1_node[1]
                            if q1_num != j_1_node[1]:
                                continue

                            # for p_node_ in range(64 * q):
                            #     p_node_nucpair = self.reverse_index(p_node_)
                            #     # print('i_node_nucpair:', i_node_nucpair)
                            #     temppairp = (int(p_node_nucpair.node_first), int(p_node_nucpair.node_second),
                            #                 int(p_node_nucpair.nucpair))
                            #     temp_state = self.bestM2.get_state(q_node, temppairp)
                            for temppairp in self.alive_M2.get(q_node, ()):
                                temp_state = self.bestM2.get_state(q_node, temppairp)
                                if temp_state.score == INT_MIN:
                                    continue

                                # p_node_nuc = self.reverse_index(p_node_)
                                # p_node = (p_node_nuc.node_first, p_node_nuc.node_second, p_node_nuc.nucpair)
                                # p = p_node[0]
                                p, p_num, pair_nuc = temppairp
                                nucp = PTLN(pair_nuc)
                                p_node = (p, p_num, nucp)

                                if p <= i:
                                    continue

                                for i1_node_nuci in dfa.right_edges.get(i_node, []):
                                    i1_node = i1_node_nuci[0]

                                    if p == i + 1 and p_node != i1_node:
                                        continue

                                    if p == i + 2:
                                        for p_1_node_nucp in dfa.left_edges.get(p_node, []):
                                            p_1_node = p_1_node_nucp[0]
                                            p_1_num = p_1_node[1]
                                            if p_1_num != i1_node[1]:
                                                continue
                                            else:
                                                weight_nuci = float(i1_node_nuci[1])

                                                m2_state = self.bestM2.get_state(q_node,p_node)
                                                cai_score = (
                                                        m2_state.cai_score +
                                                        weight_nuci +
                                                        self.get_broken_codon_score(i1_node, p_node) +
                                                        self.get_broken_codon_score(q_node, j_1_node) +
                                                        weight_nucj_1
                                                )

                                                if (state.score == m2_state.score and
                                                        abs(state.cai_score - cai_score) < epsilon):
                                                    stk.append((p_node, q_node, m2_state, BeamType.BEAM_M2, -1))

                                                    temp_string = self.get_nuc_from_dfa_cai(
                                                        dfa, i1_node, p_node, self.protein,
                                                        self.best_path_in_one_codon_unit,
                                                        self.aa_best_path_in_a_whole_codon
                                                    )
                                                    count = i + 1
                                                    for nuc in temp_string:
                                                        sequence[count] = nuc
                                                        count += 1
                                                    assert count == p

                                                    temp_string = self.get_nuc_from_dfa_cai(
                                                        dfa, q_node, j_1_node, self.protein,
                                                        self.best_path_in_one_codon_unit,
                                                        self.aa_best_path_in_a_whole_codon
                                                    )
                                                    count = q
                                                    for nuc in temp_string:
                                                        sequence[count] = nuc
                                                        count += 1

                                                    assert count == j - 1
                                                    no_backpointer = False
                                                    break
                                        if not no_backpointer:
                                            break
                                    else:
                                        weight_nuci = float(i1_node_nuci[1])
                                        m2_state = self.bestM2.get_state(q_node, p_node)
                                        cai_score = (
                                                m2_state.cai_score +
                                                weight_nuci +
                                                self.get_broken_codon_score(i1_node, p_node) +
                                                self.get_broken_codon_score(q_node, j_1_node) +
                                                weight_nucj_1
                                        )

                                        if (state.score == m2_state.score and
                                                abs(state.cai_score - cai_score) < epsilon):
                                            stk.append((p_node, q_node, m2_state, BeamType.BEAM_M2, -1))

                                            temp_string = self.get_nuc_from_dfa_cai(
                                                dfa, i1_node, p_node, self.protein,
                                                self.best_path_in_one_codon_unit,
                                                self.aa_best_path_in_a_whole_codon
                                            )
                                            count = i + 1
                                            for nuc in temp_string:
                                                sequence[count] = nuc
                                                count += 1
                                            assert count == p

                                            temp_string = self.get_nuc_from_dfa_cai(
                                                dfa, q_node, j_1_node, self.protein,
                                                self.best_path_in_one_codon_unit,
                                                self.aa_best_path_in_a_whole_codon
                                            )
                                            count = q
                                            for nuc in temp_string:
                                                sequence[count] = nuc
                                                count += 1

                                            assert count == j - 1
                                            no_backpointer = False
                                            break
                            if not no_backpointer:
                                break
                        if not no_backpointer:
                            break
                    else:
                        # for p_node_ in range(64 * q):
                        #     p_node_pair = self.reverse_index(p_node_)
                        #     # print('i_node_nucpair:', i_node_nucpair)
                        #     p_node_temppair = (int(p_node_pair.node_first), int(p_node_pair.node_second),
                        #                 int(p_node_pair.nucpair))
                        for temppairp in self.alive_M2.get(q_node, ()):
                            temp_state = self.bestM2.get_state(q_node, temppairp)
                            if temp_state.score == INT_MIN:
                                continue

                            # p_node_nuc = self.reverse_index(p_node_)
                            # p_node = (p_node_nuc.node_first, p_node_nuc.node_second, p_node_nuc.nucpair)
                            # p = p_node[0]
                            p, p_num, pair_nuc = temppairp
                            nucp = PTLN(pair_nuc)
                            p_node = (p, p_num, nucp)

                            if p <= i:
                                continue

                            for i1_node_nuci in dfa.right_edges.get(i_node, []):
                                i1_node = i1_node_nuci[0]

                                if p == i + 1 and p_node != i1_node:
                                    continue

                                if p == i + 2:
                                    for p_1_node_nucp in dfa.left_edges.get(p_node, []):
                                        p_1_node = p_1_node_nucp[0]
                                        p_1_num = p_1_node[1]
                                        if p_1_num != i1_node[1]:
                                            continue
                                        else:
                                            weight_nuci = float(i1_node_nuci[1])

                                            m2_state = self.bestM2.get_state(q_node, p_node)
                                            cai_score = (
                                                    m2_state.cai_score +
                                                    weight_nuci +
                                                    self.get_broken_codon_score(i1_node, p_node) +
                                                    self.get_broken_codon_score(q_node, j_1_node) +
                                                    weight_nucj_1
                                            )

                                            if (state.score == m2_state.score and
                                                    abs(state.cai_score - cai_score) < epsilon):
                                                stk.append((p_node, q_node, m2_state, BeamType.BEAM_M2, -1))

                                                temp_string = self.get_nuc_from_dfa_cai(
                                                    dfa, i1_node, p_node, self.protein,
                                                    self.best_path_in_one_codon_unit,
                                                    self.aa_best_path_in_a_whole_codon
                                                )
                                                count = i + 1
                                                for nuc in temp_string:
                                                    sequence[count] = nuc
                                                    count += 1
                                                assert count == p

                                                temp_string = self.get_nuc_from_dfa_cai(
                                                    dfa, q_node, j_1_node, self.protein,
                                                    self.best_path_in_one_codon_unit,
                                                    self.aa_best_path_in_a_whole_codon
                                                )
                                                count = q
                                                for nuc in temp_string:
                                                    sequence[count] = nuc
                                                    count += 1

                                                assert count == j - 1
                                                no_backpointer = False
                                                break
                                    if not no_backpointer:
                                        break
                                else:
                                    weight_nuci = float(i1_node_nuci[1])
                                    m2_state = self.bestM2.get_state(q_node, p_node)
                                    cai_score = (
                                            m2_state.cai_score +
                                            weight_nuci +
                                            self.get_broken_codon_score(i1_node, p_node) +
                                            self.get_broken_codon_score(q_node, j_1_node) +
                                            weight_nucj_1
                                    )

                                    if (state.score == m2_state.score and
                                            abs(state.cai_score - cai_score) < epsilon):
                                        stk.append((p_node, q_node, m2_state, BeamType.BEAM_M2, -1))

                                        temp_string = self.get_nuc_from_dfa_cai(
                                            dfa, i1_node, p_node, self.protein,
                                            self.best_path_in_one_codon_unit,
                                            self.aa_best_path_in_a_whole_codon
                                        )
                                        count = i + 1
                                        for nuc in temp_string:
                                            sequence[count] = nuc
                                            count += 1
                                        assert count == p

                                        temp_string = self.get_nuc_from_dfa_cai(
                                            dfa, q_node, j_1_node, self.protein,
                                            self.best_path_in_one_codon_unit,
                                            self.aa_best_path_in_a_whole_codon
                                        )
                                        count = q
                                        for nuc in temp_string:
                                            sequence[count] = nuc
                                            count += 1

                                        assert count == j - 1
                                        no_backpointer = False
                                        break
                        if not no_backpointer:
                            break
                assert not no_backpointer, "No path matches for BeamType.BEAM_MULTI"

            elif beam_type == BeamType.BEAM_M2:
                # 处理 BeamType.BEAM_M2
                i = i_node[0]
                j = j_node[0]

                # for m_node_nucpair_ in range(64 * j):
                #     m_node_nuc = self.reverse_index(m_node_nucpair_)
                #     # print('i_node_nucpair:', i_node_nucpair)
                #     temppairm = (
                #     int(m_node_nuc.node_first), int(m_node_nuc.node_second), int(m_node_nuc.nucpair))
                for temppairm in self.alive_P.get(j_node, ()):
                    p_state = self.bestP.get_state(j_node, temppairm)
                    if p_state.score == INT_MIN:
                        continue
                    # m_node_nucpair_obj = self.reverse_index(m_node_nucpair_)
                    # m = m_node_nucpair_obj.node_first
                    # m_num = m_node_nucpair_obj.node_second
                    # pair_nuc = m_node_nucpair_obj.nucpair

                    m, m_num, pair_nuc = temppairm
                    nucm = PTLN(pair_nuc)
                    nucj_1 = PTRN(pair_nuc)
                    m_node = (m, m_num, nucm)

                    if m <= i + 4:
                        continue  # no sharpturn

                    newscore = -func6(-1, -1, -1, -1, nucm, nucj_1, -1, self.seq_length, self.params) + p_state.score

                    m_state = self.bestM.get_state(m_node, i_node)
                    cai_score = m_state.cai_score + p_state.cai_score

                    if (state.score == m_state.score + newscore and abs(state.cai_score - cai_score) < epsilon):
                        stk.append((i_node, m_node, m_state, BeamType.BEAM_M1, -1))
                        stk.append((m_node, j_node, p_state, BeamType.BEAM_P, pair_nuc))

                        no_backpointer = False
                        break

                    if not no_backpointer:
                        break

                assert not no_backpointer, "No path matches for BeamType.BEAM_M2"
                break

            elif beam_type == BeamType.BEAM_M1:
                # 处理 BeamType.BEAM_M1
                # M = M+U
                for j_1_node, weight_nucj_1 in dfa.left_edges.get(j_node, []):
                    m_state = self.bestM.get_state(j_1_node, i_node)
                    cai_score = m_state.cai_score + weight_nucj_1

                    if (state.score == m_state.score and abs(state.cai_score - cai_score) < epsilon):
                        nucj_1 = j_1_node[2]
                        stk.append((i_node, j_1_node, m_state, BeamType.BEAM_M1, -1))
                        sequence[j - 1] = GET_ACGU(nucj_1)
                        # structure[j - 1] = ')'
                        no_backpointer = False
                        break
                # M = P
                if no_backpointer:
                    for j_1_node, _ in dfa.left_edges.get(j_node, []):
                        nucj_1 = j_1_node[2]
                        for i1_node, _ in dfa.right_edges.get(i_node, []):
                            nuci1 = i1_node[2]
                            pair_nuc = NTP(nuci, nucj_1)
                            temp = (i_node[0], i_node[1], pair_nuc)
                            p_state = self.bestP.get_state(j_node, temp)
                            newscore = -func6(-1, -1, -1, -1, nuci, nucj_1, -1, self.seq_length, self.params) + p_state.score

                            if (state.score == newscore and abs(state.cai_score - p_state.cai_score) < epsilon):
                                stk.append((i_node, j_node, p_state, BeamType.BEAM_P, pair_nuc))
                                no_backpointer = False
                                break
                        if not no_backpointer:
                            break

                # M = M2
                if no_backpointer:
                    m2_state = self.bestM2.get_state(j_node, i_node)
                    if (state.score == m2_state.score and abs(state.cai_score - m2_state.cai_score) < epsilon):
                        stk.append((i_node, j_node, m2_state, BeamType.BEAM_M2, -1))
                        no_backpointer = False

                assert not no_backpointer, "No path matches for BeamType.BEAM_M1"
                break

        # 最终生成的序列和结构
        final_sequence = ''.join(sequence)
        final_structure = ''.join(structure)
        return BacktraceResult(final_sequence, final_structure)


