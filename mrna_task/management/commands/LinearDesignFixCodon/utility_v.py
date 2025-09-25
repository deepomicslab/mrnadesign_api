# fastcky_utility_v.py

import math

import numpy as np
#func15,14,12,6,3,1(special_hp)
# 常量定义
NOTON = 5
NOTOND = 25
NOTONT = 125

EXPLICIT_MAX_LEN = 4
SINGLE_MIN_LEN = 0
SINGLE_MAX_LEN = 20
HAIRPIN_MAX_LEN = 30
BULGE_MAX_LEN = SINGLE_MAX_LEN
INTERNAL_MAX_LEN = SINGLE_MAX_LEN
SYMMETRIC_MAX_LEN = 15
ASYMMETRY_MAX_LEN = 28
SPECIAL_HAIRPIN_SCORE_BASELINE = -10000
SPECIAL_HP = 0


def MIN2(a, b):
    return a if a < b else b

# 宏替换为函数或lambda
def GET_ACGU(x: int) -> str:
    # x: int
    # C++: (x==1? 'A' : (x==2? 'C' : (x==3? 'G' : (x==4?'U': 'X'))))
    if x == 1:
        return 'A'
    elif x == 2:
        return 'C'
    elif x == 3:
        return 'G'
    elif x == 4:
        return 'U'
    else:
        return 'X'

def GET_ACGU_NUC(x: str) -> int:
    # (x=='A'?1:(x=='C'?2:(x=='G'?3:(x=='U'?4:0))))
    if x == 'A':
        return 1
    elif x == 'C':
        return 2
    elif x == 'G':
        return 3
    elif x == 'U':
        return 4
    return 0

def HAIRPINTYPE(x: int) -> int:
    # (x==5?0:(x==6?1:(x==8?2:3)))
    if x == 5:
        return 0
    elif x == 6:
        return 1
    elif x == 8:
        return 2
    else:
        return 3

# 宏 NTP, PTLN, PTRN 需要以函数形式实现
def NTP(x: int, y: int) -> int:
    # (x==1?(y==4?5:0): (x==2?(y==3?1:0): (x==3?(y==2?2:(y==4?3:0)):(x==4?(y==3?4:(y==1?6:0)):0))))
    if x == 1:
        return 5 if y == 4 else 0
    elif x == 2:
        return 1 if y == 3 else 0
    elif x == 3:
        if y == 2:
            return 2
        elif y == 4:
            return 3
        else:
            return 0
    elif x == 4:
        if y == 3:
            return 4
        elif y == 1:
            return 6
        else:
            return 0
    return 0

def PTLN(x: int) -> int:
    # (x==1?2:((x==2||x==3)?3:(x==5)?1:4))
    if x == 1:
        return 2
    elif x == 2 or x == 3:
        return 3
    elif x == 5:
        return 1
    else:
        return 4

def PTRN(x: int) -> int:
    # (x==2?2:((x==1||x==4)?3:(x==6)?1:4))
    if x == 2:
        return 2
    elif x == 1 or x == 4:
        return 3
    elif x == 6:
        return 1
    else:
        return 4

# 声明的全局变量
#_allowed_pairs = [[0]*NOTON for _ in range(NOTON)]
# 您需要根据实际情况对_allowed_pairs进行初始化,如果在其他地方有初始化，请在此引入。

# 假设以下全局变量已定义并初始化
# Constants
NST = 0      # Energy for nonstandard stacked pairs
DEF = -50    # Default terminal mismatch, used for I and any non_pairing bases
NSM = 0      # Terminal mismatch for non standard pairs
# Public variable
K0 = 273.15  # Offset for converting Celsius to Kelvin
Tmeasure = 37 + K0  # Measurement temperature in Kelvin
# The gas constant (in cal/K)
GASCONST = 1.98717
# Infinity as used in minimization routines
INF = 10_000_000
EMAX = INF // 10
# forbidden
FORBIDDEN = 9999
# bonus contribution
BONUS = 10000
# The minimum loop length
TURN = 3
# The maximum loop length
MAXLOOP = 30
UNIT = 100
MINPSCORE = -2 * UNIT
PI = 3.141592653589793

NBPAIRS = 7

# Tetraloops
Tetraloops = [
    "CAACGG",
    "CCAAGG",
    "CCACGG",
    "CCCAGG",
    "CCGAGG",
    "CCGCGG",
    "CCUAGG",
    "CCUCGG",
    "CUAAGG",
    "CUACGG",
    "CUCAGG",
    "CUCCGG",
    "CUGCGG",
    "CUUAGG",
    "CUUCGG",
    "CUUUGG"
]

