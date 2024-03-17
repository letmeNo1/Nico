
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

    var blankLeft = (displayedWidth - scaledWidth) / 2;
    var blankTop = (displayedHeight - scaledHeight) / 2;

    for (var i = 0; i < listItems.length; i++) {
        var bounds = listItems[i].getAttribute('bounds'); /* 获取当前被悬停元素的bounds属性 */
        var identifier = listItems[i].getAttribute('identifier'); /* 获取当前被悬停元素的bounds属性 */

        if (bounds) {
            var matches = bounds.match(/\[(\d+),(\d+)\]\[(\d+),(\d+)\]/);
                if (matches) {
                    var x1 = parseInt(matches[1]) * scale + blankLeft;
                    var y1 = parseInt(matches[2]) * scale + blankTop; ;
                    var x2 = parseInt(matches[3]) * scale + blankLeft;
                    var y2 = parseInt(matches[4]) * scale + blankTop;
                }
        }
        // 添加控件元素
        var imageControl = document.createElement('div');
        imageControl.setAttribute('img-identifier', identifier);
        imageControl.style.position = 'absolute';
        imageControl.style.left = x1 + "px"; /* 相对于目标元素左侧距离 */
        imageControl.style.top = y1 + "px"; /* 相对于目标元素顶部距离 */
        imageControl.style.width = x2 -x1 + "px"; /* 新元素宽度 */
        imageControl.style.height = y2 -y1 + "px"; /* 新元素高度 */
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
                var attrs = this.attributes; // 获取当前被悬停元素的所有属性
                infoList.innerHTML = ''; // 清空ul元素的内容
                for (var j = 0; j < attrs.length; j++) {
                    if (attrs[j].name != 'class' && attrs[j].name != 'style' && attrs[j].name != 'identifier') {
                        var attr = attrs[j];
                        var li = document.createElement('li'); // 创建一个新的li元素
                        li.textContent = attr.name + ': ' + attr.value; // 设置li元素的内容
                        infoList.appendChild(li); // 将li元素添加到ul元素中
                    }
                }
                var identifier = this.getAttribute("identifier");
                console.log('[img-identifier="${identifier}"]')

                var img_element = document.querySelector(`[img-identifier="${identifier}"]`);
                console.log(img_element)
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


window.onload = function() {
    refreshData();
};

function crate_attributes_list(text_element){
    var infoList = document.getElementById('info-list'); // 获取新的ul元素
    var attrs = text_element.attributes; // 获取当前被悬停元素的所有属性
    infoList.innerHTML = ''; // 清空ul元素的内容
    for (var j = 0; j < attrs.length; j++) {
        console.log("hank"+ attrs[j].name != 'class')
        if (attrs[j].name != 'class' && attrs[j].name != 'style' && attrs[j].name != 'identifier') {
            var attr = attrs[j];
            var li = document.createElement('li'); // 创建一个新的li元素
            li.textContent = attr.name + ': ' + attr.value; // 设置li元素的内容
            infoList.appendChild(li); // 将li元素添加到ul元素中
        }
    }
}


function addImageListeners() {
    var imageControlList = document.getElementsByClassName('imageControl'); // 获取新的ul元素
    for (var i = 0; i < imageControlList.length; i++) {
        imageControlList[i].addEventListener('mouseover', function() {
            console.log('"mousemove" event on canvas');
    
            this.style.backgroundColor = 'rgba(144, 238, 144, 0.5)';
            var identifier = this.getAttribute("img-identifier");
            var text_element = document.querySelector(`[identifier="${identifier}"]`);

            text_element.classList.add('hovered');
            crate_attributes_list(text_element)

        });

        imageControlList[i].addEventListener('click', function() {
            console.log('"mousemove" event on canvas');
    
            this.style.backgroundColor = 'rgba(144, 238, 144, 0.5)';
            var identifier = this.getAttribute("img-identifier");
            var text_element = document.querySelector(`[identifier="${identifier}"]`);
            crate_attributes_list(text_element)
            text_element.classList.add('hovered');
            text_element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });

           

        });
        imageControlList[i].addEventListener('mouseout', function() {
            this.style.backgroundColor = 'rgba(144, 238, 144, 0)';
            var identifier = this.getAttribute("img-identifier");
            var text_element = document.querySelector(`[identifier="${identifier}"]`);
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

$(document).ready(function() {
    $('#refresh-button').click(function() {
        refreshData();
    });
});