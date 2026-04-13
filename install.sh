#!/bin/bash

# API Capture Extension 安装脚本
# 使用方法: chmod +x install.sh && ./install.sh

echo "🔍 API Capture & Analyzer 扩展安装脚本"
echo "=========================================="

# 检查是否在正确的目录
if [ ! -f "manifest.json" ]; then
    echo "❌ 错误: 请在扩展目录中运行此脚本"
    exit 1
fi

# 检查Chrome是否安装
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  警告: 未检测到Chrome或Chromium浏览器"
    echo "   请确保已安装Chrome浏览器"
fi

# 创建图标目录
echo "📁 创建图标目录..."
mkdir -p icons

# 检查图标文件
echo "🖼️  检查图标文件..."
if [ ! -f "icons/icon16.png" ] || [ ! -f "icons/icon48.png" ] || [ ! -f "icons/icon128.png" ]; then
    echo "⚠️  警告: 图标文件不完整"
    echo "   请在浏览器中打开 generate-icons.js"
    echo "   在控制台中运行 generateAllIcons() 生成图标"
    echo "   然后将下载的PNG文件放入 icons/ 文件夹"
else
    echo "✅ 图标文件检查通过"
fi

# 检查文件完整性
echo "📋 检查文件完整性..."
required_files=(
    "manifest.json"
    "background.js"
    "content.js"
    "popup.html"
    "popup.js"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 缺失"
    fi
done

# 显示安装说明
echo ""
echo "🎉 安装准备完成！"
echo ""
echo "📖 安装步骤:"
echo "1. 打开Chrome浏览器"
echo "2. 访问 chrome://extensions/"
echo "3. 开启右上角的「开发者模式」"
echo "4. 点击「加载已解压的扩展程序」"
echo "5. 选择当前目录: $(pwd)"
echo ""
echo "🚀 使用说明:"
echo "1. 安装后，访问任意网页"
echo "2. 点击浏览器工具栏中的扩展图标"
echo "3. 扩展会自动捕获网络请求"
echo "4. 在弹出窗口中查看和分析请求"
echo ""
echo "📚 更多信息请查看 README.md"
echo ""
echo "⚠️  注意: 如果图标未生成，请先运行 generate-icons.js"