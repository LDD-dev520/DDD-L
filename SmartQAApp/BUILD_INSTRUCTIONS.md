# SmartQA银行助手 - APK构建说明

## 配置文件修复

我们已经修复了以下问题：

1. 修正了`buildozer.spec`文件中的重复选项：
   - 合并了两处`source.include_patterns`选项
   - 现在包含：`resources/*,data/*,assets/*,fonts/*,*.py`

2. 更新了`buildozer.demo.spec`文件中的图标引用：
   - 从`icon.jpg`更正为`icon.png`

3. 确认图片文件已正确优化：
   - 图标：`assets/icon.png`（25.6KB）
   - 启动画面：`assets/splash.jpg`（26.9KB）

## 构建APK的步骤

现在您可以按照以下步骤构建APK：

### 在WSL（Ubuntu）中构建

1. 打开WSL终端：
   ```
   wsl
   ```

2. 进入项目目录（假设已复制到WSL中）：
   ```bash
   cd ~/SmartQAApp
   ```

3. 构建APK：
   ```bash
   buildozer -v android debug
   ```

### 构建演示版APK

如果您想构建功能较少但构建更简单的演示版：

```bash
buildozer -v -f -r -c -k demo_app.py android debug
```

## 常见问题排查

如果出现构建错误：

1. 确保WSL中已安装所需的依赖项：
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

2. 检查buildozer日志文件：
   ```bash
   cat ~/.buildozer/logs/buildozer.log
   ```

3. 按需重新安装buildozer：
   ```bash
   pip3 install --user --upgrade buildozer
   ```

## APK安装

构建完成后：

1. APK文件位于`bin`目录
2. 通过USB或网络传输到Android设备
3. 在设备上安装APK（需要允许"未知来源"的应用）

## 图片优化说明

已优化的图片文件非常适合APK构建：
- 图标：从4.3MB缩小到25.6KB（减少99.4%）
- 启动画面：从4.7MB缩小到26.9KB（减少99.4%）

这将使APK文件大小保持在合理范围，并提高应用的启动速度。 