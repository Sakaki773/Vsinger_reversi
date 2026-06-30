# ADR-0003-增加 AI 难度和网络对弈骨架

## 状态

已接受

## 背景

翻转棋的核心策略是优先占角，其次占边。原先电脑只使用单一启发式，不便于玩家选择对弈强度，也没有双人或网络对弈扩展点。

## 决策

新增三档 AI 难度：

- 简单：优先翻子数量。
- 中等：优先占角、占边，并避开空角旁危险位置。
- 高难：加入位置权重、后续机动性、压制对手合法落子和避免送角。

新增三种模式：

- 单人模式。
- 双人模式。
- 联机模式骨架。

网络骨架通过 `NetworkSession` 暴露连接、发送落子、接收落子接口，当前不做真实网络通信。

## 影响

- `core.py` 成为 AI 难度和网络骨架的统一入口。
- Tkinter 可以选择模式和 AI 难度。历史上 Streamlit 调试页也曾同步该能力，但已在 ADR-0006 中移除。
- 后续接入真实网络时，不需要重写棋盘规则和 UI 主流程。

## 涉及改动

- `core.py`
- `tk_ui.py`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `knowledge/`

## 验证

```powershell
python -m py_compile .\core.py .\tk_ui.py .\tk_run.py .\reversi.py
python .\tk_run.py --self-check-imports
```

## 运行逻辑

单人模式下电脑执棋方自动调用 `choose_ai_move()`。双人模式不触发 AI。联机模式当前只记录预留接口动作，真实远端同步留给后续实现。
