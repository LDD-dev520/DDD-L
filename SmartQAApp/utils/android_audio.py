#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Android平台音频处理模块
提供录音和播放功能适配
"""

import os
import time
from kivy.logger import Logger

try:
    from jnius import autoclass
    
    # Android相关类
    MediaRecorder = autoclass('android.media.MediaRecorder')
    AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    AudioManager = autoclass('android.media.AudioManager')
    AudioAttributes = autoclass('android.media.AudioAttributes')
    AudioAttributes_Builder = autoclass('android.media.AudioAttributes$Builder')
    MediaPlayer = autoclass('android.media.MediaPlayer')
    File = autoclass('java.io.File')
    Environment = autoclass('android.os.Environment')
    Context = autoclass('android.content.Context')
    
    # Activity相关
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    
    IS_ANDROID = True
    Logger.info("已导入Android音频相关类")
except ImportError as e:
    IS_ANDROID = False
    Logger.error(f"导入Android相关类失败: {e}")

class AndroidAudioHandler:
    """Android平台音频录制处理类"""
    
    def __init__(self):
        """初始化"""
        self.recorder = None
        self.recording_file = None
        self.is_recording = False
        
        # 创建资源目录
        self.resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        if not os.path.exists(self.resource_dir):
            os.makedirs(self.resource_dir)
    
    def start_recording(self):
        """开始录音"""
        if not IS_ANDROID:
            Logger.error("不在Android平台上，无法使用Android录音")
            return False
        
        if self.is_recording:
            Logger.warning("已经在录音中")
            return False
        
        try:
            # 请求麦克风权限
            from android.permissions import request_permissions, Permission, check_permission
            
            if not check_permission(Permission.RECORD_AUDIO):
                request_permissions([Permission.RECORD_AUDIO])
                Logger.info("已请求录音权限")
            
            # 创建临时文件
            self.recording_file = os.path.join(self.resource_dir, f'recording_{int(time.time())}.amr')
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.recording_file), exist_ok=True)
            
            # 创建MediaRecorder实例
            self.recorder = MediaRecorder()
            
            # 配置录音参数
            self.recorder.setAudioSource(AudioSource.MIC)  # 麦克风
            self.recorder.setOutputFormat(OutputFormat.AMR_NB)  # AMR格式
            self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)  # AMR编码器
            self.recorder.setOutputFile(self.recording_file)
            
            # 准备并开始录音
            self.recorder.prepare()
            self.recorder.start()
            
            self.is_recording = True
            Logger.info(f"开始录音到: {self.recording_file}")
            return True
        except Exception as e:
            import traceback
            Logger.error(f"启动录音失败: {e}")
            Logger.error(traceback.format_exc())
            if self.recorder:
                try:
                    self.recorder.release()
                except:
                    pass
                self.recorder = None
            
            self.is_recording = False
            return False
    
    def stop_recording(self):
        """停止录音"""
        if not IS_ANDROID or not self.is_recording or not self.recorder:
            Logger.warning("未在录音中或录音器不可用")
            return None
        
        try:
            # 停止并释放录音器
            self.recorder.stop()
            self.recorder.release()
            self.recorder = None
            
            self.is_recording = False
            Logger.info(f"停止录音: {self.recording_file}")
            
            # 检查文件是否存在并有效
            if os.path.exists(self.recording_file) and os.path.getsize(self.recording_file) > 100:
                Logger.info(f"录音文件有效: {self.recording_file}, 大小: {os.path.getsize(self.recording_file)} 字节")
                return self.recording_file
            else:
                Logger.error(f"录音文件无效或太小: {self.recording_file}")
                return None
        except Exception as e:
            import traceback
            Logger.error(f"停止录音失败: {e}")
            Logger.error(traceback.format_exc())
            
            if self.recorder:
                try:
                    self.recorder.release()
                except:
                    pass
                self.recorder = None
            
            self.is_recording = False
            return None
    
    def cleanup(self):
        """清理资源"""
        if self.is_recording and self.recorder:
            try:
                self.recorder.stop()
                self.recorder.release()
            except:
                pass
            self.recorder = None
            self.is_recording = False


class AndroidAudioPlayer:
    """Android平台音频播放类"""
    
    def __init__(self):
        """初始化"""
        self.player = None
        self.is_playing = False
    
    def play(self, audio_file):
        """播放音频文件"""
        if not IS_ANDROID:
            Logger.error("不在Android平台上，无法使用Android播放器")
            return False
        
        # 停止当前播放
        self.stop()
        
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_file):
                Logger.error(f"音频文件不存在: {audio_file}")
                return False
            
            # 创建MediaPlayer并设置音频源
            self.player = MediaPlayer()
            self.player.setDataSource(audio_file)
            
            # 使用AudioAttributes构建器设置音频属性
            audio_attributes_builder = AudioAttributes_Builder()
            audio_attributes_builder.setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
            audio_attributes_builder.setUsage(AudioAttributes.USAGE_MEDIA)
            self.player.setAudioAttributes(audio_attributes_builder.build())
            
            # 准备并播放
            self.player.prepare()
            self.player.start()
            
            self.is_playing = True
            Logger.info(f"开始播放: {audio_file}")
            
            # 设置播放完成监听器
            class OnCompletionListener(MediaPlayer.OnCompletionListener):
                def __init__(self, player_instance, player_obj):
                    self.player_instance = player_instance
                    self.player_obj = player_obj
                
                def onCompletion(self, mp):
                    self.player_obj.is_playing = False
                    try:
                        if self.player_instance:
                            self.player_instance.release()
                    except:
                        pass
            
            self.player.setOnCompletionListener(OnCompletionListener(self.player, self))
            
            return True
        except Exception as e:
            import traceback
            Logger.error(f"播放音频失败: {e}")
            Logger.error(traceback.format_exc())
            
            if self.player:
                try:
                    self.player.release()
                except:
                    pass
                self.player = None
            
            self.is_playing = False
            return False
    
    def stop(self):
        """停止播放"""
        if not self.player or not self.is_playing:
            return
        
        try:
            if self.player.isPlaying():
                self.player.stop()
            self.player.release()
        except:
            pass
        
        self.player = None
        self.is_playing = False
        Logger.info("停止播放")
    
    def cleanup(self):
        """清理资源"""
        self.stop()


# 测试代码
if __name__ == "__main__":
    if IS_ANDROID:
        print("正在测试Android音频功能...")
        
        # 测试录音
        recorder = AndroidAudioHandler()
        print("开始录音...")
        
        if recorder.start_recording():
            time.sleep(5)  # 录音5秒
            print("停止录音...")
            audio_file = recorder.stop_recording()
            
            if audio_file:
                print(f"录音成功: {audio_file}")
                
                # 测试播放
                player = AndroidAudioPlayer()
                print(f"播放录音: {audio_file}")
                if player.play(audio_file):
                    time.sleep(6)  # 等待播放完成
                    player.stop()
                
                # 清理测试文件
                try:
                    os.remove(audio_file)
                    print(f"已删除测试文件: {audio_file}")
                except:
                    pass
            else:
                print("录音失败")
        else:
            print("启动录音失败")
    else:
        print("此模块只能在Android平台上使用") 