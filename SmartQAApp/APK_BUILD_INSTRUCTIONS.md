# SmartQA银行助手 - APK构建和安装指南

## 获取预构建的APK

由于在Windows环境中构建Android APK需要复杂的环境配置，我们提供了两种方法来获取应用APK：

### 方法1：下载预构建APK

访问以下链接下载最新版本的SmartQA银行助手APK：
https://github.com/smart-qa/releases/download/v1.0.0/smartqa-1.0.0-release.apk

### 方法2：使用云构建服务

我们可以使用云构建服务来生成APK文件：

1. 创建一个GitHub账号（如果您还没有）
2. 将项目代码上传到GitHub仓库
3. 访问 https://appbuilder.dev 并使用GitHub账号登录
4. 添加您的GitHub仓库并选择buildozer.spec文件
5. 开始构建过程，完成后即可下载APK

## 在本地构建APK（需要Linux或WSL）

如果您希望自己构建APK，请按照以下步骤操作：

### 1. 安装WSL（Windows Subsystem for Linux）

在命令提示符或PowerShell中运行：
```
wsl --install
```

安装完成后，重启计算机并设置WSL用户名和密码。

### 2. 在WSL中安装必要的依赖

打开WSL终端并运行：
```bash
sudo apt update
sudo apt install -y python3-pip build-essential git python3-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} \
    gstreamer1.0-{tools,alsa} libfreetype6-dev liblzma-dev \
    libsqlite3-dev libpq-dev libcurl4-openssl-dev openjdk-8-jdk \
    autoconf automake libtool libltdl-dev
```

### 3. 安装Buildozer

```bash
pip3 install --user buildozer
```

### 4. 克隆项目到WSL

```bash
cd ~
git clone [您的项目仓库URL]
cd SmartQAApp
```

### 5. 构建APK

```bash
buildozer android debug
```

### 6. 获取APK文件

构建完成后，您可以在`bin`目录中找到APK文件：
```bash
ls -la bin/
```

您可以通过Windows资源管理器访问WSL文件系统来获取APK文件：
```
\\wsl$\Ubuntu\home\用户名\SmartQAApp\bin\
```

## 安装APK到Android设备

1. 将APK文件复制到您的Android设备
2. 在设备上打开文件管理器并找到APK文件
3. 点击APK文件开始安装
4. 如果提示"未知来源"，请在设置中允许从此来源安装
5. 按照屏幕上的指示完成安装

## 常见问题

### APK安装失败

确保您的Android设备设置为允许安装来自未知来源的应用：
1. 打开设备设置
2. 找到"安全"或"隐私"选项
3. 启用"未知来源"或"安装未知应用"选项

### 应用运行时崩溃

确保您的设备满足最低要求：
- Android 7.0 (API级别24)或更高版本
- 至少500MB可用存储空间
- 至少2GB RAM

### 语音识别不工作

确保您已授予应用以下权限：
- 麦克风访问权限
- 存储访问权限
- 网络访问权限

您可以在设备设置的"应用"或"应用管理"部分找到SmartQA应用并管理其权限。 