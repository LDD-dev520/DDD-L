import os
from PIL import Image

def optimize_image(input_path, output_path, max_size, quality=85):
    try:
        with Image.open(input_path) as img:
            width, height = img.size
            ratio = min(max_size[0] / width, max_size[1] / height)
            new_size = (int(width * ratio), int(height * ratio))
            
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            if output_path.lower().endswith('.png'):
                resized_img.save(output_path, optimize=True)
            else:
                resized_img.save(output_path, quality=quality, optimize=True)
            
            original_size = os.path.getsize(input_path) / 1024
            new_size = os.path.getsize(output_path) / 1024
            reduction = (1 - new_size / original_size) * 100
            
            print(f'已优化 {os.path.basename(input_path)}:')
            print(f'  原始尺寸: {width}x{height}, {original_size:.2f} KB')
            print(f'  优化尺寸: {resized_img.width}x{resized_img.height}, {new_size:.2f} KB')
            print(f'  减少: {reduction:.2f}%')
            
            return True
    except Exception as e:
        print(f'优化图片失败 {input_path}: {e}')
        return False

assets_dir = 'assets'
optimized_dir = os.path.join(assets_dir, 'optimized')
os.makedirs(optimized_dir, exist_ok=True)

icon_path = os.path.join(assets_dir, 'icon.jpg')
icon_output = os.path.join(optimized_dir, 'icon.png')
if os.path.exists(icon_path):
    print('正在优化应用图标...')
    optimize_image(icon_path, icon_output, (144, 144), 90)
else:
    print(f'找不到图标文件: {icon_path}')

splash_path = os.path.join(assets_dir, 'splash.jpg')
splash_output = os.path.join(optimized_dir, 'splash.jpg')
if os.path.exists(splash_path):
    print('正在优化启动画面...')
    optimize_image(splash_path, splash_output, (480, 800), 80)
else:
    print(f'找不到启动画面文件: {splash_path}')

print('\n优化完成！请检查 assets/optimized 目录中的图片。') 