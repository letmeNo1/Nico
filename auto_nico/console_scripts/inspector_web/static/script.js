var refreshInterval;

function calculateCenter(bounds) {
    // 使用正则表达式提取坐标
    var matches = bounds.match(/\[(\d+),(\d+)\]\[(\d+),(\d+)\]/);
    if (matches) {
        var x1 = parseInt(matches[1]);
        var y1 = parseInt(matches[2]);
        var x2 = parseInt(matches[3]);
        var y2 = parseInt(matches[4]);

        // 计算中心点坐标
        var centerX = (x1 + x2) / 2;
        var centerY = (y1 + y2) / 2;

        return { centerX: centerX, centerY: centerY };
    } else {
        throw new Error("Invalid bounds format");
    }
}

function initImageControl(){
    var listItems = document.getElementsByClassName('node');
    var ui_image = document.getElementById('ui_image');
    var img = document.getElementById('image_')
    var displayedWidth = img.clientWidth;
    var displayedHeight = img.clientHeight;
    var actualWidth = img.naturalWidth;
    var actualHeight = img.naturalHeight;

    var scale = Math.min(displayedWidth / actualWidth, displayedHeight / actualHeight);
    var scaledWidth = scale * actualWidth;
    var scaledHeight = scale * actualHeight;
    // 对于iOS 需要将所有元素的宽高都 * （图像真实宽高/第一个窗口的宽高(也就是调用获取的屏幕的宽高))
    if (listItems[0].innerText.indexOf("iOS") !== -1) {
         console.log(listItems[1].getAttribute('bounds'))
         h_from_api = parseInt(listItems[1].getAttribute('bounds').split(',').pop().match(/\d+/)[0])
         scale = scale * actualHeight/h_from_api

    }

    var blankLeft = (displayedWidth - scaledWidth) / 2;
    var blankTop = (displayedHeight - scaledHeight) / 2;

    for (var i = 0; i < listItems.length; i++) {
        var bounds = listItems[i].getAttribute('bounds');
        var identifier_number = listItems[i].getAttribute('identifier_number');
        if (bounds) {
            var matches = bounds.match(/\[(\d+),(\d+)\]\[(\d+),(\d+)\]/);
                if (matches) {
                    var x1 = parseInt(matches[1]) * scale + blankLeft;
                    var y1 = parseInt(matches[2]) * scale + blankTop; ;
                    if (listItems[0].innerText.indexOf("iOS") !== -1) {
                        var x2 = parseInt(matches[3]) * scale;
                        var y2 = parseInt(matches[4]) * scale;
                    }else{
                        var x2 = parseInt(matches[3]) * scale + blankLeft;
                        var y2 = parseInt(matches[4]) * scale + blankTop;}
                }
        }

        // 添加控件元素
        var imageControl = document.createElement('div');
        imageControl.setAttribute('img-identifier_number', identifier_number);
        imageControl.style.position = 'absolute';
        imageControl.style.left = x1 + "px"; /* 相对于目标元素左侧距离 */
        imageControl.style.top = y1 + "px"; /* 相对于目标元素顶部距离 */
        if (listItems[0].innerText.indexOf("iOS") !== -1) {
            imageControl.style.width = x2 + "px"; /* 新元素宽度 */
            imageControl.style.height = y2 + "px"; /* 新元素高度 */
        }else{
            imageControl.style.width = x2 -x1 + "px"; /* 新元素宽度 */
            imageControl.style.height = y2 -y1 + "px"; /* 新元素高度 */
        }


        imageControl.style.backgroundColor = 'rgba(144, 238, 144, 0)';
        imageControl.className = 'imageControl';
        ui_image.appendChild(imageControl);
    }
}

function addTextControlHoverListeners() {
    var listItems = document.getElementsByClassName('node');
    var infoList = document.getElementById('info-list'); // 获取新的ul元素
    for (var i = 0; i < listItems.length; i++) {
        listItems[i].addEventListener('mouseover', function() {
            this.classList.add('hovered');
            infoList.innerHTML = ''; // 清空ul元素的内容
            xpath = this.getAttribute('xpath')
            crate_attributes_list(this)

            var identifier_number = this.getAttribute("identifier_number");
            var img_element = document.querySelector(`[img-identifier_number="${identifier_number}"]`);
            img_element.style.backgroundColor = 'rgba(144, 238, 144, 0.5)';
        });
        listItems[i].addEventListener('mouseout', function() {
            this.classList.remove('hovered');
            var imageControlList = document.getElementsByClassName('imageControl'); // 获取新的ul元素
            for (var i = 0; i < imageControlList.length; i++) {
                imageControlList[i].style.backgroundColor = 'rgba(144, 238, 144, 0)';
            }
        });
    }
}

