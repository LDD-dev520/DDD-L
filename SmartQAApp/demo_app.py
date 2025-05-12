#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SmartQA银行助手 - 演示版
简化版本，可以直接在Android设备上运行
"""

import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# 设置窗口大小
Window.size = (360, 640)

class SmartQADemoApp(App):
    """SmartQA银行助手演示应用"""
    
    def build(self):
        """构建应用界面"""
        # 主布局
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 添加标题
        title_layout = BoxLayout(size_hint=(1, 0.2))
        title_label = Label(
            text='SmartQA银行助手',
            font_size='24sp',
            color=(0.2, 0.6, 1, 1)
        )
        title_layout.add_widget(title_label)
        layout.add_widget(title_layout)
        
        # 添加标识图像
        logo_layout = BoxLayout(size_hint=(1, 0.3))
        # 如果logo文件存在则使用，否则使用占位符
        logo_path = os.path.join('assets', 'icon.png')
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint=(1, 1))
        else:
            logo = Label(text='[SmartQA图标]', font_size='32sp', color=(0.2, 0.6, 1, 1))
        logo_layout.add_widget(logo)
        layout.add_widget(logo_layout)
        
        # 聊天消息显示区域
        self.chat_history = Label(
            text='欢迎使用SmartQA银行助手演示版\n请输入您的问题',
            size_hint=(1, 0.3),
            halign='left',
            valign='top',
            text_size=(Window.width - 30, None),
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.chat_history)
        
        # 输入区域
        input_layout = BoxLayout(size_hint=(1, 0.1), spacing=5)
        self.input_text = TextInput(
            hint_text='请输入您的问题...',
            multiline=False,
            size_hint=(0.8, 1),
            font_size='16sp'
        )
        self.input_text.bind(on_text_validate=self.on_send)
        
        # 发送按钮
        send_button = Button(
            text='发送',
            size_hint=(0.2, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        send_button.bind(on_press=self.on_send)
        
        input_layout.add_widget(self.input_text)
        input_layout.add_widget(send_button)
        layout.add_widget(input_layout)
        
        # 功能按钮区域
        button_layout = BoxLayout(size_hint=(1, 0.1), spacing=5)
        
        # 语音按钮
        voice_button = Button(
            text='语音',
            size_hint=(0.33, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        voice_button.bind(on_press=self.on_voice)
        
        # 历史按钮
        history_button = Button(
            text='历史',
            size_hint=(0.33, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        history_button.bind(on_press=self.on_history)
        
        # 设置按钮
        settings_button = Button(
            text='设置',
            size_hint=(0.34, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        settings_button.bind(on_press=self.on_settings)
        
        button_layout.add_widget(voice_button)
        button_layout.add_widget(history_button)
        button_layout.add_widget(settings_button)
        layout.add_widget(button_layout)
        
        # 版权信息
        footer = Label(
            text='© 2024 SmartQA Team',
            size_hint=(1, 0.05),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(footer)
        
        # 检查平台
        if platform == 'android':
            self.check_permissions()
        
        return layout
    
    def check_permissions(self):
        """检查并请求Android权限"""
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            print("已请求Android权限")
        except Exception as e:
            print(f"请求权限失败: {e}")
    
    def on_send(self, instance):
        """发送按钮处理"""
        text = self.input_text.text.strip()
        if text:
            # 显示用户输入
            self.chat_history.text += f'\n\n您: {text}'
            
            # 清空输入框
            self.input_text.text = ''
            
            # 模拟回答
            Clock.schedule_once(lambda dt: self.answer_question(text), 1)
    
    def answer_question(self, question):
        """回答问题"""
        # 简单的问答逻辑
        answers = {
            '你好': '您好！我是SmartQA银行助手，有什么可以帮您？',
            '你是谁': '我是SmartQA银行助手，一个智能问答系统。',
            '什么是智能存款': '智能存款是一种灵活的存款产品，可以根据您的需求自动调整利率和期限。',
            '如何办理信用卡': '您可以通过手机银行、网上银行或前往银行网点申请办理信用卡。',
            '贷款利率是多少': '我们的贷款利率根据产品类型和个人信用评分有所不同，基准利率为4.35%。'
        }
        
        # 寻找匹配的问题
        answer = None
        for key, value in answers.items():
            if key in question:
                answer = value
                break
        
        # 如果没有匹配项，使用默认回答
        if not answer:
            answer = '非常抱歉，我无法理解您的问题。请尝试其他问题或联系客服。'
        
        # 显示回答
        self.chat_history.text += f'\n\n银行助手: {answer}'
    
    def on_voice(self, instance):
        """语音按钮处理"""
        self.chat_history.text += '\n\n[语音识别功能在完整版中可用]'
    
    def on_history(self, instance):
        """历史按钮处理"""
        self.chat_history.text += '\n\n[历史记录功能在完整版中可用]'
    
    def on_settings(self, instance):
        """设置按钮处理"""
        self.chat_history.text += '\n\n[设置功能在完整版中可用]'

if __name__ == '__main__':
    SmartQADemoApp().run() 