# Hexaloops
Hexaloops = [
    "ACAGUACU",
    "ACAGUGAU",
    "ACAGUGCU",
    "ACAGUGUU"
]
# Triloops
Triloops = [
    "CAACG",
    "GUUAC"
]
# 定义 Triloop37 列表
# Special loops
Tetraloops = [
    "CAACGG",
    "CCAAGG",
    "CCACGG",
    "CCCAGG",
    "CCGAGG",
    "CCGCGG",
    "CCUAGG",
    "CCUCGG",
    "CUAAGG",
    "CUACGG",
    "CUCAGG",
    "CUCCGG",
    "CUGCGG",
    "CUUAGG",
    "CUUCGG",
    "CUUUGG"
]
Hexaloops = [
    "ACAGUACU",
    "ACAGUGAU",
    "ACAGUGCU",
    "ACAGUGUU"
]
Triloops = [
    "CAACG",
    "GUUAC"
]

# 原代码中的列表定义替换为以下np.load语句
from . import settings
# 替换单值参数
lxc37 = np.load(settings.get_abs_home() / 'original_parameters/lxc37.npy')
ML_intern37 = np.load(settings.get_abs_home() / 'original_parameters/ML_intern37.npy')
ML_closing37 = np.load(settings.get_abs_home() / 'original_parameters/ML_closing37.npy')
MAX_NINIO = np.load(settings.get_abs_home() / 'original_parameters/MAX_NINIO.npy')
ninio37 = np.load(settings.get_abs_home() / 'original_parameters/ninio37.npy')
TerminalAU37 = np.load(settings.get_abs_home() / 'original_parameters/TerminalAU37.npy')
ML_BASE37 = np.load(settings.get_abs_home() / 'original_parameters/ML_BASE37.npy')
ML_BASEdH = np.load(settings.get_abs_home() / 'original_parameters/ML_BASEdH.npy')
DuplexInit37 = np.load(settings.get_abs_home() / 'original_parameters/DuplexInit37.npy')
TripleC37 = np.load(settings.get_abs_home() / 'original_parameters/TripleC37.npy')
MultipleCA37 = np.load(settings.get_abs_home() / 'original_parameters/MultipleCA37.npy')
MultipleCB37 = np.load(settings.get_abs_home() / 'original_parameters/MultipleCB37.npy')

# 替换多维数组参数
stack37 = np.load(settings.get_abs_home() / 'original_parameters/stack37.npy')
hairpin37 = np.load(settings.get_abs_home() / 'original_parameters/hairpin37.npy')
bulge37 = np.load(settings.get_abs_home() / 'original_parameters/bulge37.npy')
internal_loop37 = np.load(settings.get_abs_home() / 'original_parameters/internal_loop37.npy')

Tetraloop37 = np.load(settings.get_abs_home() / 'original_parameters/Tetraloop37.npy')
Hexaloop37 = np.load(settings.get_abs_home() / 'original_parameters/Hexaloop37.npy')
Triloop37 = np.load(settings.get_abs_home() / 'original_parameters/Triloop37.npy')

mismatchI37 = np.load(settings.get_abs_home() / 'original_parameters/mismatchI37.npy')
mismatchH37 = np.load(settings.get_abs_home() / 'original_parameters/mismatchH37.npy')
mismatchM37 = np.load(settings.get_abs_home() / 'original_parameters/mismatchM37.npy')
mismatch1nI37 = np.load(settings.get_abs_home() / 'original_parameters/mismatch1nI37.npy')
mismatch23I37 = np.load(settings.get_abs_home() / 'original_parameters/mismatch23I37.npy')
mismatchExt37 = np.load(settings.get_abs_home() / 'original_parameters/mismatchExt37.npy')

dangle5_37 = np.load(settings.get_abs_home() / 'original_parameters/dangle5_37.npy')
dangle3_37 = np.load(settings.get_abs_home() / 'original_parameters/dangle3_37.npy')

int11_37 = np.load(settings.get_abs_home() / 'original_parameters/int11_37.npy')
int21_37 = np.load(settings.get_abs_home() / 'original_parameters/int21_37.npy')
int22_37 = np.load(settings.get_abs_home() / 'original_parameters/int22_37.npy')


def func1(sequence: str, hairpin_type: int) -> float:
    """
    获取特定发夹环类型的能量。

    参数:
    - sequence (str): 发夹环的序列字符串。
    - hairpin_type (int): 发夹环类型（0：三碱基发夹环，1：四碱基发夹环，2：六碱基发夹环，其它值：未知类型）。

    返回:
    - float: 发夹环的自由能（dcal/mol），如果未找到匹配序列则返回默认高能量值。
    """
    # 根据发夹环类型查找对应能量
    if hairpin_type == 2:  # 六碱基发夹环
        try:
            index = Hexaloops.index(sequence)
            return -Hexaloop37[index]
        except ValueError:
            pass  # 未找到匹配的六碱基发夹环
    elif hairpin_type == 1:  # 四碱基发夹环
        try:
            index = Tetraloops.index(sequence)
            return -Tetraloop37[index]
        except ValueError:
            pass  # 未找到匹配的四碱基发夹环
    elif hairpin_type == 0:  # 三碱基发夹环
        try:
            index = Triloops.index(sequence)
            return -Triloop37[index]
        except ValueError:
            pass  # 未找到匹配的三碱基发夹环

    # 如果未找到匹配的发夹环序列，则返回默认高能量值
    return 4294957296.0  # 通常表示未找到匹配序列

