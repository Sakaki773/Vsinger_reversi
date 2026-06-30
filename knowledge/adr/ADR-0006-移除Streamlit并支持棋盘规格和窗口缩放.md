# ADR-0006-移除 Streamlit 并支持棋盘规格和窗口缩放

## 状态

已接受

## 背景

项目当前交付目标是 Tkinter 桌面游戏和 Nuitka EXE，不再需要 Streamlit 调试页面。同时游戏需要支持常见棋盘规格，并允许 Tk 窗口放大缩小。

## 决策

- 删除 `streamlit_ui.py` 和 `streamlit_run.py`。
- 从 `requirements.txt` 移除 Streamlit 依赖。
- 文档和知识库改为 Tkinter + Nuitka 结构。
- `ReversiGame` 支持 6x6、8x8、10x10、12x12。
- Tk 窗口允许缩放，棋盘保持正方形并在画布区域内始终居中，格子、棋子、合法落子提示随窗口自动缩放。
- 窗口设置动态最小尺寸，棋盘区域设置 grid 最小尺寸，不能缩到遮挡棋盘和顶部控制区。
- 言和棋使用更深底盘，天依棋使用更浅底盘，以增强视觉区分。

## 影响

- 启动和交付路径更简单。
- 不再维护浏览器调试页面。
- UI 需要在不同窗口尺寸和不同棋盘规格下保持稳定。

## 涉及改动

- `core.py`
- `tk_ui.py`
- `requirements.txt`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `knowledge/`

## 验证

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" -m py_compile .\core.py .\tk_ui.py .\tk_run.py .\reversi.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py --self-check-imports
```
