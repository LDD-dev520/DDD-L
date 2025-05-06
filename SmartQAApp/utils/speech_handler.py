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
from gtts import gTTS
import speech_recognition as sr
from kivy.core.audio import SoundLoader

# 尝试导入pyttsx3作为备用TTS引擎
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False


class SpeechHandler:
    """语音处理类"""
    
    def __init__(self):
        """初始化"""
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.recording = False
        self.audio = None
        self.voice_output_enabled = True
        self.voice_recognition_enabled = True
        self.current_sound = None
    
    def initialize(self):
        """初始化资源"""
        # 创建资源目录
        self.resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        if not os.path.exists(self.resource_dir):
            os.makedirs(self.resource_dir)
        
        # 初始化语音识别器
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # 调整识别器参数
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            print("语音识别器初始化成功")
        except Exception as e:
            print(f"语音识别器初始化失败: {e}")
            self.recognizer = None
            self.microphone = None
        
        # 初始化TTS引擎
        if HAS_PYTTSX3:
            try:
                self.tts_engine = pyttsx3.init()
                # 设置中文语音
                voices = self.tts_engine.getProperty('voices')
                # 尝试找到中文语音
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                # 设置语速
                self.tts_engine.setProperty('rate', 150)
                print("本地TTS引擎初始化成功")
            except Exception as e:
                print(f"本地TTS引擎初始化失败: {e}")
                self.tts_engine = None
    
    def start_recording(self):
        """开始录音"""
        if not self.recognizer or not self.microphone or not self.voice_recognition_enabled:
            print("语音识别不可用或已禁用")
            return False
        
        self.recording = True
        
        # 在线程中启动录音
        threading.Thread(target=self._record_audio).start()
        
        return True
    
    def _record_audio(self):
        """录制音频"""
        try:
            with self.microphone as source:
                print("开始录音...")
                self.audio = self.recognizer.listen(source, timeout=5.0)
                print("录音完成")
        except Exception as e:
            print(f"录音失败: {e}")
            self.audio = None
        finally:
            self.recording = False
    
    def stop_recording_and_recognize(self):
        """停止录音并识别语音"""
        if not self.audio:
            return None
        
        try:
            # 尝试使用多种语音识别服务
            try:
                print("使用Google语音识别...")
                text = self.recognizer.recognize_google(self.audio, language="zh-CN")
            except:
                try:
                    print("使用Sphinx语音识别...")
                    text = self.recognizer.recognize_sphinx(self.audio, language="zh-CN")
                except:
                    print("所有语音识别服务均失败")
                    return None
            
            print(f"识别结果: {text}")
            return text
        except Exception as e:
            print(f"语音识别失败: {e}")
            return None
        finally:
            self.audio = None
    
    def speak(self, text):
        """文本转语音"""
        if not self.voice_output_enabled:
            print("语音输出已禁用")
            return False
        
        # 停止当前正在播放的语音
        self.stop_speaking()
        
        # 创建线程进行语音合成和播放
        threading.Thread(target=self._synthesize_and_play, args=(text,)).start()
        
        return True
    
    def _synthesize_and_play(self, text):
        """合成并播放语音"""
        try:
            # 优先使用Google TTS
            temp_file = os.path.join(self.resource_dir, 'temp_speech.mp3')
            
            try:
                # 使用Google TTS
                tts = gTTS(text=text, lang='zh-cn', slow=False)
                tts.save(temp_file)
                print("使用Google TTS生成语音")
            except Exception as e:
                print(f"Google TTS失败: {e}")
                
                # 回退到本地TTS
                if self.tts_engine:
                    temp_file = os.path.join(self.resource_dir, 'temp_speech.wav')
                    self.tts_engine.save_to_file(text, temp_file)
                    self.tts_engine.runAndWait()
                    print("使用本地TTS生成语音")
                else:
                    print("无可用TTS引擎")
                    return
            
            # 播放语音
            self.current_sound = SoundLoader.load(temp_file)
            if self.current_sound:
                self.current_sound.play()
                print("开始播放语音")
            else:
                print("语音加载失败")
        except Exception as e:
            print(f"语音合成或播放失败: {e}")
    
    def stop_speaking(self):
        """停止语音播放"""
        if self.current_sound and self.current_sound.state == 'play':
            self.current_sound.stop()
            print("停止播放语音")
    
    def set_voice_output_enabled(self, enabled):
        """设置语音输出是否启用"""
        self.voice_output_enabled = enabled
        if not enabled:
            self.stop_speaking()
    
    def set_voice_recognition_enabled(self, enabled):
        """设置语音识别是否启用"""
        self.voice_recognition_enabled = enabled
        if not enabled and self.recording:
            self.recording = False
    
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
                except:
                    pass
        
        # 清理TTS引擎
        if self.tts_engine:
            del self.tts_engine
            self.tts_engine = None 