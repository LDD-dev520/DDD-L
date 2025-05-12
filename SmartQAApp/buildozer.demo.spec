[app]

# 应用名称
title = SmartQA银行助手演示版

# 应用包名
package.name = smartqademo

# 应用域名
package.domain = org.smartqa

# 源代码位置
source.dir = .

# 包含的源文件
source.include_exts = py,png,jpg,kv,atlas

# 包含的数据目录
source.include_patterns = assets/*

# 包含的包
requirements = python3,kivy

# Android特定配置
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.sdk = 30
android.ndk = 21e

# NDK API配置
android.ndk_api = 21

# 应用版本
version = 1.0.0

# 所有者信息
author = SmartQA Team
author_email = your.email@example.com

# 指定主文件
source.main = demo_app.py

# 指定了Android相关的配置
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# 图标和启动图
android.presplash_color = #FFFFFF
android.icon.filename = %(source.dir)s/assets/icon.png
android.presplash.filename = %(source.dir)s/assets/splash.png

# 构建选项
buildozer.warn_on_root = 0

# 用于p4a
p4a.branch = master

# 指定使用PyJNIus或否
android.enable_androidx = True 