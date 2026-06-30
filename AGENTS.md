# AGENTS.md

## 项目定位

- 本项目是 Python/Tkinter 桌面小游戏 `V家翻转棋`。
- 当前结构为核心规则、Tkinter 桌面窗口和 Nuitka 打包脚本。
- 当前支持单人、双人、联机骨架三种模式。
- 用户可见名称为 `V家翻转棋`，先手显示为 `言和棋`，后手显示为 `天依棋`。

## 文件职责

- `core.py`：游戏规则、棋盘规格、AI 难度策略和联机模式骨架，不依赖 UI。
- `tk_ui.py`：Tkinter 桌面界面，负责资源加载、窗口缩放、棋盘渲染和交互。
- `tk_run.py`：Tkinter 启动入口，也是 Nuitka 打包入口。
- `reversi.py`：兼容入口，转发到 `tk_run.py`。
- `build_nuitka.ps1`：Nuitka 打包脚本。
- `pic/background.png`：棋盘背景。
- `pic/qizi0.png`：言和棋素材。
- `pic/qizi1.png`：天依棋素材。
- `requirements.txt`：Pillow 和 Nuitka 打包依赖。

## 运行与验证

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" -m py_compile .\core.py .\tk_ui.py .\tk_run.py .\reversi.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py --self-check-imports
$null = [scriptblock]::Create((Get-Content -Raw .\build_nuitka.ps1 -Encoding utf8))
```

## 开发边界

- 棋盘规则放在 `core.py`，UI 层不得复制核心规则。
- Tkinter 可见文案保持中文。
- Tkinter 资源加载依赖 Pillow，打包时必须把 `pic/` 带入 Nuitka 数据文件。
- AI 难度统一通过 `choose_ai_move(game, player, difficulty)` 进入。
- 联机对弈先通过 `NetworkSession` 占位接口扩展，不要把真实网络逻辑写死在 UI 层。
- 新增第三方依赖时必须同步更新 `requirements.txt`、README 和运行交付文档。

## 完成标准

- README 已同步。
- 依赖文件已同步。
- knowledge 已同步或明确无需更新。
- 最小验证通过，或说明无法验证的原因。
