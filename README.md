# URL 目录下载器

输入一个网页地址，自动下载该目录下的所有文件。支持多线程、递归、扩展名过滤。

## 快速使用 (命令行)

```bash
# 无需安装任何第三方库（只用 Python 标准库）
python3 downloader.py https://example.com/files/
python3 downloader.py https://example.com/files/ -o ./myfiles -r
python3 downloader.py https://example.com/files/ -e .pdf .docx -t 10
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `url` | 网页目录地址（必填） |
| `-o, --output` | 保存目录 (默认: downloads) |
| `-r, --recursive` | 递归下载子目录 |
| `-e, --extensions` | 只下载指定扩展名，如 `.pdf .jpg` |
| `-t, --threads` | 并发线程数 (默认: 5) |
| `--delay` | 每个文件后延迟秒数 |
| `--overwrite` | 覆盖已有文件 |

## 打包 EXE (Windows)

**前置条件:** 在 Windows 机器上安装 Python 3.8+

```cmd
# 方法一：双击运行
双击 build_exe.bat

# 方法二：手动执行
pip install pyinstaller
pyinstaller --onefile --name "url-downloader-cli" downloader.py
pyinstaller --onefile --windowed --name "url-downloader-gui" downloader_gui.py
```

输出在 `dist/` 目录：
- `url-downloader-cli.exe` — 命令行版本
- `url-downloader-gui.exe` — 图形界面版本

## 打包 APK (Android)

**前置条件:** Linux 环境 + Python 3.8+

```bash
# 1. 安装 buildozer
pip install buildozer cython

# 2. 初始化（已有 buildozer.spec 可跳过）
buildozer init

# 3. 编译 APK（首次会下载 Android SDK/NDK，约1GB）
buildozer android debug

# APK 生成在 bin/ 目录
```

> 首次编译较慢，因为需要下载 Android SDK/NDK、交叉编译 Python 和 Kivy。

## 文件清单

```
url-downloader/
├── downloader.py          # 核心脚本（命令行）
├── downloader_gui.py      # Kivy GUI 版本（用于 APK）
├── requirements.txt       # 依赖清单
├── build_exe.bat          # Windows EXE 打包脚本
├── buildozer.spec         # Android APK 打包配置
└── README.md              # 本文件 (可选)
```
