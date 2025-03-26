# ♟️ Chess-Graph: 强化学习阶段说明文档

本模块旨在构建一个图结构的国际象棋AI强化学习系统，以 `FEN` 作为唯一标识，对每个棋盘状态建模并记录访问情况、奖励值和估值信息，最终为后续神经网络训练和策略学习提供高质量数据。

---

## 📁 文件结构

| 文件名          | 功能描述 |
|----------------|----------|
| `node.py`       | 定义 `Node` 类：每一个棋盘状态节点，包含 FEN、访问次数、Q值、子节点等信息 |
| `node_manager.py` | 定义 `NodeManager` 类：用于加载、保存和更新节点到 `Node.csv` |
| `main.py`       | 强化学习主流程：进行对弈、节点更新、Q值计算与存储 |
| `Node.csv`      | 存储所有棋盘节点数据（FEN、visit_count、Q、nn_Q、r、子节点FEN） |

---

## 🧠 节点数据结构（Node）

每个棋盘状态在图结构中作为一个“节点”存在，保存的信息如下：

- `fen`: 棋盘状态唯一标识（只保留前半部分 FEN）
- `visit_count`: 被访问次数（默认初始化为1）
- `Q`: 强化学习的价值估计（随着数据不断更新）
- `nn_Q`: 预留给神经网络的Q值预测（初始化为0）
- `r`: 奖励值，使用如下函数定义：

```python
def examine_status(board):
    if board.is_checkmate():
        return 1.0 if board.turn == chess.BLACK else -1.0
    else:
        return 0.0
