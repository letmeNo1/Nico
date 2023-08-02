Nico - using ADB to do UI Automator

ADB automator is an automated testing framework that only uses adb commands to operate and control Android devices

Background

Due to the operation mechanism of poco, our app(jabra meeting) is unstable in the running process, which is prone to problems such as flash back and returning to the desktop.

So by developing this new test framework for Android testing, It does not rely on middleware forwarding, can reduce the impact of the test framework on the system itself.



Install

pip install --index-url=http://10.86.212.237:8080/simple/ adb_uiautomator --trusted-host 10.86.212.237

Usage

Init

Use udid to specify which Android app you want to control



from adb_uiautomator.nico import AdbAutoNico

self.nico = AdbAutoNico(udid)



Find element.

support query:

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

wait_for_appearance :Waiting for an element to appear, It will keep looking for elements for a specified amount of time until it finds them or times out. If the specified time is exceeded, an exception is thrown

 nico(**query).wait_for_appearance()
 timeout is not required,The default value is 5s

 e.g  `nico(text="start").wait_for_appearance(10)`
 
To support fuzzy matching, add "Match" after the matching method
 e.g  `nico(textMatch="St").wait_for_appearance(10)`

 query is required,You can use multiple query
 e.g `nico(text="auto", class_name="UIItemsView").wait_for_appearance(10)`

exists : Determines if an element is present, It performs a single element lookup to see if the element exists on the page. The return value is True or False

nico(**query).exists()

Action

This object contains click, long click, set text,

nico(text="start").click()
nico(text="start").long_click()
nico(text="start").set_text()



Get Attribute

Directly obtained by attribute name, please refer to qur for the supported attributes

nico(text="start").text
nico(text="start").resource_id
nico(text="start").class_name
...
