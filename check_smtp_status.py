#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信邮箱SMTP服务状态检查脚本
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def check_smtp_connection():
    """检查SMTP连接状态"""
    print("🔍 检查企业微信邮箱SMTP服务状态...")
    
    # 企业微信邮箱SMTP配置
    smtp_server = 'smtp.exmail.qq.com'
    smtp_port = 465
    
    try:
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        print(f"📡 正在连接 {smtp_server}:{smtp_port}...")
        
        # 尝试连接SMTP服务器
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("✅ SMTP服务器连接成功")
            
            # 获取服务器信息
            print(f"📋 服务器信息: {server.ehlo()}")
            
            return True
            
    except smtplib.SMTPConnectError as e:
        print(f"❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_smtp_auth(username, password):
    """测试SMTP认证"""
    print(f"\n🔐 测试认证: {username}")
    
    smtp_server = 'smtp.exmail.qq.com'
    smtp_port = 465
    
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("📡 SMTP连接成功")
            
            # 尝试登录
            print("🔐 正在登录...")
            server.login(username, password)
            print("✅ 认证成功！")
            
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("企业微信邮箱SMTP服务诊断工具")
    print("=" * 50)
    
    # 1. 检查SMTP服务状态
    print("\n1️⃣ 检查SMTP服务状态")
    if not check_smtp_connection():
        print("❌ SMTP服务不可用，请检查网络或联系管理员")
        return
    
    # 2. 测试认证
    print("\n2️⃣ 测试SMTP认证")
    username = input("请输入邮箱地址: ").strip()
    password = input("请输入客户端专用密码: ").strip()
    
    if not username or not password:
        print("❌ 邮箱地址和密码不能为空")
        return
    
    if test_smtp_auth(username, password):
        print("\n🎉 诊断完成：SMTP服务正常，认证成功！")
    else:
        print("\n🔧 诊断完成：需要进一步排查")
        print("\n建议检查：")
        print("1. 确认使用的是客户端专用密码，不是登录密码")
        print("2. 确认企业微信邮箱SMTP服务已开启")
        print("3. 确认账户有SMTP使用权限")
        print("4. 联系企业微信管理员确认设置")

if __name__ == "__main__":
    main() 