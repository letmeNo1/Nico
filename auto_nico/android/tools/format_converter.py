import re


def add_xpath_att(node_root):
    def add_xpath(node, xpath='', skip_root=True):
        # 如果skip_root为True，将其设置为False并返回
        if skip_root:
            skip_root = False
        else:
            # 生成这个节点的XPath
            xpath += '/' + node.get("class_name").split(".")[-1] + '[' + str(node.get('index')) + ']'

            # 将XPath添加到节点的属性中
            node.set('xpath', xpath[1:])

        # 对每个子节点递归调用这个函数
        for i, child in enumerate(node, start=0):
            child.set('index', str(i))
            add_xpath(child, xpath, skip_root)

    # 解析XML文件
    root = node_root

    # 对根节点调用add_xpath函数
    add_xpath(root)

    return root


def convert_xpath(input_xpath):
    # 使用正则表达式匹配所有的元素和索引
    matches = re.findall(r'(\w+)\[(\d+)\]', input_xpath)

    # 生成新的XPath
    output_xpath = '.'
    for match in matches:
        element, index = match
        class_name = f'[contains(@class_name,"widget.{element}")]'
        output_xpath += f'/child::*[{int(index) + 1}]{class_name}'
    return output_xpath
