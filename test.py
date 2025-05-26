import requests
#
# 服务器地址和端口
url = "http://localhost:8200/get_current_bundleIdentifier"
# 若需要传递参数，可在字典中指定
params = {
    "bundle_ids": "com.example.app1,com.example.app2"
}

try:
    response = requests.get(url, params=params)
    # 检查响应状态码
    print(response.text)

except requests.RequestException as e:
    print(f"请求发生错误：{e}")

# url = "http://localhost:8200/check_status"
# # 若需要传递参数，可在字典中指定
#
#
# try:
#     response = requests.get(url)
#     # 检查响应状态码
#     print(response)
#
# except requests.RequestException as e:
#     print(f"请求发生错误：{e}")

from auto_nico.android.adb_utils import AdbUtils