def func2(a: str, b: int, c: list, d: list, e: list):
    return 0.0

# def func3(a: int, b: int, c: int, d: int, e: int) -> int:
#     return 0.0

def func3(i: int,
          j_minus_1: int,
          nuci: int,
          nucj_1: int,
          seq_length: int) -> int:
    """
    判断 (nuci, nucj_1) 这对碱基是否是 U-A / U-G / A-U / G-U 的末端配对。
    若是，则返回 TerminalAU37[0]；否则返回 0。

    参数说明:
    - i           : RNA 序列中某碱基的索引
    - j_minus_1   : 另一个碱基 j-1 的索引
    - nuci        : i位置的碱基编码 (1=A, 2=C, 3=G, 4=U)
    - nucj_1      : (j-1)位置的碱基编码
    - seq_length  : RNA 总长度(未用到)
    """

    if nuci == 4:  # 左侧是 U
        if (nucj_1 | 2) != 3:  # 检查 nucj_1 是否为 A(1) or G(3)
            return 0
    else:
        # 左侧若不是 G(3) 也不是 A(1)，或者右侧不是 U(4)，都返回 0
        if (nuci not in (1, 3)) or (nucj_1 != 4):
            return 0
    return TerminalAU37[0]

# def func4(a: int, b: int, c: int, d: int, e: int, f: int, g: int) -> int:
#     return 0.0

def func4(a1, a2, n5d, base_i, base_j, n3d):
    """
    Python复现：评估外环碱基对(base_i, base_j)及左右邻居(n5d, n3d)所产生的能量。

    :param a1, a2:   与C版本相同，目前不使用
    :param n5d:      5' 邻接碱基编码 (>=0时有效, <0时无效)
    :param base_i:   i侧碱基类型
    :param base_j:   j侧碱基类型
    :param n3d:      3' 邻接碱基编码 (>=0时有效, <0时无效)
    :return:         整数形式的能量 (类似 dcal/mol)
    """
    # 第 1 步：根据 (base_i, base_j) 映射到“类型” v6
    v6 = 0
    v7 = 0
    # 这个 bool 是用来决定是否覆盖 v6
    # IDA里是 v8=(base_j==2) 或 (base_j==3)等判断
    # 这里我们直接用 python 语法写
    # -----------------------------------------
    if base_i == 1:  # A
        if base_j == 4:  # A-U
            v6 = 5
        else:
            v6 = 0
    elif base_i == 2:  # C
        if base_j == 3:  # C-G
            v6 = 1
        else:
            v6 = 0
    elif base_i == 3:  # G
        v6 = 2
        if base_j == 4:
            v7 = 3
        else:
            v7 = 0
        if base_j != 2:
            v6 = v7
    elif base_i == 4:  # U
        v6 = 4
        if base_j == 1:
            v7 = 6
        else:
            v7 = 0
        if base_j != 3:
            v6 = v7
    else:
        v6 = 0

    # 第 2 步：依据 n5d/n3d 是否 >=0，决定使用 mismatch / dangle5 / dangle3 / 无
    temp_energy = 0
    n5d_valid = (n5d >= 0)
    n3d_valid = (n3d >= 0)

    if n5d_valid and n3d_valid:
        # 使用 mismatchExt37
        # IDA 中见到地址：100*v6 + 20*n5d + 4*n3d  => 说明每一层嵌套的乘法
        index = (v6 * 25) + (n5d * 5) + n3d
        temp_energy = mismatchExt37[index]
    elif n5d_valid and (not n3d_valid):
        # 使用 dangle5_37
        index = (v6 * 5) + n5d
        temp_energy = dangle5_37[index]
    elif (not n5d_valid) and n3d_valid:
        # 使用 dangle3_37
        index = (v6 * 5) + n3d
        temp_energy = dangle3_37[index]
    else:
        # 两侧都无效
        temp_energy = 0

    # 第 3 步：如果 v6>2，则加 TerminalAU37[0]
    add_terminal = TerminalAU37[0] if (v6 > 2) else 0

    # 第 4 步：返回相加
    return temp_energy + add_terminal

# ===============  测试调用  ===============
# if __name__ == "__main__":
#     # 示例：i碱基=1(A), j碱基=4(U)，n5d=2, n3d=-1
#     # 只做简单演示，实际你要用真实数据
#     result = func4(0, 0, 2, 1, 4, -1)
#     print("func4 ->", result)

# def func5(a: int, b: int, c: int) -> int:
#     return 0.0
def func5(py_type: int, b: int, c: int) -> int:
    """
    Python版本: 计算 RNA 多分支环能量修正

    :param py_type:  与C版本中 a1 等效, 表示某个配对类型或标识
    :return:         整型表示能量(此处直接return int)
    """
    if py_type <= 2:
        # 不额外加 TerminalAU37[0]
        return ML_intern37[0]
    else:
        # 额外加 TerminalAU37[0]
        return ML_intern37[0] + TerminalAU37[0]


