const actionLayer = document.getElementById('action-layer');

function getPercentageCoordinates(x, y) {
    const rect = actionLayer.getBoundingClientRect();
    const xPercent = ((x - rect.left) / rect.width) * 100;
    const yPercent = ((y - rect.top) / rect.height) * 100;
    return { xPercent, yPercent };
}

function sendEventToServer(eventType, xPercent, yPercent) {
    fetch('/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ eventType, xPercent, yPercent })
    })
    .then(response => response.json())
    .then(data => console.log('Server response:', data))
    .catch(error => console.error('Error:', error));
}

function sendActionToServer(actionType, xPercent, yPercent) {
    fetch('/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({actionType, xPercent, yPercent })
    })
    .then(response => response.json())
    .then(data => console.log('Server response:', data))
    .catch(error => console.error('Error:', error));
}

actionLayer.addEventListener('mousedown', (event) => {
    const startX = event.clientX;
    const startY = event.clientY;
    const { xPercent, yPercent } = getPercentageCoordinates(startX, startY);
    console.log('Press detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');

    sendActionToServer("touch_down",xPercent.toFixed(2), yPercent.toFixed(2));
});

actionLayer.addEventListener('mousemove', (event) => {
    const { xPercent, yPercent } = getPercentageCoordinates(event.clientX, event.clientY);
    console.log('Move detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    sendActionToServer("touch_move",xPercent.toFixed(2), yPercent.toFixed(2));
});

actionLayer.addEventListener('mouseup', (event) => {
    const endX = event.clientX;
    const endY = event.clientY;
    const { xPercent, yPercent } = getPercentageCoordinates(endX, endY);
    console.log('Release detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    sendActionToServer("touch_up",xPercent.toFixed(2), yPercent.toFixed(2));
});

// For touch devices
actionLayer.addEventListener('touchstart', (event) => {
    const touch = event.touches[0];
    const startX = touch.clientX;
    const startY = touch.clientY;
    const { xPercent, yPercent } = getPercentageCoordinates(startX, startY);
    console.log('Press detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    sendEventToServer('press', xPercent.toFixed(2), yPercent.toFixed(2));
});

actionLayer.addEventListener('touchmove', (event) => {
    const touch = event.touches[0];
    const { xPercent, yPercent } = getPercentageCoordinates(touch.clientX, touch.clientY);
    console.log('Move detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    sendEventToServer('move', xPercent.toFixed(2), yPercent.toFixed(2));
});

actionLayer.addEventListener('touchend', (event) => {
    const touch = event.changedTouches[0];
    const endX = touch.clientX;
    const endY = touch.clientY;
    const { xPercent, yPercent } = getPercentageCoordinates(endX, endY);
    console.log('Release detected at:', xPercent.toFixed(2) + '%', yPercent.toFixed(2) + '%');
    sendEventToServer('release', xPercent.toFixed(2), yPercent.toFixed(2));
});