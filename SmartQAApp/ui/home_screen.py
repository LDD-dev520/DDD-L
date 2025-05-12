#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主屏幕模块
包含问答交互的主界面
专门优化Microsoft拼音输入法支持
"""

import os
import time
from datetime import datetime
from threading import Thread

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.core.window import Window
from kivy.logger import Logger

# 用户消息类
class UserMessage:
    """用户消息类"""
    def __init__(self, text=""):
        self.text = text
        self.timestamp = datetime.now()

class MessageBubble(BoxLayout):
    """消息气泡组件"""
    
    def __init__(self, message, is_user=True, **kwargs):
        super(MessageBubble, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(100)  # 初始高度，会根据内容自适应
        self.padding = [dp(10), dp(5), dp(10), dp(5)]
        self.spacing = dp(5)
        
        # 创建消息内容布局
        content_layout = BoxLayout()
        content_layout.size_hint_y = None
        content_layout.height = dp(80)
        content_layout.padding = [dp(10), dp(5), dp(10), dp(5)]
        
        # 设置消息气泡的样式
        if is_user:
            content_layout.orientation = 'horizontal'
            
            # 用户消息靠右
            spacer = BoxLayout()
            spacer.size_hint_x = 0.2
            content_layout.add_widget(spacer)
            
            # 消息内容标签
            message_label = Label()
            message_label.text = message
            message_label.color = (0.1, 0.1, 0.1, 1)
            message_label.size_hint = (0.8, 1)
            message_label.halign = 'right'
            message_label.valign = 'middle'
            message_label.text_size = (dp(200), None)
            message_label.bind(size=message_label.setter('text_size'))
            message_label.padding = [dp(10), dp(10)]
            
            # 添加到布局中
            content_layout.add_widget(message_label)
        else:
            content_layout.orientation = 'horizontal'
            
            # 消息内容标签 - 修改以确保文本完整显示
            message_label = Label()
            message_label.text = message
            message_label.color = (0.1, 0.1, 0.1, 1)
            message_label.size_hint = (0.8, None)  # 高度为None，允许自动调整
            message_label.height = max(dp(80), len(message) * 0.2)  # 基于文本长度调整高度
            message_label.halign = 'left'
            message_label.valign = 'top'
            message_label.text_size = (dp(250), None)  # 宽度固定，高度自适应
            message_label.bind(texture_size=self._update_label_height)
            message_label.padding = [dp(10), dp(10)]
            
            # 保存对标签的引用以便播放语音
            self.message_label = message_label
            self.message_text = message
            
            # 添加到布局中
            content_layout.add_widget(message_label)
            
            # 添加语音播放按钮（仅AI回复有）
            voice_button = Button()
            voice_button.text = "🔊"
            voice_button.size_hint = (None, None)
            voice_button.size = (dp(40), dp(40))
            voice_button.background_color = (0.3, 0.7, 0.9, 1)
            voice_button.bind(on_release=lambda x: self.play_voice(message))
            self.voice_button = voice_button
            
            content_layout.add_widget(voice_button)
            
            # 空白占位
            spacer = BoxLayout()
            spacer.size_hint_x = 0.05
            content_layout.add_widget(spacer)
        
        # 添加时间戳标签
        time_label = Label()
        time_label.text = datetime.now().strftime("%H:%M:%S")
        time_label.font_size = dp(12)
        time_label.color = (0.5, 0.5, 0.5, 1)
        time_label.size_hint_y = None
        time_label.height = dp(20)
        time_label.halign = 'right' if is_user else 'left'
        time_label.valign = 'bottom'
        
        # 添加到主布局
        self.add_widget(content_layout)
        self.add_widget(time_label)
        
        # 调整整体高度以适应内容
        Clock.schedule_once(lambda dt: self._adjust_height(), 0.1)
    
    def _update_label_height(self, instance, size):
        """根据文本内容更新标签高度"""
        # 调整标签高度以适应内容
        instance.height = max(dp(80), size[1] + dp(20))
        # 重新调整整体布局
        Clock.schedule_once(lambda dt: self._adjust_height(), 0)
    
    def _adjust_height(self):
        """调整气泡整体高度"""
        if hasattr(self, 'message_label'):
            # 获取消息标签的实际高度
            label_height = self.message_label.texture_size[1] + dp(20)
            # 调整气泡高度
            new_height = max(dp(100), label_height + dp(40))
            self.height = new_height
            # 调整内容布局高度
            if len(self.children) > 0 and isinstance(self.children[0], BoxLayout):
                self.children[0].height = new_height - dp(30)
    
    def play_voice(self, text):
        """播放语音"""
        try:
            if not hasattr(self, 'app'):
                from kivy.app import App
                self.app = App.get_running_app()
            
            if hasattr(self.app, 'speech_handler'):
                # 如果当前是否播放此消息
                if self.app.speech_handler.is_speaking and self.voice_button.text == "⏹️":
                    # 如果正在播放，则停止
                    self.app.speech_handler.stop_speaking()
                    self.voice_button.text = "🔊"
                    self.voice_button.background_color = (0.3, 0.7, 0.9, 1)
                else:
                    # 停止其他可能正在播放的语音
                    self.app.speech_handler.stop_speaking()
                    
                    # 直接调用语音处理器播放新的语音
                    self.app.speech_handler.speak(text)
                    
                    # 更新播放按钮状态
                    self.voice_button.text = "⏹️"
                    self.voice_button.background_color = (0.9, 0.3, 0.3, 1)
                    
                    # 等待播放完成后恢复按钮状态
                    Clock.schedule_interval(self._check_sound_status, 0.5)
        except Exception as e:
            Logger.error(f"播放语音失败: {e}")
            
    def _check_sound_status(self, dt):
        """检查语音播放状态"""
        try:
            if hasattr(self.app, 'speech_handler'):
                if not self.app.speech_handler.is_speaking:
                    self.voice_button.text = "🔊"
                    self.voice_button.background_color = (0.3, 0.7, 0.9, 1)
                    return False  # 停止定时器
            return True  # 继续检查
        except:
            return False  # 出错时停止定时器

class HomeScreen(Screen):
    """主屏幕类"""
    
    is_recording = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.qa_processor = None
        self.speech_handler = None
        self.history = []
        
        # 为Windows平台添加更好的输入法支持
        if platform == 'win':
            Window.bind(on_key_down=self._on_keyboard_down)
            
            # 当窗口尺寸变化时重置输入框焦点
            Window.bind(on_resize=self._on_window_resize)
        
        # 添加定时器刷新输入框，以解决中文输入问题
        Clock.schedule_interval(self.refresh_text_input, 0.05)
        
        # 处理输入法状态
        self._ime_composition_active = False
    
    def on_pre_enter(self):
        """进入屏幕前调用"""
        # 给输入框设置焦点
        self._reset_input_focus()
    
    def _reset_input_focus(self):
        """重置输入框焦点"""
        if hasattr(self, 'ids') and hasattr(self.ids, 'input_text'):
            # 先移除焦点再设置，强制重新初始化输入法
            self.ids.input_text.focus = False
            
            # 延迟添加焦点，确保输入法正确初始化
            Clock.schedule_once(lambda dt: setattr(self.ids.input_text, 'focus', True), 0.3)
            
            # 更新输入框提示
            self.ids.input_text.hint_text = "请输入您的问题..."
    
    def _on_window_resize(self, instance, width, height):
        """窗口尺寸变化时重置输入焦点"""
        Clock.schedule_once(lambda dt: self._reset_input_focus(), 0.5)
    
    def refresh_text_input(self, dt=None):
        """刷新文本输入框
        专门为Microsoft拼音输入法优化
        增强对退格键操作的支持
        """
        if not hasattr(self, 'ids') or not hasattr(self.ids, 'input_text'):
            return
        
        # 更新发送按钮状态
        if hasattr(self.ids, 'send_button'):
            # 获取输入文本
            has_text = bool(self.ids.input_text.text and self.ids.input_text.text.strip())
            
            # 检测输入法组合状态
            in_composition = False
            if hasattr(self.ids.input_text, 'ime_composition'):
                in_composition = self.ids.input_text.ime_composition
            
            # 只有有文本且不在输入法组合状态时才启用发送按钮
            self.ids.send_button.disabled = not has_text or in_composition
            
            # 输出调试信息
            if in_composition and has_text:
                Logger.debug(f"输入法组合中: {self.ids.input_text.text}")
        
        # 确保输入框状态正确
        if hasattr(self.ids.input_text, 'canvas'):
            # 强制重绘画布
            self.ids.input_text.canvas.ask_update()
            
            # 尝试重新激活输入框
            if hasattr(self.ids.input_text, '_refresh'):
                self.ids.input_text._refresh(0)
            
            # 尝试刷新系统键盘状态
            if hasattr(Window, '_system_keyboard') and Window._system_keyboard:
                try:
                    Window._system_keyboard.refresh_keyboard()
                except:
                    pass
    
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        """处理键盘按键事件
        专门为Microsoft拼音输入法优化
        """
        # 处理keycode可能是整数或列表/元组的情况
        key_value = keycode[0] if isinstance(keycode, (list, tuple)) else keycode
        
        # 按下回车键
        if key_value == 13:  # Enter键
            if hasattr(self.ids, 'input_text') and self.ids.input_text.focus:
                # 检查是否在输入法组合状态
                if not hasattr(self.ids.input_text, 'ime_composition') or not self.ids.input_text.ime_composition:
                    self.send_message()
                    return True
                else:
                    Logger.debug("输入法组合中，忽略回车键")
                    return True
        
        # 处理输入法状态切换键
        elif key_value == 304 or (key_value == 32 and 'ctrl' in modifiers):  # Shift或Ctrl+空格
            # 可能是切换输入法，需要刷新按钮状态
            if hasattr(self, 'update_send_button_state'):
                Clock.schedule_once(lambda dt: self.update_send_button_state(), 0.1)
        
        # 检测Escape键 - 取消输入法组合
        elif key_value == 27:  # Escape键
            if hasattr(self.ids, 'input_text') and self.ids.input_text.focus and hasattr(self.ids.input_text, 'ime_composition'):
                self.ids.input_text.ime_composition = False
                if hasattr(self, 'update_send_button_state'):
                    self.update_send_button_state()
                return True
        
        return False  # 事件继续传递
    
    def set_qa_processor(self, processor):
        """设置QA处理器"""
        self.qa_processor = processor
    
    def set_speech_handler(self, handler):
        """设置语音处理器"""
        self.speech_handler = handler
    
    def send_message(self):
        """发送消息
        专门为Microsoft拼音输入法优化
        """
        try:
            # 检查组件是否存在
            if not hasattr(self.ids, 'input_text') or not hasattr(self.ids, 'send_button'):
                Logger.error("组件不存在，无法发送消息")
                return
            
            # 检查是否在输入法组合状态
            in_composition = False
            if hasattr(self.ids.input_text, 'ime_composition'):
                in_composition = self.ids.input_text.ime_composition
            
            # 如果在输入法组合状态，不发送消息
            if in_composition:
                Logger.warning("在输入法组合状态中，等待组合完成")
                # 显示提示文本
                self.ids.send_button.text = "选字中"
                # 延迟恢复按钮文本
                Clock.schedule_once(lambda dt: setattr(self.ids.send_button, 'text', '发送'), 1.5)
                return
            
            # 获取文本内容
            text = self.ids.input_text.text.strip()
            if not text:
                return
            
            # 停止当前正在播放的语音（新增）
            if self.speech_handler:
                self.speech_handler.stop_speaking()
            
            # 记录发送的文本
            Logger.info(f"发送消息: {text}")
            
            # 添加消息到聊天窗口
            self.add_message_to_chat(text, is_user=True)
            
            # 清空输入框
            self.ids.input_text.text = ""
            
            # 处理用户消息
            self.process_user_message(text)
            
            # 禁用发送按钮
            self.ids.send_button.disabled = True
            
            # 0.5秒后重新启用发送按钮
            Clock.schedule_once(lambda dt: setattr(self.ids.send_button, 'disabled', False), 0.5)
            
            # 重新聚焦输入框，准备下一次输入
            Clock.schedule_once(lambda dt: setattr(self.ids.input_text, 'focus', True), 0.1)
        except Exception as e:
            Logger.error(f"发送消息时出错: {e}")
            # 确保发送按钮可用
            if hasattr(self.ids, 'send_button'):
                self.ids.send_button.disabled = False
    
    def process_user_message(self, text):
        """处理用户消息"""
        # 确保QA处理器已初始化
        if not self.qa_processor:
            Logger.error("QA处理器未初始化")
            self.show_response("系统尚未准备好，请稍后再试...")
            return
        
        # 停止之前的语音播放
        if self.speech_handler:
            self.speech_handler.stop_speaking()
        
        # 记录到历史
        self.history.append(UserMessage(text))
        
        # 显示思考中指示器
        self.show_thinking_indicator()
        
        # 启动后台线程处理
        thread = Thread(target=self._process_in_background, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _process_in_background(self, text):
        """后台处理用户消息
        专门增强对银行业务问题的处理
        """
        try:
            # 使用QA处理器处理查询
            Logger.info(f"处理用户查询: {text}")
            
            # 检查是否是银行业务相关问题
            is_banking_related = self._is_banking_query(text)
            
            # 使用增强的处理器处理查询
            response = self.qa_processor.process_query(text)
            
            # 为银行业务问题添加专业提示
            if is_banking_related and "很抱歉" not in response and "无法" not in response:
                # 添加银行业务免责声明
                disclaimer = "\n\n(注：以上信息仅供参考，具体业务请以银行官方政策为准。)"
                response += disclaimer
            
            # 在主线程中显示回复
            Clock.schedule_once(lambda dt: self.show_response(response), 0)
        except Exception as e:
            # 处理异常
            Logger.error(f"处理消息时出错: {str(e)}")
            error_msg = "抱歉，处理您的问题时遇到了错误，请稍后再试。"
            Clock.schedule_once(lambda dt: self.show_response(error_msg), 0)
    
    def _is_banking_query(self, text):
        """检查是否是银行业务相关查询"""
        # 银行业务关键词
        banking_keywords = [
            "银行", "账户", "卡", "存款", "取款", "转账", "汇款", "贷款", 
            "信用卡", "储蓄", "理财", "利率", "利息", "手续费", "ATM", 
            "开户", "销户", "余额", "密码", "网银", "手机银行", "支付", 
            "房贷", "车贷", "消费贷", "按揭", "抵押", "信用", "征信",
            "基金", "保险", "外汇", "汇率", "定期", "活期", "大额存单"
        ]
        
        # 检查文本中是否包含银行业务关键词
        for keyword in banking_keywords:
            if keyword in text:
                return True
        
        return False
    
    def show_thinking_indicator(self):
        """显示思考中指示器"""
        thinking_box = BoxLayout(orientation='horizontal', 
                                 size_hint_y=None, 
                                 height=dp(40),
                                 padding=[dp(10), dp(5)])
        
        thinking_label = Label(text="AI思考中...", 
                               size_hint_x=0.3,
                               color=(0.5, 0.5, 0.5, 1))
        
        thinking_box.add_widget(thinking_label)
        
        # 将思考指示器添加到聊天区域
        self.ids.chat_container.add_widget(thinking_box)
        self.ids.chat_container.height += thinking_box.height
        self.ids.chat_scroll.scroll_to(thinking_box)
        
        # 保存引用以便移除
        self.thinking_indicator = thinking_box
    
    def show_response(self, response):
        """显示AI回复"""
        # 移除思考指示器
        if hasattr(self, 'thinking_indicator'):
            self.ids.chat_container.remove_widget(self.thinking_indicator)
            self.ids.chat_container.height -= self.thinking_indicator.height
            delattr(self, 'thinking_indicator')
        
        # 确保回复文本不为空
        if not response or response.strip() == "":
            response = "抱歉，未能生成有效回复。请重新提问。"
        
        # 添加AI回复到聊天区域
        self.add_message_to_chat(response, is_user=False)
        
        # 保存到历史记录
        self.history.append({"text": response, "is_user": False, "timestamp": datetime.now()})
        
        # 如果启用了语音输出且自动播放设置开启，延迟1秒后播放语音
        if self.speech_handler and hasattr(self.speech_handler, 'voice_output_enabled'):
            if self.speech_handler.voice_output_enabled and hasattr(self.speech_handler, 'auto_play'):
                if self.speech_handler.auto_play:
                    Logger.info("延迟1秒后自动播放语音回复")
                    self.speech_handler.speak(response, delay=1.0)  # 延迟1秒播放
    
    def add_message_to_chat(self, text, is_user=True):
        """添加消息到聊天区域"""
        # 创建消息气泡
        message_bubble = MessageBubble(text, is_user=is_user)
        
        # 添加到聊天容器
        self.ids.chat_container.add_widget(message_bubble)
        
        # 调整聊天容器高度
        self.ids.chat_container.height += message_bubble.height
        
        # 滚动到底部
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
    
    def scroll_to_bottom(self):
        """滚动到聊天底部"""
        if self.ids.chat_container.children:
            self.ids.chat_scroll.scroll_to(self.ids.chat_container.children[0])
    
    def start_voice_input(self):
        """开始语音输入"""
        if not self.speech_handler:
            return
        
        self.is_recording = True
        self.ids.mic_button.text = "录音中"
        self.ids.mic_button.background_color = (0.8, 0.2, 0.2, 1)
        
        # 开始录音
        self.speech_handler.start_recording()
    
    def stop_voice_input(self):
        """停止语音输入"""
        if not self.speech_handler or not self.is_recording:
            return
        
        self.is_recording = False
        self.ids.mic_button.text = "语音"
        self.ids.mic_button.background_color = (0.8, 0.2, 0.2, 1)
        
        # 停止录音并获取文本
        recognized_text = self.speech_handler.stop_recording_and_recognize()
        
        if recognized_text:
            # 设置到输入框
            self.ids.input_text.text = recognized_text
            # 自动发送消息
            Logger.info(f"语音识别结果: {recognized_text}")
            self.send_message()
        else:
            # 显示语音识别失败提示
            self.ids.input_text.hint_text = "未能识别语音，请重试..."
            Logger.warning("语音识别失败或无结果")
            
            # 尝试检查麦克风状态
            if hasattr(self.speech_handler, 'microphone') and not self.speech_handler.microphone:
                Logger.error("麦克风未初始化或不可用")
                self.ids.input_text.hint_text = "麦克风不可用，请检查设备..."
    
    def update_send_button_state(self, *args):
        """根据输入状态更新发送按钮状态
        专门为Microsoft拼音输入法优化
        """
        # 检查组件是否存在
        if not hasattr(self.ids, 'input_text') or not hasattr(self.ids, 'send_button'):
            return
        
        # 获取输入文本和输入法状态
        has_text = bool(self.ids.input_text.text.strip())
        in_composition = hasattr(self.ids.input_text, 'ime_composition') and self.ids.input_text.ime_composition
        
        # 只有有文本且不在输入法组合状态时才启用发送按钮
        self.ids.send_button.disabled = not has_text or in_composition
        
        # 记录日志
        if in_composition:
            Logger.debug(f"输入法组合中，发送按钮禁用: {self.ids.input_text.text}")
        
        # 确保输入框获得焦点
        if self.ids.input_text.focus == False and in_composition:
            self.ids.input_text.focus = True 
    
    # 新增：控制语音播放的功能
    def toggle_voice_output(self):
        """切换语音输出状态"""
        if not self.speech_handler:
            return
            
        current_state = self.speech_handler.voice_output_enabled
        self.speech_handler.set_voice_output_enabled(not current_state)
        
        # 更新界面状态（如果有相关控件）
        if hasattr(self.ids, 'voice_toggle'):
            self.ids.voice_toggle.text = "语音:开" if self.speech_handler.voice_output_enabled else "语音:关"
    
    def toggle_auto_play(self):
        """切换自动播放语音状态"""
        if not self.speech_handler or not hasattr(self.speech_handler, 'auto_play'):
            return
            
        self.speech_handler.set_auto_play(not self.speech_handler.auto_play)
        
        # 更新界面状态（如果有相关控件）
        if hasattr(self.ids, 'auto_play_toggle'):
            self.ids.auto_play_toggle.text = "自动播放:开" if self.speech_handler.auto_play else "自动播放:关" 