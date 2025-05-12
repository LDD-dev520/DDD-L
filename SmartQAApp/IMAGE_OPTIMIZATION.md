# SmartQA银行助手 - 图片优化指南

当前项目使用的图片文件较大（icon.jpg ~ 4.3MB，splash.jpg ~ 4.8MB），这会导致APK文件体积过大。为了优化应用性能和用户体验，建议优化这些图片。

## 为什么需要优化图片

1. **减少APK文件大小**：更小的APK安装更快，占用更少存储空间
2. **加快应用启动时间**：小图片加载更快，应用启动更迅速
3. **降低内存使用**：大图片会占用大量内存，可能导致应用在低端设备上崩溃

## 图片大小建议

根据Android开发最佳实践，建议使用以下大小和格式：

1. **应用图标**：
   - 建议尺寸：144x144像素
   - 建议格式：PNG（支持透明背景）
   - 建议文件大小：不超过100KB

2. **启动画面**：
   - 建议尺寸：480x800像素（16:9比例）
   - 建议格式：JPG或PNG
   - 建议文件大小：不超过200KB

## 优化方法

### 方法1：使用在线图片压缩工具

1. 访问在线图片压缩工具：
   - https://tinypng.com/
   - https://squoosh.app/
   - https://www.iloveimg.com/compress-image

2. 上传当前的大图片文件并进行压缩
3. 下载压缩后的图片并替换到项目的assets目录中

### 方法2：使用图片编辑软件

1. 使用Photoshop、GIMP或其他图片编辑软件打开图片
2. 调整图片尺寸到推荐大小
3. 导出为适当格式，设置适当的压缩级别（JPG：70-80%质量通常足够）

### 方法3：使用命令行工具

如果您熟悉命令行，可以使用以下工具：

#### 使用ImageMagick（需要先安装）：

```bash
# 安装ImageMagick (Windows)
choco install imagemagick

# 调整图标大小并优化
magick assets/icon.jpg -resize 144x144 -quality 90 assets/icon_optimized.png

# 调整启动画面大小并优化
magick assets/splash.jpg -resize 480x800 -quality 80 assets/splash_optimized.jpg
```

## 其他注意事项

1. **测试不同设备**：确保优化后的图片在不同尺寸和分辨率的设备上显示良好
2. **保留原图**：在优化前备份原始图片文件
3. **图标透明度**：应用图标通常需要透明背景，最好使用PNG格式
4. **考虑不同分辨率**：可以为不同密度的屏幕准备不同尺寸的图片（hdpi, xhdpi, xxhdpi等）

## 更新图片后的步骤

完成图片优化后，请确保：

1. 更新buildozer.spec中的文件引用（如果文件名或格式有变化）
2. 更新demo_app.py中的图片路径引用
3. 重新构建APK以验证大小是否减小 