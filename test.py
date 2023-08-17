import psutil

# 获取所有进程列表
processes = psutil.process_iter()

# 遍历进程列表并打印进程信息
for process in processes:
    print(process.name(), process.pid)