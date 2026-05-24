@echo off
REM ====================================
REM 打包 Windows EXE
REM 需要在 Windows 环境下运行
REM ====================================
REM
REM 前置条件:
REM   1. 安装 Python 3.8+
REM   2. pip install pyinstaller
REM
REM 使用方法:
REM   双击运行 或 在命令行执行: build_exe.bat
REM

echo ====================================
echo  URL 目录下载器 — 打包 EXE
echo ====================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装
    pause
    exit /b 1
)

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] PyInstaller...
    pip install pyinstaller
)

echo [打包] 正在编译 CLI 版本...
pyinstaller --onefile --name "url-downloader-cli" downloader.py

echo [打包] 正在编译 GUI 版本...
pyinstaller --onefile --windowed --name "url-downloader-gui" downloader_gui.py

echo.
echo ====================================
echo  完成！
echo  CLI: dist\url-downloader-cli.exe
echo  GUI: dist\url-downloader-gui.exe
echo ====================================
pause
