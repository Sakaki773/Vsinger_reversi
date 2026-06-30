# CLAUDE.md

## 项目说明

- 项目名称：VsingerReversi
- 用户可见名称：V家翻转棋
- 项目类型：Python/Tkinter 桌面小游戏，附 Nuitka 打包脚本
- 桌面入口：`tk_run.py`
- 兼容入口：`reversi.py`
- 打包入口：`build_nuitka.ps1`
- 游戏模式：单人、双人、联机骨架
- AI 难度：简单、中等、高难
- 棋盘规格：6x6、8x8、10x10、12x12
- 棋子主题：言和棋、天依棋

## 关键文件

- `core.py`：核心规则、棋盘规格、AI 难度策略和联机模式骨架。
- `tk_ui.py`：Tkinter 桌面界面。
- `tk_run.py`：Tkinter 启动入口，也是 Nuitka 打包入口。
- `reversi.py`：兼容入口。
- `build_nuitka.ps1`：Nuitka 打包脚本。
- `pic/`：棋盘背景和棋子素材。
- `knowledge/00_导航/00_知识库导航.md`：知识库入口。

## 常用命令

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" -m py_compile .\core.py .\tk_ui.py .\tk_run.py .\reversi.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py --self-check-imports
powershell -ExecutionPolicy Bypass -File .\build_nuitka.ps1 -LowMemory
```

## 工作原则

- Python/Tkinter 优先，保持小范围修改。
- 不提交真实数据、本地配置、缓存和构建产物。
- 修改运行方式、依赖、核心规则或 UI 入口后，同步检查 README、AGENTS 和 knowledge。
- 新增依赖必须同步维护 `requirements.txt` 和 README。
- Nuitka 只打包 `tk_run.py`。
- 真实联机对弈后续应从 `NetworkSession` 扩展，避免把 socket 或 HTTP 逻辑直接塞进 UI。
