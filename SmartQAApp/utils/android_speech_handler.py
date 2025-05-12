#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Android平台的语音处理适配模块
集成百度语音API实现语音识别功能
"""

import os
import time
import threading
import json
import requests
import sys
from kivy.logger import Logger
from kivy.clock import Clock

# 导入Android特定模块
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission, check_permission
    from utils.android_audio import AndroidAudioHandler, AndroidAudioPlayer
    
    # Android TTS类
    Locale = autoclass('java.util.Locale')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    
    IS_ANDROID = True
    Logger.info("正在Android平台上运行语音处理模块")
except ImportError as e:
    IS_ANDROID = False
    Logger.error(f"导入Android模块失败: {e}")

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


class AndroidSpeechHandler:
    """Android平台语音处理类"""
    
    def __init__(self):
        """初始化"""
        # 确保 AipSpeech 是全局变量
        global AipSpeech, HAS_BAIDU_API
        
        self.android_audio_handler = None
        self.android_audio_player = None
        self.tts_engine = None
        self.recording = False
        self.audio_file = None
        self.voice_output_enabled = True
        self.voice_recognition_enabled = True
        self.is_speaking = False
        self.auto_play = True
        self.delayed_speak_event = None
        self.delayed_speak_text = None
        
        # 百度语音API设置
        try:
            # 尝试从环境变量加载
            self.baidu_app_id = os.environ.get('BAIDU_APP_ID', '')
            self.baidu_api_key = os.environ.get('BAIDU_API_KEY', '')
            self.baidu_secret_key = os.environ.get('BAIDU_SECRET_KEY', '')
            
            # 如果环境变量为空，直接使用硬编码的值
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
                else:
                    Logger.warning(f"百度API凭证不完整或无效，无法初始化客户端")
            else:
                Logger.warning("未找到AipSpeech模块")
        except Exception as e:
            import traceback
            Logger.error(f"初始化百度语音客户端时出错: {e}")
            Logger.error(traceback.format_exc())
        
        # 初始化Android音频处理器
        if IS_ANDROID:
            try:
                self.android_audio_handler = AndroidAudioHandler()
                self.android_audio_player = AndroidAudioPlayer()
                Logger.info("Android音频处理器初始化成功")
                
                # 初始化Android TTS
                self.init_android_tts()
            except Exception as e:
                Logger.error(f"Android音频处理器初始化失败: {e}")
        
        # 创建资源目录
        self.resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        if not os.path.exists(self.resource_dir):
            os.makedirs(self.resource_dir)
    
    def init_android_tts(self):
        """初始化Android TTS引擎"""
        if not IS_ANDROID:
            return
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            # 创建TTS实例
            self.tts_engine = TextToSpeech(activity, None)
            
            # 设置中文语言
            chinese = Locale.SIMPLIFIED_CHINESE
            result = self.tts_engine.setLanguage(chinese)
            
            if result == TextToSpeech.LANG_MISSING_DATA or result == TextToSpeech.LANG_NOT_SUPPORTED:
                Logger.warning("Android TTS不支持中文，尝试使用默认语言")
                self.tts_engine.setLanguage(Locale.getDefault())
            
            # 设置语速和音调
            self.tts_engine.setSpeechRate(1.0)
            self.tts_engine.setPitch(1.0)
            
            Logger.info("Android TTS引擎初始化成功")
        except Exception as e:
            Logger.error(f"Android TTS引擎初始化失败: {e}")
            self.tts_engine = None
    
    def start_recording(self):
        """开始录音"""
        if not IS_ANDROID or not self.android_audio_handler or not self.voice_recognition_enabled:
            Logger.warning("Android录音不可用或已禁用")
            return False
        
        if self.recording:
            Logger.warning("已经在录音中")
            return False
        
        self.recording = True
        success = self.android_audio_handler.start_recording()
        
        if success:
            Logger.info("Android录音开始")
            return True
        else:
            Logger.error("Android录音启动失败")
            self.recording = False
            return False
    
    def stop_recording_and_recognize(self):
        """停止录音并识别语音"""
        if not IS_ANDROID or not self.android_audio_handler or not self.recording:
            Logger.warning("Android录音未开始或不可用")
            return None
        
        try:
            # 停止录音
            audio_file = self.android_audio_handler.stop_recording()
            self.recording = False
            
            if not audio_file or not os.path.exists(audio_file):
                Logger.warning("录音文件为空或不存在")
                return None
            
            Logger.info(f"录音文件: {audio_file}")
            
            # 使用百度API识别语音
            recognized_text = self.recognize_with_baidu(audio_file)
            
            # 清理临时文件
            try:
                os.remove(audio_file)
                Logger.info(f"已删除临时录音文件: {audio_file}")
            except:
                pass
            
            return recognized_text
        except Exception as e:
            import traceback
            Logger.error(f"停止录音或识别失败: {e}")
            Logger.error(traceback.format_exc())
            self.recording = False
            return None
    
    def recognize_with_baidu(self, audio_file):
        """使用百度API识别语音"""
        if not self.baidu_client:
            Logger.warning("百度语音客户端未初始化")
            return None
        
        try:
            Logger.info("使用百度语音识别...")
            
            # 读取音频文件
            with open(audio_file, "rb") as f:
                audio_data = f.read()
            
            audio_data_len = len(audio_data)
            Logger.info(f"发送至百度API的音频数据大小: {audio_data_len} 字节")
            
            # 如果音频数据太小，可能无法识别
            if audio_data_len < 2000:
                Logger.warning("音频数据过小，可能无法识别")
                return None
            
            # 百度语音识别参数
            options = {
                'dev_pid': self.baidu_speech_model,
                'format': 'amr',  # Android MediaRecorder使用AMR格式
                'rate': 16000,    # 采样率
                'channel': 1,     # 声道数
                'cuid': 'SmartQAAndroid',  # 用户标识
                'speech_quality': self.baidu_speech_quality,
            }
            
            # 发送识别请求
            result = self.baidu_client.asr(audio_data, 'amr', 16000, options)
            
            # 输出完整的API返回结果以便调试
            Logger.info(f"百度API返回结果: {result}")
            
            if result and 'err_no' in result and result['err_no'] == 0 and 'result' in result and result['result']:
                recognized_text = result['result'][0]
                Logger.info(f"百度语音识别结果: {recognized_text}")
                return recognized_text
            else:
                error_code = result.get('err_no', 'unknown') if isinstance(result, dict) else 'non-dict'
                error_msg = result.get('err_msg', '未知错误') if isinstance(result, dict) else '返回格式错误'
                Logger.warning(f"语音识别失败: 错误码={error_code}, 错误信息={error_msg}")
                return None
        except Exception as e:
            import traceback
            Logger.error(f"百度语音识别失败: {e}")
            Logger.error(traceback.format_exc())
            return None
    
    def speak(self, text, delay=0):
        """文本转语音"""
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
        self.is_speaking = True
        threading.Thread(target=self._synthesize_and_play, args=(text,)).start()
        return True
    
    def _synthesize_and_play(self, text):
        """合成并播放语音"""
        try:
            if not IS_ANDROID:
                Logger.warning("不在Android平台上，无法使用Android TTS")
                self.is_speaking = False
                return
            
            # 首先尝试使用Android TTS
            if self.tts_engine:
                try:
                    # 使用Android TTS引擎合成语音
                    temp_file = os.path.join(self.resource_dir, 'temp_speech.wav')
                    
                    # 使用TextToSpeech的speak方法直接播放
                    result = self.tts_engine.speak(text, TextToSpeech.QUEUE_FLUSH, None)
                    
                    if result == TextToSpeech.SUCCESS:
                        Logger.info("Android TTS成功播放语音")
                    else:
                        Logger.error(f"Android TTS播放失败: {result}")
                        # 尝试使用百度TTS
                        self._try_baidu_tts(text)
                except Exception as e:
                    Logger.error(f"Android TTS失败: {e}")
                    # 尝试使用百度TTS
                    self._try_baidu_tts(text)
            else:
                # 如果没有Android TTS，尝试使用百度TTS
                self._try_baidu_tts(text)
                
            # 标记语音播放完成
            self.is_speaking = False
            
        except Exception as e:
            Logger.error(f"语音合成或播放失败: {e}")
            self.is_speaking = False
    
    def _try_baidu_tts(self, text):
        """尝试使用百度TTS"""
        try:
            if not self.baidu_client:
                Logger.warning("百度语音客户端未初始化，无法使用百度TTS")
                return
            
            temp_file = os.path.join(self.resource_dir, 'temp_speech.mp3')
            result = self.baidu_client.synthesis(text, 'zh', 1, {
                'vol': 5,  # 音量
                'spd': 5,  # 语速
                'pit': 5,  # 音调
                'per': 0,  # 发音人，0为女声，1为男声
            })
            
            # 如果结果是字典类型，则出错
            if not isinstance(result, dict):
                with open(temp_file, 'wb') as f:
                    f.write(result)
                Logger.info("使用百度TTS生成语音成功")
                
                # 使用Android播放器播放
                if self.android_audio_player:
                    self.android_audio_player.play(temp_file)
            else:
                Logger.error(f"百度TTS错误: {result}")
        except Exception as e:
            Logger.error(f"百度TTS失败: {e}")
    
    def stop_speaking(self):
        """停止语音播放"""
        # 取消延迟播放
        self.cancel_delayed_speak()
        
        if IS_ANDROID:
            # 停止Android TTS
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                    Logger.info("已停止Android TTS")
                except:
                    pass
            
            # 停止Android音频播放器
            if self.android_audio_player:
                self.android_audio_player.stop()
        
        self.is_speaking = False
    
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
        
        # 如果在Android平台上，清理Android资源
        if IS_ANDROID:
            if self.android_audio_handler:
                self.android_audio_handler.cleanup()
            
            if self.android_audio_player:
                self.android_audio_player.cleanup()
            
            if self.tts_engine:
                self.tts_engine.shutdown()
                self.tts_engine = None
        
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


# 用于测试
if __name__ == "__main__":
    handler = AndroidSpeechHandler()
    
    if IS_ANDROID:
        print("正在测试Android语音功能...")
        # 测试语音识别
        print("开始录音...")
        handler.start_recording()
        time.sleep(5)  # 录制5秒
        print("停止录音并识别...")
        text = handler.stop_recording_and_recognize()
        print(f"识别结果: {text}")
        
        # 测试语音合成
        if text:
            print(f"播放识别结果: {text}")
            handler.speak(text)
            time.sleep(5)  # 等待播放完成
        else:
            print("播放测试语音...")
            handler.speak("这是一个Android语音合成测试")
            time.sleep(5)  # 等待播放完成
        
        print("测试完成")
    else:
        print("此模块只能在Android平台上使用") 