# V家翻转棋

一个使用 Python 核心逻辑、Tkinter 桌面窗口和 Nuitka 打包脚本组织的 V 家主题翻转棋小游戏，并新增 Kotlin/Jetpack Compose 原生 Android 工程骨架。

## 功能

- 单人模式：玩家在开始前选择言和棋或天依棋，电脑执另一方。
- 双人模式：本机两名玩家轮流操作。
- 联机模式骨架：预留选棋、连接、发送落子、接收落子接口，当前版本不发起真实网络连接。
- 棋盘规格：6x6、8x8、10x10、12x12。
- Tk 窗口可放大缩小，棋盘保持正方形并自动居中缩放，且不会小于棋盘和顶部控制区所需的最小尺寸。
- 电脑难度：简单、中等、高难。
- 使用淡化后的 `pic/background.png` 作为棋盘背景。
- 使用 `pic/qizi0.png` 作为言和棋，`pic/qizi1.png` 作为天依棋。
- 言和棋使用更深底盘，天依棋使用更浅底盘，便于区分。
- Android 工程位于 `android/`，使用 Kotlin 原生实现，不运行 Python 代码。

## AI 难度

- 简单：主要看本步能翻多少子。
- 中等：优先占角，再考虑边线，并避免空角旁边的危险位置。
- 高难：在中等策略基础上加入棋盘位置权重、后续机动性、压制对手选择和避免送角。

## 目录结构

```text
.
├── core.py
├── tk_ui.py
├── tk_run.py
├── reversi.py
├── build_nuitka.ps1
├── build_android.ps1
├── sync_android_assets.ps1
├── requirements.txt
├── android/
├── pic/
│   ├── background.png
│   ├── qizi0.png
│   └── qizi1.png
└── knowledge/
```

## 入口

- `core.py`：V 家翻转棋核心规则、AI 难度策略、联机模式骨架。
- `tk_ui.py`：Tkinter 桌面界面。
- `tk_run.py`：Tkinter 启动入口，也是 Nuitka 打包入口。
- `reversi.py`：兼容入口，内部转发到 `tk_run.py`。
- `build_nuitka.ps1`：Windows 下的 Nuitka 打包脚本。
- `android/`：Kotlin + Jetpack Compose Android 工程，规则和界面均为 Android 原生实现。
- `build_android.ps1`：Android 命令行构建入口，默认构建 debug APK。
- `sync_android_assets.ps1`：把根目录 `pic/` 素材同步到 Android 资源目录。

## Android 工程

Android 工程与 Python 桌面版是双实现：

- Android 不运行 `core.py`，不依赖 Tkinter、Streamlit、Nuitka、Pillow 或 `requirements.txt`。
- Android 规则层参考 `core.py`，实现于 `android/app/src/main/java/com/vsinger/reversi/ReversiCore.kt`。
- Android 界面实现于 `android/app/src/main/java/com/vsinger/reversi/MainActivity.kt`。
- 修改 `core.py`、AI 策略、棋盘规格、模式语义或棋子名称时，需要同步检查 Android Kotlin 实现。
- 修改 `pic/` 素材后，需要执行素材同步并重新构建 Android APK。

首次开发建议使用 Android Studio 打开 `android/`。

命令行构建：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_android.ps1
```

同步 Android 素材：

```powershell
powershell -ExecutionPolicy Bypass -File .\sync_android_assets.ps1
```

APK 默认输出目录：

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

## 安装依赖

当前统一使用 `envs2` 环境：

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" -m pip install -r .\requirements.txt
```

## 运行 Tkinter 桌面版

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py
```

兼容旧入口：

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\reversi.py
```

## Nuitka 打包

```powershell
powershell -ExecutionPolicy Bypass -File .\build_nuitka.ps1 -LowMemory
```

生成 onefile 单文件：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_nuitka.ps1 -LowMemory -OneFile
```

打包脚本默认使用 `C:\Users\admin\.conda\envs\envs2\python.exe`，输出文件名为 `VsingerReversi.exe`。

## 验证

```powershell
& "C:\Users\admin\.conda\envs\envs2\python.exe" -m py_compile .\core.py .\tk_ui.py .\tk_run.py .\reversi.py
& "C:\Users\admin\.conda\envs\envs2\python.exe" .\tk_run.py --self-check-imports
$null = [scriptblock]::Create((Get-Content -Raw .\build_nuitka.ps1 -Encoding utf8))
$null = [scriptblock]::Create((Get-Content -Raw .\build_android.ps1 -Encoding utf8))
$null = [scriptblock]::Create((Get-Content -Raw .\sync_android_assets.ps1 -Encoding utf8))
```

未明确要求时，不主动执行 Nuitka 打包。
未配置 Android SDK/JDK 时，不执行 Android APK 构建。
