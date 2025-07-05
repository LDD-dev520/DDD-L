/**
 * 录音和语音识别工具类
 * 提供录音功能并通过后端API进行语音识别
 */

import { speechToAnswer } from './api.js';

// 全局变量
let recorderManager = null; // 录音管理器
let recordFilePath = null;  // 录音文件路径
let isRecording = false;    // 是否正在录音
let deviceId = null;        // 设备唯一标识符

/**
 * 创建wav目录（如果需要）
 * @returns {Promise} 返回Promise
 */
export function createWavDirIfNeeded() {
  return new Promise((resolve, reject) => {
    try {
      // 检查是否有保存录音的目录
      const wavDir = `${uni.env.USER_DATA_PATH}/wav`;
      
      uni.getFileSystemManager().access({
        path: wavDir,
        success: () => {
          console.log('[Speech] wav目录已存在');
          resolve(wavDir);
        },
        fail: () => {
          // 目录不存在，创建目录
          uni.getFileSystemManager().mkdir({
            dirPath: wavDir,
            recursive: true,
            success: () => {
              console.log('[Speech] wav目录创建成功');
              resolve(wavDir);
            },
            fail: (err) => {
              console.error('[Speech] wav目录创建失败:', err);
              reject(err);
            }
          });
        }
      });
    } catch (error) {
      console.error('[Speech] 检查/创建wav目录失败:', error);
      resolve(); // 即使失败也继续执行，不影响应用启动
    }
  });
}

/**
 * 检查百度API配置
 * @returns {Promise<boolean>} 返回配置是否有效
 */
export function checkBaiduApiConfig() {
  return new Promise((resolve) => {
    // 这里只是一个模拟实现，实际应该调用API检查配置
    setTimeout(() => {
      resolve(true);
    }, 500);
  });
}

/**
 * 初始化设备唯一标识符
 * @returns {string} 设备唯一标识符
 */
export function initDeviceId() {
  if (deviceId) return deviceId;
  
  try {
    // 尝试从存储中获取设备ID
    deviceId = uni.getStorageSync('device_id');
    
    if (!deviceId) {
      // 生成一个新的设备ID
      deviceId = 'dev_' + Date.now() + '_' + Math.random().toString(36).substring(2, 10);
      uni.setStorageSync('device_id', deviceId);
    }
    
    return deviceId;
  } catch (error) {
    console.error('[Speech] 初始化设备ID失败:', error);
    // 返回一个临时ID
    return 'temp_' + Date.now();
  }
}

/**
 * 初始化录音管理器
 * @returns {RecorderManager} 录音管理器实例
 */
export function initRecorder() {
  if (!recorderManager) {
    try {
      // 创建录音管理器
      recorderManager = uni.getRecorderManager();
      
      // 标记是否已初始化事件处理器
      recorderManager._eventInitialized = false;
      
      // 只在首次初始化时设置事件处理器
      if (!recorderManager._eventInitialized) {
        // 设置录音结束事件监听
        const defaultStopHandler = (res) => {
          console.log('[Speech] 录音结束:', res);
          isRecording = false;
          
          // 保存录音文件路径
          if (res.tempFilePath) {
            recordFilePath = res.tempFilePath;
            console.log('[Speech] 录音文件路径:', recordFilePath);
          }
        };
        
        // 保存默认处理器供以后恢复
        recorderManager._onStopHandler = defaultStopHandler;
        recorderManager.onStop(defaultStopHandler);
        
        // 设置录音错误事件监听
        recorderManager.onError((res) => {
          console.error('[Speech] 录音错误:', res);
          isRecording = false;
          uni.showToast({
            title: '录音失败: ' + (res.errMsg || '未知错误'),
            icon: 'none'
          });
        });
        
        // 设置录音开始事件监听
        recorderManager.onStart(() => {
          console.log('[Speech] 录音开始');
          isRecording = true;
        });
        
        // 标记事件已初始化
        recorderManager._eventInitialized = true;
      }
      
      console.log('[Speech] 录音管理器初始化成功');
    } catch (error) {
      console.error('[Speech] 初始化录音管理器失败:', error);
      uni.showToast({
        title: '录音初始化失败',
        icon: 'none'
      });
      return null;
    }
  }
  
  return recorderManager;
}

