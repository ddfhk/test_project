# coding = utf-8
# Author: 李波
# Date: 2024/10/23 20:05
import os
import sys
import logging
import warnings
import argparse
import signal
import atexit

# 忽略不需要的警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置第三方库的日志级别
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.WARNING)

import pytest

# 安全退出函数
def safe_exit():
    """确保在脚本退出时清理所有浏览器进程"""
    logging.info("正在安全退出，清理资源...")
    
    # 强制结束所有chrome进程
    try:
        if sys.platform.startswith('win'):
            os.system('taskkill /f /im chromedriver.exe /t > nul 2>&1')
            os.system('taskkill /f /im chrome.exe /t > nul 2>&1')
        elif sys.platform.startswith('linux'):
            os.system('pkill -f chrome > /dev/null 2>&1')
            os.system('pkill -f chromedriver > /dev/null 2>&1')
        elif sys.platform.startswith('darwin'):  # macOS
            os.system('pkill -f "Google Chrome" > /dev/null 2>&1')
            os.system('pkill -f chromedriver > /dev/null 2>&1')
    except:
        pass

# 注册退出处理函数
atexit.register(safe_exit)

# 信号处理函数
def signal_handler(sig, frame):
    """处理中断信号"""
    logging.info("收到中断信号，正在清理资源...")
    safe_exit()
    sys.exit(1)

# 注册信号处理
if sys.platform != 'win32':  # Unix系统
    signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C

def send_report_email(report_dir, excel_report_path=None, email_body=None):
    """
    发送测试报告邮件，可选择性附加Excel报告。
    
    Args:
        report_dir (str): Allure报告目录。
        excel_report_path (str, optional): Excel报告路径. Defaults to None.
        email_body (str, optional): 邮件正文. Defaults to None.
    """
    try:
        # 导入邮件发送模块
        from utils.email_sender import EmailSender, EMAIL_CONFIGS
        from config.email_config import get_email_config, get_smtp_config, validate_email_config
        
        # 尝试从环境变量获取配置
        try:
            from config.email_env import get_email_config_from_env
            email_config = get_email_config_from_env()
            logging.info("使用环境变量配置")
        except ImportError:
            email_config = get_email_config()
            logging.info("使用默认配置文件")
        
        # 验证配置
        errors = validate_email_config()
        if errors:
            logging.error("邮件配置错误:")
            for error in errors:
                logging.error(f"  - {error}")
            logging.error("请检查 config/email_config.py 文件或环境变量配置")
            return False
        
        # 获取发件人配置
        sender_config = email_config['sender']
        email_type = sender_config['email_type']
        username = sender_config['username']
        password = sender_config['password']
        
        # 获取SMTP配置
        smtp_config = get_smtp_config(email_type)
        if not smtp_config:
            logging.error(f"不支持的邮箱类型: {email_type}")
            return False
        
        # 创建邮件发送器
        email_sender = EmailSender(
            smtp_server=smtp_config['smtp_server'],
            smtp_port=smtp_config['smtp_port'],
            username=username,
            password=password,
            use_ssl=smtp_config['use_ssl']
        )
        
        # 获取收件人列表
        recipients = email_config['recipients']
        
        # 生成邮件主题
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"{email_config['content']['subject_prefix']} - {current_time}"
        
        # 发送邮件
        success = email_sender.send_report_email(
            to_emails=recipients,
            report_dir=report_dir,
            subject=subject,
            excel_attachment_path=excel_report_path,
            email_body=email_body
        )
        
        if success:
            logging.info(f"测试报告邮件已成功发送到: {', '.join(recipients)}")
        else:
            logging.error("发送邮件失败")
        
        return success
        
    except ImportError as e:
        logging.error(f"导入邮件模块失败: {e}")
        logging.error("请确保已安装所需的依赖包")
        return False
    except Exception as e:
        logging.error(f"发送邮件时出现错误: {e}")
        return False

def parse_arguments():
    """处理命令行参数"""
    parser = argparse.ArgumentParser(description="运行YAML测试用例")
    parser.add_argument('-f', '--file', help='指定要运行的YAML文件路径')
    parser.add_argument('-d', '--directory', help='指定要运行的目录，默认为examples', default='examples')
    parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志输出')
    parser.add_argument('--headless', action='store_true', help='使用无头模式运行浏览器')
    parser.add_argument('--report', action='store_true', help='生成Allure报告')
    parser.add_argument('--email', action='store_true', help='生成报告后发送邮件')
    
    return parser.parse_args()

if __name__ == '__main__':
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置要运行的YAML文件
        yaml_file = args.file
        
        # 是否开启详细日志输出
        verbose = args.verbose
        
        # 是否使用无头模式
        headless = args.headless
        
        # 基本命令
        if yaml_file:
            # 只运行指定的YAML文件
            cmd = ["-sv" if verbose else "-s", "./test_case/test_runner3.py", "--yaml-file", yaml_file]
        else:
            # 运行指定目录下的所有测试
            cmd = ["-sv" if verbose else "-s", "./test_case/test_runner3.py", "--yaml-dir", args.directory]
            
            # 如果需要生成报告，添加相关参数
            if args.report:
                cmd.extend(["--alluredir", "./allure-results", "--clean-alluredir"])
        
        # 添加无头模式参数
        if headless:
            cmd.append("--headless")
        
        # 只添加未处理的位置参数，跳过已经作为选项值处理的参数
        if len(sys.argv) > 1:
            # 获取所有已处理的选项值
            processed_values = []
            if yaml_file:
                processed_values.append(yaml_file)
            if args.directory != 'examples':  # 只有非默认值才添加
                processed_values.append(args.directory)
                
            # 只添加未处理的位置参数
            additional_args = []
            for arg in sys.argv[1:]:
                if not arg.startswith('-') and '=' not in arg and arg not in processed_values:
                    additional_args.append(arg)
                    
            cmd.extend(additional_args)
        
        # 运行测试
        logging.info(f"运行命令: pytest {' '.join(cmd)}")
        pytest_exit_code = pytest.main(cmd)
        
        # 如果需要生成报告
        if args.report:
            # 生成报告
            os.system("allure generate -c -o report")
            logging.info("已生成Allure报告，可在report目录查看")

            excel_path = None
            email_body = None # 初始化邮件正文
            # 如果需要发送邮件，则先生成报告
            if args.email:
                try:
                    from utils.report_generator import generate_excel_report
                    excel_path = generate_excel_report()
                except Exception as e:
                    logging.error(f"生成Excel报告失败: {e}")

                try:
                    from utils.email_body_generator import generate_email_body
                    email_body = generate_email_body()
                except Exception as e:
                    logging.error(f"生成邮件正文失败: {e}")

                logging.info("开始发送测试报告邮件...")
                send_report_email("./report", excel_report_path=excel_path, email_body=email_body)
        
        # 返回pytest的退出码
        sys.exit(pytest_exit_code)
    
    except KeyboardInterrupt:
        # 处理Ctrl+C中断
        logging.info("用户中断运行，正在清理资源...")
        safe_exit()
        sys.exit(1)
    except Exception as e:
        # 处理其他异常
        logging.error(f"运行出错: {str(e)}")
        safe_exit()
        sys.exit(1)