# def func6(a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int) -> int:
#     return 0.0

def func6(i: int,
          j_minus_1_first: int,
          j_minus_1_second: int,
          dummy: int,
          nuci: int,  # 对应 a5
          nucj_1: int,  # 对应 a6
          dummy2: int,
          seq_length: int) -> int:
    """
    判断 (nuci, nucj_1) 是否为 AU、UA、GU、UG 配对：
      - 若是，则返回 TerminalAU37[0] + ML_intern37[0]
      - 否则只返回 ML_intern37[0]
    其他参数 (i, j_minus_1_first, j_minus_1_second, dummy, dummy2, seq_length)
    在逆向后发现并未在逻辑中使用。
    """
    # 如果左侧是 U(4)
    if nuci == 4:
        # 检查右侧是否为 A(1) 或 G(3)
        if (nucj_1 | 2) != 3:
            return ML_intern37[0]
    else:
        # 若左侧不是 A(1) 并且也不是 G(3)，或者右侧不是 U(4)
        if (nuci not in (1, 3)) or (nucj_1 != 4):
            return ML_intern37[0]

    return TerminalAU37[0] + ML_intern37[0]

# def func7(a: int, b: int, c: int, d: int, e: int, h: int, i: int) -> int:
#     return 0.0

def func7(param1: int,
             param2: int,
             baseLeft: int,   # a3
             neighbor3: int,  # a4
             neighbor5: int,  # a5
             baseRight: int,   # a6
             k:int
             ) -> int:
    """
    Python 版，对应逆向 C 函数 func7 的逻辑：
      1. 通过 switch(baseRight) + if(baseLeft == x) 推断配对类型 pairType
      2. 根据 neighbor5 / neighbor3 是否有效 (>=0) 来获取 mismatch 或 dangle
      3. 若 pairType>2 则加 TerminalAU37[0]
      4. 返回 ML_closing37[0] + ML_intern37[0] + mismatch + (TerminalAU)

    :param param1: 原函数 a1 (此处并未使用)
    :param param2: 原函数 a2 (此处并未使用)
    :param baseLeft:  左侧碱基类型
    :param neighbor3: 3' 侧相邻碱基 (若<0表示无)
    :param neighbor5: 5' 侧相邻碱基 (若<0表示无)
    :param baseRight: 右侧碱基类型

    :return: 计算得到的多分支环能量贡献
    """
    # --- 1) switch(baseRight) => pairType ---
    if baseRight == 1:  # A?
        if baseLeft == 4:  # U
            pairType = 5
        else:
            pairType = 0
    elif baseRight == 2:  # C?
        # pairType = (baseLeft == 3) ? 1 : 0
        pairType = 1 if (baseLeft == 3) else 0
    elif baseRight == 3:  # G?
        pairType = 2
        if baseLeft == 4:
            tempVal = 3
        else:
            tempVal = 0
        condition = (baseLeft == 2)
        if not condition:
            pairType = tempVal
    elif baseRight == 4:  # U?
        pairType = 4
        if baseLeft == 1:
            tempVal = 6
        else:
            tempVal = 0
        condition = (baseLeft == 3)
        if not condition:
            pairType = tempVal
    else:
        pairType = 0

    # --- 2) mismatch / dangle ---
    mismatchVal = 0
    # 检查是否 neighbor5 >= 0 && neighbor3 >= 0
    if (neighbor5 >= 0) and (neighbor3 >= 0):
        index = (pairType * 25) + (neighbor5 * 5) + neighbor3
        mismatchVal = mismatchM37[index]
    elif (neighbor5 >= 0):
        index = pairType * 5 + neighbor5
        mismatchVal = dangle5_37[index]
    elif (neighbor3 >= 0):
        index = pairType * 5 + neighbor3
        mismatchVal = dangle3_37[index]
    else:
        mismatchVal = 0

    # --- 3) TerminalAU37[0] 或 0 ---
    if pairType > 2:
        termAU = TerminalAU37[0]
    else:
        termAU = 0

    # --- 4) 返回计算结果 ---
    result = ML_closing37[0] + ML_intern37[0] + mismatchVal + termAU
    return result


# # ---------------- 测试/演示 ----------------
# if __name__ == "__main__":
#     # 假设 baseLeft=4(U), baseRight=1(A), neighbor5=2(C), neighbor3=2(C)
#     score = func7_py(0, 0, 4, 2, 2, 1)
#     print("func7_py result =", score)

def func8(a: int, b: int) -> int:
    return 0.0

# def func9(a: int, b: int):
#     return 0.0
def func9(a: int, b: int):
    global unk_3A17C, unk_3A184, _allowed_pairs, byte_3A18C
    # 赋值
    unk_3A17C = 0x10000000100
    unk_3A184 = 0x100010001000100
    # 将 _allowed_pairs 中所有元素设为 False
    byte_3A18C = 0

# def func10(a: int, b: int, c: int) -> int:
#     return 0.0

