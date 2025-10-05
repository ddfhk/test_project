#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Allure报告诊断工具
用于检查报告完整性和解决加载问题
"""

import os
import json
import zipfile
from datetime import datetime

def check_report_structure(report_dir):
    """检查报告目录结构"""
    print("=" * 60)
    print("📊 Allure报告结构检查")
    print("=" * 60)
    
    if not os.path.exists(report_dir):
        print(f"❌ 报告目录不存在: {report_dir}")
        return False
    
    print(f"✅ 报告目录存在: {report_dir}")
    
    # 检查必需的文件和目录
    required_files = [
        'index.html',
        'app.js', 
        'styles.css',
        'favicon.ico'
    ]
    
    required_dirs = [
        'data',
        'widgets',
        'plugins',
        'history'
    ]
    
    print("\n📁 检查必需文件:")
    for file in required_files:
        file_path = os.path.join(report_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} - 缺失")
    
    print("\n📂 检查必需目录:")
    for dir_name in required_dirs:
        dir_path = os.path.join(report_dir, dir_name)
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            print(f"  ✅ {dir_name}/ ({file_count} 个文件)")
        else:
            print(f"  ❌ {dir_name}/ - 缺失")
    
    return True

def check_data_files(report_dir):
    """检查数据文件"""
    print("\n" + "=" * 60)
    print("📊 数据文件检查")
    print("=" * 60)
    
    data_dir = os.path.join(report_dir, 'data')
    if not os.path.exists(data_dir):
        print("❌ data目录不存在")
        return False
    
    # 检查关键数据文件
    key_data_files = [
        'behaviors.json',
        'suites.json', 
        'timeline.json',
        'categories.json'
    ]
    
    for file in key_data_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  ✅ {file} - 有效JSON")
            except Exception as e:
                print(f"  ❌ {file} - JSON解析失败: {e}")
        else:
            print(f"  ❌ {file} - 缺失")
    
    return True

def check_widgets_files(report_dir):
    """检查组件文件"""
    print("\n" + "=" * 60)
    print("🎯 组件文件检查")
    print("=" * 60)
    
    widgets_dir = os.path.join(report_dir, 'widgets')
    if not os.path.exists(widgets_dir):
        print("❌ widgets目录不存在")
        return False
    
    # 检查关键组件文件
    key_widget_files = [
        'summary.json',
        'status-chart.json',
        'severity.json',
        'duration.json'
    ]
    
    for file in key_widget_files:
        file_path = os.path.join(widgets_dir, file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  ✅ {file} - 有效JSON")
            except Exception as e:
                print(f"  ❌ {file} - JSON解析失败: {e}")
        else:
            print(f"  ❌ {file} - 缺失")
    
    return True

def check_plugins_files(report_dir):
    """检查插件文件"""
    print("\n" + "=" * 60)
    print("🔌 插件文件检查")
    print("=" * 60)
    
    plugins_dir = os.path.join(report_dir, 'plugins')
    if not os.path.exists(plugins_dir):
        print("❌ plugins目录不存在")
        return False
    
    # 检查关键插件
    key_plugins = [
        'behaviors/index.js',
        'packages/index.js',
        'screen-diff/index.js',
        'screen-diff/styles.css'
    ]
    
    for plugin in key_plugins:
        plugin_path = os.path.join(plugins_dir, plugin)
        if os.path.exists(plugin_path):
            size = os.path.getsize(plugin_path)
            print(f"  ✅ {plugin} ({size} bytes)")
        else:
            print(f"  ❌ {plugin} - 缺失")
    
    return True

def create_test_zip(report_dir):
    """创建测试zip文件"""
    print("\n" + "=" * 60)
    print("🗜️ 创建测试zip文件")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"test_allure_report_{timestamp}.zip"
    zip_path = os.path.join(os.path.dirname(report_dir), zip_filename)
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(report_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, report_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    total_size += os.path.getsize(file_path)
        
        zip_size = os.path.getsize(zip_path)
        print(f"✅ 测试zip文件创建成功: {zip_path}")
        print(f"📊 文件数量: {file_count}")
        print(f"📁 原始大小: {total_size / 1024 / 1024:.2f} MB")
        print(f"🗜️ 压缩大小: {zip_size / 1024 / 1024:.2f} MB")
        
        return zip_path
        
    except Exception as e:
        print(f"❌ 创建zip文件失败: {e}")
        return None

def extract_and_test_zip(zip_path, extract_dir):
    """解压并测试zip文件"""
    print("\n" + "=" * 60)
    print("📦 解压并测试zip文件")
    print("=" * 60)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        print(f"✅ 文件解压成功到: {extract_dir}")
        
        # 检查解压后的文件
        index_path = os.path.join(extract_dir, 'index.html')
        if os.path.exists(index_path):
            print(f"✅ index.html存在: {index_path}")
            
            # 检查文件内容
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'spinner' in content:
                    print("✅ index.html包含加载动画元素")
                else:
                    print("⚠️ index.html可能不完整")
        else:
            print("❌ index.html不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 解压文件失败: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n" + "=" * 60)
    print("🔧 解决方案建议")
    print("=" * 60)
    
    print("如果HTML文件显示loading且无法加载，可能的原因和解决方案：")
    print("\n1. 📁 文件路径问题:")
    print("   - 确保解压后保持完整的目录结构")
    print("   - 不要移动或重命名任何文件")
    print("   - 确保所有相对路径正确")
    
    print("\n2. 🌐 浏览器兼容性:")
    print("   - 使用现代浏览器（Chrome、Firefox、Edge）")
    print("   - 禁用浏览器的安全限制")
    print("   - 尝试使用本地服务器（如Live Server）")
    
    print("\n3. 🔒 安全限制:")
    print("   - 某些浏览器阻止本地文件访问")
    print("   - 解决方案：使用简单的HTTP服务器")
    print("   - 命令：python -m http.server 8000")
    
    print("\n4. 📂 目录结构:")
    print("   - 确保解压到空目录")
    print("   - 不要嵌套目录结构")
    print("   - 直接解压到根目录")
    
    print("\n5. 🚀 推荐使用方法:")
    print("   - 解压到本地目录")
    print("   - 在该目录运行：python -m http.server 8000")

def main():
    """主函数"""
    print("🤖 Allure报告诊断工具")
    print("用于检查报告完整性和解决加载问题")
    
    report_dir = "./report"
    
    # 检查报告结构
    if not check_report_structure(report_dir):
        return
    
    # 检查数据文件
    check_data_files(report_dir)
    
    # 检查组件文件
    check_widgets_files(report_dir)
    
    # 检查插件文件
    check_plugins_files(report_dir)
    
    # 创建测试zip文件
    zip_path = create_test_zip(report_dir)
    
    if zip_path:
        # 解压并测试
        extract_dir = f"./test_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_and_test_zip(zip_path, extract_dir)
        
        # 清理测试文件
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"\n🧹 已清理测试zip文件: {zip_path}")
    
    # 提供解决方案
    provide_solutions()

if __name__ == "__main__":
    main() 