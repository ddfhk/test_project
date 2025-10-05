# coding = utf-8
# Author: 李波
# Date: 2024/10/23 21:33
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from extend.driver_manager import DriverManager
import allure
import sys
import os

# 禁用urllib3连接池的警告
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

# 存储所有创建的WebDriver实例，用于全局清理
_active_drivers = []

# 默认的本地驱动路径
DEFAULT_CHROME_DRIVER_PATH = r"D:\program\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# 使用我们的驱动管理器，自动检查和更新驱动
@pytest.fixture(scope="function")
def driver(request):
    browser_type = request.config.getoption("--browser", default="chrome")
    headless = request.config.getoption("--headless", default=False)
    
    # 获取驱动路径，如果命令行没有指定，则使用默认路径
    local_driver_path = request.config.getoption("--driver-path")
    if local_driver_path is None:  # 如果命令行没有指定驱动路径
        local_driver_path = DEFAULT_CHROME_DRIVER_PATH
    
    options = None
    if browser_type.lower() == "chrome":
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        # 添加额外的Chrome选项，减少错误日志
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--log-level=3')  # 仅显示致命错误
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-dev-shm-usage')
        
        # 添加性能优化选项
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
    
    # 使用驱动管理器获取驱动
    driver_manager = DriverManager()
    
    # 检查本地驱动路径是否存在
    if os.path.exists(local_driver_path):
        logging.info(f"使用本地驱动: {local_driver_path}")
        driver_manager.set_local_driver_path(browser_type, local_driver_path)
    else:
        logging.warning(f"本地驱动路径不存在: {local_driver_path}，将使用自动下载的驱动")
    
    driver = driver_manager.get_driver(browser_type, options)
    
    # 将驱动添加到活动驱动列表中
    _active_drivers.append(driver)
    
    # 设置浏览器窗口大小
    driver.maximize_window()
    
    yield driver
    
    # 测试结束后关闭浏览器，使用静默关闭来减少连接错误
    try:
        driver.execute_script("window.onbeforeunload = function() {};")  # 禁用页面的beforeunload事件
        driver.quit()
        # 从活动驱动列表中移除
        if driver in _active_drivers:
            _active_drivers.remove(driver)
    except Exception as e:
        logging.debug(f"关闭浏览器时出现错误（通常可以忽略）: {e}")

# 测试会话结束时的清理函数
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    全局清理：确保所有浏览器在测试会话结束时被关闭
    无论测试成功还是失败，这个函数都会执行
    """
    global _active_drivers
    
    if _active_drivers:
        logging.warning(f"发现 {len(_active_drivers)} 个未关闭的浏览器实例，正在强制关闭...")
        
        for driver in _active_drivers[:]:  # 使用副本进行迭代
            try:
                # 检查驱动是否还活着
                try:
                    # 尝试执行一个简单操作，如果失败则说明浏览器已关闭
                    driver.current_url
                    # 浏览器仍在运行，需要关闭
                    logging.info("正在关闭浏览器实例...")
                    driver.execute_script("window.onbeforeunload = function() {};")
                    driver.quit()
                    logging.info("成功关闭浏览器实例")
                except Exception as e:
                    # 浏览器可能已经关闭，但未从列表中移除
                    logging.debug(f"浏览器实例已关闭或无法访问: {str(e)}")
                
                # 从列表中移除，无论是否成功关闭
                _active_drivers.remove(driver)
            except Exception as e:
                logging.error(f"尝试关闭浏览器时出错: {e}")
        
        # 清空列表
        _active_drivers.clear()
        logging.info("所有浏览器实例已清理完毕")
        
        # 强制结束所有chrome进程（作为最后的保险措施）
        try:
            if sys.platform.startswith('win'):
                os.system('taskkill /f /im chromedriver.exe /t')
                os.system('taskkill /f /im chrome.exe /t')
                logging.info("已强制结束Chrome相关进程")
            elif sys.platform.startswith('linux'):
                os.system('pkill -f chrome')
                os.system('pkill -f chromedriver')
                logging.info("已强制结束Chrome相关进程")
            elif sys.platform.startswith('darwin'):  # macOS
                os.system('pkill -f "Google Chrome"')
                os.system('pkill -f chromedriver')
                logging.info("已强制结束Chrome相关进程")
        except Exception as e:
            logging.error(f"强制结束Chrome进程时出错: {e}")

# 添加命令行参数
def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption("--browser", action="store", default="chrome",
                     help="指定浏览器类型: chrome, firefox, edge")
    parser.addoption("--headless", action="store_true", default=False,
                     help="是否使用无头模式")
    parser.addoption("--driver-path", action="store", default=None,
                     help="指定本地驱动文件路径，不指定则使用默认路径")
    parser.addoption("--yaml-file", action="store", default=None,
                     help="指定要运行的YAML文件路径")
    parser.addoption("--yaml-dir", action="store", default="examples",
                     help="指定要运行的YAML文件目录，默认为examples")

# 测试会话开始时重置驱动检查标志
@pytest.fixture(scope="session", autouse=True)
def reset_driver_check_flag():
    DriverManager.reset_check_flag()
    yield

# 异常处理：在每个测试失败后检查浏览器状态
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call, report):
    """在测试异常时检查浏览器状态"""
    if call.excinfo is not None and report.failed:
        logging.warning("测试失败，检查浏览器状态...")
        
        # 对所有活动浏览器实例进行检查
        global _active_drivers
        for driver in _active_drivers[:]:  # 使用副本进行迭代
            try:
                # 尝试访问浏览器
                driver.current_url
                logging.info("发现活动浏览器实例，保持运行状态")
            except:
                # 如果浏览器已关闭但仍在列表中，移除它
                logging.info("发现无效浏览器实例，从跟踪列表移除")
                try:
                    _active_drivers.remove(driver)
                except:
                    pass
