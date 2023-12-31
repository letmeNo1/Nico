# Nico - 使用 ADB 进行 UI Automator

ADB Automator 是一个自动化测试框架，它仅使用 ADB 命令来操作和控制 Android 设备。

## 背景

由于 Poco 的操作机制，我们的应用程序（Jabra Meeting）在运行过程中不稳定，容易出现闪退和返回桌面等问题。

因此，通过开发这个新的 Android 测试框架，它不依赖于中间件转发，可以减少测试框架对系统本身的影响。

## 安装

pass

## 使用

### 初始化

使用 udid 指定要控制的 Android 应用程序

```python
from adb_uiautomator.nico import AdbAutoNico

self.nico = AdbAutoNico(udid)
```

### 查找元素
支持以下查询：
```
index
text
resource_id
class_name
package
content_desc
checkable
checked
clickable
enabled
focusable
focused
scrollable
long_clickable
password
selected
```
***wait_for_appearance：***

等待元素出现，它会在指定的时间内不断查找元素，直到找到它们或超时。如果超过指定时间，则会抛出异常。
```
nico(**query).wait_for_appearance()
```
超时不是必需的，默认值为 5 秒。
```
例如：nico(text="start").wait_for_appearance(10)
```
为了支持模糊匹配，在匹配方法后添加“Match”
```
例如：nico(textMatch="St").wait_for_appearance(10)
```
query 是必需的，您可以使用多个 query
```
例如：nico(text="auto", class_name="UIItemsView").wait_for_appearance(10)
```
***exists：***

确定元素是否存在，它执行单个元素查找，以查看元素是否存在于页面上。返回值为 True 或 False。
```
nico(**query).exists()
```
###  操作
此对象包含单击、长按、设置文本等操作。
```
nico(text="start").click()
nico(text="start").long_click()
nico(text="start").set_text()
```
### 获取属性
直接通过属性名称获取，请参阅 qur 支持的属性
```
nico(text="start").text
nico(text="start").id
nico(text="start").class_name
```