/**
 * 开始录音
 * @param {Object} options 录音选项
 * @returns {Promise} 返回Promise
 */
export function startRecording(options = {}) {
  return new Promise((resolve, reject) => {
    try {
      // 确保录音管理器已初始化
      const recorder = initRecorder();
      
      // 默认录音选项
      const defaultOptions = {
        duration: 60000,         // 最长录音时长，单位ms，默认60s
        sampleRate: 16000,       // 采样率，默认16000Hz
        numberOfChannels: 1,     // 录音通道数，默认1（单声道）
        encodeBitRate: 48000,    // 编码码率，默认48000
        format: 'wav',           // 音频格式，默认wav
        frameSize: 50            // 帧大小，默认50
      };
      
      // 合并选项
      const recordOptions = Object.assign({}, defaultOptions, options);
      
      // 开始录音
      recorder.start(recordOptions);
      
      // 提供触觉反馈
      try {
        uni.vibrateShort({
          success: () => {
            console.log('[Speech] 震动反馈成功');
          }
        });
      } catch (vibError) {
        console.log('[Speech] 震动反馈失败，但不影响录音', vibError);
      }
      
      // 延迟一点时间再返回，确保录音已经开始
      setTimeout(() => {
        if (isRecording) {
          resolve();
        } else {
          reject(new Error('录音启动失败，请检查权限'));
        }
      }, 300);
    } catch (error) {
      console.error('[Speech] 开始录音失败:', error);
      reject(error);
    }
  });
}

/**
 * 停止录音
 * @returns {Promise<string>} 录音文件路径
 */
export function stopRecording() {
  return new Promise((resolve, reject) => {
    try {
      if (!recorderManager) {
        reject(new Error('录音管理器未初始化'));
        return;
      }
      
      if (!isRecording) {
        console.log('[Speech] 当前没有正在进行的录音');
        resolve(recordFilePath); // 返回上一次的录音路径
        return;
      }
      
      // 保存原始onStop处理器
      const originalOnStopHandler = recorderManager._onStopHandler;
      
      // 创建一个新的onStop处理器
      const handleStop = (res) => {
        // 恢复原始处理器（如果存在）
        if (originalOnStopHandler) {
          recorderManager.onStop(originalOnStopHandler);
        } else {
          // 如果没有原始处理器，设置一个空函数
          recorderManager.onStop(() => {
            console.log('[Speech] 录音结束');
          });
        }
        
        if (res.tempFilePath) {
          resolve(res.tempFilePath);
        } else {
          reject(new Error('未获取到录音文件路径'));
        }
      };
      
      // 保存当前处理器供以后恢复
      recorderManager._onStopHandler = handleStop;
      
      // 设置临时事件处理器
      recorderManager.onStop(handleStop);
      
      // 停止录音
      recorderManager.stop();
    } catch (error) {
      console.error('[Speech] 停止录音失败:', error);
      reject(error);
    }
  });
}

/**
 * 语音识别并获取回答
 * @param {Object} options 选项
 * @returns {Promise<Object>} 返回结果
 */
