import os, sys, time
from typing import List, Optional
from .codon import Codon, cvt_to_seq, split, k_void_nuc
from . import base
from .dfa_network import prepare_codon_unit_lattice,get_dfa_with_codon_overrides,load_codon_overrides_csv
from .parser import BeamCKYParser
from . import settings

def print_dfa_info(dfa, label="DFA"):
    """
    打印 DFA 的关键信息，便于 smoke test 和排查：
      - 位置数（index 的不同取值个数）
      - 节点总数
      - 右出边/左入边数量
      - 第三位（完整密码子）节点数量（若可用）
      - 前若干个位置的节点与出度示例
    """
    nodes = getattr(dfa, "nodes", {})
    right = getattr(dfa, "right_edges", {})
    left = getattr(dfa, "left_edges", {})
    codon3 = getattr(dfa, "codon_at_node3", {})

    # 统计
    total_pos = len(nodes)
    total_nodes = sum(len(v) for v in nodes.values()) if nodes else 0
    total_right_edges = sum(len(v) for v in right.values()) if right else 0
    total_left_edges = sum(len(v) for v in left.values()) if left else 0
    total_codon3 = len(codon3) if isinstance(codon3, dict) else 0
    max_index = max(nodes.keys()) if nodes else -1

    print(f"[DFA] {label}: positions={total_pos}, nodes={total_nodes}, "
          f"right_edges={total_right_edges}, left_edges={total_left_edges}, "
          f"codon_pos3_nodes={total_codon3}, max_index={max_index}", flush=True)

    # 展示前几个 index 的节点与出边示例（避免过长输出）
    demo_idx = sorted(nodes.keys())[:5]
    for idx in demo_idx:
        node_list = nodes.get(idx, [])
        print(f"  [pos {idx}] nodes={len(node_list)}", flush=True)
        for node in node_list[:5]:  # 每个位置只展示前 5 个节点
            out_edges = right.get(node, [])
            try:
                base = node[2]
            except Exception:
                base = "?"
            print(f"    - node={node} base={base} out_degree={len(out_edges)}", flush=True)

def output_result(result, duration, lam, is_verbose, codon, CODON_TABLE):
    """
    输出结果信息。

    参数：
    - result (dict): 包含 "sequence", "structure", "score", "cai_score" 的字典。
    - duration (float): 程序运行时间。
    - lam (float): lambda 值。
    - is_verbose (bool): 是否启用详细输出。
    - codon (Codon): Codon 对象，用于计算 CAI。
    - CODON_TABLE (str): 使用的密码子频率表名称。
    """
    lines = []
    if is_verbose:
        lines.append(f"Using lambda = {lam/100.}; Using codon frequency table = {CODON_TABLE}")
    lines.append(f"mRNA sequence:  {result['sequence']}")
    lines.append(f"mRNA structure: {result['structure']}")
    cai_val = codon.calc_cai(result['sequence'])
    lines.append(f"mRNA folding free energy: {result['score']:.2f} kcal/mol; mRNA CAI: {cai_val:.3f}")
    if is_verbose:
        lines.append(f"Runtime: {duration} seconds")

    print("\n".join(lines))
    print()
    return "\n".join(lines)

