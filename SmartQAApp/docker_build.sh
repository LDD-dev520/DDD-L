#!/bin/bash
# Docker构建脚本 - 使用Docker容器构建Android APK

# 确保Docker已安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    echo "在Ubuntu/WSL中运行: sudo apt-get update && sudo apt-get install docker.io"
    exit 1
fi

# 确保Docker服务正在运行
if ! docker info &> /dev/null; then
    echo "启动Docker服务..."
    sudo service docker start
fi

# 确认当前目录是否包含buildozer.spec文件
if [ ! -f "buildozer.spec" ]; then
    echo "错误: 未找到buildozer.spec文件"
    echo "请确保在项目根目录中运行此脚本"
    exit 1
fi

# 询问是否构建完整版还是演示版
echo "===== SmartQA银行助手APK构建 ====="
echo "请选择要构建的版本:"
echo "1) 完整版 (使用buildozer.spec)"
echo "2) 演示版 (使用buildozer.demo.spec)"
read -p "请输入选择 [1/2]: " version_choice

# 准备构建命令
if [ "$version_choice" = "1" ]; then
    echo "将构建完整版APK..."
    BUILD_CMD="buildozer android debug"
else
    echo "将构建演示版APK..."
    BUILD_CMD="buildozer -v -f -r -c -k -f -f demo_app.py android debug"
fi

# 拉取最新的kivy/buildozer Docker镜像
echo "拉取最新的kivy/buildozer Docker镜像..."
docker pull kivy/buildozer

# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)

# 运行Docker容器进行构建
echo "开始构建APK..."
docker run --volume "$CURRENT_DIR":/home/user/hostcwd kivy/buildozer sh -c "cd /home/user/hostcwd && $BUILD_CMD"

# 检查构建结果
if [ -d "bin" ] && [ "$(ls -A bin)" ]; then
    echo "===== 构建成功! ====="
    echo "APK文件位于bin目录中:"
    ls -la bin/*.apk
    echo ""
    echo "使用以下命令将APK复制到您的计算机:"
    echo "cp bin/*.apk /mnt/c/Users/YourUsername/Desktop/"
else
    echo "===== 构建可能失败 ====="
    echo "未在bin目录中找到APK文件"
    echo "请检查构建日志以获取详细信息"
fi

echo "构建过程完成" 