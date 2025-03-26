import csv
import os
from typing import Dict, Tuple
import chess
from node import Node, extract_fen

class NodeManager:
    def __init__(self, filename='Node.csv'):
        """
        管理CSV文件, 读写Node
        """
        self.filename = filename
        self.columns = ["FEN", "visit_count", "Q", "nn_Q", "r", "children_fens"]
        self.init_csv()

    def init_csv(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writeheader()

    def load_nodes(self) -> Dict[str, Node]:
        nodes = {}
        with open(self.filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 根据CSV构造Node
                node = Node(board=None)
                node.fen = row['FEN']
                node.visit_count = int(row['visit_count'])
                node.Q = float(row['Q'])
                node.nn_Q = float(row['nn_Q'])
                node.r = float(row['r'])
                node.children = row['children_fens'].split(',') if row['children_fens'].strip() else []
                nodes[node.fen] = node
        return nodes

    def save_node(self, node: Node):
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writerow(node.to_dict())

    def save_all(self, all_nodes: Dict[str, Node]):
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            for n in all_nodes.values():
                writer.writerow(n.to_dict())

    def update_node(self, node: Node):
        all_nodes = self.load_nodes()
        all_nodes[node.fen] = node
        self.save_all(all_nodes)

    def find_or_create_node(self, board: chess.Board) -> Tuple[Node, Dict[str, Node]]:
        all_nodes = self.load_nodes()
        fen = extract_fen(board)
        if fen in all_nodes:
            return all_nodes[fen], all_nodes
        else:
            r_val = self.examine_status(board)
            new_node = Node(board=board, r=r_val, Q=r_val)
            self.save_node(new_node)
            all_nodes[fen] = new_node
            return new_node, all_nodes

    def find_or_create_node_fen(self, fen: str) -> Tuple[Node, Dict[str, Node]]:
        all_nodes = self.load_nodes()
        if fen in all_nodes:
            return all_nodes[fen], all_nodes
        else:
            new_node = Node(board=None, r=0.0)
            new_node.fen = fen
            self.save_node(new_node)
            all_nodes[fen] = new_node
            return new_node, all_nodes

    def examine_status(self, board: chess.Board) -> float:
        """
        简单奖励:
          胜=1, 和=0, 负=-1
        """
        if board.is_checkmate():
            # 被将死的一方 = board.turn
            # 如果 black要走 => black死 => white赢 => +1
            status = '1-0' if board.turn == chess.BLACK else '0-1'
        else:
            status = '0-0'

        if status == '1-0':
            return 1.0
        elif status == '0-0':
            return 0.0
        else:
            return -1.0
