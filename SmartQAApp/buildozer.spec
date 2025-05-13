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

# 包含的包
requirements = python3==3.10,kivy==2.1.0,pyttsx3,gtts,chardet,speech_recognition,baidu-aip,python-Levenshtein,scikit-learn,joblib,fuzzywuzzy,comtypes,requests,numpy

# Android特定配置
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b

# NDK API配置
android.ndk_api = 21

# 应用版本
version = 1.0.0

# 要求语音输入
android.features = android.hardware.microphone

# 所有者信息
author = SmartQA Team
author_email = your.email@example.com

# 指定了Android P8相关的配置
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# 图标和启动图
android.presplash_color = #FFFFFF
android.icon.filename = %(source.dir)s/assets/icon.png
android.presplash.filename = %(source.dir)s/assets/splash.jpg

# Gradle相关配置
android.gradle_dependencies = 
android.gradle_repositories =

# 构建选项
buildozer.warn_on_root = 0

# 指定主应用程序
source.main = main.py

# 使用p4a
p4a.branch = master

# 指定使用PyJNIus或否
android.enable_androidx = True

# 指定服务
services = SmartQAService:service.py

# 允许应用使用音频焦点
android.manifest.activity.config = ["android:screenOrientation='portrait'"]
android.manifest.receivers = ["com.smartqa.receivers.BootReceiver:android.intent.action.BOOT_COMPLETED"]

# 自动备份配置
android.backup_rules = %(source.dir)s/backup_rules.xml

# 允许混合Web内容
android.allow_mixed_content = True 