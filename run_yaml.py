# coding = utf-8
# Author: 李波
import os
import sys
import logging
import argparse
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 忽略不需要的警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 设置第三方库的日志级别
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.WARNING)

from extend.driver_manager import DriverManager
from extend.keywords import Keywords
from parse.YamlCase import read_yaml_file2

def execute_yaml_file(yaml_file_path, headless=False, driver=None, keywords=None, close_driver=True):
    """
    执行单个YAML文件
    
    参数:
        yaml_file_path: YAML文件路径
        headless: 是否使用无头模式
        driver: 可选的WebDriver实例，如果提供则使用该实例
        keywords: 可选的Keywords实例，如果提供则使用该实例
        close_driver: 是否在执行结束后关闭driver（仅当driver是在函数内创建时有效）
    
    返回:
        tuple: (driver, keywords) 如果需要复用浏览器会话
    """
    logging.info(f"准备执行YAML文件: {yaml_file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(yaml_file_path):
        logging.error(f"文件不存在: {yaml_file_path}")
        return None, None
    
    # 创建一个临时目录，只包含要执行的YAML文件
    temp_dir = "temp_yaml"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 复制YAML文件到临时目录
    import shutil
    yaml_filename = os.path.basename(yaml_file_path)
    temp_yaml_path = os.path.join(temp_dir, yaml_filename)
    shutil.copy(yaml_file_path, temp_yaml_path)
    
    # 从临时目录读取YAML文件
    cases = read_yaml_file2(temp_dir)
    
    if not cases:
        logging.error("未能从YAML文件解析出测试用例")
        shutil.rmtree(temp_dir)
        return None, None
    
    case = cases[0]  # 获取第一个测试用例
    
    # 检查是否有依赖文件需要先执行
    depends_on = case.get("depends_on", [])
    if depends_on and (driver is None or keywords is None):
        logging.info(f"检测到依赖文件: {depends_on}")
        # 创建driver和keywords，用于执行依赖文件
        if driver is None:
            # 创建driver
            driver_manager = DriverManager()
            options = Options()
            if headless:
                options.add_argument("--headless")
            
            # 添加通用选项
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--log-level=3')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            
            driver = driver_manager.get_driver("chrome", options)
            driver.maximize_window()
        
        # 获取默认超时时间
        config = case.get("config", {})
        default_timeout = config.get("default_timeout", 10)
        
        if keywords is None:
            # 创建keywords实例
            keywords = Keywords(driver, default_timeout=default_timeout)
        
        # 依次执行依赖文件
        for depend_file in depends_on:
            depend_path = depend_file
            if not os.path.isabs(depend_path):
                # 如果是相对路径，则相对于当前文件的目录
                depend_path = os.path.join(os.path.dirname(yaml_file_path), depend_file)
            
            logging.info(f"执行依赖文件: {depend_path}")
            # 递归执行依赖文件，不关闭driver
            execute_yaml_file(depend_path, headless, driver, keywords, False)
    
    # 如果没有提供driver和keywords，则创建新的
    driver_created = False
    if driver is None:
        driver_created = True
        # 创建driver
        driver_manager = DriverManager()
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        # 添加通用选项
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        
        driver = driver_manager.get_driver("chrome", options)
        driver.maximize_window()
    
    # 获取默认超时时间
    config = case.get("config", {})
    default_timeout = config.get("default_timeout", 10)
    
    if keywords is None:
        # 创建keywords实例
        keywords = Keywords(driver, default_timeout=default_timeout)
    else:
        # 更新超时时间
        keywords.default_timeout = default_timeout
    
    try:
        logging.info(f"开始执行测试用例: {case['title']}")
        logging.info(f"测试用例描述: {case['description']}")
        
        # 处理先决条件（如登录）
        handle_prerequisites(case, keywords)
        
        # 执行测试步骤
        for step in case["steps"]:
            step_name = list(step.keys())[0]
            step_value = list(step.values())[0]
            key = step_value["关键字"]
            
            logging.info(f"执行步骤: {step_name}")
            
            try:
                key_func = keywords.__getattribute__(key)
            except AttributeError:
                # 如果关键字不在Keywords类中，尝试从其他模块导入
                sys.path.append("./other")
                module = __import__(key)
                class_ = getattr(module, key)
                key_func = getattr(class_(keywords.driver), key)
            
            # 执行步骤
            key_func(**step_value)
            
            logging.info(f"步骤 {step_name} 执行成功")
        
        logging.info(f"测试用例 {case['title']} 执行完成")
        
    except Exception as e:
        logging.error(f"执行YAML文件时出错: {str(e)}")
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # 如果是我们创建的driver且需要关闭，则关闭它
        if driver_created and close_driver:
            try:
                driver.quit()
            except:
                pass
    
    # 返回driver和keywords，以便复用
    return driver, keywords

def execute_yaml_sequence(yaml_files, headless=False):
    """
    按顺序执行多个YAML文件，复用同一个浏览器会话
    
    参数:
        yaml_files: YAML文件路径列表
        headless: 是否使用无头模式
    """
    if not yaml_files:
        logging.error("没有提供YAML文件路径")
        return
    
    logging.info(f"准备按顺序执行以下YAML文件: {yaml_files}")
    
    driver = None
    keywords = None
    
    try:
        # 按顺序执行每个YAML文件
        for i, yaml_file_path in enumerate(yaml_files):
            # 检查文件是否存在
            if not os.path.exists(yaml_file_path):
                logging.error(f"文件不存在: {yaml_file_path}")
                continue
            
            # 对于最后一个文件，允许关闭driver
            close_driver = (i == len(yaml_files) - 1)
            
            # 执行YAML文件，复用driver和keywords
            driver, keywords = execute_yaml_file(
                yaml_file_path, 
                headless, 
                driver, 
                keywords, 
                close_driver
            )
            
            if driver is None or keywords is None:
                logging.error(f"执行 {yaml_file_path} 时出错，无法继续执行后续文件")
                break
        
    except Exception as e:
        logging.error(f"执行YAML文件序列时出错: {str(e)}")
    finally:
        # 确保driver被关闭
        if driver is not None:
            try:
                driver.quit()
            except:
                pass

def handle_prerequisites(case, keywords):
    """处理测试用例的先决条件，例如登录操作"""
    prerequisites = case.get("prerequisites", [])
    logging.info(f"处理先决条件: {prerequisites}")
    if not prerequisites:
        logging.info("没有先决条件需要处理")
        return
        
    for prerequisite in prerequisites:
        prerequisite_type = prerequisite.get("type")
        logging.info(f"处理先决条件类型: {prerequisite_type}")
        
        # 处理登录先决条件
        if prerequisite_type == "login":
            username = prerequisite.get("username")
            password = prerequisite.get("password")
            logging.info(f"执行登录操作，用户名: {username}")
            
            # 执行登录操作
            # 打开登录页面
            keywords.open_browser(数据内容="https://www.leadong.com/login.html")
            
            # 输入用户名
            keywords.input_context(定位方式="id", 目标对象="loginName", 数据内容=username)
            
            # 输入密码
            keywords.input_context(定位方式="id", 目标对象="password", 数据内容=password)
            
            # 点击登录按钮
            keywords.option_click(定位方式="id", 目标对象="loginSubmit")
            
            # 等待登录完成
            keywords.wait_sleep(数据内容="3")
            
            # 尝试关闭可能出现的视频弹窗
            try:
                keywords.option_click(定位方式="xpath", 目标对象="//*[@id=\"app\"]/div[3]/div/div[1]")
            except:
                logging.info("没有找到视频弹窗，继续执行")
                
            logging.info(f"成功执行登录操作，用户名: {username}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="执行单个YAML文件或YAML文件序列")
    parser.add_argument("yaml_files", nargs='+', help="YAML文件路径或多个YAML文件路径")
    parser.add_argument("--headless", action="store_true", help="使用无头模式")
    parser.add_argument("--sequence", action="store_true", help="按顺序执行多个YAML文件，复用同一个浏览器会话")
    
    args = parser.parse_args()
    
    if args.sequence and len(args.yaml_files) > 1:
        execute_yaml_sequence(args.yaml_files, args.headless)
    else:
        for yaml_file in args.yaml_files:
            execute_yaml_file(yaml_file, args.headless) 