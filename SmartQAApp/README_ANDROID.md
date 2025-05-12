# SmartQA银行助手 - Android打包指南

本文档介绍如何将SmartQA银行助手应用打包为Android应用并安装到手机上。

## 1. 环境准备

### 1.1 安装必要的软件

首先，需要安装以下软件：

- Python 3.7+ (推荐使用3.8)
- Java JDK 8
- Android SDK
- Android NDK
- Gradle
- Buildozer

### 1.2 在Windows上安装Buildozer

Buildozer主要设计用于在Linux上运行，但你可以通过WSL (Windows Subsystem for Linux) 或者使用虚拟机来在Windows上使用。

在Linux/WSL上安装Buildozer:

```bash
pip install buildozer
```

### 1.3 安装依赖

在Ubuntu/WSL中安装Buildozer的依赖项：

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

## 2. 项目配置

### 2.1 Buildozer配置文件

项目中已经包含了一个`buildozer.spec`文件，该文件定义了应用程序的配置信息，包括应用名称、包名、所需的权限等。

你可以根据需要修改以下参数：

- title: 应用名称
- package.name: 应用包名
- version: 应用版本
- requirements: 应用依赖的Python包
- android.permissions: 应用需要的权限

### 2.2 准备应用图标和启动画面

在`buildozer.spec`文件中，取消注释以下行并指定你的图标和启动画面：

```
android.icon.filename = %(source.dir)s/assets/icon.png
android.presplash.filename = %(source.dir)s/assets/splash.png
```

确保`assets`目录中包含名为`icon.png`和`splash.png`的文件，分别作为应用图标和启动画面。

## 3. 构建Android应用

### 3.1 清理构建环境（可选）

如果你之前已经构建过，可以清理旧的构建文件：

```bash
buildozer android clean
```

### 3.2 构建Debug版本

构建用于测试的Debug版本：

```bash
buildozer android debug
```

### 3.3 构建Release版本

构建用于发布的Release版本：

```bash
buildozer android release
```

## 4. 安装到设备

### 4.1 通过ADB安装

确保你的手机已经连接到电脑，并且开启了USB调试模式：

```bash
adb install -r bin/smartqa-0.1-debug.apk
```

### 4.2 直接安装

你也可以将APK文件复制到手机上，然后在手机上点击安装。APK文件位于项目的`bin`目录下。

## 5. 发布应用

### 5.1 签名APK

构建Release版本后，需要对APK进行签名：

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/smartqa-0.1-release-unsigned.apk alias_name
```

### 5.2 优化APK

使用zipalign优化APK：

```bash
zipalign -v 4 bin/smartqa-0.1-release-unsigned.apk bin/smartqa-0.1-release.apk
```

### 5.3 上传到应用商店

现在你可以将签名后的APK上传到Google Play Store或其他Android应用商店。

## 6. 常见问题

### 6.1 构建失败

如果构建过程中遇到问题，可以尝试：

1. 查看`buildozer.log`文件以获取详细的错误信息
2. 确保所有依赖项都已正确安装
3. 尝试清理构建环境：`buildozer android clean`
4. 检查网络连接，因为构建过程需要下载一些依赖项

### 6.2 无法导入模块

如果应用在运行时报告无法导入某些模块，请检查：

1. `buildozer.spec`文件中的`requirements`部分是否包含所有必要的依赖
2. 确保依赖的版本是兼容的

### 6.3 权限问题

如果应用无法访问麦克风或存储，请检查：

1. `buildozer.spec`文件中的`android.permissions`部分是否包含必要的权限
2. 应用在运行时是否正确请求了这些权限

## 7. 后续维护

### 7.1 更新应用

修改代码后，只需重新运行构建命令即可生成新版本的APK：

```bash
buildozer android debug
```

### 7.2 版本管理

更新应用时，请记得修改`buildozer.spec`文件中的`version`字段，以便用户能够识别新版本。

---

祝你构建成功！如有任何问题，请联系开发团队。 