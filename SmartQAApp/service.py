#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Android服务模块，用于后台运行语音识别
"""

import os
import time
from jnius import autoclass

# Android相关类导入
Service = autoclass('android.app.Service')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
Notification = autoclass('android.app.Notification')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationManager = autoclass('android.app.NotificationManager')
Context = autoclass('android.content.Context')
Build = autoclass('android.os.Build')
Uri = autoclass('android.net.Uri')

# 自定义Android服务
class SmartQAService:
    """SmartQA后台服务"""
    
    # 服务ID
    service_id = 100
    
    def __init__(self):
        # 获取当前服务
        self.service = autoclass('org.smartqa.ServiceSmartQAService').mService
        # 创建通知通道
        self.create_notification_channel()
    
    def create_notification_channel(self):
        """创建通知通道"""
        if Build.VERSION.SDK_INT >= 26:
            channel_id = "smartqa_service"
            channel_name = "SmartQA服务"
            channel_description = "SmartQA银行助手后台服务"
            importance = NotificationManager.IMPORTANCE_LOW
            
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription(channel_description)
            
            # 获取通知管理器
            nm = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            nm.createNotificationChannel(channel)
            
            return channel_id
        else:
            return "smartqa_service"
    
    def start(self):
        """启动服务"""
        # 创建前台服务通知
        channel_id = self.create_notification_channel()
        
        # 创建通知
        notification_builder = Notification.Builder(self.service)
        if Build.VERSION.SDK_INT >= 26:
            notification_builder = notification_builder.setChannelId(channel_id)
        
        # 设置通知内容
        notification_builder = notification_builder\
            .setContentTitle("SmartQA银行助手")\
            .setContentText("正在后台运行语音识别服务")\
            .setOngoing(True)
        
        # 启动前台服务
        self.service.startForeground(self.service_id, notification_builder.build())
        
        # 初始化并启动语音识别
        self.init_speech_recognition()
    
    def init_speech_recognition(self):
        """初始化语音识别"""
        try:
            # 这里可以添加初始化语音识别的代码
            pass
        except Exception as e:
            print(f"初始化语音识别失败: {e}")
    
    def stop(self):
        """停止服务"""
        # 停止前台服务
        if Build.VERSION.SDK_INT >= 24:
            self.service.stopForeground(Service.STOP_FOREGROUND_REMOVE)
        else:
            self.service.stopForeground(True)
        
        # 停止服务本身
        self.service.stopSelf()


def start_service():
    """启动服务的函数"""
    service = SmartQAService()
    service.start()
    
    # 返回服务实例以便后续操作
    return service


# 当作为主程序运行时创建服务
if __name__ == '__main__':
    start_service() 