def func10(pairType: int, neighbor5: int, neighbor3: int) -> int:
    """
    Python版，与C版func10对应。
    模拟multibranch stem能量计算：
      - mismatch/dangle
      - optional TerminalAU37[0]
      - + ML_intern37[0]
    保留switch逻辑(在Python中用if-elif-else模拟)，保留类似指针偏移的思路。
    """

    partialEnergy = 0  # 对应C版的 v5
    # --- 1) mismatch / dangle / 0 ---
    if (neighbor5 >= 0) and (neighbor3 >= 0):
        index = (pairType * 25) + (neighbor5 * 5) + neighbor3
        partialEnergy = mismatchM37[index]
    elif (neighbor5 >= 0):
        index = pairType * 5 + neighbor5
        partialEnergy = dangle5_37[index]
    elif (neighbor3 >= 0):
        index = pairType * 5 + neighbor3
        partialEnergy = dangle3_37[index]
    else:
        partialEnergy = 0  # both sides invalid => 0

    # --- 2) 根据 pairType>2 与否 => TerminalAU37[0] or 0
    # 这里用if-elif-else来模拟switch
    if pairType in (0,1,2):
        termAU = 0
    else:
        termAU = TerminalAU37[0]

    # --- 3) 返回 partialEnergy + termAU + ML_intern37[0]
    return partialEnergy + termAU + ML_intern37[0]


# def func11(a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int) -> int:
#     return 0.0
def func11(a1: int, a2: int, a3: int,
              neighbor5: int,  # a4
              baseType1: int,  # a5
              baseType2: int,  # a6
              neighbor3: int   # a7
              ) -> int:
    """
    Python版：与C版func11功能对应
    保留switch逻辑，以及用类似指针偏移的思路取 mismatch/dangle。
    """

    # --- 1) switch(baseType1) => 由(baseType1, baseType2)推断 pairType ---
    if baseType1 == 1:
        if baseType2 == 4:
            pairType = 5
        else:
            pairType = 0
    elif baseType1 == 2:
        # pairType = 1 if baseType2==3 else 0
        pairType = 1 if (baseType2 == 3) else 0
    elif baseType1 == 3:
        pairType = 2
        if baseType2 == 4:
            tmpVal = 3
        else:
            tmpVal = 0
        if baseType2 != 2:
            pairType = tmpVal
    elif baseType1 == 4:
        pairType = 4
        if baseType2 == 1:
            tmpVal = 6
        else:
            tmpVal = 0
        if baseType2 != 3:
            pairType = tmpVal
    else:
        pairType = 0

    # --- 2) mismatch/dangle ---
    # neighbor5, neighbor3
    # 检查是否 neighbor5 >= 0 && neighbor3 >= 0
    if (neighbor5 >= 0) and (neighbor3 >= 0):
        index = (pairType * 25) + (neighbor5 * 5) + neighbor3
        mismatchVal = mismatchM37[index]
    elif (neighbor5 >= 0):
        index = pairType * 5 + neighbor5
        mismatchVal = dangle5_37[index]
    elif (neighbor3 >= 0):
        index = pairType * 5 + neighbor3
        mismatchVal = dangle3_37[index]
    else:
        mismatchVal = 0

    # --- 3) pairType>2 => TerminalAU, else 0
    if pairType > 2:
        termAU = TerminalAU37[0]
    else:
        termAU = 0

    # --- 4) return mismatchVal + termAU + ML_intern37[0]
    return mismatchVal + termAU + ML_intern37[0]

