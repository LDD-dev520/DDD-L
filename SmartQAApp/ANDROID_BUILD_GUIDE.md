# SmartQA银行助手 - Android构建完整指南

本指南提供了构建SmartQA银行助手Android APK的详细步骤，包括解决常见问题的方法。

## 1. 最近解决的问题

### 1.1 重复配置选项

在`buildozer.spec`文件中，`source.include_patterns`选项出现了两次，已修复并合并为一个选项。

### 1.2 Python 3.12中的distutils缺失

Python 3.12已移除`distutils`模块，而buildozer依赖此模块。我们通过以下方式解决：

- 修改`buildozer.spec`指定使用Python 3.10
- 提供Docker构建脚本以避免环境问题

## 2. 构建APK的三种方法

### 2.1 方法A: 使用Docker（推荐）

这是最简单可靠的方法，避免环境配置问题：

1. 在WSL中安装Docker:
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io
   sudo service docker start
   ```

2. 使用提供的脚本构建:
   ```bash
   chmod +x docker_build.sh
   ./docker_build.sh
   ```
   
3. 按提示选择构建完整版或演示版

### 2.2 方法B: 在WSL中配置Python 3.10环境

1. 安装Python 3.10:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.10 python3.10-dev python3.10-venv
   ```

2. 创建虚拟环境:
   ```bash
   python3.10 -m venv ~/buildozer-env
   source ~/buildozer-env/bin/activate
   ```

3. 安装buildozer:
   ```bash
   pip install buildozer
   ```

4. 构建APK:
   ```bash
   cd ~/SmartQAApp
   buildozer -v android debug
   ```

### 2.3 方法C: 安装setuptools来提供distutils

如果您想在Python 3.12中构建:

```bash
sudo apt-get update
sudo apt-get install python3-setuptools
pip3 install --user setuptools
```

然后尝试正常构建:

```bash
buildozer -v android debug
```

## 3. 优化的图片资源

我们已优化项目中的图片资源:

- **图标**: `assets/icon.png` (25.6KB, 144x144像素)
- **启动画面**: `assets/splash.jpg` (26.9KB, 480x270像素)

这些文件已从原始大小减少了99.4%，确保APK大小合理。

## 4. 构建不同版本

### 完整版

包含所有功能，包括智能问答、语音识别等:

```bash
buildozer -v android debug
```

### 演示版

功能较少但构建要求更低:

```bash
buildozer -v -f -r -c -k demo_app.py android debug
```

## 5. 故障排除

### 构建日志

检查构建日志以获取详细错误信息:

```bash
cat ~/.buildozer/logs/buildozer.log
```

### 常见错误

1. **缺少依赖**:
   ```bash
   sudo apt-get install -y python3-pip build-essential git python3-dev \
       libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
       libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} \
       gstreamer1.0-{tools,alsa} libfreetype6-dev liblzma-dev \
       libsqlite3-dev libpq-dev libcurl4-openssl-dev openjdk-8-jdk \
       autoconf automake libtool libltdl-dev
   ```

2. **JAVA_HOME未设置**:
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
   ```

3. **buildozer缓存问题**:
   ```bash
   buildozer -v clean
   ```

## 6. 安装APK到设备

1. 通过USB传输APK或使用ADB:
   ```bash
   adb install -r bin/smartqa-0.1-debug.apk
   ```

2. 或复制到Windows并通过文件管理器安装:
   ```bash
   cp bin/*.apk /mnt/c/Users/YourUsername/Desktop/
   ```

## 7. 后续开发

- 测试不同Android设备上的兼容性
- 关注权限请求是否正常运行
- 检查语音识别功能在Android上的表现

我们建议首先尝试使用Docker构建方法，因为它提供了最一致的环境，避免了大多数依赖问题。 