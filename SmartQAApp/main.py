#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能问答APP主程序
基于Kivy框架实现
"""

import os
import sys
import time

# ======== 关键环境变量 ========
# 专门针对Microsoft拼音输入法优化
os.environ['KIVY_TEXT'] = 'sdl2'  # 使用SDL2作为文本后端
os.environ['KIVY_IME'] = '1'  # 启用IME
os.environ['KIVY_NO_ARGS'] = '1'  # 禁用命令行参数处理
os.environ['KIVY_WIN_DISABLE_KEYFILTER'] = '1'  # 禁用键盘过滤
# Microsoft拼音专用设置
os.environ['KIVY_IME_FRAMEWORK'] = 'win'  # Windows输入法框架
os.environ['SDL_IME_SHOW_UI'] = '1'  # 显示输入法UI
os.environ['SDL_IME_ENABLE'] = '1'  # 启用SDL输入法
os.environ['SDL_HINT_IME_SHOW_UI'] = '1'  # SDL IME提示

# Kivy导入必须在环境变量设置之后
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.config import Config
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# ======== Kivy配置 ========
# 桌面模式配置
Config.set('kivy', 'desktop', '1')
# 使用系统键盘模式，这对输入法至关重要
Config.set('kivy', 'keyboard_mode', 'system')
# 输入相关设置
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# 禁用多重采样以避免某些GPU问题
Config.set('graphics', 'multisamples', '0')
# 保存配置并立即生效
Config.write()

# ======== 窗口设置 ========
# 设置窗口尺寸，适合输入法显示
Window.size = (540, 960)
# 启用窗口边框，这有助于输入法捕获窗口
Window.borderless = False
# 确保正确使用系统光标
Window.set_system_cursor = True

# Windows平台特殊处理
if platform == 'win':
    try:
        # 输出系统区域信息，用于调试
        import locale
        lang, encoding = locale.getdefaultlocale()
        print(f"系统区域设置: {lang}, 编码: {encoding}")
        
        # 尝试预加载输入法相关模块
        try:
            import ctypes
            # 获取默认IME窗口
            default_ime = ctypes.windll.imm32.ImmGetDefaultIMEWnd(0)
            print(f"系统默认IME窗口: {default_ime}")
        except Exception as e:
            print(f"获取IME信息失败: {e}")
    except Exception as e:
        print(f"获取系统信息出错: {e}")

# 导入自定义模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.home_screen import HomeScreen
from ui.history_screen import HistoryScreen
from ui.settings_screen import SettingsScreen
from models.qa_processor import QAProcessor
from utils.speech_handler import SpeechHandler

class ChineseTextInput(TextInput):
    """专为输入法优化的文本输入组件"""
    
    def __init__(self, **kwargs):
        # 基础属性设置
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('use_bubble', True)
        kwargs.setdefault('use_handles', True)
        kwargs.setdefault('allow_copy', True)
        kwargs.setdefault('input_type', 'text')
        
        # 中文输入相关设置
        kwargs.setdefault('font_name', 'SimHei')  # 确保使用支持中文的字体
        kwargs.setdefault('cursor_width', '2sp')
        
        # 父类初始化
        super(ChineseTextInput, self).__init__(**kwargs)
        
        # 状态变量
        self.ime_composition = False
        self.prev_text = self.text
        self.last_change_time = time.time()
        
        # Windows平台专用处理
        if platform == 'win':
            # 事件绑定
            self.bind(focus=self._on_focus)
            self.bind(text=self._on_text)
            
            # 专门绑定窗口级键盘事件用于捕获删除键
            Window.bind(on_key_down=self._on_keypress)
            
            # 定时器 - 频繁刷新保证输入法显示
            Clock.schedule_interval(self._refresh, 0.02)
    
    def _on_focus(self, instance, value):
        """处理焦点变化事件"""
        if value:  # 获得焦点
            # 重置状态
            self.ime_composition = False
            # 主动激活输入法
            self._activate_ime()
        else:
            # 失去焦点时重置状态
            self.ime_composition = False
    
    def _on_text(self, instance, value):
        """处理文本变化事件，增强对删除操作的支持"""
        if value != self.prev_text:
            # 检测是否是删除操作
            if len(value) < len(self.prev_text) and self.prev_text.startswith(value):
                # 删除操作，不设置组合状态
                self.ime_composition = False
                Logger.debug("检测到删除操作，结束输入法组合状态")
            else:
                # 可能是输入操作，判断是否包含中文
                if any(ord(c) > 127 for c in value):
                    # 中文字符，结束组合状态
                    self.ime_composition = False
                else:
                    # 可能是拼音输入，设为组合状态
                    self.ime_composition = True
        
        # 保存当前文本
        self.prev_text = value
        
        # 刷新显示
        self._refresh(0)
    
    def _on_keypress(self, window, keycode, scancode, codepoint, modifiers):
        """处理键盘按键，特别是删除键"""
        if not self.focus:
            return False
            
        # 处理keycode可能是整数或列表/元组的情况
        key = keycode[0] if isinstance(keycode, (list, tuple)) else keycode
        
        # 处理退格键和删除键
        if key in (8, 127):  # Backspace或Delete键
            # 确保退出组合状态
            if self.ime_composition:
                self.ime_composition = False
                Logger.info("删除键按下，结束输入法组合状态")
                
            # 如果有文本，直接删除一个字符
            if len(self.text) > 0:
                # 保存光标位置
                cursor_pos = self.cursor_index()
                if key == 8 and cursor_pos > 0:  # Backspace键
                    # 手动删除字符
                    new_text = self.text[:cursor_pos-1] + self.text[cursor_pos:]
                    self.text = new_text
                    # 重新设置光标位置
                    self.cursor = (cursor_pos - 1, 0)
                    # 更新内部状态
                    self.prev_text = self.text
                    Logger.info(f"直接删除前一个字符，新文本: '{self.text}'")
                    # 立即刷新
                    self._refresh(0)
                    return True
                elif key == 127 and cursor_pos < len(self.text):  # Delete键
                    # 手动删除光标后的字符
                    new_text = self.text[:cursor_pos] + self.text[cursor_pos+1:]
                    self.text = new_text
                    # 更新内部状态
                    self.prev_text = self.text
                    Logger.info(f"直接删除后一个字符，新文本: '{self.text}'")
                    # 立即刷新
                    self._refresh(0)
                    return True
        
        return False  # 继续传递事件
        
    def _activate_ime(self):
        """激活输入法"""
        if platform == 'win':
            try:
                import ctypes
                
                # 获取窗口句柄
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
            except Exception as e:
                Logger.warning(f"激活输入法失败: {e}")
    
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
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """处理键盘按键事件，增强对删除键的支持"""
        # 处理keycode可能是整数或列表/元组的情况
        key = keycode[0] if isinstance(keycode, (list, tuple)) else keycode
        
        # 退格键和删除键处理
        if key in (8, 127) and self.ime_composition:  # Backspace或Delete键
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
        
        # 回车键处理
        elif key == 13:  # Enter键
            if not self.multiline and not self.ime_composition:
                # 回车处理
                return False
            # 在组合状态下阻止回车键
            if self.ime_composition:
                return True
        
        # 重置组合状态的键
        elif key == 27:  # Escape键
            self.ime_composition = False
            self._refresh(0)
            return True
        
        # 切换输入法的键
        elif key == 304 or (key == 32 and 'ctrl' in modifiers):  # Shift或Ctrl+Space
            # 可能是切换输入法，需要重置状态
            self.ime_composition = False
            self._activate_ime()
        
        # 调用父类处理
        return super(ChineseTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
    
    def do_backspace(self, from_undo=False, mode='bkspc'):
        """增强删除键处理"""
        # 确保退出组合状态
        if self.ime_composition:
            self.ime_composition = False
            Logger.info("删除操作前结束输入法组合状态")
        
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

class SmartQAApp(App):
    """智能问答APP主类"""
    
    def build(self):
        """构建APP界面"""
        # 输出系统信息，帮助调试
        self._print_system_info()
        
        # 加载中文字体
        self._load_fonts()
        
        # 加载KV文件
        Builder.load_file(os.path.join(os.path.dirname(__file__), 'ui', 'smartqa.kv'))
        
        # 初始化屏幕管理器
        self.screen_manager = ScreenManager()
        
        # 添加各个屏幕
        self.home_screen = HomeScreen(name='home')
        self.history_screen = HistoryScreen(name='history')
        self.settings_screen = SettingsScreen(name='settings')
        
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.history_screen)
        self.screen_manager.add_widget(self.settings_screen)
        
        # 初始化QA处理器和语音处理器
        self.qa_processor = QAProcessor()
        self.speech_handler = SpeechHandler()
        
        # 将处理器注入到各屏幕
        self.home_screen.set_qa_processor(self.qa_processor)
        self.home_screen.set_speech_handler(self.speech_handler)
        
        # 切换到主屏幕
        self.screen_manager.current = 'home'
        
        # 设置输入法的额外支持
        Clock.schedule_once(self._post_keyboard_setup, 1)
        
        return self.screen_manager
    
    def _post_keyboard_setup(self, dt):
        """专门为Microsoft拼音输入法优化的设置"""
        Logger.info("配置Microsoft拼音输入法支持")
        
        # 尝试启动SDL文本输入
        try:
            import ctypes
            # SDL_StartTextInput在win32环境下相当于调用ImmSetOpenStatus
            if hasattr(Window, '_sdl2_window') and hasattr(Window._sdl2_window, 'SDL_StartTextInput'):
                Window._sdl2_window.SDL_StartTextInput()
                Logger.info("已启动SDL文本输入")
        except Exception as e:
            Logger.warning(f"无法启动SDL文本输入: {e}")
        
        if platform == 'win':
            try:
                import ctypes
                from ctypes import wintypes
                
                # 获取前台窗口句柄
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    Logger.info(f"前台窗口句柄: {hwnd}")
                    
                    # Microsoft拼音专用API常量
                    WM_INPUTLANGCHANGEREQUEST = 0x0050
                    INPUTLANGCHANGE_SYSCHARSET = 0x0001
                    KL_NAMELENGTH = 9
                    
                    # 获取IME上下文
                    ime_context = ctypes.windll.imm32.ImmGetContext(hwnd)
                    if ime_context:
                        # 确保IME开启
                        if not ctypes.windll.imm32.ImmGetOpenStatus(ime_context):
                            ctypes.windll.imm32.ImmSetOpenStatus(ime_context, 1)
                            Logger.info("已开启输入法")
                        
                        # 释放IME上下文
                        ctypes.windll.imm32.ImmReleaseContext(hwnd, ime_context)
                    
                    # 尝试激活中文输入法
                    try:
                        # 获取系统中可用的键盘布局
                        buf_size = ctypes.windll.user32.GetKeyboardLayoutList(0, None)
                        if buf_size > 0:
                            layouts = (wintypes.HKL * buf_size)()
                            ctypes.windll.user32.GetKeyboardLayoutList(buf_size, layouts)
                            
                            # 输出所有可用键盘布局，帮助诊断
                            Logger.info("系统中的键盘布局:")
                            for i, layout in enumerate(layouts):
                                layout_id = layout & 0xFFFF
                                Logger.info(f"  {i}: {hex(layout)} (ID: {hex(layout_id)})")
                            
                            # 寻找中文键盘布局
                            chinese_layout = None
                            for layout in layouts:
                                layout_id = layout & 0xFFFF
                                # 0x0804: 简体中文, 0x0404: 繁体中文
                                if layout_id == 0x0804 or layout_id == 0x0404:
                                    chinese_layout = layout
                                    break
                            
                            # 如果找到中文布局，激活它
                            if chinese_layout:
                                # 切换到中文键盘布局
                                result = ctypes.windll.user32.ActivateKeyboardLayout(chinese_layout, 0)
                                Logger.info(f"激活中文键盘布局结果: {result}")
                                
                                # 请求系统切换输入法
                                result = ctypes.windll.user32.PostMessageW(
                                    hwnd, 
                                    WM_INPUTLANGCHANGEREQUEST, 
                                    INPUTLANGCHANGE_SYSCHARSET,
                                    chinese_layout
                                )
                                Logger.info(f"发送输入法切换请求结果: {result}")
                            else:
                                Logger.warning("未找到中文键盘布局")
                                # 尝试直接加载中文布局
                                result = ctypes.windll.user32.LoadKeyboardLayoutW("00000804", 1)
                                Logger.info(f"加载中文键盘布局结果: {result}")
                    except Exception as e:
                        Logger.warning(f"激活中文布局失败: {e}")
                    
                    # 尝试模拟键盘快捷键激活输入法
                    try:
                        # 模拟按键的常量
                        KEYEVENTF_KEYDOWN = 0x0
                        KEYEVENTF_KEYUP = 0x2
                        VK_SHIFT = 0x10
                        VK_CONTROL = 0x11
                        VK_SPACE = 0x20
                        
                        # 模拟Shift键 - 常用于切换中英文
                        ctypes.windll.user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYDOWN, 0)
                        ctypes.windll.user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
                        
                        # 短暂延迟
                        import time
                        time.sleep(0.1)
                        
                        # 模拟Ctrl+Space - 常用于切换中英文
                        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYDOWN, 0)
                        ctypes.windll.user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYDOWN, 0)
                        ctypes.windll.user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)
                        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
                        
                        Logger.info("已模拟键盘快捷键激活输入法")
                    except Exception as e:
                        Logger.warning(f"模拟按键激活输入法失败: {e}")
                
                # 设置延迟重新激活输入法
                Clock.schedule_once(self._delayed_activate_input, 0.5)
                
            except Exception as e:
                Logger.error(f"配置输入法支持时出错: {e}")
        
        # 添加窗口级文本输入事件转发
        Window.bind(on_textinput=self._on_window_textinput)
    
    def _delayed_activate_input(self, dt):
        """延迟激活输入法，确保窗口已完全初始化"""
        # 确保home_screen已初始化
        if hasattr(self, 'home_screen') and hasattr(self.home_screen, 'ids'):
            # 给文本输入框焦点
            if hasattr(self.home_screen.ids, 'input_text'):
                self.home_screen.ids.input_text.focus = True
                
                # 尝试激活输入法
                if hasattr(self.home_screen.ids.input_text, '_activate_ime'):
                    try:
                        self.home_screen.ids.input_text._activate_ime()
                        Logger.info("延迟激活输入法成功")
                    except Exception as e:
                        Logger.warning(f"延迟激活输入法失败: {e}")
    
    def _on_window_textinput(self, window, text):
        """处理窗口级别的文本输入事件"""
        # 文本输入事件可能来自输入法
        if hasattr(self, 'home_screen') and hasattr(self.home_screen, 'ids'):
            if hasattr(self.home_screen.ids, 'input_text') and self.home_screen.ids.input_text.focus:
                # 中文字符检测
                is_chinese = any(ord(c) > 127 for c in text)
                if is_chinese:
                    Logger.info(f"窗口级中文输入: {text}")
                    
                # 尝试将文本转发给当前焦点的输入框
                self.home_screen.ids.input_text.insert_text(text)
                return True
        
        return False
    
    def _print_system_info(self):
        """打印系统信息"""
        Logger.info(f"系统平台: {platform}")
        Logger.info(f"Python版本: {sys.version}")
        Logger.info(f"Kivy版本: {kivy.__version__}")
        Logger.info(f"IME环境变量: KIVY_TEXT={os.environ.get('KIVY_TEXT', '未设置')}")
        
        if platform == 'win':
            import locale
            Logger.info(f"系统区域设置: {locale.getdefaultlocale()}")
            try:
                import ctypes
                Logger.info(f"活动IME: {ctypes.windll.imm32.ImmGetDefaultIMEWnd(0)}")
            except:
                Logger.info("无法获取IME信息")
    
    def on_start(self):
        """APP启动时执行"""
        # 初始化资源和模型
        Clock.schedule_once(self._init_resources, 0.5)
        
        # 为Windows系统设置输入相关事件
        if platform == 'win':
            Window.bind(on_key_down=self._on_key_down)
            Clock.schedule_interval(self._check_ime_state, 1)
    
    def _check_ime_state(self, dt):
        """定期检查并输出IME状态（仅调试用）"""
        if hasattr(self, 'home_screen') and hasattr(self.home_screen, 'ids'):
            input_widget = self.home_screen.ids.input_text
            if input_widget and input_widget.focus:
                Logger.debug(f"IME状态: 组合={input_widget.ime_composition}, 光标={input_widget.cursor_index()}")
    
    def _on_key_down(self, window, keycode, scancode, codepoint, modifiers):
        """全局按键处理，用于调试和特殊操作"""
        # Ctrl+Shift+R 重新加载配置
        if 'ctrl' in modifiers and 'shift' in modifiers and scancode == 82:  # R键
            Logger.info("用户触发配置重载")
            self._reload_ime_config()
            return True
        return False
    
    def _reload_ime_config(self):
        """重新加载IME配置"""
        # 刷新输入框
        if hasattr(self, 'home_screen') and hasattr(self.home_screen, 'ids'):
            input_widget = self.home_screen.ids.input_text
            if input_widget:
                # 强制重新加载
                input_widget.focus = False
                Clock.schedule_once(lambda dt: setattr(input_widget, 'focus', True), 0.1)
                Logger.info("已重新加载输入法配置")
    
    def _init_resources(self, dt):
        """初始化资源（模型加载等）"""
        # 这里可以异步加载模型等资源
        self.qa_processor.initialize()
        self.speech_handler.initialize()
    
    def on_pause(self):
        """APP暂停时执行"""
        return True
    
    def on_resume(self):
        """APP恢复时执行"""
        pass
    
    def on_stop(self):
        """APP停止时执行"""
        # 清理资源
        self.qa_processor.cleanup()
        self.speech_handler.cleanup()

    def _load_fonts(self):
        """加载字体"""
        fonts_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
        
        # 确保字体目录存在
        if not os.path.exists(fonts_path):
            os.makedirs(fonts_path)
        
        # 添加字体路径
        resource_add_path(fonts_path)
        
        # 是否成功加载字体的标志
        font_loaded = False
        
        # 尝试注册系统中的字体（Windows系统）
        if platform == 'win':
            # 尝试使用系统中的中文字体
            system_fonts = [
                ('SimHei', 'C:/Windows/Fonts/simhei.ttf'),  # 黑体
                ('SimSun', 'C:/Windows/Fonts/simsun.ttc'),  # 宋体
                ('Microsoft YaHei', 'C:/Windows/Fonts/msyh.ttc'),  # 微软雅黑
                ('DengXian', 'C:/Windows/Fonts/dengxian.ttf')  # 等线体
            ]
            
            for font_name, font_path in system_fonts:
                if os.path.exists(font_path):
                    try:
                        LabelBase.register(font_name, font_path)
                        # 设置默认字体
                        LabelBase.register(name='Roboto', 
                                         fn_regular=font_path,
                                         fn_bold=font_path,
                                         fn_italic=font_path,
                                         fn_bolditalic=font_path)
                        print(f"已加载中文字体: {font_name}")
                        font_loaded = True
                        break
                    except Exception as e:
                        print(f"加载字体 {font_name} 失败: {e}")
        elif platform == 'linux':
            # Linux系统字体
            system_fonts = [
                ('WenQuanYi', '/usr/share/fonts/wenquanyi/wqy-microhei.ttc'),
                ('Noto Sans CJK', '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc')
            ]
            
            for font_name, font_path in system_fonts:
                if os.path.exists(font_path):
                    try:
                        LabelBase.register(font_name, font_path)
                        LabelBase.register(name='Roboto', fn_regular=font_path)
                        print(f"已加载中文字体: {font_name}")
                        font_loaded = True
                        break
                    except Exception as e:
                        print(f"加载字体 {font_name} 失败: {e}")
        elif platform == 'macosx':
            # macOS系统字体
            system_fonts = [
                ('PingFang', '/System/Library/Fonts/PingFang.ttc'),
                ('Hiragino Sans GB', '/Library/Fonts/Hiragino Sans GB.ttc')
            ]
            
            for font_name, font_path in system_fonts:
                if os.path.exists(font_path):
                    try:
                        LabelBase.register(font_name, font_path)
                        LabelBase.register(name='Roboto', fn_regular=font_path)
                        print(f"已加载中文字体: {font_name}")
                        font_loaded = True
                        break
                    except Exception as e:
                        print(f"加载字体 {font_name} 失败: {e}")
        
        # 如果没有成功加载系统字体，尝试使用备用方案
        if not font_loaded:
            print("无法加载系统中文字体，尝试使用备用方案...")
            
            # 注册默认字体，确保至少可以显示ASCII字符
            try:
                # 使用Kivy内置的Roboto字体
                print("使用Kivy内置的Roboto字体作为备用")
                
                # 对中文文本使用特殊处理
                from kivy.core.text import Label as CoreLabel
                # 修改默认字体渲染方法以支持中文
                original_render = CoreLabel.render
                
                def patched_render(self, text, *args, **kwargs):
                    # 将不支持的字符替换为问号
                    encoded_text = text.encode('ascii', 'replace').decode('ascii')
                    return original_render(self, encoded_text, *args, **kwargs)
                
                # 应用补丁
                CoreLabel.render = patched_render
            except Exception as e:
                print(f"应用字体备用方案失败: {e}")

if __name__ == '__main__':
    import kivy
    SmartQAApp().run() 