function crate_attributes_list(text_element){
    var infoList = document.getElementById('info-list'); // 获取新的ul元素
    var first_node = document.getElementById('Title')
    var attrs = text_element.attributes; // 获取当前被悬停元素的所有属性
    var platform = first_node.getAttribute("nico_ui_platform")

    infoList.innerHTML = ''; // 清空ul元素的内容
    xpath = text_element.getAttribute('xpath')
    package_name = first_node.getAttribute('current_package_name')
    if (platform == "iOS") {
        url = `/get_element_attribute?id=${package_name}&xpath=${xpath}`
        console.log(url)

        var element_attribute;

        $.ajax({
            url: url,
            type: 'GET',
            async: false,
            success: function(data) {
                element_attribute = data;
            }
        });

        // 将字典中的键值对添加到 NamedNodeMap 中
       Object.entries(element_attribute).forEach(function([key, value]) {
            var li = document.createElement('li'); // 创建一个新的li元素
            li.textContent = key + ': ' + value; // 设置li元素的内容
            infoList.appendChild(li); // 将li元素添加到ul元素中
        });

    }else{
        var attrs = text_element.attributes; // 获取当前被悬停元素的所有属性
        for (var j = 0; j < attrs.length; j++) {
            if (attrs[j].name != 'class' && attrs[j].name != 'style' && attrs[j].name != 'identifier_number') {
                var attr = attrs[j];
                var li = document.createElement('li'); // 创建一个新的li元素
                li.textContent = attr.name + ': ' + attr.value; // 设置li元素的内容
                infoList.appendChild(li); // 将li元素添加到ul元素中
            }
        }
    }
}

function addImageListeners() {
    var first_node = document.getElementById('Title')
    var platform = first_node.getAttribute("nico_ui_platform")
    var imageControlList = document.getElementsByClassName('imageControl'); // 获取新的ul元素
    for (var i = 0; i < imageControlList.length; i++) {
        imageControlList[i].addEventListener('mouseover', function() {
            console.log('"mousemove" event on canvas');
            this.style.backgroundColor = 'rgba(144, 238, 144, 0.5)';
            var identifier_number = this.getAttribute("img-identifier_number");
            var text_element = document.querySelector(`[identifier_number="${identifier_number}"]`);
            text_element.classList.add('hovered');
            crate_attributes_list(text_element)
        });

        imageControlList[i].addEventListener('click', function() {
            console.log('"mousemove" event on canvas');
            this.style.backgroundColor = 'rgba(144, 238, 144, 0.5)';
            var identifier_number = this.getAttribute("img-identifier_number");
            var text_element = document.querySelector(`[identifier_number="${identifier_number}"]`);
            crate_attributes_list(text_element)
            text_element.classList.add('hovered');
            text_element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        });

        imageControlList[i].addEventListener('dblclick', function() {
            console.log('"dblclick" event on canvas');
            var identifier_number = this.getAttribute("img-identifier_number");
            var text_element = document.querySelector(`[identifier_number="${identifier_number}"]`);
            text_element.classList.add('hovered');
            var center = calculateCenter(text_element.getAttribute("bounds"));
            console.log(platform)

            // 在这里添加双击事件的逻辑
            if (platform == "iOS") {



             }
             else {
                url = `/android_excute_action?action=click&x=${center.centerX}&y=${center.centerY}`;
                console.log(url);
                var element_attribute;

                $.ajax({
                    url: url,
                    type: 'GET',
                    async: true, // 确保请求是异步的
                    success: function(data) {
                       setTimeout(function() {
                            refreshData();
                        }, 500); // 1000毫秒 = 1秒
                    },
                    error: function(xhr, status, error) {
                        console.error('Request failed:', status, error);
                        // 即使请求失败，也可以选择调用refreshData
                        refreshData();
                    }
                });
            }
        });


        imageControlList[i].addEventListener('mouseout', function() {
            this.style.backgroundColor = 'rgba(144, 238, 144, 0)';
            var identifier_number = this.getAttribute("img-identifier_number");
            var text_element = document.querySelector(`[identifier_number="${identifier_number}"]`);
            text_element.classList.remove('hovered');
        });
    }
}

function refreshData() {
    bounds_list = []
    // 发送GET请求到服务器，刷新图片
    $.get('/refresh_image', function(data) {
        var img = document.querySelector('img');
        img.src = 'data:image/png;base64,' + data;
        img.setAttribute("id","image_")
    });

    // 发送GET请求到服务器，刷新XML
    $.get('/refresh_ui_xml', function(data) {
        var xmlContainer = document.querySelector('.content-inner');
        xmlContainer.innerHTML = data;
        initImageControl()
        addTextControlHoverListeners(); // 添加新的事件监听器
        addImageListeners(); // 添加新的事件监听器
    });
}

window.onload = function() {
    refreshData();
};