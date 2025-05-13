[app]

# 应用名称
title = SmartQA银行助手

# 应用包名
package.name = smartqa

# 应用域名
package.domain = org.smartqa

# 源代码位置
source.dir = .

# 包含的源文件
source.include_exts = py,png,jpg,kv,atlas,json,md,wav,mp3,ttf,txt

# 包含的数据目录和源文件
source.include_patterns = resources/*,data/*,assets/*,fonts/*,*.py

# 包含的包 - 简化版本
requirements = python3==3.11.12,kivy==2.1.0,Cython==0.29.33

# Android特定配置
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 21

# 应用版本
version = 1.0.0

# 要求语音输入
android.features = android.hardware.microphone

# 所有者信息
author = SmartQA Team
author_email = your.email@example.com

# 架构支持 - 只使用一种架构简化构建
android.archs = arm64-v8a

# Android P8相关的配置
android.accept_sdk_license = True

# 图标和启动图
android.presplash_color = #FFFFFF
android.icon.filename = %(source.dir)s/assets/icon.png
android.presplash.filename = %(source.dir)s/assets/splash.jpg

# 构建选项
buildozer.warn_on_root = 0

# 指定主应用程序
source.main = main.py

# 使用p4a
p4a.branch = master

# 指定使用PyJNIus或否
android.enable_androidx = True

# 允许混合Web内容
android.allow_mixed_content = True

