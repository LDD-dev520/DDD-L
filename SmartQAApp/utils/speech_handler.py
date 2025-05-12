#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语音处理模块
实现语音识别和语音合成功能
"""

import os
import time
import tempfile
import threading
import json
import requests
import importlib
import sys
from gtts import gTTS
import speech_recognition as sr
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.clock import Clock  # 添加Clock导入用于延迟操作

# 打印当前 Python 路径信息
Logger.info(f"Python 路径: {sys.path}")

# 尝试导入pyttsx3作为备用TTS引擎
try:
    import pyttsx3
    HAS_PYTTSX3 = True
    Logger.info("成功导入 pyttsx3")
except ImportError:
    HAS_PYTTSX3 = False
    Logger.warning("无法导入 pyttsx3")

# 全局变量，用于存储 AipSpeech 类
AipSpeech = None
HAS_BAIDU_API = False

# 尝试导入百度语音识别所需包
try:
    # 确保百度AI平台包已安装
    from aip import AipSpeech
    HAS_BAIDU_API = True
    Logger.info("成功导入百度 AipSpeech")
except ImportError:
    HAS_BAIDU_API = False
    Logger.warning("无法导入百度 AipSpeech，尝试使用 pip install baidu-aip 安装")
    # 尝试自动安装
    try:
        Logger.info("尝试自动安装 baidu-aip...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "baidu-aip"])
        # 安装后重新导入
        from aip import AipSpeech
        HAS_BAIDU_API = True
        Logger.info("成功安装并导入百度 AipSpeech")
    except Exception as e:
        Logger.error(f"自动安装 baidu-aip 失败: {e}")


class SpeechHandler:
    """语音处理类"""
    
    def __init__(self):
        """初始化"""
        # 确保 AipSpeech 是全局变量
        global AipSpeech, HAS_BAIDU_API
        
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.recording = False
        self.audio = None
        self.voice_output_enabled = True
        self.voice_recognition_enabled = True
        self.current_sound = None
        self.is_speaking = False  # 表示当前是否正在播放语音
        self.auto_play = True  # 是否自动播放回答语音
        self.delayed_speak_event = None  # 新增：用于存储延迟播放的事件引用
        self.delayed_speak_text = None  # 新增：存储即将播放的文本内容
        
        # 百度语音API设置 - 直接硬编码，避免环境变量加载问题
        try:
            # 尝试从环境变量加载
            self.baidu_app_id = os.environ.get('BAIDU_APP_ID', '')
            self.baidu_api_key = os.environ.get('BAIDU_API_KEY', '')
            self.baidu_secret_key = os.environ.get('BAIDU_SECRET_KEY', '')
            
            # 如果环境变量为空，直接使用硬编码的值（从.env文件内容获取）
            if not self.baidu_app_id or not self.baidu_api_key or not self.baidu_secret_key:
                Logger.warning("环境变量中未找到百度API设置，使用硬编码值")
                self.baidu_app_id = "118495094"
                self.baidu_api_key = "DJfifGIeUTbjbzsAzCgzlQqP" 
                self.baidu_secret_key = "0KdfJO3DJgOyMgXojwfXM1OOBOxIBSrF"
            
            # 百度语音识别参数
            try:
                self.baidu_speech_model = int(os.environ.get('BAIDU_SPEECH_MODEL', '1537'))
                self.baidu_speech_quality = int(os.environ.get('BAIDU_SPEECH_QUALITY', '4'))
            except ValueError:
                # 转换失败时使用默认值
                self.baidu_speech_model = 1537  # 普通话
                self.baidu_speech_quality = 4   # 最高质量
            
            # 输出环境变量信息
            Logger.info(f"百度API设置: APP_ID='{self.baidu_app_id}', API_KEY='{self.baidu_api_key[:4]}...'")
            Logger.info(f"百度语音识别参数: 模型ID={self.baidu_speech_model}, 质量级别={self.baidu_speech_quality}")
        except Exception as e:
            import traceback
            Logger.error(f"加载百度API设置出错: {e}")
            Logger.error(traceback.format_exc())
            # 设置默认值
            self.baidu_app_id = "118495094"
            self.baidu_api_key = "DJfifGIeUTbjbzsAzCgzlQqP" 
            self.baidu_secret_key = "0KdfJO3DJgOyMgXojwfXM1OOBOxIBSrF"
            self.baidu_speech_model = 1537
            self.baidu_speech_quality = 4
        
        # 初始化百度语音客户端
        self.baidu_client = None
        try:
            # 尝试强制导入百度API模块
            if not HAS_BAIDU_API or AipSpeech is None:
                Logger.warning("尝试强制导入百度API...")
                try:
                    # 安装chardet依赖
                    import subprocess
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        Logger.info("成功安装 chardet 依赖")
                    except Exception as e:
                        Logger.warning(f"安装 chardet 失败，可能已安装: {e}")
                    
                    # 先确保baidu-aip已安装
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "baidu-aip"], 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    Logger.info("成功安装 baidu-aip 包")
                    
                    # 刷新导入缓存
                    if 'aip' in sys.modules:
                        del sys.modules['aip']
                    
                    # 重新导入
                    from aip import AipSpeech
                    # 更新全局变量
                    globals()['AipSpeech'] = AipSpeech
                    HAS_BAIDU_API = True
                    Logger.info("成功重新导入 AipSpeech")
                except Exception as e:
                    Logger.error(f"强制导入百度API失败: {e}")
                    import traceback
                    Logger.error(traceback.format_exc())
            
            # 检查是否已导入百度API模块
            if AipSpeech is not None:
                Logger.info("已导入百度语音API模块")
                
                # 验证API参数有效性
                if (self.baidu_app_id and self.baidu_api_key and self.baidu_secret_key and 
                    len(self.baidu_api_key) > 10 and len(self.baidu_secret_key) > 10):
                    
                    Logger.info("尝试初始化百度API客户端...")
                    # 将app_id转为字符串以确保类型兼容
                    try:
                        self.baidu_client = AipSpeech(str(self.baidu_app_id), self.baidu_api_key, self.baidu_secret_key)
                        Logger.info("百度语音API初始化成功")
                        
                        # 验证百度API连接
                        try:
                            # 简单测试API是否正常工作
                            test_text = "测试"
                            test_result = self.baidu_client.synthesis(test_text, 'zh', 1, {'vol': 5})
                            if not isinstance(test_result, dict):
                                Logger.info("百度API连接测试成功")
                            else:
                                error_msg = test_result.get('err_msg', '未知错误') if test_result else '空结果'
                                Logger.warning(f"百度API连接测试失败: {error_msg}")
                        except Exception as e:
                            Logger.warning(f"百度API连接测试失败: {e}")
                    except Exception as e:
                        Logger.error(f"百度语音客户端初始化失败: {e}")
                        import traceback
                        Logger.error(traceback.format_exc())
                else:
                    Logger.warning(f"百度API凭证不完整或无效，无法初始化客户端")
            else:
                Logger.warning("尝试所有方法后，依然无法导入AipSpeech模块")
        except Exception as e:
            import traceback
            Logger.error(f"初始化百度语音客户端时出错: {e}")
            Logger.error(traceback.format_exc())
            
        # 立即初始化语音资源
        self.initialize()
    
    def initialize(self):
        """初始化资源"""
        # 创建资源目录
        self.resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        if not os.path.exists(self.resource_dir):
            os.makedirs(self.resource_dir)
        
        # 初始化语音识别器
        try:
            self.recognizer = sr.Recognizer()
            
            # 调整识别器参数提高识别准确性
            self.recognizer.energy_threshold = 300  # 提高能量阈值
            self.recognizer.dynamic_energy_threshold = True  # 使用动态能量阈值
            self.recognizer.pause_threshold = 0.8  # 缩短暂停阈值
            self.recognizer.phrase_threshold = 0.2  # 降低短语阈值
            
            # 尝试获取默认麦克风
            try:
                self.microphone = sr.Microphone()
                # 检测是否有活跃的麦克风
                available_mics = sr.Microphone.list_microphone_names()
                Logger.info(f"检测到{len(available_mics)}个麦克风: {available_mics}")
                
                # 调整识别器参数
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                Logger.info("语音识别器初始化成功")
            except Exception as e:
                Logger.error(f"麦克风初始化失败: {e}")
                
                # 尝试使用特定设备索引
                try:
                    # 获取所有可用设备
                    devices = sr.Microphone.list_microphone_names()
                    Logger.info(f"尝试使用第一个可用麦克风: {devices[0]}")
                    self.microphone = sr.Microphone(device_index=0) 
                    
                    # 调整识别器参数
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        
                    Logger.info("使用备用麦克风初始化成功")
                except Exception as e2:
                    Logger.error(f"备用麦克风初始化失败: {e2}")
                    self.microphone = None
        except Exception as e:
            Logger.error(f"语音识别器初始化失败: {e}")
            self.recognizer = None
            self.microphone = None
        
        # 初始化TTS引擎
        if HAS_PYTTSX3:
            try:
                self.tts_engine = pyttsx3.init()
                # 设置中文语音
                voices = self.tts_engine.getProperty('voices')
                # 输出所有语音
                for i, voice in enumerate(voices):
                    Logger.info(f"语音引擎 {i}: {voice.name} ({voice.id})")
                
                # 尝试找到中文语音
                chinese_voice_found = False
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower() or 'zh' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        Logger.info(f"已选择中文语音: {voice.name}")
                        chinese_voice_found = True
                        break
                
                if not chinese_voice_found and voices:
                    # 如果没有找到中文语音，使用第一个可用的语音
                    self.tts_engine.setProperty('voice', voices[0].id)
                    Logger.info(f"未找到中文语音，使用默认语音: {voices[0].name}")
                
                # 设置语速和音量
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                Logger.info("本地TTS引擎初始化成功")
            except Exception as e:
                Logger.error(f"本地TTS引擎初始化失败: {e}")
                self.tts_engine = None
    
    def start_recording(self):
        """开始录音"""
        # 取消之前计划的延迟播放
        self.cancel_delayed_speak()
        
        # 停止当前正在播放的语音
        self.stop_speaking()
        
        if not self.recognizer or not self.microphone or not self.voice_recognition_enabled:
            Logger.warning("语音识别不可用或已禁用")
            return False
        
        if self.recording:
            Logger.warning("已经在录音中")
            return False
        
        self.recording = True
        
        # 在线程中启动录音
        threading.Thread(target=self._record_audio).start()
        
        Logger.info("开始录音")
        return True
    
    def _record_audio(self):
        """录制音频"""
        try:
            with self.microphone as source:
                Logger.info("请说话...")
                # 调整麦克风参数
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 增加超时时间，避免用户未及时说话导致录音结束
                # 同时增加短语阈值，使系统更容易识别句子结束
                self.audio = self.recognizer.listen(
                    source, 
                    timeout=8.0,  # 更长的超时时间
                    phrase_time_limit=15.0,  # 更长的短语时间限制
                    snowboy_configuration=None
                )
                Logger.info("录音完成")
                
                # 输出录音信息
                if self.audio:
                    Logger.info(f"录音格式: {self.audio.sample_rate}Hz, {self.audio.sample_width}字节宽度")
                    # 获取音频字节数据大小
                    wav_data = self.audio.get_wav_data()
                    Logger.info(f"录音数据大小: {len(wav_data)} 字节")
                    # 检查音频是否为静音
                    if len(wav_data) < 1000:
                        Logger.warning("警告: 录音数据过小，可能为静音")
                else:
                    Logger.error("录音对象为空")
        except Exception as e:
            import traceback
            Logger.error(f"录音失败: {e}")
            Logger.error(f"错误详情: {traceback.format_exc()}")
            self.audio = None
        finally:
            self.recording = False
    
    def stop_recording_and_recognize(self):
        """停止录音并识别语音"""
        # 确保 AipSpeech 是全局变量
        global AipSpeech
        
        if not self.audio:
            Logger.warning("没有录制的音频")
            return None
        
        try:
            # 尝试使用多种语音识别服务
            recognized_text = None
            
            # 输出调试信息
            Logger.info(f"语音识别开始 - 百度客户端状态: {self.baidu_client is not None}, AipSpeech状态: {AipSpeech is not None}")
            
            # 如果百度客户端未初始化，尝试重新初始化
            if not self.baidu_client:
                Logger.warning("检测到百度客户端未初始化，尝试重新初始化...")
                try:
                    # 确保 AipSpeech 已经被导入
                    if AipSpeech is None:
                        Logger.warning("尝试重新导入 AipSpeech...")
                        try:
                            from aip import AipSpeech
                            globals()['AipSpeech'] = AipSpeech
                            Logger.info("成功导入 AipSpeech")
                        except ImportError:
                            Logger.error("无法导入 AipSpeech 模块")
                            return None
                    
                    # 现在尝试初始化客户端
                    self.baidu_client = AipSpeech(str(self.baidu_app_id), self.baidu_api_key, self.baidu_secret_key)
                    Logger.info("百度语音API重新初始化成功")
                except Exception as e:
                    Logger.error(f"百度语音API重新初始化失败: {e}")
            
            # 首先尝试百度语音识别（国内访问更快）
            if self.baidu_client:
                try:
                    Logger.info("使用百度语音识别...")
                    # 将录音数据保存为临时WAV文件
                    temp_wav = os.path.join(self.resource_dir, 'temp_speech.wav')
                    with open(temp_wav, "wb") as f:
                        f.write(self.audio.get_wav_data())
                    
                    # 输出临时文件信息
                    if os.path.exists(temp_wav):
                        file_size = os.path.getsize(temp_wav)
                        Logger.info(f"临时音频文件大小: {file_size} 字节")
                        
                        # 如果文件太小，可能是静音
                        if file_size < 1000:
                            Logger.warning("音频文件太小，可能是静音录制")
                    else:
                        Logger.error("临时音频文件创建失败")
                    
                    # 读取文件并发送至百度API
                    with open(temp_wav, 'rb') as f:
                        audio_data = f.read()
                    
                    audio_data_len = len(audio_data)
                    Logger.info(f"发送至百度API的音频数据大小: {audio_data_len} 字节")
                    
                    # 如果音频数据太小，可能无法识别
                    if audio_data_len < 2000:
                        Logger.warning("音频数据过小，可能无法识别")
                    
                    # 百度语音识别参数
                    options = {
                        'dev_pid': self.baidu_speech_model,
                        'format': 'pcm',  # 音频格式
                        'rate': 16000,    # 采样率
                        'channel': 1,     # 声道数
                        'cuid': 'SmartQAApp',  # 用户标识，可帮助定位问题
                        'speech_quality': self.baidu_speech_quality,   # 语音识别质量等级，4表示最高质量
                    }
                    
                    # 尝试不同的格式和参数组合
                    formats_to_try = ['pcm', 'wav']
                    for audio_format in formats_to_try:
                        try:
                            Logger.info(f"尝试使用 {audio_format} 格式进行识别...")
                            options['format'] = audio_format
                            
                            # 发送识别请求
                            result = self.baidu_client.asr(audio_data, audio_format, 16000, options)
                            
                            # 输出完整的API返回结果以便调试
                            Logger.info(f"百度API返回结果: {result}")
                            
                            if result and 'err_no' in result and result['err_no'] == 0 and 'result' in result and result['result']:
                                recognized_text = result['result'][0]
                                Logger.info(f"百度语音识别结果: {recognized_text}")
                                break  # 成功识别，跳出循环
                            else:
                                error_code = result.get('err_no', 'unknown') if isinstance(result, dict) else 'non-dict'
                                error_msg = result.get('err_msg', '未知错误') if isinstance(result, dict) else '返回格式错误'
                                Logger.warning(f"使用 {audio_format} 格式识别失败: 错误码={error_code}, 错误信息={error_msg}")
                        except Exception as e:
                            import traceback
                            Logger.warning(f"使用 {audio_format} 格式识别出错: {e}")
                            Logger.warning(traceback.format_exc())
                    
                    # 如果所有格式尝试都失败
                    if not recognized_text:
                        Logger.error("所有百度语音格式尝试均失败")
                except Exception as e:
                    import traceback
                    Logger.error(f"百度语音识别失败: {e}")
                    Logger.error(f"错误详情: {traceback.format_exc()}")
            else:
                Logger.warning("百度语音客户端未初始化，跳过百度语音识别")
            
            # 然后尝试Google语音识别
            if not recognized_text:
                try:
                    Logger.info("使用Google语音识别...")
                    recognized_text = self.recognizer.recognize_google(self.audio, language="zh-CN")
                    Logger.info(f"Google识别结果: {recognized_text}")
                except Exception as e:
                    Logger.error(f"Google语音识别失败: {e}")
            
            if not recognized_text:
                Logger.warning("所有语音识别服务均失败")
                return None
                
            return recognized_text
        except Exception as e:
            import traceback
            Logger.error(f"语音识别过程失败: {e}")
            Logger.error(f"错误详情: {traceback.format_exc()}")
            return None
        finally:
            self.audio = None
    
    def speak(self, text, delay=0):
        """文本转语音
        
        Args:
            text: 要播放的文本
            delay: 延迟播放的时间（秒）
        """
        if not self.voice_output_enabled:
            Logger.info("语音输出已禁用")
            return False
        
        if not text:
            Logger.warning("没有要播放的文本")
            return False
        
        # 取消之前计划的延迟播放
        self.cancel_delayed_speak()
        
        # 停止当前正在播放的语音
        self.stop_speaking()
        
        # 如果需要延迟播放
        if delay > 0:
            Logger.info(f"计划延迟{delay}秒后播放语音")
            self.delayed_speak_text = text
            # 使用Clock.schedule_once来延迟执行播放
            self.delayed_speak_event = Clock.schedule_once(
                lambda dt: self._actual_speak(text), delay
            )
            return True
        else:
            # 立即播放
            return self._actual_speak(text)
    
    def cancel_delayed_speak(self):
        """取消计划的延迟语音播放"""
        if self.delayed_speak_event:
            Logger.info("取消延迟播放语音")
            self.delayed_speak_event.cancel()
            self.delayed_speak_event = None
            self.delayed_speak_text = None
    
    def _actual_speak(self, text):
        """实际执行语音播放功能"""
        Logger.info(f"开始合成语音: {text[:30]}...")
        self.is_speaking = True  # 设置状态为正在播放
        threading.Thread(target=self._synthesize_and_play, args=(text,)).start()
        return True
    
    def _synthesize_and_play(self, text):
        """合成并播放语音"""
        try:
            # 优先使用本地TTS（更快速）
            temp_file = os.path.join(self.resource_dir, 'temp_speech.wav')
            
            # 首先尝试使用本地TTS引擎
            if self.tts_engine:
                try:
                    self.tts_engine.save_to_file(text, temp_file)
                    self.tts_engine.runAndWait()
                    Logger.info("使用本地TTS生成语音成功")
                except Exception as e:
                    Logger.error(f"本地TTS失败: {e}")
                    temp_file = None
            
            # 如果本地TTS失败，尝试百度TTS
            if (not temp_file or not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0) and self.baidu_client:
                try:
                    temp_file = os.path.join(self.resource_dir, 'temp_speech.mp3')
                    result = self.baidu_client.synthesis(text, 'zh', 1, {
                        'vol': 5,  # 音量
                        'spd': 5,  # 语速
                        'pit': 5,  # 音调
                        'per': 0,  # 发音人，0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
                    })
                    
                    # 如果结果是字典类型，则出错
                    if not isinstance(result, dict):
                        with open(temp_file, 'wb') as f:
                            f.write(result)
                        Logger.info("使用百度TTS生成语音成功")
                    else:
                        Logger.error(f"百度TTS错误: {result}")
                        temp_file = None
                except Exception as e:
                    Logger.error(f"百度TTS失败: {e}")
                    temp_file = None
            
            # 如果前两种方法都失败，使用Google TTS
            if not temp_file or not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                try:
                    temp_file = os.path.join(self.resource_dir, 'temp_speech.mp3')
                    tts = gTTS(text=text, lang='zh-cn', slow=False)
                    tts.save(temp_file)
                    Logger.info("使用Google TTS生成语音成功")
                except Exception as e:
                    Logger.error(f"Google TTS失败: {e}")
                    self.is_speaking = False
                    return
            
            # 播放语音
            if temp_file and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                self.current_sound = SoundLoader.load(temp_file)
                if self.current_sound:
                    # 绑定语音播放完成事件
                    self.current_sound.bind(on_stop=self._on_sound_finished)
                    self.current_sound.play()
                    Logger.info("开始播放语音")
                else:
                    Logger.error("语音文件加载失败")
                    self.is_speaking = False
            else:
                Logger.error(f"语音文件不存在或为空: {temp_file}")
                self.is_speaking = False
        except Exception as e:
            Logger.error(f"语音合成或播放失败: {e}")
            self.is_speaking = False
    
    def _on_sound_finished(self, instance):
        """语音播放完成后的回调函数"""
        Logger.info("语音播放完成")
        self.is_speaking = False
        self.current_sound = None
    
    def stop_speaking(self):
        """停止语音播放"""
        # 取消延迟播放
        self.cancel_delayed_speak()
        
        # 停止当前正在播放的声音
        if self.current_sound and self.current_sound.state == 'play':
            self.current_sound.stop()
            Logger.info("已停止播放语音")
        self.is_speaking = False
        self.current_sound = None
    
    def set_voice_output_enabled(self, enabled):
        """设置语音输出是否启用"""
        self.voice_output_enabled = enabled
        Logger.info(f"语音输出已{'启用' if enabled else '禁用'}")
        if not enabled:
            self.stop_speaking()
    
    def set_voice_recognition_enabled(self, enabled):
        """设置语音识别是否启用"""
        self.voice_recognition_enabled = enabled
        Logger.info(f"语音识别已{'启用' if enabled else '禁用'}")
        if not enabled and self.recording:
            self.recording = False
    
    def set_auto_play(self, enabled):
        """设置是否自动播放语音回答"""
        self.auto_play = enabled
        Logger.info(f"自动语音播放已{'启用' if enabled else '禁用'}")
    
    def cleanup(self):
        """清理资源"""
        # 停止语音播放
        self.stop_speaking()
        
        # 清理临时文件
        temp_files = ['temp_speech.mp3', 'temp_speech.wav']
        for file in temp_files:
            path = os.path.join(self.resource_dir, file)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    Logger.info(f"已删除临时文件: {path}")
                except Exception as e:
                    Logger.warning(f"删除临时文件失败: {e}")
        
        # 清理TTS引擎
        if self.tts_engine:
            try:
                del self.tts_engine
                self.tts_engine = None
                Logger.info("已清理TTS引擎")
            except Exception as e:
                Logger.warning(f"清理TTS引擎失败: {e}") 