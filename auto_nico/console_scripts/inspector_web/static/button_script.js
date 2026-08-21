$(document).ready(function() {
    // 监听开关状态变化
    $('#realtime-switch').change(function() {
        if ($(this).is(':checked')) {
            // 开启实时显示
            startRealtimeUpdates();
        } else {
            // 关闭实时显示
            stopRealtimeUpdates();
        }
    });

    // 刷新按钮点击事件
    $('#refresh-button').click(function() {
        refreshData();
    });

    // 模拟实时更新的函数
    function startRealtimeUpdates() {
        console.log("实时显示已开启");
        document.body.classList.add('realtime-mode');
        $('.node').removeClass('hovered');
        $('.imageControl').css('background-color', 'rgba(144, 238, 144, 0)');
        $('#info-list').empty();
        if (platform === "android") {
            var image = document.getElementById('image_');
            image.src = `/android_video_feed?timestamp=${Date.now()}`;
        } else {
            refreshInterval = setInterval(refreshImage, 500);
        }
    }

    function stopRealtimeUpdates() {
        console.log("实时显示已关闭");
        document.body.classList.remove('realtime-mode');
        clearInterval(refreshInterval); // 停止调用refreshData
        refreshInterval = null;
        refreshData();
    }

    // 提取的请求函数
    function sendRequest(url) {
        console.log(url);
        $.ajax({
            url: url,
            type: 'GET',
            async: true, // 确保请求是异步的
            success: function(data) {
                setTimeout(function() {
                    refreshData();
                }, 500); // 500毫秒 = 0.5秒
            },
            error: function(xhr, status, error) {
                console.error('Request failed:', status, error);
                // 即使请求失败，也可以选择调用refreshData
                refreshData();
            }
        });
    }

    var first_node = document.getElementById('Title');
    var platform = first_node.getAttribute("nico_ui_platform");

    if (platform === "iOS") {
        enableRealtimeIosGestures();
        $('#volume-up').click(function() {
            fetch('/ios_execute_action?action=volume_up');
        });
        $('#volume-down').click(function() {
            fetch('/ios_execute_action?action=volume_down');
        });
    } else {
        $('#ios-gesture-mode-control').hide();
        enableRealtimeAndroidGestures();
        // 处理提交按钮的点击事件
        $('#submit-button').click(function() {
            var inputValue = $('#text-input').val();
            if (inputValue) {
                var url = `/android_excute_action?action=input&inputValue=${inputValue}`;
                sendRequest(url);
            } else {
                alert('Please enter some text.');
            }
        });

        // 处理 home 按钮的点击事件
        $('#home-button').click(function() {
            var url = `/android_excute_action?action=home`;
            sendRequest(url);
        });

        // 处理 back 按钮的点击事件
        $('#back-button').click(function() {
            var url = `/android_excute_action?action=back`;
            sendRequest(url);
        });

        // 处理 menu 按钮的点击事件
        $('#menu-button').click(function() {
            var url = `/android_excute_action?action=menu`;
            sendRequest(url);
        });

        $('#switch-button').click(function() {
            var url = `/android_excute_action?action=switch_app`;
            sendRequest(url);
        });

        $('#volume-up').click(function() {
            var url = `/android_excute_action?action=volume_up`;
            sendRequest(url);
        });

        $('#volume-down').click(function() {
            var url = `/android_excute_action?action=volume_down`;
            sendRequest(url);
        });

        $('#power').click(function() {
            var url = `/android_excute_action?action=power`;
            sendRequest(url);
        });

        $('#delete_text').click(function() {
            var url = `/android_excute_action?action=delete_text`;
            sendRequest(url);
        });
    }

    function enableRealtimeAndroidGestures() {
        var preview = document.getElementById('ui_image');
        var activePointer = null;
        var lastPoint = null;
        var lastMoveTime = 0;
        var touchQueue = Promise.resolve();

        function getImagePoint(event) {
            var image = document.getElementById('image_');
            if (!image || !image.naturalWidth || !image.naturalHeight) {
                return null;
            }
            var rect = image.getBoundingClientRect();
            var scale = Math.min(rect.width / image.naturalWidth, rect.height / image.naturalHeight);
            var renderedWidth = image.naturalWidth * scale;
            var renderedHeight = image.naturalHeight * scale;
            var left = rect.left + (rect.width - renderedWidth) / 2;
            var top = rect.top + (rect.height - renderedHeight) / 2;
            var x = event.clientX - left;
            var y = event.clientY - top;
            if (x < 0 || y < 0 || x > renderedWidth || y > renderedHeight) {
                return null;
            }
            return { x: x / renderedWidth, y: y / renderedHeight };
        }

        function sendTouch(action, point) {
            var params = new URLSearchParams({
                action: action,
                x: point.x.toFixed(6),
                y: point.y.toFixed(6)
            });
            touchQueue = touchQueue
                .then(function() { return fetch(`/android_touch?${params.toString()}`); })
                .catch(function(error) { console.error('Android touch failed:', error); });
        }

        preview.addEventListener('pointerdown', function(event) {
            if (!document.body.classList.contains('realtime-mode')) {
                return;
            }
            var point = getImagePoint(event);
            if (!point) {
                return;
            }
            activePointer = event.pointerId;
            lastPoint = point;
            lastMoveTime = performance.now();
            preview.setPointerCapture(event.pointerId);
            sendTouch('down', point);
            event.preventDefault();
        });

        preview.addEventListener('pointermove', function(event) {
            if (event.pointerId !== activePointer) {
                return;
            }
            var now = performance.now();
            if (now - lastMoveTime < 33) {
                return;
            }
            var point = getImagePoint(event);
            if (point) {
                lastPoint = point;
                lastMoveTime = now;
                sendTouch('move', point);
            }
            event.preventDefault();
        });

        function finishTouch(event) {
            if (event.pointerId !== activePointer) {
                return;
            }
            var point = getImagePoint(event) || lastPoint;
            if (point) {
                sendTouch('up', point);
            }
            activePointer = null;
            lastPoint = null;
            event.preventDefault();
        }

        preview.addEventListener('pointerup', finishTouch);
        preview.addEventListener('pointercancel', finishTouch);
    }

    function enableRealtimeIosGestures() {
        var preview = document.getElementById('ui_image');
        var gestureStart = null;
        var gestureEnd = null;
        var activePointer = null;

        function isDragMode() {
            return $('#ios-drag-switch').is(':checked');
        }

        function sendIosAction(params) {
            var url = `/ios_execute_action?${params.toString()}`;
            console.log('[iOS gesture] request', url);
            fetch(url)
                .then(function(response) { return response.text().then(function(body) { return { response: response, body: body }; }); })
                .then(function(result) { console.log('[iOS gesture] response', result.response.status, result.body); })
                .catch(function(error) { console.error('[iOS gesture] request failed', error); });
        }

        function getDevicePoint(event) {
            var image = document.getElementById('image_');
            var windowNode = document.querySelector('.node[class_name="Window"][bounds]');
            if (!image || !image.naturalWidth || !windowNode) {
                return null;
            }

            var bounds = windowNode.getAttribute('bounds').match(/\[(-?\d+),(-?\d+)\]\[(\d+),(\d+)\]/);
            if (!bounds) {
                return null;
            }

            var rect = image.getBoundingClientRect();
            var scale = Math.min(rect.width / image.naturalWidth, rect.height / image.naturalHeight);
            var renderedWidth = image.naturalWidth * scale;
            var renderedHeight = image.naturalHeight * scale;
            var imageLeft = rect.left + (rect.width - renderedWidth) / 2;
            var imageTop = rect.top + (rect.height - renderedHeight) / 2;
            var imageX = event.clientX - imageLeft;
            var imageY = event.clientY - imageTop;

            if (imageX < 0 || imageY < 0 || imageX > renderedWidth || imageY > renderedHeight) {
                return null;
            }

            return {
                x: imageX / renderedWidth * parseInt(bounds[3]),
                y: imageY / renderedHeight * parseInt(bounds[4])
            };
        }

        preview.addEventListener('pointerdown', function(event) {
            if (!document.body.classList.contains('realtime-mode')) {
                return;
            }
            var point = getDevicePoint(event);
            if (!point) {
                console.warn('[iOS gesture] pointerdown ignored: invalid image coordinates');
                return;
            }
            gestureStart = { x: point.x, y: point.y, time: performance.now() };
            gestureEnd = point;
            activePointer = event.pointerId;
            console.log('[iOS gesture] down', { point: gestureStart, mode: isDragMode() ? 'drag' : 'swipe' });
            preview.setPointerCapture(event.pointerId);
            if (isDragMode()) {
                sendIosAction(new URLSearchParams({
                    action: 'tap',
                    x: point.x.toFixed(2),
                    y: point.y.toFixed(2)
                }));
            }
            event.preventDefault();
        });

        preview.addEventListener('pointermove', function(event) {
            if (event.pointerId !== activePointer) {
                return;
            }
            var point = getDevicePoint(event);
            if (isDragMode() && point && Math.hypot(point.x - gestureEnd.x, point.y - gestureEnd.y) >= 3) {
                console.log('[iOS gesture] move', { start: gestureEnd, end: point });
                sendIosAction(new URLSearchParams({
                    action: 'move',
                    x: gestureEnd.x.toFixed(2),
                    y: gestureEnd.y.toFixed(2),
                    x2: point.x.toFixed(2),
                    y2: point.y.toFixed(2),
                    duration: '0.10'
                }));
                gestureEnd = point;
            }
            event.preventDefault();
        });

        function finishGesture(event) {
            if (event.pointerId !== activePointer) {
                return;
            }
            if (!gestureStart || !document.body.classList.contains('realtime-mode')) {
                gestureStart = null;
                gestureEnd = null;
                activePointer = null;
                return;
            }
            var end = getDevicePoint(event) || gestureEnd;
            if (!end) {
                console.warn('[iOS gesture] pointerup ignored: no valid end coordinates');
                gestureStart = null;
                gestureEnd = null;
                activePointer = null;
                return;
            }

            var moveStart = isDragMode() ? gestureEnd : gestureStart;
            var distance = Math.hypot(end.x - gestureStart.x, end.y - gestureStart.y);
            if (!isDragMode() && distance < 10) {
                console.log('[iOS gesture] swipe mode tap', { point: gestureStart });
                sendIosAction(new URLSearchParams({
                    action: 'tap',
                    x: gestureStart.x.toFixed(2),
                    y: gestureStart.y.toFixed(2)
                }));
            } else if ((isDragMode() && Math.hypot(end.x - moveStart.x, end.y - moveStart.y) >= 1) ||
                       (!isDragMode() && distance >= 10)) {
                console.log('[iOS gesture] final move', { start: moveStart, end: end });
                sendIosAction(new URLSearchParams({
                    action: 'move',
                    x: moveStart.x.toFixed(2),
                    y: moveStart.y.toFixed(2),
                    x2: end.x.toFixed(2),
                    y2: end.y.toFixed(2),
                    duration: isDragMode() ? '0.10' : '0.20'
                }));
            }
            console.log('[iOS gesture] finished', { mode: isDragMode() ? 'drag' : 'swipe' });
            gestureStart = null;
            gestureEnd = null;
            activePointer = null;
            event.preventDefault();
        }

        preview.addEventListener('pointerup', finishGesture);
        preview.addEventListener('pointercancel', finishGesture);
    }
});