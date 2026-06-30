# V家翻转棋 Android 工程

这是 `V家翻转棋` 的原生 Android 工程骨架，使用 Kotlin + Jetpack Compose。

## 关系边界

- Android 不运行 `core.py`。
- Android 不依赖 Tkinter、Streamlit、Nuitka、Pillow 或 `requirements.txt`。
- Android 规则层位于 `app/src/main/java/com/vsinger/reversi/ReversiCore.kt`。
- Android 界面位于 `app/src/main/java/com/vsinger/reversi/MainActivity.kt`。
- 当前复用根目录 `pic/` 下的图片素材，复制到 `app/src/main/res/drawable-nodpi/`。

## 打开方式

用 Android Studio 打开本目录 `android/`，等待 Gradle Sync 完成后运行 `app`。

## 命令行构建

在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_android.ps1
```

生成 APK 的默认位置：

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

如果本目录没有 `gradlew.bat`，脚本会尝试使用系统 `gradle` 命令。首次开发建议优先用 Android Studio 打开工程。

## 素材同步

修改根目录 `pic/` 后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\sync_android_assets.ps1
```

这只同步图片资源，不同步 Python 规则或 Tkinter 界面。
