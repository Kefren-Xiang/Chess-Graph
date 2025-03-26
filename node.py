import math
import chess

def extract_fen(board: chess.Board) -> str:
    """
    提取棋盘部分的FEN (只取空格前面部分).
    """
    full_fen = board.fen()
    return full_fen.split(' ')[0]

class Node:
    def __init__(self, board=None, visit_count=1, Q=0.0, nn_Q=0.0, r=0.0):
        """
        board: chess.Board 或者 None。
        visit_count: 初始访问次数
        Q: 强化学习中的Q值
        nn_Q: 留给后续神经网络使用
        r: 该节点的初始奖励 (通过 examine_status 可得到)
        children: 存放子节点Fen列表
        """
        if board is not None:
            self.fen = extract_fen(board)
            self.player_to_move = 'w' if board.turn == chess.WHITE else 'b'
            self.depth = board.fullmove_number
        else:
            self.fen = ""
            self.player_to_move = 'w'
            self.depth = 1

        self.visit_count = visit_count
        self.Q = Q
        self.nn_Q = nn_Q
        self.r = r
        # 只存FEN，不存子Node对象
        self.children = []

    def add_child(self, child_fen: str):
        if child_fen not in self.children:
            self.children.append(child_fen)

    def update_visit_count(self):
        self.visit_count += 1

    def calculate_alpha(self) -> float:
        """
        学习率 α = 0.9 * exp(-visit_count/100) + 0.05
        """
        return 0.9 * math.exp(-self.visit_count / 100) + 0.05

    def calculate_gamma(self) -> float:
        """
        折扣因子 γ = 0.9 * exp(-depth/100) + 0.05
        """
        return 0.9 * math.exp(-self.depth / 100) + 0.05

    def update_Q(self, reward: float, max_min_Q: float):
        """
        Q-learning更新:
          Q = Q + α * (reward + γ * (max_min_Q - Q))
        """
        alpha = self.calculate_alpha()
        gamma = self.calculate_gamma()
        self.Q += alpha * (reward + gamma * (max_min_Q - self.Q))

    def to_dict(self) -> dict:
        return {
            "FEN": self.fen,
            "visit_count": self.visit_count,
            "Q": self.Q,
            "nn_Q": self.nn_Q,
            "r": self.r,
            "children_fens": ",".join(self.children)
        }
