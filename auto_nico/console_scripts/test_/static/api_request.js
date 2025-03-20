let intervalId;
let longPressTimeout;
const longPressDuration = 500; // 500 milliseconds for long press
let startX, startY;

async function fetchImage() {
    const deviceId = "emulator-5554"; // Replace with your actual device ID
    const imageElement = document.getElementById('dynamicImage');
    const overlay = document.getElementById('action-layer');
    try {
        const response = await fetch(`/image?device_id=${deviceId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        imageElement.src = imageUrl;

        // 等待图片加载完成
        await new Promise((resolve) => {
            if (imageElement.complete) {
                resolve();
            } else {
                imageElement.addEventListener('load', resolve);
            }
        });
        console.log('图片实际宽度：', imageElement.offsetWidth);
        console.log('图片实际高度：', imageElement.offsetHeight);
        // 设置 overlay 的宽度和高度与图片一致
        overlay.style.width = `${imageElement.offsetWidth}px`;
        overlay.style.height = `${imageElement.offsetHeight}px`;

        overlay.style.display = 'block'; // Hide overlay on success
    } catch (error) {
        console.error('Error fetching image:', error);
        overlay.style.display = 'flex'; // Show overlay on error
    }
}

function startFetching() {
    if (!intervalId) {
        intervalId = setInterval(fetchImage, 100); // Fetch image every 30 milliseconds
    }
}

function stopFetching() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
}