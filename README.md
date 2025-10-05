.
├── allure-results/        # Allure测试结果输出目录
├── common/                # 公共YAML用例目录（如登录）
├── config/                # 配置文件目录
├── examples/              # 示例YAML用例目录
├── extend/                # 扩展功能模块（关键字库、重试机制等）
├── other/                 # 其他扩展模块
├── parse/                 # YAML解析模块
├── report/                # 测试报告输出目录
├── test_case/             # 测试执行器目录
├── README.md              # 项目说明文档
├── requirements.txt       # Python依赖包列表
├── run.py                 # 主运行入口
└── run_yaml.py            # YAML用例执行入口
```

## 🛠️ 环境部署
### 安装依赖
```bash
pip install -r requirements.txt
```

### 推荐开发工具
- **PyCharm**：用于Python代码编写和调试
- **VSCode**：用于YAML用例编写和预览

## 📁 目录与文件说明
| 文件/目录 | 作用 |
|----------|------|
| `allure-results/` | 存放Allure测试结果数据 |
| `common/` | 存放公共YAML用例，如登录操作 |
| `config/` | 存放全局配置文件，如浏览器设置、日志级别 |
| `examples/` | 示例YAML测试用例目录 |
| `extend/` | 关键字库、重试机制、驱动管理器等核心逻辑 |
| `other/` | 其他扩展模块，可选功能存放于此 |
| `parse/` | YAML文件解析模块 |
| `report/` | 生成的测试报告 |
| `test_case/` | 测试执行器，主要包含pytest执行逻辑 |
| `requirements.txt` | Python依赖列表 |
| `run.py` | 启动测试主入口 |
| `run_yaml.py` | 单独运行YAML用例的入口 |

## 🧪 YAML用例编写规范
### 基本结构
```yaml
title: 用例标题
description: 用例描述
case_type: 用例类型
tags: [标签1, 标签2]
config:
  default_timeout: 5    # 默认等待时间
  retry_count: 2        # 整体失败后重试次数
prerequisites:
  - type: login          # 登录前置条件
    username: user123    # 用户名
    password: pass123    # 密码
depends_on:
  - common/login.yaml    # 依赖的其他YAML文件
steps:
  - 步骤名称1:
      关键字: open_browser
      参数1: value1
  - 步骤名称2:
      关键字: input_context
      参数1: value2
```

### 字段说明
| 字段 | 描述 |
|------|------|
| `title` | 用例标题 |
| `description` | 用例描述 |
| `case_type` | 用例类型 |
| `tags` | 用例标签（数组形式） |
| `config` | 用例配置 |
| `prerequisites` | 前置条件（如登录） |
| `depends_on` | 依赖的其他YAML文件 |
| `steps` | 用例具体步骤 |

### 支持的关键字
#### 浏览器操作
- `open_browser`: 打开浏览器并访问指定URL
- `close_browser`: 关闭浏览器
- `switch_to_handle`: 切换浏览器窗口
- `iframe_switch_to`: 切换到指定iframe
- `assert_url`: 断言当前URL

#### 元素操作
- `input_context`: 输入文本到元素中
- `option_click`: 点击元素
- `get_element_text`: 获取元素文本
- `get_element_attribute`: 获取元素属性值
- `clear_input`: 清空输入框

#### 等待与延时
- `wait_sleep`: 固定等待时间

#### 拖拽相关
- `drag_and_drop`: 拖拽元素到目标元素上
- `drag_by_offset`: 按偏移量拖拽
- `drag_and_drop_js`: 使用JavaScript触发HTML5拖拽事件

#### 文件上传与弹窗处理
- `upload_file`: 上传文件
- `close_browser_popup`: 关闭浏览器弹窗

#### 截图与异常处理
- `jietu`: 执行截图（所有操作都会自动截图）
- `safe_quit`: 安全关闭浏览器并忽略异常

#### 高级交互
- `locator_with_wait`: 显示等待+元素定位（所有操作都基于此方法）
- `quit`: 强制退出浏览器

## 📘 关键字详细说明

以下为关键字的完整说明，这些关键字定义在 [keywords.py](file://D:\pythonProject\web_auto_test\extend\keywords.py) 中。

### 🔧 浏览器操作类

#### `open_browser`
- **用途**: 打开浏览器并访问指定URL
- **参数**:
  - `数据内容`: 要访问的URL

#### `close_browser`
- **用途**: 安全关闭浏览器
- **参数**: 无

#### `switch_to_handle`
- **用途**: 切换到指定编号的浏览器窗口
- **参数**:
  - `数据内容`: 窗口索引（如 `-1` 表示最后一个窗口）

#### `iframe_switch_to`
- **用途**: 切换到指定的 iframe
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: iframe 的定位表达式

#### `assert_url`
- **用途**: 断言当前页面的URL是否匹配预期值
- **参数**:
  - `数据内容`: 要断言的URL

### ✏️ 元素操作类

#### `input_context`
- **用途**: 在输入框中输入文本
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: 元素定位表达式
  - `数据内容`: 要输入的文本

#### `option_click`
- **用途**: 点击指定元素
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: 元素定位表达式

#### `get_element_text`
- **用途**: 获取元素的文本内容
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: 元素定位表达式

#### `get_element_attribute`
- **用途**: 获取元素的指定属性值
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: 元素定位表达式
  - `属性名`: 要获取的属性名称

#### `clear_input`
- **用途**: 清空输入框中的内容
- **参数**:
  - `定位方式`: 如 `id`, `xpath`
  - `目标对象`: 元素定位表达式

### ⏱️ 等待与延时

#### `wait_sleep`
- **用途**: 固定时间等待
- **参数**:
  - `数据内容`: 等待时间（秒）

### 🖱️ 拖拽相关

#### `drag_and_drop`
- **用途**: 将一个元素拖拽到另一个元素上
- **参数**:
  - `定位方式`: 源元素的定位方式（如 `id`, `xpath`）
  - `目标对象`: 源元素的定位表达式
  - `目标定位方式`: 目标元素的定位方式
  - `目标定位值`: 目标元素的定位表达式

#### `drag_by_offset`
- **用途**: 按照指定的X/Y偏移量拖拽元素
- **参数**:
  - `定位方式`: 源元素的定位方式
  - `目标对象`: 源元素的定位表达式
  - `x_offset`: X轴偏移量
  - `y_offset`: Y轴偏移量

#### `drag_and_drop_js`
- **用途**: 使用JavaScript模拟HTML5拖拽行为
- **参数**:
  - `定位方式`: 源元素的定位方式
  - `目标对象`: 源元素的定位表达式
  - `目标定位方式`: 目标元素的定位方式
  - `目标定位值`: 目标元素的定位表达式

### 📤 文件上传与弹窗处理

#### `upload_file`
- **用途**: 上传文件
- **参数**:
  - `定位方式`: 文件输入框的定位方式
  - `目标对象`: 文件输入框的定位表达式
  - `数据内容`: 要上传的文件路径

#### `close_browser_popup`
- **用途**: 关闭浏览器原生弹窗（如重新加载提示）
- **参数**:
  - `定位方式`: 弹窗关闭按钮的定位方式
  - `目标对象`: 弹窗关闭按钮的定位表达式

### 📸 截图与异常处理

#### `jietu`
- **用途**: 自动截图并附加到Allure报告中
- **参数**: 无

#### `safe_quit`
- **用途**: 安全地关闭浏览器并忽略常见错误
- **参数**: 无

#### `quit`
- **用途**: 强制退出浏览器
- **参数**: 无

### 🔍 高级交互

#### `locator_with_wait`
- **用途**: 显示等待某个元素出现
- **参数**:
  - `定位方式`: 元素定位方式（如 `id`, `xpath`）
  - `目标对象`: 元素定位表达式
  - `等待时间`: 自定义等待时间（不提供则使用默认值）

## 📝 编写YAML测试用例
### 示例
```yaml
title: 新增自定义页面然后删除
description:
  1.点击编辑网站
  2.新增自定义页面
  3.删除自定义页面
