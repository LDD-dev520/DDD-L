#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
历史记录屏幕模块
展示用户的历史问答记录
"""

from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.app import App


class HistoryItem(BoxLayout):
    """历史记录项组件"""
    
    def __init__(self, question, answer, timestamp, **kwargs):
        super(HistoryItem, self).__init__(**kwargs)
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(150)
        self.padding = [dp(10), dp(5), dp(10), dp(5)]
        self.spacing = dp(5)
        self.question = question
        self.answer = answer
        
        # 设置背景色
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._update_rect, size=self._update_rect)
        
        # 创建时间标签
        time_label = Label()
        time_label.text = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        time_label.font_size = dp(12)
        time_label.color = (0.5, 0.5, 0.5, 1)
        time_label.size_hint_y = None
        time_label.height = dp(20)
        time_label.halign = 'left'
        
        # 创建问题标签
        question_label = Label()
        question_label.text = f"问: {question}"
        question_label.color = (0.1, 0.1, 0.1, 1)
        question_label.font_size = dp(16)
        question_label.size_hint_y = None
        question_label.height = dp(40)
        question_label.halign = 'left'
        question_label.valign = 'middle'
        question_label.text_size = (self.width - dp(20), None)
        question_label.bind(size=self._update_label_width)
        
        # 创建简略回答标签
        answer_preview = answer[:50] + "..." if len(answer) > 50 else answer
        answer_label = Label()
        answer_label.text = f"答: {answer_preview}"
        answer_label.color = (0.3, 0.3, 0.3, 1)
        answer_label.font_size = dp(14)
        answer_label.size_hint_y = None
        answer_label.height = dp(60)
        answer_label.halign = 'left'
        answer_label.valign = 'top'
        answer_label.text_size = (self.width - dp(20), None)
        answer_label.bind(size=self._update_label_width)
        
        # 创建操作按钮
        buttons_layout = BoxLayout()
        buttons_layout.orientation = 'horizontal'
        buttons_layout.size_hint_y = None
        buttons_layout.height = dp(30)
        buttons_layout.spacing = dp(10)
        
        view_button = Button()
        view_button.text = "查看详情"
        view_button.font_size = dp(14)
        view_button.size_hint = (0.5, 1)
        view_button.background_color = get_color_from_hex('#2196F3')
        view_button.bind(on_release=self.view_detail)
        
        reask_button = Button()
        reask_button.text = "重新提问"
        reask_button.font_size = dp(14)
        reask_button.size_hint = (0.5, 1)
        reask_button.background_color = get_color_from_hex('#4CAF50')
        reask_button.bind(on_release=self.reask_question)
        
        buttons_layout.add_widget(view_button)
        buttons_layout.add_widget(reask_button)
        
        # 添加到主布局
        self.add_widget(time_label)
        self.add_widget(question_label)
        self.add_widget(answer_label)
        self.add_widget(buttons_layout)
    
    def _update_rect(self, instance, value):
        """更新背景矩形"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _update_label_width(self, instance, value):
        """更新标签宽度"""
        instance.text_size = (value[0] - dp(20), None)
    
    def view_detail(self, instance):
        """查看详情"""
        app = App.get_running_app()
        # 回到主屏幕并显示这组问答
        app.screen_manager.current = 'home'
        app.home_screen.add_message_to_chat(self.question, is_user=True)
        app.home_screen.add_message_to_chat(self.answer, is_user=False)
    
    def reask_question(self, instance):
        """重新提问"""
        app = App.get_running_app()
        # 回到主屏幕并设置输入框
        app.screen_manager.current = 'home'
        app.home_screen.ids.input_text.text = self.question


class HistoryScreen(Screen):
    """历史记录屏幕类"""
    
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.history_data = []
    
    def on_pre_enter(self):
        """进入屏幕前调用"""
        # 清空历史容器
        self.ids.history_container.clear_widgets()
        
        # 加载历史记录
        self.load_history()
        
        # 显示历史记录
        self.display_history()
    
    def load_history(self):
        """加载历史记录"""
        # 实际应用中，这里会从数据库或文件中加载历史记录
        # 临时从主屏幕获取历史
        try:
            app = self.parent.parent
            if hasattr(app, 'home_screen') and app.home_screen.history:
                self.history_data = app.home_screen.history
            else:
                # 示例数据
                self.history_data = [
                    {
                        "text": "什么是人工智能?", 
                        "is_user": True, 
                        "timestamp": datetime.now()
                    },
                    {
                        "text": "人工智能是计算机科学的一个分支，致力于创造能够模拟人类智能的机器。它包括机器学习、深度学习、自然语言处理等多个领域。", 
                        "is_user": False, 
                        "timestamp": datetime.now()
                    },
                    {
                        "text": "今天天气怎么样?", 
                        "is_user": True, 
                        "timestamp": datetime.now()
                    },
                    {
                        "text": "我无法获取实时天气信息。您可以查看天气预报应用或网站获取当前天气状况。", 
                        "is_user": False, 
                        "timestamp": datetime.now()
                    }
                ]
        except Exception as e:
            print(f"加载历史记录出错: {e}")
            self.history_data = []
    
    def display_history(self):
        """显示历史记录"""
        if not self.history_data:
            # 如果没有历史记录，显示提示信息
            empty_label = Label(text="暂无历史记录", 
                               font_size=dp(18),
                               color=(0.5, 0.5, 0.5, 1))
            self.ids.history_container.add_widget(empty_label)
            return
        
        # 按对话组合并历史记录
        conversation_pairs = []
        question = None
        
        for i, item in enumerate(self.history_data):
            if item["is_user"]:
                question = item
            elif question:
                # 找到了一对问答
                conversation_pairs.append({
                    "question": question["text"],
                    "answer": item["text"],
                    "timestamp": question["timestamp"]
                })
                question = None
        
        # 显示历史对话
        for pair in reversed(conversation_pairs):  # 最近的对话显示在顶部
            history_item = HistoryItem(
                question=pair["question"],
                answer=pair["answer"],
                timestamp=pair["timestamp"]
            )
            self.ids.history_container.add_widget(history_item)
            
        # 更新容器高度
        self.ids.history_container.height = sum(child.height for child in self.ids.history_container.children)
    
    def clear_history(self):
        """清空历史记录"""
        # 清空数据
        self.history_data = []
        
        # 清空主屏幕历史
        app = self.parent.parent
        if hasattr(app, 'home_screen'):
            app.home_screen.history = []
        
        # 重新显示（空）
        self.ids.history_container.clear_widgets()
        self.display_history() 