# def func12(a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int) -> int:
#     return 0.0
def func12(i, jnext, nuci, nuci1, nucjnext_1, nucjnext, tetra_hex_tri):
    """
    Calculate the free energy of a hairpin-loop.

    Parameters:
    <PRE>
     *        a3 a4
     *      a2     a5
     *      a1     a6
     *        X - Y
     *        |   |
     *        5'  3'
     *  </PRE>
    - i (int): X index (position in RNA)
    - jnext (int): Y index (position in RNA)
    - nuci (int): X base type
    - nuci1 (int): 5'-mismatching nucleotide (a1)
    - nucjnext_1 (int): 3'-mismatching nucleotide (a6)
    - nucjnext (int): Y base type
    - tetra_hex_tri (int): Flag indicating loop type (tetraloop, hexaloop, triloop; -1 for none)

    Returns:
    - int: Free energy of the hairpin-loop in dcal/mol

    """
    # Compute adjusted length
    hairpin_length = jnext-i-1  # Equivalent to -i -1 + jnext

    # Determine energy category based on 'nuci' and 'nucjnext'
    if nuci == 1:
        energy_category = 5 if nucjnext == 4 else 0
    elif nuci == 2:
        energy_category = 1 if nucjnext == 3 else 0
    elif nuci == 3:
        if nucjnext == 4:
            energy_category = 3
        elif nucjnext == 2:
            energy_category = 2
        else:
            energy_category = 0
    elif nuci == 4:
        if nucjnext == 1:
            energy_category = 6
        elif nucjnext == 3:
            energy_category = 4
        else:
            energy_category = 0
    else:
        energy_category = 0

    if hairpin_length >= 31:
        scaled_length = hairpin_length * 0.0333333333
        log_input = math.log(scaled_length)
        energy_result = hairpin37[30] + int(lxc37[0] * log_input)

        # Calculate mismatch energy
        mismatch_index = 25 * energy_category + 5 * nuci1 + nucjnext_1
        mismatch_energy = mismatchH37[mismatch_index]
        final_energy = mismatch_energy + energy_result

        return final_energy
    else:
        # Get hairpin energy from hairpin37 table
        energy_result = hairpin37[hairpin_length]
        if hairpin_length >= 3:
            if hairpin_length == 4 and (tetra_hex_tri & 0x80000000) == 0:
                return Tetraloop37[tetra_hex_tri]  # Specific tetraloop energy
            if hairpin_length == 6 and (tetra_hex_tri & 0x80000000) == 0:
                return Hexaloop37[tetra_hex_tri]     # Specific hexaloop energy
            if hairpin_length == 3:
                if (tetra_hex_tri & 0x80000000) == 0:
                    return Triloop37[tetra_hex_tri]   # Specific triloop energy
                else:
                    TermiAU = TerminalAU37[0] if energy_category > 2 else 0
                    return TermiAU + energy_result  # Add TerminalAU if applicable
            # Add mismatch energy
            mismatch_index = 25 * energy_category + 5 * nuci1 + nucjnext_1
            mismatch_energy = mismatchH37[mismatch_index]
            final_energy = mismatch_energy + energy_result

            return final_energy

        return energy_result  # Return base energy if hairpin_length < 3

# 示例调用
# if __name__ == "__main__":
#     # 示例参数
#     i = 5               # X 的 index
#     jnext = 10          # Y 的 index
#     nuci = 1            # Pair type of closing pair
#     nuci1 = 2           # 5'-mismatching nucleotide (a1)
#     nucjnext_1 = 3      # 3'-mismatching nucleotide (a6)
#     nucjnext = 4        # Y base type (nucjnext)
#     tetra_hex_tri = 0   # Flag indicating loop type (none)
#
#     energy = func12(i, jnext, nuci, nuci1, nucjnext_1, nucjnext, tetra_hex_tri)
#     print(f"内部环的自由能: {energy} dcal/mol")

def func13(a: int, b: int) -> int:
    return 0.0

# def func14(a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int, q: int, v: int, z: int, j: int) -> int:
#     return 0.0

