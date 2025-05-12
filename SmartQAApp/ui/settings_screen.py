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
from kivy.logger import Logger
from kivy.utils import get_color_from_hex


class SettingsScreen(Screen):
    """设置屏幕类"""
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.settings = {
            "voice_output": True,
            "voice_recognition": True,
            "auto_play": True,  # 新增：自动播放语音设置
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
                Logger.info(f"成功加载设置: {self.settings}")
            except Exception as e:
                Logger.error(f"加载设置出错: {e}")
                # 使用默认设置
        else:
            # 如果文件不存在，使用默认设置并创建文件
            Logger.info("设置文件不存在，使用默认设置")
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
            Logger.info("成功保存设置")
        except Exception as e:
            Logger.error(f"保存设置出错: {e}")
    
    def update_settings_ui(self):
        """更新设置UI状态"""
        # 获取应用实例
        app = self.get_app_instance()
        
        # 更新语音输出按钮
        if hasattr(self.ids, 'voice_output_toggle'):
            enabled = self.settings.get("voice_output", True)
            self.ids.voice_output_toggle.text = "开启" if enabled else "关闭"
            self.ids.voice_output_toggle.background_color = get_color_from_hex('#4CAF50') if enabled else get_color_from_hex('#F44336')
            
            # 同步应用状态
            if app and hasattr(app, 'speech_handler'):
                app.speech_handler.set_voice_output_enabled(enabled)
        
        # 更新自动播放按钮
        if hasattr(self.ids, 'auto_play_toggle'):
            enabled = self.settings.get("auto_play", True)
            self.ids.auto_play_toggle.text = "开启" if enabled else "关闭"
            self.ids.auto_play_toggle.background_color = get_color_from_hex('#4CAF50') if enabled else get_color_from_hex('#F44336')
            
            # 同步应用状态
            if app and hasattr(app, 'speech_handler'):
                if hasattr(app.speech_handler, 'set_auto_play'):
                    app.speech_handler.set_auto_play(enabled)
        
        # 更新语音识别按钮
        if hasattr(self.ids, 'voice_recognition_toggle'):
            enabled = self.settings.get("voice_recognition", True)
            self.ids.voice_recognition_toggle.text = "开启" if enabled else "关闭"
            self.ids.voice_recognition_toggle.background_color = get_color_from_hex('#4CAF50') if enabled else get_color_from_hex('#F44336')
            
            # 同步应用状态
            if app and hasattr(app, 'speech_handler'):
                app.speech_handler.set_voice_recognition_enabled(enabled)
    
    def get_app_instance(self):
        """获取应用实例"""
        try:
            # 尝试通过父级获取应用实例
            if hasattr(self, 'parent') and self.parent:
                if hasattr(self.parent, 'parent') and self.parent.parent:
                    return self.parent.parent
            
            # 如果失败，尝试直接获取
            from kivy.app import App
            return App.get_running_app()
        except Exception as e:
            Logger.error(f"获取应用实例失败: {e}")
            return None
    
    def toggle_voice_output(self):
        """切换语音输出设置"""
        # 反转当前状态
        current_value = self.settings.get("voice_output", True)
        new_value = not current_value
        self.settings["voice_output"] = new_value
        
        # 更新UI
        if hasattr(self.ids, 'voice_output_toggle'):
            self.ids.voice_output_toggle.text = "开启" if new_value else "关闭"
            self.ids.voice_output_toggle.background_color = get_color_from_hex('#4CAF50') if new_value else get_color_from_hex('#F44336')
        
        # 更新主页的语音按钮
        app = self.get_app_instance()
        if app and hasattr(app, 'home_screen') and hasattr(app.home_screen, 'ids'):
            if hasattr(app.home_screen.ids, 'voice_toggle'):
                app.home_screen.ids.voice_toggle.text = "语音:开" if new_value else "语音:关"
                app.home_screen.ids.voice_toggle.background_color = get_color_from_hex('#4CAF50') if new_value else get_color_from_hex('#F44336')
        
        # 保存设置并更新应用状态
        self.save_settings()
        app = self.get_app_instance()
        if app and hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_output_enabled(new_value)
            Logger.info(f"语音输出已{'启用' if new_value else '禁用'}")
    
    def toggle_auto_play(self):
        """切换自动播放设置"""
        # 反转当前状态
        current_value = self.settings.get("auto_play", True)
        new_value = not current_value
        self.settings["auto_play"] = new_value
        
        # 更新UI
        if hasattr(self.ids, 'auto_play_toggle'):
            self.ids.auto_play_toggle.text = "开启" if new_value else "关闭"
            self.ids.auto_play_toggle.background_color = get_color_from_hex('#4CAF50') if new_value else get_color_from_hex('#F44336')
        
        # 保存设置并更新应用状态
        self.save_settings()
        app = self.get_app_instance()
        if app and hasattr(app, 'speech_handler'):
            if hasattr(app.speech_handler, 'set_auto_play'):
                app.speech_handler.set_auto_play(new_value)
                Logger.info(f"自动播放已{'启用' if new_value else '禁用'}")
    
    def toggle_voice_recognition(self):
        """切换语音识别设置"""
        # 反转当前状态
        current_value = self.settings.get("voice_recognition", True)
        new_value = not current_value
        self.settings["voice_recognition"] = new_value
        
        # 更新UI
        if hasattr(self.ids, 'voice_recognition_toggle'):
            self.ids.voice_recognition_toggle.text = "开启" if new_value else "关闭"
            self.ids.voice_recognition_toggle.background_color = get_color_from_hex('#4CAF50') if new_value else get_color_from_hex('#F44336')
        
        # 保存设置并更新应用状态
        self.save_settings()
        app = self.get_app_instance()
        if app and hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_recognition_enabled(new_value)
            Logger.info(f"语音识别已{'启用' if new_value else '禁用'}")
    
    def toggle_auto_save_history(self, value):
        """切换自动保存历史记录设置"""
        self.settings["auto_save_history"] = value
        self.save_settings()
    
    def toggle_night_mode(self, value):
        """切换夜间模式设置"""
        self.settings["night_mode"] = value
        self.save_settings()
        
        # 更新应用中的夜间模式
        app = self.get_app_instance()
        if app and hasattr(app, 'toggle_night_mode'):
            app.toggle_night_mode(value)
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.settings["font_size"] = size
        self.save_settings()
        
        # 更新应用中的字体大小
        app = self.get_app_instance()
        if app and hasattr(app, 'set_font_size'):
            app.set_font_size(size)
    
    def reset_settings(self):
        """重置设置"""
        self.settings = {
            "voice_output": True,
            "voice_recognition": True,
            "auto_play": True,
            "auto_save_history": True,
            "night_mode": False,
            "font_size": "medium"
        }
        self.save_settings()
        self.update_settings_ui()
        
        # 更新应用设置
        app = self.get_app_instance()
        if app and hasattr(app, 'speech_handler'):
            app.speech_handler.set_voice_output_enabled(True)
            app.speech_handler.set_voice_recognition_enabled(True)
            if hasattr(app.speech_handler, 'set_auto_play'):
                app.speech_handler.set_auto_play(True)
        
        if app:
            if hasattr(app, 'toggle_night_mode'):
                app.toggle_night_mode(False)
            
            if hasattr(app, 'set_font_size'):
                app.set_font_size("medium")
            
            # 更新主页的语音按钮
            if hasattr(app, 'home_screen') and hasattr(app.home_screen, 'ids'):
                if hasattr(app.home_screen.ids, 'voice_toggle'):
                    app.home_screen.ids.voice_toggle.text = "语音:开"
                    app.home_screen.ids.voice_toggle.background_color = get_color_from_hex('#4CAF50') 