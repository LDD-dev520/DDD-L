#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Android启动接收器模块，用于在设备启动时自动启动SmartQA服务
"""

from jnius import autoclass

# Android相关类
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Context = autoclass('android.content.Context')
String = autoclass('java.lang.String')
BroadcastReceiver = autoclass('android.content.BroadcastReceiver')

# SmartQA服务
ServiceIntent = autoclass('android.content.Intent')

class BootReceiver(BroadcastReceiver):
    """启动接收器"""
    
    def __init__(self):
        super(BootReceiver, self).__init__()
    
    def onReceive(self, context, intent):
        """接收启动消息"""
        action = intent.getAction()
        if String('android.intent.action.BOOT_COMPLETED').equals(action):
            # 创建启动服务的Intent
            service_intent = ServiceIntent(context, autoclass('org.smartqa.ServiceSmartQAService'))
            
            # 启动服务
            if autoclass('android.os.Build$VERSION').SDK_INT >= 26:
                context.startForegroundService(service_intent)
            else:
                context.startService(service_intent) 