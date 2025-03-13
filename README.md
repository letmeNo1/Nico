# Nico - Cross-Platform Mobile Automation Framework
[![GitHub stars](https://img.shields.io/github/stars/yourusername/Nico.svg?style=social)](https://github.com/yourusername/Nico/stargazers)
[![PyPI version](https://badge.fury.io/py/AutoNico.svg)](https://badge.fury.io/py/AutoNico)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)

For iOS, need to compile [nico_dump](https://github.com/letmeNo1/IOSHierarchyDumper)
Install to your iPhone device

<a name="background"></a>
## 📖 Full Documentation Table of Contents
- [English](#background)
- [Chinese Version](#chinese-version)
- [Installation](#installation)
- [Element Locators](#element-locators)
- [User Guide](#user-guide)
- [NicoElement API](#nicoelement-api)
- [ADB Toolset](#adb-utils)
- [IDB Toolset](#idb-utils)
- [Command Line Shortcuts](#command-line-shortcuts)
- [Best Practices](#best-practices)
- [Contribution Guidelines](#contribution-guidelines)

## 🚀 Quick Start
### 1. Installation
```bash
pip install AutoNico
```

### 2. Launch UI Inspector
```bash
nico_ui -s {udid}  # View real-time interface structure
```

### 3. Basic Test Script
```python
# Android Example
from auto_nico.android.nico_android import NicoAndroid

nico = NicoAndroid("emulator-5554")
nico(text="Add network").wait_for_appearance().click()
nico(class_name="EditText").set_text("TestSSID")
nico(text="Save").click()

# iOS Example
from auto_nico.ios.nico_ios import NicoIOS

nico = NicoIOS("00008020-00105C883A42001E")
nico(identifier="login_button").wait_for_appearance().click()
nico(xpath="//XCUIElementTypeTextField").set_text("user@example.com")
```

<a name="chinese-version"></a>
# Nico - 跨平台移动自动化测试框架
[![GitHub stars](https://img.shields.io/github/stars/yourusername/Nico.svg?style=social)](https://github.com/yourusername/Nico/stargazers)
[![PyPI version](https://badge.fury.io/py/AutoNico.svg)](https://badge.fury.io/py/AutoNico)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)

对于iOS, 需要自行编译[nico_dump](https://github.com/letmeNo1/IOSHierarchyDumper)
安装到iPhone设备上

<a name="background-cn"></a>
## 📖 完整文档目录
- [English](#background)
- [中文版](#chinese-version)
- [安装](#installation-cn)
- [元素定位](#element-locators-cn)
- [使用指南](#user-guide-cn)
- [NicoElement API](#nicoelement-api-cn)
- [ADB工具集](#adb-utils-cn)
- [IDB工具集](#idb-utils-cn)
- [命令行快捷方式](#command-line-shortcuts-cn)
- [最佳实践](#best-practices-cn)
- [贡献指南](#contribution-guidelines-cn)

## 🌟 核心特性
- **跨平台支持**：同时支持Android (UIAutomation2)和iOS (XCUITest)
- **后台运行**：测试全程在后台执行，不干扰用户操作
- **智能元素定位**：支持属性查询、正则匹配、模糊匹配
- **丰富操作库**：点击/滑动/输入/截图等30+操作方法
- **可视化调试**：内置UI Inspector实时查看界面结构

## 🚀 快速开始
### 1. 安装
```bash
pip install AutoNico
```

### 2. 启动UI Inspector
```bash
nico_ui -s {udid}  # 查看实时界面结构
```

### 3. 基础测试脚本
```python
# Android示例
from auto_nico.android.nico_android import NicoAndroid

nico = NicoAndroid("emulator-5554")
nico(text="Add network").wait_for_appearance().click()
nico(class_name="EditText").set_text("TestSSID")
nico(text="Save").click()

# iOS示例
from auto_nico.ios.nico_ios import NicoIOS

nico = NicoIOS("00008020-00105C883A42001E")
nico(identifier="login_button").wait_for_appearance().click()
nico(xpath="//XCUIElementTypeTextField").set_text("user@example.com")
```

<a name="element-locators-cn"></a>
## 📄 完整功能文档

### 🔍 元素定位
#### 启动UI Inspector
```bash
nico_ui -s {udid}
```

#### 支持的查询参数
| 参数类型       | Android支持字段                      | iOS支持字段                   |
|----------------|-------------------------------------|-------------------------------|
| 基础属性       | text, resource_id, class_name       | text, identifier, class_name  |
| 状态属性       | clickable, enabled, checked          | value, xpath                  |
| 布局属性       | index, package, content_desc        | index                         |

#### 查询示例
```python
# 模糊匹配
nico(text_contains="WiFi").wait_for_appearance()

# 正则匹配
nico(text_matches="^Search.*").click()

# 组合条件
nico(class_name="Button", enabled=True).all()
```

### 📱 使用指南
#### 初始化设备
```python
# Android初始化
from auto_nico.android.nico_android import NicoAndroid
nico_android = NicoAndroid("emulator-5554")

# iOS初始化
from auto_nico.ios.nico_ios import NicoIOS
nico_ios = NicoIOS("00008020-00105C883A42001E")
```

#### 元素等待策略
```python
# 等待元素出现
nico(text="Login").wait_for_appearance(timeout=10)

# 等待元素消失
nico(class_name="Loading").wait_for_disappearance()

# 等待任一条件
index = nico().wait_for_any([
    nico(text="Success"),
    nico(text="Error")
], timeout=15)
```

### 🛠️ NicoElement API
#### 属性访问
```python
element = nico(text="Username")
print(element.get_text())        # 获取文本
print(element.get_resource_id()) # 获取资源ID
print(element.get_enabled())    # 获取启用状态
```

#### 元素关系
```python
parent = element.parent()
sibling = element.next_sibling(2)
child = element.child(0)
```

#### 操作方法
```python
# 点击操作
element.click(x_offset=10, y_offset=20)

# 输入操作
element.set_text("password", append=True)

# 滑动操作
element.swipe(to_x=500, to_y=1000, duration=1.5)

# 滚动操作
element.scroll(direction="vertical_down")
```

<a name="adb-utils-cn"></a>
### 🧰 ADB工具集（Android专用）
通过`AdbUtils`类提供完整的Android设备控制能力：

#### 初始化方式
```python
from auto_nico.android.adb_utils import AdbUtils
adb = AdbUtils("emulator-5554")  # 通过udid初始化

# 或通过Nico实例获取
nico = NicoAndroid("emulator-5554")
adb = nico.adb_utils
```

#### 完整接口列表

| 方法名                      | 功能描述                                                                 | 参数说明                                                                 | 返回值                                                                 |
|-----------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| `get_tcp_forward_port()`    | 获取TCP转发端口                                                         | 无                                                                       | `int` 端口号 / `None`                                                 |
| `get_screen_size()`         | 获取屏幕尺寸                                                           | 无                                                                       | `tuple(width, height)`                                                |
| `start_app(package_name)`   | 启动应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `stop_app(package_name)`    | 停止应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `restart_app(package_name)` | 重启应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `qucik_shell(cmd)`          | 执行adb shell命令                                                       | `cmd`: 命令字符串                                                       | `str` 命令输出                                                        |
| `cmd(cmd)`                  | 执行完整adb命令                                                         | `cmd`: 命令字符串                                                       | `str` 命令输出                                                        |
| `is_keyboard_shown()`       | 检查键盘是否弹出                                                       | 无                                                                       | `bool`                                                                 |
| `is_screenon()`             | 检查屏幕是否亮起                                                       | 无                                                                       | `bool`                                                                 |
| `is_locked()`               | 检查屏幕是否锁定                                                       | 无                                                                       | `bool`                                                                 |
| `unlock()`                  | 解锁屏幕                                                               | 无                                                                       | 无                                                                     |
| `back()`                    | 模拟返回键                                                             | 无                                                                       | 无                                                                     |
| `menu()`                    | 模拟菜单键                                                             | 无                                                                       | 无                                                                     |
| `home()`                    | 模拟Home键                                                             | 无                                                                       | 无                                                                     |
| `snapshot(name, path)`      | 截图并保存                                                           | `name`: 文件名, `path`: 保存路径                                         | 无                                                                     |

#### 高级用法示例
```python
# 检查设备状态
if adb.is_screenon() and not adb.is_locked():
    print("设备已解锁并处于亮屏状态")
else:
    adb.unlock()

# 启动应用并等待元素出现
adb.start_app("com.android.settings")
nico(text="Wi-Fi").wait_for_appearance()

# 执行自定义adb命令
result = adb.cmd("shell dumpsys window displays")
print("Display信息：", result)
```

<a name="idb-utils-cn"></a>
### 🧰 IDB工具集（iOS专用）
通过`IdbUtils`类提供完整的iOS设备控制能力：

#### 初始化方式
```python
from auto_nico.ios.idb_utils import IdbUtils
idb = IdbUtils("00008020-00105C883A42001E")  # 通过udid初始化

# 或通过Nico实例获取
nico = NicoIOS("00008020-00105C883A42001E")
idb = nico.idb_utils
```

#### 完整接口列表

| 方法名                      | 功能描述                                                                 | 参数说明                                                                 | 返回值                                                                 |
|-----------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------|
| `get_tcp_forward_port()`    | 获取TCP转发端口                                                         | 无                                                                       | `int` 端口号 / `None`                                                 |
| `is_greater_than_ios_17()`  | 检查iOS版本是否≥17                                                      | 无                                                                       | `bool`                                                                 |
| `device_list()`             | 获取设备列表                                                           | 无                                                                       | `str` 设备信息列表                                                    |
| `set_port_forward(port)`    | 设置端口转发                                                           | `port`: 目标端口                                                       | 无                                                                     |
| `get_app_list()`            | 获取已安装应用列表                                                     | 无                                                                       | `List[str]` 应用信息列表                                               |
| `get_test_server_package()` | 获取测试服务器包名                                                     | 无                                                                       | `dict` 包含`test_server`和`main_package`                              |
| `get_wda_server_package()`  | 获取WDA服务器包名                                                      | 无                                                                       | `str` WDA包名                                                          |
| `start_app(package_name)`   | 启动应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `stop_app(package_name)`    | 停止应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `restart_app(package_name)` | 重启应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `start_recording()`         | 开始屏幕录制                                                           | 无                                                                       | 无                                                                     |
| `stop_recording(path)`      | 停止录制并保存视频                                                     | `path`: 保存路径（默认`output.mp4`）                                     | 无                                                                     |
| `get_output_device_name()`  | 获取设备名称                                                           | 无                                                                       | `str` 设备名称                                                        |
| `get_system_info()`         | 获取系统信息                                                           | 无                                                                       | `dict` 系统信息字典                                                   |
| `cmd(cmd)`                  | 执行tidevice命令                                                       | `cmd`: 命令字符串                                                       | `str` 命令输出                                                        |
| `activate_app(package_name)`| 激活应用                                                               | `package_name`: 应用包名                                                 | 无                                                                     |
| `terminate_app(package_name)`| 终止应用                                                             | `package_name`: 应用包名                                                 | 无                                                                     |
| `home()`                    | 模拟Home键                                                             | 无                                                                       | 无                                                                     |
| `get_volume()`              | 获取音量                                                               | 无                                                                       | `int` 音量值                                                          |
| `turn_volume_up()`          | 调高音量                                                               | 无                                                                       | 无                                                                     |
| `turn_volume_down()`        | 调低音量                                                               | 无                                                                       | 无                                                                     |
| `snapshot(name, path)`      | 截图并保存                                                           | `name`: 文件名, `path`: 保存路径                                         | 无                                                                     |
| `get_pic(quality=1.0)`      | 获取屏幕图片（二进制数据）                                             | `quality`: 图片质量（0.0-1.0）                                          | `bytes` 图片数据                                                      |
| `get_image_object(quality=100)` | 获取OpenCV格式图片对象                                           | `quality`: 图片质量（0-100）                                             | `numpy.ndarray` 图片对象                                               |
| `click(x, y)`               | 模拟点击坐标                                                         | `x`: X坐标, `y`: Y坐标                                                 | 无                                                                     |
| `get_current_bundleIdentifier(port)` | 获取当前应用包名                                                       | `port`: 服务端口                                                       | `str` 包名                                                             |

#### 高级用法示例
```python
# 屏幕录制
idb.start_recording()
# 执行测试操作
idb.click(100, 200)
idb.stop_recording("./test.mp4")

# 获取高质量截图
image_data = idb.get_pic(0.9)
with open("high_quality.jpg", "wb") as f:
    f.write(image_data)

# 系统音量控制
current_volume = idb.get_volume()
print(f"当前音量: {current_volume}%")
idb.turn_volume_up()
```

## 🤝 参与贡献
1. 提交代码规范：
   ```python
   # 遵循PEP8规范
   def my_function():
       """This is a docstring example"""
       pass
   ```
2. 问题反馈：[GitHub Issues](https://github.com/yourusername/Nico/issues)
3. 贡献指南：[CONTRIBUTING.md](https://github.com/yourusername/Nico/blob/main/CONTRIBUTING.md)

## 📄 许可证
MIT License - 请查看 [LICENSE](https://github.com/yourusername/Nico/blob/main/LICENSE) 文件
```