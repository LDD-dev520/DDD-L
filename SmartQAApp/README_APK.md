# SmartQA银行助手 Android APK 构建指南

## 项目概述

SmartQA银行助手是一个基于Python和Kivy的智能问答应用，现已支持打包为Android APK。本文档提供了构建和安装APK的各种方法。

## 文件清单

- **buildozer.spec**: 完整版应用的构建配置
- **buildozer.demo.spec**: 演示版应用的构建配置
- **demo_app.py**: 简化的演示版应用
- **service.py**: Android后台服务
- **receiver.py**: Android广播接收器
- **utils/android_speech_handler.py**: Android平台的语音处理
- **utils/android_audio.py**: Android平台的音频处理
- **assets/icon.png**: 应用图标
- **assets/splash.png**: 启动屏幕
- **backup_rules.xml**: Android备份规则

## 构建方法

### 方法1: 使用WSL (Windows Subsystem for Linux)

详细步骤请参考 `BUILD_APK_WINDOWS.md` 文件，主要步骤包括:

1. 安装WSL
2. 在WSL中安装依赖项
3. 安装Buildozer
4. 构建APK

### 方法2: 使用在线构建服务

参考 `APK_BUILD_INSTRUCTIONS.md` 文件中的"使用云构建服务"部分。

### 方法3: 使用演示版

如果您只想尝试基本功能，可以构建演示版:

```bash
buildozer -v -f -r -c -k -f -f demo_app.py android debug
```

## 安装到设备

1. 通过USB、电子邮件或云存储将APK文件传输到Android设备
2. 在设备上点击APK文件开始安装
3. 如果提示"未知来源"，请在设置中允许从此来源安装
4. 按照屏幕上的指示完成安装

## 应用权限

SmartQA银行助手需要以下权限:

- INTERNET - 用于连接百度语音API和其他在线服务
- RECORD_AUDIO - 用于语音识别功能
- WRITE_EXTERNAL_STORAGE - 用于保存临时音频文件

## 常见问题解答

如果您在构建或安装过程中遇到问题，请参考 `APK_BUILD_INSTRUCTIONS.md` 文件中的"常见问题"部分。

## 系统要求

- Android 7.0 (API级别24)或更高版本
- 至少500MB可用存储空间
- 至少2GB RAM

## 联系方式

如有任何问题或建议，请联系SmartQA团队。 