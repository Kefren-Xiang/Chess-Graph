import chess
import chess.engine
import random
from node_manager import NodeManager
from node import Node, extract_fen
import numpy as np
import torch

# 配置Stockfish引擎路径和参数
STOCKFISH_PATH = r"D:\stockfish\stockfish.exe"
ENGINE_CONFIG = {
    "Threads": 4,
    "Hash": 2048,
    "NumaPolicy": "hardware"
}

class StockfishAI:
    def __init__(self, color, time_limit=1.0):
        self.color = color
        self.time_limit = time_limit
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.engine.configure(ENGINE_CONFIG)

    def choose_move(self, board):
        result = self.engine.play(
            board,
            chess.engine.Limit(time=self.time_limit),
            info=chess.engine.INFO_ALL
        )
        return result.move

    def close(self):
        self.engine.quit()

def update_father_node_Q(father_node: Node, node_mgr: NodeManager):
    """
    更新父节点 Q 值
    """
    child_Q_values = []
    for child_fen in father_node.children:
        child_node, _ = node_mgr.find_or_create_node_fen(child_fen)
        child_Q_values.append(child_node.Q)

    if father_node.player_to_move == 'w':  # 白方选择最大Q值
        max_min_Q = max(child_Q_values) if child_Q_values else 0
    else:  # 黑方选择最小Q值
        max_min_Q = min(child_Q_values) if child_Q_values else 0

    board = chess.Board()
    board.set_fen(father_node.fen)  # 这里用 father_node.fen 重建
    reward = node_mgr.examine_status(board)

    father_node.update_Q(reward, max_min_Q)

    node_mgr.update_node(father_node)

def random_move(board: chess.Board):
    """随机选择一个合法走法"""
    return random.choice(list(board.legal_moves))

def test_flow():
    node_mgr = NodeManager(filename="Node.csv")
    board = chess.Board()

    white_ai = StockfishAI(chess.WHITE, time_limit=0)
    black_ai = StockfishAI(chess.BLACK, time_limit=0)

    root_node, all_nodes = node_mgr.find_or_create_node(board)
    root_node.update_visit_count()

    if not root_node.children:
        for move in board.legal_moves:
            board.push(move)
            child_fen = extract_fen(board)
            root_node.add_child(child_fen)

            node_mgr.find_or_create_node(board)
            board.pop()

    update_father_node_Q(root_node, node_mgr)

    node_mgr.update_node(root_node)

    current_node = root_node  # 设置当前节点为根节点
    while not board.is_game_over():
        current_ai = white_ai if board.turn == chess.WHITE else black_ai
        move = current_ai.choose_move(board)
        board.push(move)

        # 创建新节点（对应新棋盘状态）
        new_node, all_nodes = node_mgr.find_or_create_node(board)

        # 更新当前节点的visit_count
        new_node.update_visit_count()

        if not new_node.children:
            for move in board.legal_moves:
                board.push(move)
                child_fen = extract_fen(board)
                new_node.add_child(child_fen)

                # 为子节点登记
                node_mgr.find_or_create_node(board)
                board.pop()

        update_father_node_Q(new_node, node_mgr)

        node_mgr.update_node(new_node)

        print(f"Current FEN: {new_node.fen}, Q Value: {new_node.Q}")

        current_node = new_node  # 新的父节点

    print(f"Game Over. Final Result: {board.result()}")
    white_ai.close()
    black_ai.close()

if __name__ == "__main__":
    test_flow()
