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
        refreshInterval = setInterval(refreshData, 1000); // 每秒调用一次refreshData
    }

    function stopRealtimeUpdates() {
        console.log("实时显示已关闭");
        clearInterval(refreshInterval); // 停止调用refreshData
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

    if (platform !== "iOS") {
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
});