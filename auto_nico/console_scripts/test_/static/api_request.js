let intervalId;
let longPressTimeout;
const longPressDuration = 500; // 500 milliseconds for long press
let startX, startY;

async function fetchImage() {
    const imageElement = document.getElementById('dynamicImage');
    const overlay = document.getElementById('action-layer');
    // 保存原来图片的 src、尺寸和位置
    const originalSrc = imageElement.src;
    const originalWidth = imageElement.offsetWidth;
    const originalHeight = imageElement.offsetHeight;
    const originalLeft = imageElement.offsetLeft;
    const originalTop = imageElement.offsetTop;

    try {
        const response = await fetch(`/dynamic_image`);
        if (!response.ok) throw new Error('Network response was not ok');

        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        // 处理图片加载
        await new Promise((resolve) => {
            const tempImage = new Image();
            tempImage.src = imageUrl;
            tempImage.onload = () => {
                // 新图片加载完成后更新 src 和尺寸
                imageElement.src = imageUrl;
                imageElement.style.width = `${originalWidth}px`;
                imageElement.style.height = `${originalHeight}px`;
                // 恢复原图片位置
                imageElement.style.position = 'absolute';
                imageElement.style.left = `${originalLeft}px`;
                imageElement.style.top = `${originalTop}px`;
                resolve();
            };
            tempImage.onerror = () => {
                throw new Error('Image loading failed');
            };
        });

        console.log(imageElement.offsetWidth);
        // 关键：设置遮罩尺寸与图片一致
        overlay.style.width = `${originalWidth}px`;
        overlay.style.height = `${originalHeight}px`;
        overlay.style.left = `${originalLeft}px`;
        overlay.style.top = `${originalTop}px`;
        overlay.style.display = 'block';

    } catch (error) {
        console.log('Error fetching image:', error);
        // 加载失败恢复原来的图片
        imageElement.src = originalSrc;
        overlay.style.display = 'flex';
    }
}



function fetchStaticImage() {
    const imageElement = document.getElementById('dynamicImage');
    const overlay = document.getElementById('action-layer');
    const errorMessage = document.getElementById('error-message');
    $.get('/static_image', function(data) {
        var img = document.querySelector('img');

        // 处理可能的 JSON 格式
        if (typeof data === 'object') {
            if (data.image) {
                img.src = 'data:image/png;base64,' + data.image;
            } else {
                console.error('无效数据格式，缺少 image 字段');
                return;
            }
        } else {
            // 直接使用字符串
            img.src = 'data:image/png;base64,' + data;
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('请求失败:', errorThrown);
    });
}


function startFetching() {
    if (!intervalId) {
        intervalId = setInterval(fetchImage, 30); // Fetch image every 30 milliseconds
    }
}

function stopFetching() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
}

fetchStaticImage()

