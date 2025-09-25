import math
import re

# 来自 fondon.h 的全局数据和函数

k_void_nuc = 127

def split(s, delim):
    """将字符串 s 使用 delim 分割成列表"""
    return s.split(delim)

map_fasta = {
    'F': "Phe",
    'L': "Leu",
    'S': "Ser",
    'Y': "Tyr",
    '*': "STOP",
    'C': "Cys",
    'W': "Trp",
    'P': "Pro",
    'H': "His",
    'Q': "Gln",
    'R': "Arg",
    'I': "Ile",
    'M': "Met",
    'T': "Thr",
    'N': "Asn",
    'K': "Lys",
    'V': "Val",
    'D': "Asp",
    'E': "Glu",
    'G': "Gly",
    'A': "Ala"
}

k_map_3_1 = {
    "Phe": 'F',
    "Leu": 'L',
    "Ser": 'S',
    "Tyr": 'Y',
    "STOP": '*',
    "Cys": 'C',
    "Trp": 'W',
    "Pro": 'P',
    "His": 'H',
    "Gln": 'Q',
    "Arg": 'R',
    "Ile": 'I',
    "Met": 'M',
    "Thr": 'T',
    "Asn": 'N',
    "Lys": 'K',
    "Val": 'V',
    "Asp": 'D',
    "Glu": 'E',
    "Gly": 'G',
    "Ala": 'A'
}

def cvt_to_seq(fasta):
    """
    将单字母表示的蛋白质序列转换为由三字母氨基酸名称构成的序列（以空格分隔）。
    成功返回 (True, 转换后的字符串)，失败返回 (False, None)。
    """
    nucs = []
    for aa in fasta:
        if aa in map_fasta:
            nucs.append(map_fasta[aa])
        else:
            # print("invalid protein sequence!")
            return False, None
    return True, " ".join(nucs)


# 下面是 Codon 类的 Python 版本
class Codon:
    def __init__(self, path):
        self.codon_table_ = {}
        self.aa_table_ = {}
        self.max_aa_table_ = {}
        self.three_prime_codon_table_ = {}
        self.three_prime_aa_table_ = {}
        # 使用上面定义的 k_map_3_1
        self.k_map_3_1 = k_map_3_1

        # 从文件中读取数据
        with open(path, 'r', encoding='utf-8') as codon_file:
            index = 0
            for line in codon_file:
                line = line.rstrip()  # 相当于 rtrim
                if len(line) == 0:
                    continue
                if index == 0:
                    # 跳过第一行表头
                    index += 1
                    continue

                index += 1
                line_split = split(line, ',')
                if len(line_split) != 3:
                    # print("Wrong format of codon frequency file!")
                    raise SystemExit(1)

                codon = line_split[0]
                aa = line_split[1]
                fraction = float(line_split[2])

                self.codon_table_[codon] = (aa, fraction)

                if aa not in self.aa_table_:
                    self.aa_table_[aa] = []
                self.aa_table_[aa].append((codon, fraction))

                if aa not in self.max_aa_table_:
                    self.max_aa_table_[aa] = fraction
                else:
                    self.max_aa_table_[aa] = max(self.max_aa_table_[aa], fraction)

        if len(self.codon_table_) != 64:
            # print("Codon frequency file needs to contain 64 codons!")
            raise SystemExit(1)

    def calc_cai(self, rna_seq):
        if len(rna_seq) % 3 != 0:
            raise RuntimeError("invalid rna seq")

        protein_length = len(rna_seq) // 3
        cai = 0.0
        for i in range(0, len(rna_seq), 3):
            tri_letter = rna_seq[i:i+3]
            f_ci_aa = self.codon_table_[tri_letter]
            f_c_max = self.max_aa_table_[f_ci_aa[0]]
            w_i = f_ci_aa[1] / f_c_max
            cai += math.log2(w_i)

        return 2 ** (cai / protein_length)

    def find_max_codon(self, aa, match):
        aa_str = str(aa)
        candidate_codons = self.aa_table_[aa_str]

        max_score = 0.0
        max_codon = ""
        pattern = re.compile(match)

        for candidate in candidate_codons:
            c, score = candidate
            if pattern.fullmatch(c) and score > max_score:
                max_codon = c
                max_score = score

        if max_codon == "":
            raise RuntimeError("invalid search")

        return max_codon

    def cvt_rna_seq_to_aa_seq(self, rna_seq):
        if len(rna_seq) % 3 != 0:
            raise RuntimeError("invalid rna seq")

        aa_seq = []
        for i in range(0, len(rna_seq), 3):
            tri_letter = rna_seq[i:i+3]
            aa = self.codon_table_[tri_letter][0]
            if aa == "STOP":
                aa_seq.append("*")
                return "".join(aa_seq)
            aa_seq.append(aa)
        return "".join(aa_seq)

    def get_weight(self, aa_tri, codon):
        if aa_tri in self.k_map_3_1:
            aa_char = self.k_map_3_1[aa_tri]
            codons = self.aa_table_.get(str(aa_char), [])
            for c, val in codons:
                if c == codon:
                    return val
            raise RuntimeError("invalid codon")

        elif aa_tri in self.three_prime_aa_table_:
            return self.three_prime_aa_table_[aa_tri][1]

        return 0.0


if __name__ == "__main__":
    # 假设当前目录下有一个 codon_freq.csv 文件用于初始化 Codon 类
    codon_file_path = "codon_usage_freq_table_human.csv"
    codon_obj = Codon(codon_file_path)

    # 测试 calc_cai 函数
    # 随机使用一个RNA序列（长度为3的倍数），这里只是举例，请根据实际数据修改
    test_rna_seq = "AUGGCCAUGGCGCCCAGAACU"  # 对应: Met-Ala-Met-Ala-Pro-Arg-Asn-STOP 的一种假设序列
    try:
        cai_value = codon_obj.calc_cai(test_rna_seq)
        # print("CAI for sequence:", test_rna_seq, "is:", cai_value)
    except RuntimeError as e:
         print("Error calculating CAI:", e)

    # 测试 find_max_codon 函数
    # 假设氨基酸 "A" (Ala) 并提供一个正则匹配模式，例如匹配任意三个字符的RNA序列 "[ACGU]{3}"
    try:
        max_codon_for_A = codon_obj.find_max_codon('A', r"[ACGU]{3}")
        # print("Max codon for Alanine (A) is:", max_codon_for_A)
    except RuntimeError as e:
         print("Error finding max codon:", e)

    # 测试 cvt_rna_seq_to_aa_seq 函数
    # 使用上面定义的 test_rna_seq
    try:
        aa_seq = codon_obj.cvt_rna_seq_to_aa_seq(test_rna_seq)
        # print("Amino acid sequence for", test_rna_seq, "is:", aa_seq)
    except RuntimeError as e:
         print("Error converting RNA to AA sequence:", e)

    # 测试 get_weight 函数
    # get_weight 的参数为 aa_tri （例如 "Ala"）和 codon（例如 "GCU"）
    try:
        weight = codon_obj.get_weight("Ala", "GCU")
        # print("Weight for Ala-GCU is:", weight)
    except RuntimeError as e:
         print("Error getting weight:", e)

    # 测试 cvt_to_seq 函数（fasta 序列 -> 三字母氨基酸名称）
    # 假设一个蛋白质序列 "MAV" (Met, Ala, Val)
    success, seq_3letter = cvt_to_seq("MAV")
    if success:
         print("The three-letter code sequence for 'MAV' is:", seq_3letter)
    else:
         print("Conversion to three-letter sequence failed.")