export function recognizeSpeech(options = {}) {
  return new Promise(async (resolve, reject) => {
    try {
      // 检查是否有录音文件
      if (!recordFilePath) {
        reject(new Error('没有可用的录音文件'));
        return;
      }
      
      // 显示加载提示
      try {
        uni.showLoading({
          title: '正在处理语音...',
          mask: true
        });
      } catch (e) {}
      
      // 检查文件是否存在
      try {
        const fileInfo = await new Promise((resolveFI, rejectFI) => {
          uni.getFileInfo({
            filePath: recordFilePath,
            success: (res) => resolveFI(res),
            fail: (err) => rejectFI(err)
          });
        });
        
        console.log('[Speech] 录音文件信息:', fileInfo);
        
        // 检查文件大小，太小的文件可能是录音失败
        if (fileInfo.size < 1000) {
          reject(new Error('录音文件太小，可能录音失败'));
          return;
        }
        
        try {
          // 调用API进行语音识别并获取回答
          const result = await speechToAnswer(recordFilePath, options);
          
          // 隐藏加载提示
          try {
            uni.hideLoading();
          } catch (e) {}
          
          console.log('[Speech] 语音识别结果:', result);
          resolve(result);
        } catch (apiError) {
          try {
            uni.hideLoading();
          } catch (e) {}
          console.error('[Speech] API调用失败:', apiError);
          reject(apiError);
        }
      } catch (fileError) {
        try {
          uni.hideLoading();
        } catch (e) {}
        console.error('[Speech] 检查文件失败:', fileError);
        reject(new Error('检查录音文件失败'));
      }
    } catch (error) {
      // 隐藏加载提示
      try {
        uni.hideLoading();
      } catch (e) {}
      
      console.error('[Speech] 语音识别失败:', error);
      reject(error);
    }
  });
}

/**
 * 获取录音状态
 * @returns {boolean} 是否正在录音
 */
export function isRecordingActive() {
  return isRecording;
}

/**
 * 获取当前录音文件路径
 * @returns {string|null} 录音文件路径
 */
export function getRecordFilePath() {
  return recordFilePath;
}

/**
 * 检查文件是否存在
 * @param {string} filePath 文件路径
 * @returns {Promise<boolean>} 文件是否存在
 */
export function checkFileExists(filePath) {
  return new Promise((resolve) => {
    uni.getFileInfo({
      filePath: filePath,
      success: () => {
        resolve(true);
      },
      fail: () => {
        resolve(false);
      }
    });
  });
}

/**
 * 列出录音文件
 * @returns {Promise<Array>} 录音文件列表
 */
export function listRecordingFiles() {
  return new Promise((resolve) => {
    // 这里只是一个模拟实现，实际应该调用本地存储或文件系统API
    resolve([]);
  });
}

/**
 * 删除录音文件
 * @param {string} fileName 文件名
 * @returns {Promise<boolean>} 是否删除成功
 */
export function deleteRecordingFile(fileName) {
  return new Promise((resolve) => {
    // 这里只是一个模拟实现，实际应该调用文件系统API
    resolve(true);
  });
}

/**
 * 语音识别
 * @param {string} filePath 录音文件路径
 * @returns {Promise<Object>} 返回识别结果
 */
export function recognizeVoice(filePath) {
  return new Promise(async (resolve, reject) => {
    try {
      if (!filePath) {
        filePath = recordFilePath;
      }
      
      if (!filePath) {
        throw new Error('没有可用的录音文件');
      }
      
      // 检查文件是否存在
      const fileExists = await checkFileExists(filePath);
      if (!fileExists) {
        throw new Error('录音文件不存在');
      }
      
      console.log('[Speech] 开始语音识别, 文件路径:', filePath);
      
      // 上传文件到服务器进行识别
      uni.uploadFile({
        url: 'http://localhost:5000/api/speech/recognize',
        filePath: filePath,
        name: 'audio',
        header: {
          'device-id': deviceId || initDeviceId()
        },
        success: (uploadRes) => {
          try {
            // 解析返回的JSON
            const result = JSON.parse(uploadRes.data);
            
            if (result.success) {
              console.log('[Speech] 语音识别成功:', result);
              resolve(result);
            } else {
              console.error('[Speech] 语音识别失败:', result);
              reject(new Error(result.error || '语音识别失败'));
            }
          } catch (parseError) {
            console.error('[Speech] 解析识别结果失败:', parseError);
            reject(new Error('解析识别结果失败'));
          }
        },
        fail: (err) => {
          console.error('[Speech] 上传录音文件失败:', err);
          reject(new Error(err.errMsg || '上传录音文件失败'));
        }
      });
    } catch (error) {
      console.error('[Speech] 语音识别过程出错:', error);
      reject(error);
    }
  });
} 