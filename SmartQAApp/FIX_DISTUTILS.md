# 修复Buildozer的distutils缺失问题

## 错误分析

您遇到的错误是因为Python 3.12已经移除了`distutils`模块，但Buildozer依赖它：

```
ModuleNotFoundError: No module named 'distutils'
```

## 解决方案

### 方法1：安装setuptools（包含distutils替代品）

在WSL中运行：

```bash
sudo apt-get update
sudo apt-get install python3-setuptools
pip3 install --user setuptools
```

### 方法2：降级Python版本（推荐）

由于Python 3.12是较新版本，而许多工具还未完全兼容，建议使用Python 3.10或3.11：

```bash
# 在WSL中安装Python 3.10
sudo apt-get update
sudo apt-get install python3.10 python3.10-dev python3.10-venv

# 创建虚拟环境
python3.10 -m venv ~/buildozer-env

# 激活虚拟环境
source ~/buildozer-env/bin/activate

# 安装buildozer
pip install buildozer

# 现在在虚拟环境中构建
cd ~/SmartQAApp
buildozer -v android debug
```

### 方法3：使用Docker容器

使用预配置的Docker容器来构建：

```bash
# 在WSL中安装Docker
sudo apt-get update
sudo apt-get install docker.io

# 启动Docker服务
sudo service docker start

# 使用buildozer Docker镜像构建APK
cd ~/SmartQAApp
sudo docker run --volume "$PWD":/home/user/hostcwd kivy/buildozer android debug
```

## 修改buildozer配置（可选）

如果您希望确保与Python 3.10兼容，可以在`buildozer.spec`中指定Python版本：

```
# 修改requirements行
requirements = python3==3.10,kivy==2.3.1,...其他依赖
```

## 后续步骤

1. 选择一种解决方案并应用
2. 重新运行构建命令
3. 如果还有错误，查看详细日志：`~/.buildozer/logs/buildozer.log`

不论选择哪种方法，建议使用Python 3.10或3.11来构建，因为这些版本与大多数构建工具兼容性更好。 