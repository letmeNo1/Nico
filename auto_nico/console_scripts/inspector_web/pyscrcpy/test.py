import cv2
from auto_nico.console_scripts.test.pyscrcpy import Client
from fastapi import FastAPI
from fastapi.responses import Response
import threading

app = FastAPI()
client = None
frame_buffer = None

# 初始化设备连接（自动选择首个设备）
def on_frame(client, frame, cv=None):
    global frame_buffer
    frame_buffer = frame

def start_client():
    global client
    client = Client(max_fps=20)
    client.start(threaded=True)  # create a new thread for scrcpy
    while True:
        if client.last_frame is not None:
            on_frame(client, client.last_frame)

@app.get("/get_image")
async def get_image():
    global frame_buffer
    if frame_buffer is not None:
        ret, buffer = cv2.imencode('.jpg', frame_buffer)
        frame = buffer.tobytes()
        return Response(content=frame, media_type="image/jpeg")
    return {"message": "No frame available yet"}

def start_scrcpy():
    import uvicorn
    # 启动客户端线程
    client_thread = threading.Thread(target=start_client)
    client_thread.daemon = True
    client_thread.start()

    # 启动 FastAPI 服务
    uvicorn.run(app, host="0.0.0.0", port=5000)