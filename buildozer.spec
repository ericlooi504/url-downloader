# Buildozer 配置 — 打包 Android APK
# 使用方法:
#   pip install buildozer cython
#   buildozer init        # 生成 buildozer.spec（如果有这个文件了就不用）
#   buildozer android debug   # 开始编译 APK
#
# 注意: 首次运行会自动下载 Android SDK/NDK（~1GB），耗时较久

[app]

# (str) Title of your application
title = URL 目录下载器

# (str) Package name
package.name = urldownloader

# (str) Package domain (needed for android/ios packaging)
package.domain = com.downloader

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (match pattern)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
# source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (match pattern)
source.exclude_exts = spec

# (list) List of directory to exclude (match pattern)
# source.exclude_dirs = tests, bin

# (list) List of requirements (pip packages)
requirements = python3,kivy,requests

# (str) Presplash of the application (image file used on boot)
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application (image file for the logo)
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX / iOS / Android specific
#

# (str) Android category
android.category = TOOLS

# (str) Android entry point (default main.py)
android.entrypoint = downloader_gui.py

# (list) List of Java .jar files to add
# android.add_jars = foo.jar,bar.jar

# (bool) Indicate if the application should be fullscreen or not
android.fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 24

# (str) Android NDK version to use
# android.ndk = 27

# (bool) Enable AndroidX support (needed for modern Android)
android.enable_androidx = True

# (str) Android package name suffix
# android.package_name_suffix =

#
# Build configuration
#

# (str) The Android arch to build for (armeabi-v7a, arm64-v8a, x86, x86_64)
android.archs = arm64-v8a, armeabi-v7a

# (str) Python for android branch (default: master)
# p4a.branch = develop

# (str) Output filename (default: package-name-VERSION.apk)
# android.filename = urldownloader

# (int) Version code for Android (must be incremented per release)
android.version_code = 1

# (str) Version name
android.version = 1.0.0

#
# iOS specific
#

# (str) Name of the certificate to use for iOS signing
# ios.codesign.allowed = true

# (str) Path to the provisioning profile
# ios.codesign.provisioning_profile =

[buildozer]

# (int) Log level (0=error, 1=warning, 2=info, 3=debug)
log_level = 2

# (int) Number of parallel jobs to use
# jobs = 1

# (str) Where to store the log file
log_filename = buildozer.log
