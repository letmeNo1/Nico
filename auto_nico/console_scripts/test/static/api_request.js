let intervalId;
let isDragging = false;
let longPressTimeout;
const longPressDuration = 500; // 500 milliseconds for long press
let startX, startY;

async function fetchImage() {
    const deviceId = "RFCXA08RFMM"; // Replace with your actual device ID
    const imageElement = document.getElementById('device-image');
    const overlay = document.getElementById('overlay');
    try {
        const response = await fetch(`/image?device_id=${deviceId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        imageElement.src = imageUrl;
        overlay.style.display = 'none'; // Hide overlay on success
    } catch (error) {
        console.error('Error fetching image:', error);
        overlay.style.display = 'flex'; // Show overlay on error
    }
}

function startFetching() {
    if (!intervalId) {
        intervalId = setInterval(fetchImage, 30); // Fetch image every 30 milliseconds
    }
}
