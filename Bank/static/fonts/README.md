# 阿里巴巴iconfont字体文件

## 解决图标显示乱码问题

当前界面中发送、语音、提示按键图标显示乱码，需要下载正确的ttf字体文件。

## 下载步骤

1. 访问阿里巴巴iconfont官网 https://www.iconfont.cn/
2. 登录账号
3. 创建项目，添加图标到项目
4. 下载至本地（推荐选择"Font class"方式）
5. 解压下载的压缩包
6. 将解压后的文件中的iconfont.ttf文件复制到当前目录

## 文件说明

本项目需要使用以下图标：
- icon-history (历史记录)
- icon-back (返回)
- icon-mic (麦克风)
- icon-send (发送)
- icon-clear (清空)
- icon-keyboard (键盘)
- icon-ask (提问)
- icon-voice (语音播报)
- icon-copy (复制)
- icon-share (分享)
- icon-user (用户)
- icon-ai (AI助手)
- icon-star (收藏)
- icon-delete (删除)
- icon-right (右箭头)

请确保下载的ttf文件包含上述图标。

## 语音播报问题解决

如果项目无法正常播放语音，可能是因为在浏览器环境中，语音合成服务没有正确初始化。项目中的语音播报功能实现主要在以下文件：

1. utils/text-to-speech.js - 语音合成工具类
2. utils/speech-recognition.js - 语音识别工具类
3. main.js - 全局混入语音相关方法

请确保相关文件已正确配置，并在真机环境中测试，因为浏览器环境对某些API的支持有限。 