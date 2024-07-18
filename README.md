Nico - Automated Testing on Android Mobile
=================================

-   [English](#Background)
-   [中文版](#背景)

Background
==========
Nico is an automated testing framework based on `UIAUTOMATION2`, which executes in the background and does not need to start the app in the foreground

Install 
===============

```
pip install AutoNico
```


Element locate
===============
![示例GIF](https://github.com/letmeNo1/Nico/blob/main/05c8044a-2ac3-45c8-87fa-d1feaa737368.gif))


Input `nico_ui -s {udid} -p1 {the port that forwards the request} -p2 {the port that launches the UI inspector}` at  command line


if success, it will start a server to show UI inspector
```
input:
nico_ui -s emulator-5554 -p1 5000 -p2 6000


output:

forward tcp:5000 tcp:5000
 * Serving Flask app 'auto_nico.console_scripts.inspector_web.nico_inspector'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:6000
Press CTRL+C to quit
INSTRUMENTATION_STATUS: class=hank.dump_hierarchy.HierarchyTest
INSTRUMENTATION_STATUS: current=1
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: numtests=1
INSTRUMENTATION_STATUS: stream=
hank.dump_hierarchy.HierarchyTest:
INSTRUMENTATION_STATUS: test=TestCase1
INSTRUMENTATION_STATUS_CODE: 1

```


Usage
==========

## initialize an NicoServer by udid
 ```
from auto_nico.android.nico_android import NicoAndroid


nico = NicoAndroid(udid)
```

## Find elements
### *support query* ：
* You can use these as query terms to get `NicoElement`

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
      `nico(text="test_contesxts") -> NicoElement

*  By default, the first eligible element is returned, If there are multiple identical results, use `get(index)` to get the specified index
  ```
  nico(text="test_contesxts").get(1)
  ``` 

*  Use `all()` to get all matched result
  ```
  nico(text="test_contesxts").all()
  ``` 

* You can also retrieve element's attribute via `get_`+ `query name`, e.g. `nico("class_name="xxx").get_index`

### *wait_for_appearance*：

* Waiting for elements to appear, which keeps looking for elements for a specified amount of time until they are found or time out. If the specified time is exceeded, an exception is thrown.
    ```
    nico(**query).wait_for_appearance()
    ```

* The timeout is not required and defaults to 5 seconds. You can specify a timeout explicitly

    ```
    `nico(text="start").wait_for_appearance(10)
    ```

* Query are required, and you can use more than one
    ```
    nico(text="automation", class_name="UIItemsView").wait_for_appearance(10)
    ```
* Support regular expression matching(`_matches`) and fuzzy matching(`_contains`)
    ```
    # Common matching
    nico(text_matches="automation").wait_for_appearance(10)
  
    # Regular expression matching
    nico(text_matches="*auto*.").wait_for_appearance(10)
    
    # Fuzzy matching
    nico(text_contains="auto").wait_for_appearance(10)
    ```
### *wait_for_disappearance*：

  * The parameter transfer mode is the same, the effect is opposite

### *wait_for_any*:

   * Wait for any condition to be fulfilled or time out, The return value is index of condition
     ```
     nico().wait_for_any([nico(text="start"), nico(text="begin")],timeout=10)
     ```
    
### *exists*：

* To determine if an element exists, it performs a single element lookup to see if the element exists on the page. The return value is `True` or `False`.  By default, timeout is not set. If you need to wait, please pass timeout

    ```
    nico(**query).exists()
    ```
    or 
    ```
    nico(**query).exists(5)
    ```
  
## Nico Element
### *Attribute@property*：

  * `get_{all support query}`:
    Return attribute of NicoElement

### *Attribute@nonproperty*：

  * `last_sibling(self, index=1)`:
    Return current NicoElement's last sibling node,
    `index` means the number of brothers


  * `next_sibling(self, index=1)`:
Return current NicoElement's next sibling node,
`index` means the number of brothers


  * `parent(self)`:
Return current NicoElement's parent node


  * `child(self,index)`:
Return current NicoElement's parent node,
`index` means the number of children

### *Action*
For all action method  
`x_offset`, `y_offset` are optional. The offset xy is offset based on the current xy axis

  * `click(self, x=None, y=None, x_offset=None, y_offset=None)`: 
    Perform the click action


  * `long_click(self, duration, x_offset=None, y_offset=None)`:
    Perform the long click action


  * `set_text(self, text, append=False, x_offset=None, y_offset=None)`:
  Simulate keyboard input actions


  * `scroll(self, duration=200, direction='vertical_up')`
    Simulate scroll, `direction` include `vertical_up` or `vertical_down` or `horizontal_left` or `horizontal_right`

  * `swipe(self, to_x, to_y, plus_duration=0)`:
    Simulate swipe action, plus_duration will affect the duration of swipe, The larger the value, the slower the swipe speed. Please note that if it exceeds 1800, it will turn into a drag

  * `drag(self, to_x, to_y, plus_duration=0)`:
    Simulate drag action, plus_duration will affect the duration of drag


## adb utils
**initialize**
```
from from auto_nico.nico.adb_utils import AdbUtils

adb_utils = AdbUtils(udid)
```


**interface**

* `get_tcp_forward_port()`:
Get tcp forward port


* `get_screen_size()`:
Get device screen size，Return `width`, `height`


* `start_app(package_name)`:
Lancuh app by package name


* `stop_app(package_name)`:
Kill app by package name


* `restart_app(package_name)`:
Restart app by package name


* `qucik_shell(cmd)`:
Run the adb shell command


* `cmd(cmd)`:
Run the adb command


* `is_keyboard_shown()`:
Check whether the keyboard pops up, Return `True` or `False`


* `is_screenon()`:
Check whether the screen lights up, Return `True` or `False`


* `is_locked()`:
Check whether the screen is locked, Return `True` or `False`


* `unlock()`:
Unlock screen


* `back()`:
Simulated back button


* `menu()`:
Simulated menu button


* `home()`:
Simulated menu button


* `snapshot(name, path)`:
take a photo from device

# Shortcut command
`nico_screenshot` : Take a screenshot with this command and save it to your desktop

`-m` It means to code the digital part of the image
`-u` It means udid

e.g.
`
PS C:\Users\hanhuang\apollo-tools\ApolloModule\AutoNico> nico_screenshot -u 122079aac2a29a1e -m      
`


背景
==========
Nico是一个基于`UIAUTOMATION2`的自动化测试框架，全程后台执行，不需要前台启动app

安装 
===============

```
pip install Nico
```


元素定位
===============

在命令行输入`nico_dump {udid}`

如果成功，它将像这样返回。打开`{udid}_ui.xml`文件查看UI树

```
输入:
nico_dump 1234567

输出:

2024-01-03 11:14:15,781 Nico - DEBUG - 514f465834593398's test server is ready
2024-01-03 11:14:15,781 Nico - DEBUG - 514f465834593398's uiautomator was initialized successfully
C:\Users\hanhuang\AppData\Local\Temp/514f465834593398_ui.xml

```


使用
==========

## 通过udid初始化NicoServer

 ```
from auto_nico.android.nico_android import NicoAndroid


nico = NicoAndroid(udid)
```

## 查找元素
### 支持查询:
* 你可以使用这些作为查询词条来获取`NicoElement`
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
      `nico(text="test_contesxts") -> NicoElement

* 默认返回第一个符合条件的元素，如果有多个相同的结果，使用`get(index)` '`获取指定的索引
* ```
  nico(text="test_contesxts").get(1) -> NicoElement
  ``` 

* 使用`all()`来获取所有匹配的结果

  ```
  nico(text="test_contesxts").all() -> List[NicoElement]
  ``` 

* 你也可以通过`get_`+ `query name`来获取元素的属性，例如: `Nico(class_name = "xxx") .get_index`

### *wait_for_appearance*：

* 等待元素出现，在指定的时间内持续查找元素，直到找到元素或超时。如果超过了指定的时间，就会抛出异常。    
* ```
    nico(**query).wait_for_appearance()
    ```

* 不需要超时，默认为5秒。可以显式指定超时

    ```
    `nico(text="start").wait_for_appearance(10)
    ```

* 查询是条件必需的，并且您可以使用多个
    ```
    nico(text="automation", class_name="UIItemsView").wait_for_appearance(10)
    ```
* 支持正则表达式匹配(`_matches`)和模糊匹配(`_contains`)
    ```
    # 常规匹配
    nico(text_matches="automation").wait_for_appearance(10)
  
    # 正则表达式匹配
    nico(text_matches="*auto*.").wait_for_appearance(10)
    
    # 模糊匹配
    nico(text_contains="auto").wait_for_appearance(10)
    ```
### *wait_for_disappearance*：

  * 参数传递方式相同，效果相反

### *wait_for_any*:

   * 等待条件满足或超时时，返回值为条件的索引
     ```
     nico().wait_for_any([nico(text="start"), nico(text="begin")],timeout=10)
     ```
    
### *exists*：

* 为了确定元素是否存在，它会执行单元素查找，以确定元素是否存在于页面中。返回值是`True`或`False`。默认情况下，未设置超时。如果需要等待，请传入超时时间
     ```
    nico(**query).exists()
    ```
    or 
    ```
    nico(**query).exists(5)
    ```
  
## Nico Element
### *Attribute@property*：

  * `get_{all support query}`:
    返回NicoElement所支持的属性


### *Attribute@nonproperty*：

* `last_sibling(self, index=1)`:
返回当前NicoElement的最后一个兄弟节点，
`index`表示兄弟节点的索引值


* `next_sibling(self, index=1)`:
返回当前NicoElement的下一个兄弟节点，
`index`表示兄弟节点的索引值


  * `child(self,index)`:
返回当前NicoElement的父节点，
`index` 表示子节点的索引

### *动作*
对于所有动作方法
`x_offset `， ` y_offset `是可选的。偏移量xy是基于当前xy轴的偏移量

  * `click(self, x=None, y=None, x_offset=None, y_offset=None)`: 
    执行点击操作

  * `long_click(self, duration, x_offset=None, y_offset=None)`:
    执行长按动作


  * `set_text(self, text, append=False, x_offset=None, y_offset=None)`:
   模拟输入事件


  * `scroll(self, duration=200, direction='vertical_up')`
   模拟滚动，'方向'包括' vertical_up '或' vertical_down '或' horizontal_left '或' horizontal_right '

  * `swipe(self, to_x, to_y, plus_duration=0)`:
   模拟滑动，plus_duration将影响滑动的持续时间，单位为秒，值越大，滑动速度越慢。请注意，如果超过1.8秒，它将变成拖动

  * `drag(self, to_x, to_y, plus_duration=0)`:
    模拟拖动动作，plus_duration将影响拖动的持续时间，单位为秒

## adb utils
**初始化**
```
from from auto_nico.nico.adb_utils import AdbUtils

adb_utils = AdbUtils(udid)
```


**接口**

* `get_tcp_forward_port()`:
获取tcp转发端口


* `get_screen_size()`:
获取设备屏幕尺寸，返回`width`， ` height `


* `start_app(package_name)`:
按包名启动应用程序


* `stop_app(package_name)`:
通过包名杀死应用程序


* `restart_app(package_name)`:
根据包名重新启动应用程序


* `qucik_shell(cmd)`:
执行adb shell命令


* `cmd(cmd)`:
运行adb命令


* `is_keyboard_shown()`:
检查键盘是否弹出，返回`True`或`False`


* `is_screenon()`:
检查屏幕是否亮起，返回`True`或`False`


* `is_locked()`:
检查屏幕是否被锁住, 返回`True`或`False`


* `unlock()`:
解锁屏幕

* `back()`:
模拟返回键

* `menu()`:
模拟菜单键

* `home()`:
模拟home键


* `snapshot(name, path)`:
截图`