config:
  default_timeout: 5
  retry_count: 1
depends_on:
  - common/1_login_qz.yaml   # 依赖登录用例
steps:
- 点击选择中文简体站:
    关键字: option_click
    定位方式: xpath
    目标对象: //p[@roles='ckKfUpDLZcYj']//span//span[@value='1'][contains(text(),'中文（简体）')]

- 点击编辑网站按钮:
    关键字: option_click
    定位方式: xpath
    目标对象: //div[contains(@class,'sitewidget-mySite sitewidget-mySite-20150529193526')]//div[1]//div[2]//div[2]//div[1]//div[1]//a[1]

- 等待:
    关键字: wait_sleep
    数据内容: 2

- 切换到新窗口:
    关键字: switch_to_handle
    数据内容: -1

- 点击页面管理:
    关键字: option_click
    定位方式: xpath
    目标对象: //div[@title='页面管理']//i[@class='iconfont icon-nav-page']

- 点击新增页面按钮:
    关键字: option_click
    定位方式: xpath
    目标对象: //span[@class='newpage-text']

- 输入页面名称:
    关键字: input_context
    定位方式: xpath
    目标对象: //input[@placeholder='请填写页面名称']
    数据内容: 自动化测试页面

- 等待:
    关键字: wait_sleep
    数据内容: 2

- 点击保存按钮:
    关键字: option_click
    定位方式: xpath
    目标对象: //*[@id="leadong-editor-container"]/div[3]/div/div/footer/span/button[2]

- 等待保存完成:
    关键字: wait_sleep
    数据内容: 3

- 搜索自定义页面:
    关键字: input_context
    定位方式: xpath
    目标对象: //input[@placeholder='页面搜索']
    数据内容: 自动化测试页面

- 等待搜索结果:
    关键字: wait_sleep
    数据内容: 2

- 点击删除按钮:
    关键字: option_click
    定位方式: xpath
    目标对象: //span[text()='自动化测试页面']/ancestor::div[contains(@class, 'page-item')]//button[contains(@class, 'delete-btn')]

- 确认删除:
    关键字: option_click
    定位方式: xpath
    目标对象: //div[contains(@class, 'dialog-footer')]//button[contains(@class, 'primary')]

- 等待删除完成:
    关键字: wait_sleep
    数据内容: 2

- 关闭浏览器:
    关键字: close_browser

