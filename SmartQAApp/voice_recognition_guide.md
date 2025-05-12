# 语音识别配置指南

## 简介

本应用支持多种语音识别方式，优先使用国内服务以获得更好的体验。应用会按照以下优先级尝试不同的识别方式：

1. 百度语音识别 API（推荐，速度快、精度高、适合中国用户）
2. Google 语音识别（备选方案，需要网络连接且可能不稳定）

## 安装依赖

确保已安装所有必要的依赖：

```bash
pip install pyaudio
pip install baidu-aip
pip install SpeechRecognition
pip install pyttsx3
pip install gTTS
pip install playsound
pip install python-dotenv
```

## 配置百度语音API（强烈推荐）

1. 访问 [百度智能云](https://cloud.baidu.com/product/speech) 注册并创建语音识别应用
2. 获取 APP_ID、API_KEY 和 SECRET_KEY
3. 在项目根目录下创建或编辑 `.env` 文件，填入以下内容：

```
# 百度语音API基本配置
BAIDU_APP_ID=你的APP_ID
BAIDU_API_KEY=你的API_KEY
BAIDU_SECRET_KEY=你的SECRET_KEY

# 百度语音识别参数
BAIDU_SPEECH_MODEL=1537  # 1537=普通话, 1737=普通话远场, 1637=粤语, 1837=四川话
BAIDU_SPEECH_QUALITY=4   # 1-4，值越高质量越好但耗时更长
```

## 使用说明

### 语音识别

1. 点击应用界面中的麦克风按钮开始录音
2. 说话完毕后自动停止录音并开始识别
3. 识别结果将显示在输入框中

### 语音合成

应用也支持语音合成（文字转语音），按照以下优先级：

1. 本地 TTS 引擎（速度快）
2. 百度语音合成（如果配置了百度API）
3. Google TTS（备选方案，需要网络连接）

## 故障排除

如果遇到问题，请检查：

1. 麦克风是否正常工作并获得了应用权限
2. 网络连接是否正常（对于在线识别服务）
3. API 密钥是否正确配置
4. 查看日志文件了解详细错误信息

如果百度语音识别仍然不工作，可以尝试：

1. 确认 `.env` 文件中的百度 API 密钥是否正确
2. 检查百度智能云账户余额是否充足
3. 尝试修改 `BAIDU_SPEECH_MODEL` 和 `BAIDU_SPEECH_QUALITY` 参数
4. 重新运行程序，查看日志中百度 API 相关的错误信息

## 性能优化

1. 减少环境噪音可以提高识别准确率
2. 说话清晰且语速适中
3. 使用高质量麦克风可以提高识别效果
4. 对于较长的语音，建议分段识别，每段不超过10秒

## 关于百度语音API的详细说明

百度语音API提供了多种语言和场景的支持，在配置时可以根据需求调整以下参数：

- dev_pid (BAIDU_SPEECH_MODEL): 语言模型ID
  - 1537：普通话（默认）
  - 1737：普通话（远场）
  - 1637：粤语
  - 1837：四川话
  - 1936：普通话极速版

- 音频采样率：
  - 16000：一般场景（默认）
  - 8000：电话场景

- 识别质量 (BAIDU_SPEECH_QUALITY)：
  - 1：速度优先
  - 2：均衡
  - 3：准确率优先
  - 4：最高质量（默认）

可以在 `.env` 文件中根据需要调整这些参数以获得更好的识别效果。 