def func14(
        p_minus1,   # X 的 index (p - 1)
        q,          # Y 的 index
        i,          # U 的 index
        j_minus1,   # V 的 index (j - 1)
        nucp_1,     # X 的碱基类型
        nucp,       # a_1 的碱基类型
        nucq_1,     # b_m 的碱基类型
        nucq,       # Y 的碱基类型
        nuci_1,     # a_n 的碱基类型
        nuci,       # U 的碱基类型
        nucj_1,     # V 的碱基类型
        nucj        # b_1 的碱基类型 (原先的 sq1 对应此处)
    ):
    """
    计算内部环的自由能。
     *  This function computes the free energy @f$ E @f$ of an internal-loop with the
     *  following structure: <BR>
     *  <PRE>
     *        3'  5'
     *        |   |
     *        U - V
     *    a_n       b_1
     *     .        .
     *     .        .
     *     .        .
     *    a_1       b_m
     *        X - Y:
     *        |   |
     *        5'  3'
     *  </PRE>
     *  @param  n1      The size of the 'left'-loop (number of unpaired nucleotides)
     *  @param  n2      The size of the 'right'-loop (number of unpaired nucleotides)
     *  @param  type    The pair type of the base pair closing the internal loop (X_Y)
     *  @param  type_2  The pair type of the enclosed base pair(V_U)
     *  @param  si1     The 5'-mismatching nucleotide of the closing pair (a_1)
     *  @param  sj1     The 3'-mismatching nucleotide of the closing pair (b_m)
     *  @param  sp1     The 3'-mismatching nucleotide of the enclosed pair (a_n)
     *  @param  sq1     The 5'-mismatching nucleotide of the enclosed pair (b_1)
     *  @param  P       The datastructure containing scaled energy parameters
     *  @return The Free energy of the internal loop in dcal/mol

    参数:
    - p_minus1 (int): X 的 index (p - 1)
    - q (int): Y 的 index
    - i (int): U 的 index
    - j_minus1 (int): V 的 index (j - 1)
    - nucp_1 (int): X 的碱基类型
    - nucp (int): a_1 的碱基类型 si1
    - nucq_1 (int): b_m 的碱基类型 sj1
    - nucq (int): Y 的碱基类型
    - nuci_1 (int): a_n 的碱基类型  sp1
    - nuci (int): U 的碱基类型
    - nucj_1 (int): V 的碱基类型
    - nucj (int): b_1 的碱基类型  sq1

    返回:
    - int: 内部环的自由能 (dcal/mol)

    """
    def energy_category(base5, base3):
        """
        返回给定碱基对 (5', 3') 对应的能量类别（示例）。
        与原先判断 (nucp_1, nucq) / (nucj, nucj_1) 的逻辑类似。
        """
        # 仅示意写法，需与实际碱基类型对应规则相匹配
        if base5 == 1:
            if base3 == 4:
                return 5
            else:
                return 0
        elif base5 == 2:
            return 1 if base3 == 3 else 0
        elif base5 == 3:
            if base3 == 4:
                return 3
            elif base3 == 2:
                return 2
            else:
                return 0
        elif base5 == 4:
            if base3 == 1:
                return 6
            elif base3 == 3:
                return 4
            else:
                return 0
        else:
            return 0

    # --------------------------
    # 1. 计算关闭对 (X,Y) 的能量类别
    # --------------------------
    energy_category_closing = energy_category(nucp_1, nucq)

    # --------------------------
    # 2. 计算内部对 (V,U) 的能量类别
    #    注意：从注释看，参数 nucj_1, nucj 应该对应 (V, b1)，
    #    而 (U, a_n) 则是 (nuci, nuci_1)。此处仅做示例
    # --------------------------
    energy_category_enclosed = energy_category(nucj_1, nuci)

    # --------------------------
    # 3. 确定较长和较短的未配对区域长度 (n1, n2)
    #    这里的写法只是演示，具体应根据 (p_minus1, q, i, j_minus1) 的序列位置
    #    来计算实际的未配对碱基数量
    # --------------------------

    loop_length_left = i - p_minus1 - 1
    loop_length_right = q - j_minus1 - 1

    if loop_length_left >= loop_length_right:
        loop_length_long = loop_length_left
        loop_length_short = loop_length_right
    else:
        loop_length_long = loop_length_right
        loop_length_short = loop_length_left

    # 如果较长的未配对区域长度为 0，则为堆叠环，直接返回堆叠能量
    if loop_length_long == 0:
        return stack37[8 * energy_category_closing + energy_category_enclosed]

    # --------------------------
    # 4. 检查是否允许闭合
    #    由于 P 参数在逆向工程函数中没有提供，这里假设 no_close_flag 已由外部逻辑处理
    # --------------------------
    no_close_flag = False  # 示例：假设允许闭合
    if no_close_flag:
        return float('inf')

    # --------------------------
    # 5. 内部环能量计算
    # --------------------------
    energy = 0

    # --------------------------
    # 5.1 bulge 情况
    # --------------------------
    if loop_length_short == 0:
        if loop_length_long <= MAXLOOP:
            energy = bulge37[loop_length_long]
        else:
            energy = bulge37[30] + int(lxc37[0] * math.log(loop_length_long / 30.0))

        if loop_length_long == 1:
            # 堆叠
            energy += stack37[8 * energy_category_closing + energy_category_enclosed]
        else:
            # TerminalAU
            if energy_category_closing > 2:
                energy += TerminalAU37[0]
            if energy_category_enclosed > 2:
                energy += TerminalAU37[0]

    # --------------------------
    # 5.2 1x1 / 1x2 环
    # - nucp(int): a_1
    # 的碱基类型
    # si1
    # - nucq_1(int): b_m
    # 的碱基类型
    # sj1
    # - nuci_1(int): a_n
    # 的碱基类型
    # sp1
    # - nucj(int): b_1
    # 的碱基类型
    # sq1
    # --------------------------
    elif loop_length_short == 1:
        if loop_length_long == 1:
            # int11
            # index 的详细计算要根据具体能量表的定义
            # 这里仅示意写法
            index = (200 * energy_category_closing +
                     25 * energy_category_enclosed +
                     5 * nucp + nucq_1)
            energy = int11_37[index]
        elif loop_length_long == 2:
            # int21
            if loop_length_left == 1:
                index = (1000 * energy_category_closing +
                         125 * energy_category_enclosed +
                         25 * nucp + 5 * nucj + nucq_1)  # 原先 5 * sq1 -> 5 * nucj
                energy = int21_37[index]
            else:
                index = (1000 * energy_category_enclosed +
                         125 * energy_category_closing +
                         25 * nucj + 5 * nucp + nuci_1)  # 同理
                energy = int21_37[index]
        else:
            # 通用内部环
            if (loop_length_long + 1) <= MAXLOOP:
                energy = internal_loop37[loop_length_long + 1]
            else:
                energy = (internal_loop37[30] +
                          int(lxc37[0] * math.log((loop_length_long + 1) / 30.0)))

            energy += MIN2(MAX_NINIO[0], (loop_length_long - loop_length_short) * ninio37[0])
            # mismatch1nI
            energy += (mismatch1nI37[energy_category_closing * 25 + 5 * nucp + nucq_1] +
                       mismatch1nI37[energy_category_enclosed * 25 + 5 * nucj + nuci_1])

    # --------------------------
    # 5.3 2x2 或 2x3 环
    # --------------------------
    elif loop_length_short == 2:
        if loop_length_long == 2:
            # int22
            index = (5000 * energy_category_closing +
                     625 * energy_category_enclosed +
                     125 * nucp + 25 * nuci_1 +
                     5 * nucj + nucq_1)
            energy = int22_37[index]
        elif loop_length_long == 3:
            energy = internal_loop37[5] + ninio37[0]
            energy += (mismatch23I37[25 * energy_category_closing + 5 * nucp + nucq_1] +
                       mismatch23I37[25 * energy_category_enclosed + 5 * nucj + nuci_1])
        else:
            # 通用内部环
            total_loop_length = loop_length_long + loop_length_short
            if total_loop_length <= MAXLOOP:
                energy += internal_loop37[total_loop_length]
            else:
                energy += (internal_loop37[30] +
                           int(lxc37[0] * math.log(total_loop_length / 30.0)))
            energy += MIN2(MAX_NINIO[0], (loop_length_long - loop_length_short) * ninio37[0])
            energy += (mismatchI37[25 * energy_category_closing + 5 * nucp + nucq_1] +
                       mismatchI37[25 * energy_category_enclosed + 5 * nucj + nuci_1])

    # --------------------------
    # 5.4 通用内部环
    # --------------------------
    else:
        total_loop_length = loop_length_long + loop_length_short
        if total_loop_length <= MAXLOOP:
            energy += internal_loop37[total_loop_length]
        else:
            energy += (internal_loop37[30] +
                       int(lxc37[0] * math.log(total_loop_length / 30.0)))

        energy += MIN2(MAX_NINIO[0], (loop_length_long - loop_length_short) * ninio37[0])

        temp1 = 25 * energy_category_closing + 5 * nucp + nucq_1
        temp2 = 25 * energy_category_enclosed + 5 * nucj + nuci_1
        # if temp1 > len(mismatchI37) -1:
        #     temp1 = len(mismatchI37) -1
        # if temp2 > len(mismatchI37) - 1:
        #     temp2 = len(mismatchI37) -1
        energy += (mismatchI37[temp1] + mismatchI37[temp2])

    return energy


