# ADR-0007 新增独立 Android 原生工程

## 状态

已采纳。

## 背景

项目已有 Python `core.py`、Tkinter 桌面界面和 Nuitka 打包链路。Android 端无法直接复用 Tkinter 界面，若在 APK 中嵌入 Python 运行时，会增加包体、桥接复杂度和后续维护成本。

## 决策

新增 `android/` 原生 Android 工程，使用 Kotlin + Jetpack Compose。

- Android 不运行 `core.py`。
- Android 不依赖 Tkinter、Streamlit、Nuitka、Pillow 或 `requirements.txt`。
- Android 规则层参考 `core.py`，在 Kotlin 中双实现。
- Android 图片资源从根目录 `pic/` 同步到 `android/app/src/main/res/drawable-nodpi/`。
- 根目录新增 `sync_android_assets.ps1` 和 `build_android.ps1`。

## 影响

- Python/Tk 修改不会自动同步到 Android。
- 修改核心规则、AI 策略、棋盘规格、模式语义和用户可见名称时，必须同步检查 Android Kotlin 实现。
- 修改图片素材后，必须同步 Android 资源并重新构建 APK。
- 后续可以用共同的行为样例或测试清单约束 Python 与 Android 规则一致性。
