const socket = io.connect('http://' + document.domain + ':' + location.port + '/device');
const overlay = document.getElementById('action-layer');
const deviceImage = document.getElementById('device-image');

function setOverlaySize() {
    overlay.style.width = deviceImage.offsetWidth + 'px';
    overlay.style.height = deviceImage.offsetHeight + 'px';
}

socket.on('connect', function () {
    console.log('Connected to server');
    // 发送请求获取图像
    socket.emit('request_image', { device_id: "514f465834593398" });
});

socket.on('image_update', function (data) {
    const imageData = data.image;
    const binaryImage = hexToUint8Array(imageData);
    const blob = new Blob([binaryImage], { type: 'image/jpeg' });
    const url = URL.createObjectURL(blob);
    deviceImage.src = url;
    deviceImage.onload = setOverlaySize;
});

socket.on('status_update', function (data) {
    document.getElementById('status-message').innerHTML = data.message;
});

function hexToUint8Array(hex) {
    const length = hex.length;
    const uint8Array = new Uint8Array(length / 2);
    for (let i = 0; i < length; i += 2) {
        uint8Array[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return uint8Array;
}