def linearDesign(n: int, aa_seq_list: List[str], params, codon_constraints_csv: Optional[str] = None):
    # default args
    lam = 0.0
    is_verbose = False
    CODON_TABLE = settings.get_abs_home() / "codon_usage_freq_table_human.csv"

    lam *= 100.0

    codon = Codon(CODON_TABLE)

    aa_graphs_with_ln_weights = {}
    best_path_in_one_codon_unit = {}
    aa_best_path_in_a_whole_codon = {}

    prepare_codon_unit_lattice(settings.get_abs_home() / "coding_wheel.txt", codon,
                               aa_graphs_with_ln_weights,
                               best_path_in_one_codon_unit,
                               aa_best_path_in_a_whole_codon, lam)

    # 只允许 CSV：若提供则加载；否则为空约束（行为与原版一致）
    overrides, aa_letters = {}, {}
    if codon_constraints_csv:
        overrides, aa_letters = load_codon_overrides_csv(codon_constraints_csv)
        print(f"[INFO] loaded {len(overrides)} codon overrides from CSV: {codon_constraints_csv}")

    # main loop
    for i in range(n):
        aa_seq = aa_seq_list[i]
        aa_seq = aa_seq.upper()
        if is_verbose:
            print("Input protein:", aa_seq)
        success, aa_tri_seq = cvt_to_seq(aa_seq)
        if not success:
            continue
        print("Input protein:", aa_seq)

        protein = split(aa_tri_seq, ' ')

        parser = BeamCKYParser(
            lam,
            is_verbose,
            best_path_in_one_codon_unit,
            aa_best_path_in_a_whole_codon,
            params,
        )

        system_start = time.time()

        # 用带覆盖版本的 DFA 构建；若 overrides 为空则与原 get_dfa 等价
        dfa = get_dfa_with_codon_overrides(
            aa_graphs_with_ln_weights,
            split(aa_tri_seq, ' '),
            overrides,
            validate_aa=aa_letters
        )
        # print_dfa_info(dfa, label="BASE+TRIGRAM (with CSV overrides)")

        result = parser.parse(dfa, codon, aa_seq, protein,
                              aa_best_path_in_a_whole_codon,
                              best_path_in_one_codon_unit,
                              aa_graphs_with_ln_weights)

        system_duration = time.time() - system_start

        output_result(result, system_duration, lam, is_verbose, codon, CODON_TABLE)

def linearDesign_one_seq(aa_seq: str, params, codon_constraints_csv: Optional[str] = None):
    # default args
    lam = 0.0
    is_verbose = False
    CODON_TABLE = settings.get_abs_home() / "codon_usage_freq_table_human.csv"

    lam *= 100.0
    codon = Codon(CODON_TABLE)

    aa_graphs_with_ln_weights = {}
    best_path_in_one_codon_unit = {}
    aa_best_path_in_a_whole_codon = {}

    prepare_codon_unit_lattice(settings.get_abs_home() / "coding_wheel.txt", codon,
                               aa_graphs_with_ln_weights,
                               best_path_in_one_codon_unit,
                               aa_best_path_in_a_whole_codon, lam)

    # 只允许 CSV：若提供则加载；否则为空约束（行为与原版一致）
    overrides, aa_letters = {}, {}
    if codon_constraints_csv:
        overrides, aa_letters = load_codon_overrides_csv(codon_constraints_csv)
        print(f"[INFO] loaded {len(overrides)} codon overrides from CSV: {codon_constraints_csv}")

    aa_seq = aa_seq.upper()
    if is_verbose:
        print("Input protein:", aa_seq)
    success, aa_tri_seq = cvt_to_seq(aa_seq)
    if not success:
        print("aa_seq has wrong")

    print("Input protein:", aa_seq)
    protein = split(aa_tri_seq, ' ')

    parser = BeamCKYParser(
        lam,
        is_verbose,
        best_path_in_one_codon_unit,
        aa_best_path_in_a_whole_codon,
        params,
    )

    system_start = time.time()

    # 用带覆盖版本的 DFA 构建；若 overrides 为空则与原 get_dfa 等价
    dfa = get_dfa_with_codon_overrides(
        aa_graphs_with_ln_weights,
        split(aa_tri_seq, ' '),
        overrides,
        validate_aa=aa_letters
    )
    # print_dfa_info(dfa, label="BASE (with CSV overrides)")

    result = parser.parse(dfa, codon, aa_seq, protein,
                          aa_best_path_in_a_whole_codon,
                          best_path_in_one_codon_unit,
                          aa_graphs_with_ln_weights)

    system_duration = time.time() - system_start

    returned_result = output_result(result, system_duration, lam, is_verbose, codon, CODON_TABLE)
    return returned_result

if __name__ == "__main__":
    #aa_seq = "MIIPVRCFTCGKIVGNKWEAYLGLLQAEYTEGDALDALGLKRYCCRRMLLAHVDLIEKLLNYAPLEK*"
    aa_seq = "MSYYLNYYGGLGYGYDCKYSY*"
    #aa_seq = "MPNTL*"
    params = base.load_energy_params(settings.get_abs_home() / "original_parameters")
    result = linearDesign_one_seq(aa_seq, params, codon_constraints_csv=settings.get_abs_home() / "overrides.csv")
    print(result)