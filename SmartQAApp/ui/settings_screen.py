#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置屏幕模块
包含应用程序的各种设置选项
"""

import os
import json
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.clock import Clock


class SettingsScreen(Screen):
    """设置屏幕类"""
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.settings = {
            "voice_output": True,
            "voice_recognition": True,
            "auto_save_history": True,
            "night_mode": False,
            "font_size": "medium"
        }
        
        # 延迟加载设置
        Clock.schedule_once(self.load_settings, 0.5)
    
    def on_pre_enter(self):
        """进入屏幕前调用"""
        # 更新设置UI状态
        self.update_settings_ui()
    
    def load_settings(self, dt=None):
        """加载设置"""
        # 设置文件路径
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
        
        # 检查文件是否存在
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # 更新设置
                    self.settings.update(saved_settings)
            except Exception as e:
                print(f"加载设置出错: {e}")
                # 使用默认设置
        else:
            # 如果文件不存在，使用默认设置并创建文件
            self.save_settings()
    
    def save_settings(self):
        """保存设置"""
        # 创建数据目录
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 设置文件路径
        settings_file = os.path.join(data_dir, 'settings.json')
        
        # 保存设置
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存设置出错: {e}")
    
    def update_settings_ui(self):
        """更新设置UI状态"""
        # 更新语音输出开关
        if hasattr(self.ids, 'voice_output_switch'):
            self.ids.voice_output_switch.active = self.settings["voice_output"]
        
        # 更新语音识别开关
        if hasattr(self.ids, 'voice_recognition_switch'):
            self.ids.voice_recognition_switch.active = self.settings["voice_recognition"]
    
    def toggle_voice_output(self, value):
        """切换语音输出设置"""
        self.settings["voice_output"] = value
        self.save_settings()
        
        # 更新应用中的语音输出状态
        app = self.parent.parent
        if hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_output_enabled(value)
    
    def toggle_voice_recognition(self, value):
        """切换语音识别设置"""
        self.settings["voice_recognition"] = value
        self.save_settings()
        
        # 更新应用中的语音识别状态
        app = self.parent.parent
        if hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_recognition_enabled(value)
    
    def toggle_auto_save_history(self, value):
        """切换自动保存历史记录设置"""
        self.settings["auto_save_history"] = value
        self.save_settings()
    
    def toggle_night_mode(self, value):
        """切换夜间模式设置"""
        self.settings["night_mode"] = value
        self.save_settings()
        
        # 更新应用中的夜间模式
        app = self.parent.parent
        if hasattr(app, 'toggle_night_mode'):
            app.toggle_night_mode(value)
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.settings["font_size"] = size
        self.save_settings()
        
        # 更新应用中的字体大小
        app = self.parent.parent
        if hasattr(app, 'set_font_size'):
            app.set_font_size(size)
    
    def reset_settings(self):
        """重置设置"""
        self.settings = {
            "voice_output": True,
            "voice_recognition": True,
            "auto_save_history": True,
            "night_mode": False,
            "font_size": "medium"
        }
        self.save_settings()
        self.update_settings_ui()
        
        # 更新应用设置
        app = self.parent.parent
        if hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_output_enabled(True)
            app.speech_handler.set_voice_recognition_enabled(True)
        
        if hasattr(app, 'toggle_night_mode'):
            app.toggle_night_mode(False)
        
        if hasattr(app, 'set_font_size'):
            app.set_font_size("medium") 