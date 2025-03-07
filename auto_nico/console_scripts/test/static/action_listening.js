const actionLayer = document.getElementById('action-layer');

function getPercentageCoordinates(x, y) {
    const rect = actionLayer.getBoundingClientRect();
    const xPercent = ((x - rect.left) / rect.width) * 100;
    const yPercent = ((y - rect.top) / rect.height) * 100;
    return { xPercent, yPercent };
}

actionLayer.addEventListener('mousedown', (event) => {
    isDragging = false;
    startX = event.clientX;
    startY = event.clientY;

    longPressTimeout = setTimeout(() => {
        const { xPercent, yPercent } = getPercentageCoordinates(startX, startY);
        console.log('Long press detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    }, longPressDuration);
});

actionLayer.addEventListener('mousemove', (event) => {
    if (Math.abs(event.clientX - startX) > 5 || Math.abs(event.clientY - startY) > 5) {
        isDragging = true;
        clearTimeout(longPressTimeout);
    }
});

actionLayer.addEventListener('mouseup', (event) => {
    clearTimeout(longPressTimeout);
    const { xPercent: startXPercent, yPercent: startYPercent } = getPercentageCoordinates(startX, startY);
    const { xPercent: endXPercent, yPercent: endYPercent } = getPercentageCoordinates(event.clientX, event.clientY);
    if (isDragging) {
        console.log('Swipe/drag detected from:', startXPercent.toFixed(2) + '%', startYPercent.toFixed(2) + '%', 'to:', endXPercent.toFixed(2) + '%', endYPercent.toFixed(2) + '%');
    } else {
        console.log('Click detected at:', startXPercent.toFixed(2) + '%', startYPercent.toFixed(2) + '%');
    }
});

actionLayer.addEventListener('mouseleave', () => {
    clearTimeout(longPressTimeout);
});

// For touch devices
actionLayer.addEventListener('touchstart', (event) => {
    isDragging = false;
    const touch = event.touches[0];
    startX = touch.clientX;
    startY = touch.clientY;

    longPressTimeout = setTimeout(() => {
        const { xPercent, yPercent } = getPercentageCoordinates(startX, startY);
        console.log('Long press detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    }, longPressDuration);
});

actionLayer.addEventListener('touchmove', (event) => {
    const touch = event.touches[0];
    if (Math.abs(touch.clientX - startX) > 5 || Math.abs(touch.clientY - startY) > 5) {
        isDragging = true;
        clearTimeout(longPressTimeout);
    }
});

actionLayer.addEventListener('touchend', (event) => {
    clearTimeout(longPressTimeout);
    const touch = event.changedTouches[0];
    const { xPercent: startXPercent, yPercent: startYPercent } = getPercentageCoordinates(startX, startY);
    const { xPercent: endXPercent, yPercent: endYPercent } = getPercentageCoordinates(touch.clientX, touch.clientY);
    if (isDragging) {
        console.log('Swipe/drag detected from:', startXPercent.toFixed(2) + '%', startYPercent.toFixed(2) + '%', 'to:', endXPercent.toFixed(2) + '%', endYPercent.toFixed(2) + '%');
    } else {
        console.log('Click detected at:', startXPercent.toFixed(2) + '%', startYPercent.toFixed(2) + '%');
    }
});