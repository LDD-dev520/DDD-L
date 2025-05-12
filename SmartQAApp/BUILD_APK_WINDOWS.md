# Windows环境下构建Android APK的详细步骤

本文档提供了在Windows系统上构建SmartQA银行助手Android APK的详细步骤。

## 准备工作

1. **安装WSL (Windows Subsystem for Linux)**

   在管理员权限的PowerShell中运行：
   ```powershell
   wsl --install
   ```
   
   安装完成后重启计算机，并按照提示设置用户名和密码。

2. **在WSL中安装必要的软件**

   打开WSL终端并运行以下命令：
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y python3-pip build-essential git python3-dev \
       libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
       libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} \
       gstreamer1.0-{tools,alsa} libfreetype6-dev liblzma-dev \
       libsqlite3-dev libpq-dev libcurl4-openssl-dev openjdk-8-jdk \
       autoconf automake libtool libltdl-dev
   ```

3. **安装Buildozer**

   ```bash
   pip3 install --user buildozer
   ```

4. **安装Android开发工具**

   ```bash
   export PATH=$PATH:~/.local/bin
   buildozer android init
   ```

## 构建步骤

1. **将项目复制到WSL**

   在Windows命令提示符或PowerShell中运行：
   ```powershell
   xcopy /E /H /Y F:\AI\SmartQAApp \\wsl$\Ubuntu\home\用户名\SmartQAApp
   ```
   请将"用户名"替换为您的WSL用户名。

2. **在WSL中构建APK**

   打开WSL终端并运行：
   ```bash
   cd ~/SmartQAApp
   buildozer -v android debug
   ```
   
   这个命令将开始构建过程，可能需要一些时间。首次运行时，Buildozer会下载并安装Android SDK和NDK。

3. **获取构建结果**

   构建完成后，APK文件将位于`bin`目录中：
   ```bash
   ls -la ~/SmartQAApp/bin
   ```
   
   您可以通过Windows资源管理器访问这个文件：
   ```
   \\wsl$\Ubuntu\home\用户名\SmartQAApp\bin\
   ```

## 简化方法：使用演示版

如果完整版应用构建过程太复杂，您可以尝试构建演示版：

1. **使用演示配置**

   在WSL终端中：
   ```bash
   cd ~/SmartQAApp
   buildozer -v -f -r -c -k -f -f demo_app.py android debug
   ```

2. **直接使用在线构建服务**

   对于最简单的方法，可以使用在线构建服务：
   
   1. 访问 https://buildozer.app/
   2. 上传项目文件
   3. 选择 `buildozer.demo.spec` 配置文件
   4. 点击"构建"按钮
   5. 等待构建完成并下载APK

## 在Android设备上安装

1. 将APK文件传输到您的Android设备（通过USB、电子邮件或云存储）
2. 在设备上找到并点击APK文件开始安装
3. 允许来自未知来源的安装（如果出现提示）
4. 按照屏幕上的指示完成安装

## 故障排除

### 构建失败

- 检查您的网络连接，构建过程需要下载多个组件
- 确保您拥有足够的磁盘空间（至少需要10GB）
- 查看`~/.buildozer/logs/`中的日志文件获取详细错误信息

### 依赖缺失

如果遇到缺少依赖的错误，请尝试手动安装：
```bash
pip3 install --user cython==0.29.33 pillow
```

### WSL中无法安装软件包

如果在WSL中遇到"无法获得锁"的错误，请尝试：
```bash
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock
sudo dpkg --configure -a
```

## 附加资源

- 官方Buildozer文档：https://buildozer.readthedocs.io/
- Kivy文档：https://kivy.org/doc/stable/
- Android开发者指南：https://developer.android.com/guide 