def func15(i, j, nuci, dummy1, dummy2, nucj_1, seq_length):
    """
    计算多分支环转到 P-state 时的能量值 (Python 版).

    i, j         : RNA序列坐标
    nuci, nucj_1 : 碱基类型(整数编码)
    dummy1, dummy2: 占位(-1)，仅为对应C函数的形参
    seq_length   : RNA序列总长度(本函数并未使用)
    """
    add_terminal = 0

    if nucj_1 != 4:
        # (nucj_1 == 1 or 3) and (nuci == 4)
        if (nucj_1 in [1, 3]) and (nuci == 4):
            add_terminal = TerminalAU37[0]
    else:
        # nucj_1 == 4 的情况
        if (nuci | 2) == 3:
            add_terminal = TerminalAU37[0]

    result = ML_closing37[0] + ML_intern37[0] + add_terminal
    return result

# 示例使用
# if __name__ == "__main__":
#     # 示例全局变量初始化（请根据实际数据进行填充）
#     Hexaloops = ["AAAAAAAC", "CCCCCCGG", "GGGGGGUU"]
#     Tetraloops = ["GCGCAG", "AAAGCU", "CCCGGG"]
#     Triloops = ["AGCAG", "CGUAG", "GGCAG"]
#
#     Hexaloop37 = [-7.0, -8.5, -9.0]
#     Tetraloop37 = [-5.0, -5.5, -6.0]
#     Triloop37 = [-3.0, -3.5, -4.0]
#
#     # 示例调用
#     loop_struct_example = {
#         'flag': 1,
#         'sequence': "CCCCCCGG",
#         'pointer_sequence': ""
#     }
#     energy = calculate_loop_energy(loop_struct_example, 2)  # 六碱基发夹环
#     print(f"六碱基发夹环的自由能: {energy} dcal/mol")  # 输出: -8.5 dcal/mol
#
#     loop_struct_example = {
#         'flag': -1,
#         'sequence': "",
#         'pointer_sequence': "GCGCAG"
#     }
#     energy = calculate_loop_energy(loop_struct_example, 1)  # 四碱基发夹环
#     print(f"四碱基发夹环的自由能: {energy} dcal/mol")  # 输出: -5.0 dcal/mol
#
#     loop_struct_example = {
#         'flag': 0,
#         'sequence': "GGCAG",
#         'pointer_sequence': ""
#     }
#     energy = calculate_loop_energy(loop_struct_example, 3)  # 三碱基发夹环
#     print(f"三碱基发夹环的自由能: {energy} dcal/mol")  # 输出: -4.0 dcal/mol
#
#     loop_struct_example = {
#         'flag': 1,
#         'sequence': "UNKNOWN",
#         'pointer_sequence': ""
#     }
#     energy = calculate_loop_energy(loop_struct_example, 2)  # 未知六碱基发夹环
#     print(f"未知六碱基发夹环的自由能: {energy} dcal/mol")  # 输出: 4294957296.0 dcal/mol

