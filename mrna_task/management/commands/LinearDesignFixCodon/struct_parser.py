from typing import Dict, Optional
from .common import NodeType, NodeNucpair, State
INT_MIN = -2**31

class BestX_t_CAI:
    """
    对应 C++:
      using BestX_t_CAI = Flat<NodeType,
                               Flat<NodeNucpair, State_t, detail::NodeNucIndex>,
                               detail::NodeIndex>;

    - 外层 key: NodeType
    - 内层 key: NodeNucpair
    - value: State
    """

    def __init__(self):
        # 用字典套字典来模拟 C++ 里双层 map。
        # 外层: Dict[NodeType, Dict[NodeNucpair, State]]
        self._container: Dict[NodeType, Dict[NodeNucpair, State]] = {}

    def set_state(self, node: NodeType, node_nucpair: NodeNucpair, state: State) -> None:
        """ 在 (node -> node_nucpair) 位置存储一个 State """
        if node not in self._container:
            self._container[node] = {}
        self._container[node][node_nucpair] = state

    def get_state(self, node: NodeType, node_nucpair: NodeNucpair) -> Optional[State]:

        return self._container.get(node, {}).get(node_nucpair, State(INT_MIN, float('-inf'), (-1, -1, -1), float('-inf'), None))

    def has_state(self, node: NodeType, node_nucpair: NodeNucpair) -> bool:
        """ 判断 (node -> node_nucpair) 是否存有 State """
        return node in self._container and node_nucpair in self._container[node]

    def __repr__(self) -> str:
        """ 打印时查看当前内容 """
        return f"BestX_t_CAI({self._container})"


class BestM_t_CAI:
    """
    对应 C++:
      using BestX_t_CAI = Flat<NodeType,
                               Flat<NodeNucpair, State_t, detail::NodeNucIndex>,
                               detail::NodeIndex>;

    - 外层 key: NodeType
    - 内层 key: NodeNucpair
    - value: State
    """

    def __init__(self):
        # 用字典套字典来模拟 C++ 里双层 map。
        # 外层: Dict[NodeType, Dict[NodeNucpair, State]]
        self._container: Dict[NodeType, Dict[NodeType, State]] = {}

    def set_state(self, node: NodeType, node_type: NodeType, state: State) -> None:
        """ 在 (node -> node_nucpair) 位置存储一个 State """
        if node not in self._container:
            self._container[node] = {}
        self._container[node][node_type] = state

    def get_state(self, node: NodeType, node_type: NodeType) -> Optional[State]:
        """ 读取 (node -> node_nucpair) 位置的 State，如无则返回 None """
        return self._container.get(node, {}).get(node_type, State(INT_MIN, float('-inf'), (-1, -1, -1), float('-inf'), None))

    def has_state(self, node: NodeType, node_type: NodeType) -> bool:
        """ 判断 (node -> node_nucpair) 是否存有 State """
        return node in self._container and node_type in self._container[node]

    def __repr__(self) -> str:
        """ 打印时查看当前内容 """
        return f"BestM_t_CAI({self._container})"

class BestC_t_CAI:
    """
    对应 C++:
      using BestX_t_CAI = Flat<NodeType,
                               Flat<NodeNucpair, State_t, detail::NodeNucIndex>,
                               detail::NodeIndex>;

    - 外层 key: NodeType
    - 内层 key: NodeNucpair
    - value: State
    """

    def __init__(self):
        # 用字典套字典来模拟 C++ 里双层 map。
        # 外层: Dict[NodeType, Dict[NodeNucpair, State]]
        self._container: Dict[NodeType, State] = {}

    def set_state(self, node: NodeType, state: State) -> None:
        """ 在 (node -> node_nucpair) 位置存储一个 State """
        if node not in self._container:
            self._container[node] = {}
        self._container[node] = state

    def get_state(self, node: NodeType) -> Optional[State]:
        return self._container.get(node,  State(INT_MIN, float('-inf'), (-1, -1, -1), float('-inf'), None))

    def has_state(self, node: NodeType) -> bool:
        """ 判断 (node -> node_nucpair) 是否存有 State """
        return node in self._container

    def __repr__(self) -> str:
        """ 打印时查看当前内容 """
        return f"BestX_t_CAI({self._container})"

def main():
    # -------------------------
    # 测试 BestX_t_CAI
    # -------------------------
    # print("=== 测试 BestX_t_CAI ===")
    bestX = BestX_t_CAI()

    # 准备设置的 state
    test_state_x = State(100, 3.14, (1, 2, 3), -0.5)

    # 写入
    bestX.set_state(node=0, node_nucpair=(5, 9, 1), state=test_state_x)
    # print("写入后：", bestX)

    # 读取
    retrieved_state_x = bestX.get_state(node=0, node_nucpair=(5, 9, 1))
    # print("读取到的状态：", retrieved_state_x)

    # 判断是否存在
    has_state_x = bestX.has_state(node=0, node_nucpair=(5, 9, 1))
    # print("has_state 测试：", has_state_x)

    # 测试未设置的 key
    default_state_x = bestX.get_state(node=999, node_nucpair=(999, 999))
    # print("读取不存在的 key 时返回的默认状态：", default_state_x)

    # -------------------------
    # 测试 BestM_t_CAI
    # -------------------------
    # print("\n=== 测试 BestM_t_CAI ===")
    bestM = BestM_t_CAI()

    # 准备设置的 state
    test_state_m = State(-1, 2.71, (4, 4, 4), 10.0)

    # 写入
    bestM.set_state(node=10, node_type=20, state=test_state_m)
    # print("写入后：", bestM)

    # 读取
    retrieved_state_m = bestM.get_state(node=10, node_type=20)
    # print("读取到的状态：", retrieved_state_m)

    # 判断是否存在
    has_state_m = bestM.has_state(node=10, node_type=20)
    # print("has_state 测试：", has_state_m)

    # 测试未设置的 key
    default_state_m = bestM.get_state(node=999, node_type=999)
    # print("读取不存在的 key 时返回的默认状态：", default_state_m)

    # -------------------------
    # 测试 BestC_t_CAI
    # -------------------------
    # print("\n=== 测试 BestC_t_CAI ===")
    bestC = BestC_t_CAI()

    # 准备设置的 state
    test_state_c = State(42, 0.1234, (7, 8, 9), 100.0)

    # 写入
    bestC.set_state(node=999, state=test_state_c)
    # print("写入后：", bestC)

    # 读取
    retrieved_state_c = bestC.get_state(node=999)
    # print("读取到的状态：", retrieved_state_c)

    # 判断是否存在
    has_state_c = bestC.has_state(node=999)
    # print("has_state 测试：", has_state_c)

    # 测试未设置的 key
    default_state_c = bestC.get_state(node=123456)
    # print("读取不存在的 key 时返回的默认状态：", default_state_c)

if __name__ == "__main__":
    main()