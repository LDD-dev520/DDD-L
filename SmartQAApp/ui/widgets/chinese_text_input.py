#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中文文本输入组件
专门优化Microsoft拼音输入法支持
"""

from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.core.text import Label as CoreLabel
import time

class ChineseTextInput(TextInput):
    """专为Microsoft拼音输入法优化的文本输入组件"""
    
    def __init__(self, **kwargs):
        # 基础属性设置，针对中文输入法
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('use_bubble', True)
        kwargs.setdefault('use_handles', True)
        kwargs.setdefault('allow_copy', True)
        kwargs.setdefault('input_type', 'text')
        
        # Microsoft拼音所需的设置
        kwargs.setdefault('font_name', 'SimHei')  # 确保使用支持中文的字体
        kwargs.setdefault('cursor_width', '2sp')
        
        # 父类初始化
        super(ChineseTextInput, self).__init__(**kwargs)
        
        # 状态变量
        self.ime_composition = False
        self.prev_text = self.text
        self.last_change_time = time.time()
        self.last_key_time = time.time()
        
        # Windows平台专用处理
        if platform == 'win':
            # 事件绑定
            self.bind(focus=self._on_focus)
            self.bind(text=self._on_text)
            
            # 注册窗口级别的文本输入事件 - 关键改进
            Window.bind(on_textedit=self._on_textedit)
            Window.bind(on_textinput=self._on_textinput)
            
            # 绑定键盘事件，用于更好地捕获删除键
            Window.bind(on_key_down=self._on_keypress)
            
            # 定时器 - 频繁刷新保证输入法显示
            Clock.schedule_interval(self._refresh, 0.02)
            
            # 如果窗口大小改变，重新激活输入法
            Window.bind(on_resize=self._window_resized)
            
            # 直接激活输入法
            self._activate_ime()
    
    def _on_textedit(self, window, text):
        """处理文本编辑事件 - 跟踪输入法状态"""
        if not self.focus:
            return False
            
        Logger.debug(f"文本编辑事件: {text}")
        self.ime_composition = True
        self.last_change_time = time.time()
        
        # 刷新以确保输入法表现正确
        self._refresh(0)
        
        return True
    
    def _on_textinput(self, window, text):
        """处理文本输入事件 - 接收输入法选择的字符"""
        if not self.focus:
            return False
        
        Logger.info(f"接收到文本输入: '{text}'")
        
        # 检查是否是中文字符
        is_chinese = any(ord(c) > 127 for c in text)
        
        # 无论是否是中文字符，都直接插入
        self.insert_text(text)
        
        # 如果是中文字符，特殊处理
        if is_chinese:
            Logger.info(f"检测到中文字符: '{text}'")
            # 结束输入法组合状态
            self.ime_composition = False
        
        # 立即刷新状态
        self._refresh(0)
        
        # 返回True表示我们处理了这个事件
        return True
    
    def _on_focus(self, instance, value):
        """处理焦点变化事件"""
        if value:  # 获得焦点
            # 重置状态
            self.ime_composition = False
            # 主动激活输入法
            self._activate_ime()
            
            # 连续多次刷新，确保输入法正常显示
            for i in range(5):
                Clock.schedule_once(lambda dt: self._refresh(0), 0.1 * i)
        else:
            # 失去焦点时重置状态
            self.ime_composition = False
    
    def _on_text(self, instance, value):
        """处理文本变化事件，增强对删除操作的支持"""
        current_time = time.time()
        time_diff = current_time - self.last_change_time
        self.last_change_time = current_time
        
        # 文本有变化，更新状态
        if value != self.prev_text:
            Logger.debug(f"文本变化: '{self.prev_text}' -> '{value}'")
            
            # 检测是否为删除操作 (如果新文本是旧文本的开头部分)
            is_deletion = len(value) < len(self.prev_text) and self.prev_text.startswith(value)
            
            # 如果是删除操作，不应该启用输入法组合状态
            if is_deletion:
                Logger.debug("检测到删除操作，不启用输入法组合状态")
                self.ime_composition = False
            
            # 检测中文输入 - 如果含有中文字符则结束组合状态
            elif any(ord(c) > 127 for c in value):
                self.ime_composition = False
                Logger.debug("检测到中文字符，结束组合状态")
            else:
                # 如果是拼音输入，设置组合状态
                self.ime_composition = True
                # 短暂延迟后检查是否应结束组合状态
                Clock.schedule_once(lambda dt: self._end_composition_check(0.3), 0.3)
        
        # 保存当前文本
        self.prev_text = value
        
        # 每次输入都刷新
        self._refresh(0)
    
    def _end_composition_check(self, delay):
        """检查并结束组合状态"""
        # 如果指定时间内没有新的变化，结束组合状态
        if time.time() - self.last_change_time >= delay and self.text == self.prev_text:
            self.ime_composition = False
            Logger.debug("组合状态结束")
    
    def _activate_ime(self):
        """激活输入法"""
        if platform == 'win':
            try:
                import ctypes
                
                # 尝试获取窗口句柄
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    # 获取IME上下文
                    ime_context = ctypes.windll.imm32.ImmGetContext(hwnd)
                    if ime_context:
                        # 确保IME开启
                        if not ctypes.windll.imm32.ImmGetOpenStatus(ime_context):
                            ctypes.windll.imm32.ImmSetOpenStatus(ime_context, 1)
                        
                        # 释放IME上下文
                        ctypes.windll.imm32.ImmReleaseContext(hwnd, ime_context)
            except:
                pass
    
    def _window_resized(self, instance, width, height):
        """窗口大小变化时处理"""
        if self.focus:
            # 重新激活输入法
            Clock.schedule_once(lambda dt: self._activate_ime(), 0.5)
    
    def _refresh(self, dt):
        """刷新并确保输入法显示"""
        if not self.focus:
            return
        
        # 刷新画布和图形
        self.canvas.ask_update()
        self._trigger_update_graphics()
        
        # 确保光标可见
        if hasattr(Window, '_system_keyboard') and Window._system_keyboard:
            try:
                # 刷新系统键盘
                Window._system_keyboard.refresh_keyboard()
            except:
                pass
    
    def _on_keypress(self, instance, keycode, text, modifiers):
        """单独的键盘按键回调，用于捕获删除键"""
        # keycode是(数字, 字符串)格式
        key, key_str = keycode
        
        # 如果不是当前焦点，不处理
        if not self.focus:
            return False
        
        # 特殊处理退格键
        if key in (8, 127):  # Backspace或Delete键
            Logger.info(f"捕获删除键: {key_str}")
            
            # 强制结束输入法组合状态
            if self.ime_composition:
                self.ime_composition = False
                Logger.info("退格键按下，结束输入法组合状态")
            
            # 如果有文本，直接删除一个字符
            if len(self.text) > 0:
                # 保存光标位置
                cursor_pos = self.cursor_index()
                if cursor_pos > 0:
                    # 手动删除字符
                    new_text = self.text[:cursor_pos-1] + self.text[cursor_pos:]
                    self.text = new_text
                    # 重新设置光标位置
                    self.cursor = (cursor_pos - 1, 0)
                    # 更新内部状态
                    self.prev_text = self.text
                    Logger.info(f"直接删除字符，新文本: '{self.text}'")
                    # 立即刷新
                    self._refresh(0)
                    return True
        
        return False  # 继续传递事件
    
    def do_backspace(self, from_undo=False, mode='bkspc'):
        """增强删除键处理，确保在中文输入后也能正常删除"""
        # 记录调用信息，帮助调试
        Logger.info(f"do_backspace调用: 组合状态={self.ime_composition}, 模式={mode}")
        
        # 如果在输入法组合状态，先结束组合状态
        if self.ime_composition:
            Logger.info("删除操作前结束输入法组合状态")
            self.ime_composition = False
        
        # 如果是退格模式且有文本
        if mode == 'bkspc' and len(self.text) > 0 and self.cursor_index() > 0:
            # 手动实现退格功能，避免输入法干扰
            cursor_pos = self.cursor_index()
            # 直接删除一个字符
            new_text = self.text[:cursor_pos-1] + self.text[cursor_pos:]
            self.text = new_text
            # 重新设置光标位置
            self.cursor = (cursor_pos - 1, 0)
            # 更新内部状态
            self.prev_text = self.text
            Logger.info(f"手动实现退格，新文本: '{self.text}'")
            # 立即刷新
            self._refresh(0)
            return True
        
        # 如果不满足条件，尝试调用父类方法
        try:
            result = super(ChineseTextInput, self).do_backspace(from_undo, mode)
            # 更新状态
            self.prev_text = self.text
            self._refresh(0)
            return result
        except Exception as e:
            Logger.error(f"退格处理出错: {e}")
            return False
    
    def insert_text(self, substring, from_undo=False):
        """改进文本插入处理"""
        Logger.debug(f"插入文本: '{substring}', 组合状态: {self.ime_composition}")
        
        # 检测中文字符
        if substring and any(ord(c) > 127 for c in substring):
            # 中文字符输入，结束组合状态
            self.ime_composition = False
            Logger.info(f"插入中文字符: '{substring}', 结束组合状态")
        
        # 调用原始方法
        result = super(ChineseTextInput, self).insert_text(substring, from_undo)
        
        # 更新预存文本和状态
        self.prev_text = self.text
        
        # 立即刷新状态
        self._refresh(0)
        
        return result
    
    def _get_text_width(self, text, tab_width=None, font_name=None, font_size=None):
        """获取文本宽度，用于更准确地定位光标"""
        if not text:
            return 0
            
        if font_name is None:
            font_name = self.font_name
            
        if font_size is None:
            font_size = self.font_size
            
        try:
            label = CoreLabel(font_size=font_size, font_name=font_name)
            label.refresh()
            # 处理制表符宽度
            if tab_width and '\t' in text:
                text = text.replace('\t', ' ' * tab_width)
            return label.get_extents(text)[0]
        except Exception as e:
            # 出错时使用简单的估算方法
            return len(text) * (font_size * 0.6)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """处理键盘按键事件，增强对删除键和修改的支持"""
        # 记录最后按键时间
        self.last_key_time = time.time()
        
        # 获取实际键码和键名
        key, key_str = keycode if isinstance(keycode, (list, tuple)) else (keycode, '')
        Logger.debug(f"按键: {key} ({key_str}), 修饰键: {modifiers}")
        
        # 特殊处理229键码，这是Windows输入法的标志
        if key == 229:
            self.ime_composition = True
            Logger.debug("检测到输入法活动状态")
            return True
        
        # 如果在组合状态且按下了删除键，特殊处理
        if self.ime_composition and key in (8, 127):  # Backspace或Delete键
            Logger.info(f"在输入法组合状态下特殊处理删除键: {key_str}")
            # 结束组合状态
            self.ime_composition = False
            
            # 直接处理退格
            if key == 8 and self.cursor_index() > 0:  # Backspace
                # 手动实现退格
                cursor_pos = self.cursor_index()
                new_text = self.text[:cursor_pos-1] + self.text[cursor_pos:]
                self.text = new_text
                self.cursor = (cursor_pos - 1, 0)
                self.prev_text = self.text
                self._refresh(0)
                return True
            
            elif key == 127 and self.cursor_index() < len(self.text):  # Delete
                # 手动实现Delete键
                cursor_pos = self.cursor_index()
                new_text = self.text[:cursor_pos] + self.text[cursor_pos+1:]
                self.text = new_text
                self.prev_text = self.text
                self._refresh(0)
                return True
            
        # 特殊处理回车键
        if key == 13:  # Enter键
            if not self.multiline and not self.ime_composition:
                # 结束组合状态并传递回车事件给父级
                self.ime_composition = False
                return False
            
            # 在组合状态下阻止回车键
            if self.ime_composition:
                return True
        
        # 重置组合状态的键
        elif key == 27:  # Escape键
            self.ime_composition = False
            self._refresh(0)
            return True
        
        # 处理Shift和Ctrl+Space切换输入法的情况
        elif key == 304 or (key == 32 and 'ctrl' in modifiers):  # Shift键或Ctrl+Space
            # 可能是切换输入法，重置状态
            self.ime_composition = False
            self._activate_ime()
        
        # 调用原始方法
        return super(ChineseTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers) 