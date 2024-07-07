import lxml.etree as ET
from lxml import etree


# 用于计算缩进的函数
def count_leading_spaces(s):
    return len(s) - len(s.lstrip(' '))


def get_element_of_attr(search_str, attr_list):
    for element in attr_list:
        if search_str in element:
            return element.split(": ")[1].strip().replace("'", "")
    return ""


def exclude_invalid_rows(hierarchy_string, front, end):
    lines = hierarchy_string.split('\n')

    trimmed_lines = lines[front:end]

    trimmed_string = '\n'.join(trimmed_lines)

    return trimmed_string


def generate_xpath(element):
    parts = []
    ancestors = list(element.iterancestors())  # Convert the iterator to a list
    ancestors.reverse()
    ancestors.pop(0)  # Reverse the list
    ancestors.append(element)

    for ancestor in ancestors:
        class_name = str(ancestor.get('class_name'))
        index = sum(1 for sibling in ancestor.itersiblings(preceding=True) if sibling.get('class_name') == class_name)
        parts.append(f"{class_name}[{index}]")

    return '/'.join(parts)


def converter(hierarchy_string, front=3, end=-8) -> str:
    hierarchy_string = exclude_invalid_rows(hierarchy_string, front, end).replace("Window (Main)", "Window")
    elements_str = hierarchy_string.split('\n')
    # 创建 XML 根元素
    root = ET.Element(f"hierarchy")

    # 用于存储上一级的元素引用
    parent_stack = [(root, 0)]

    # 遍历数组中的每个字符串
    for node_index, element_str in enumerate(elements_str):
        # 计算前导空格数，以确定层级
        element_str = element_str[4:]
        indent = count_leading_spaces(element_str)
        parent, index = parent_stack[-1]
        element_attrs = element_str.strip().replace("{", "").replace("}", "").split(",")
        class_name = element_attrs[0]
        x = round(float(element_attrs[2].strip()))
        y = round(float(element_attrs[3].strip()))
        w = round(float(element_attrs[4].strip()))
        h = round(float(element_attrs[5].strip()))
        bounds = f"[{x},{y}][{w},{h}]"
        left = round(float(element_attrs[4].strip())) + x
        top = round(float(element_attrs[5].strip())) + y
        label = get_element_of_attr("label", element_attrs)
        identifier = get_element_of_attr("identifier", element_attrs)
        value = get_element_of_attr("value", element_attrs)
        title = get_element_of_attr("title", element_attrs)
        level = int(indent / 2)  # 假设每个层级缩进两个空格

        # 如果当前层级为0，重置父栈
        if level == 0 and node_index != 0:
            parent_stack = [(root, 0)]

        # 获取当前的父元素
        parent, index = parent_stack[-1]

        # 创建 XML 元素
        element = ET.Element("node")
        # 如果当前层级小于或等于栈的大小，需要回退到正确的父元素
        while level <= len(parent_stack) - 1:
            parent_stack.pop()
            if not parent_stack:  # break the loop if parent_stack is empty
                break
            parent, index = parent_stack[-1]

        # 将当前元素添加到父元素下
        parent.append(element)
        text = ""
        _index = len(parent) - 1
        for att in [label, title]:
            if att != "":
                text = att
                break
        element.set("index", str(len(parent) - 1))
        element.set("class_name", class_name)
        element.set("bounds", bounds)
        element.set("letf", str(left))
        element.set("top", str(top))
        element.set("text", text)
        element.set("value", value)
        element.set("identifier", identifier)
        element.set("xpath", generate_xpath(element))

        # print(ET.ElementTree(element).getpath(element))
        # print(element_str)

        # 更新父栈和当前元素
        parent_stack.append((element, index + 1))

    # 打印 XML 字符串
    tree = ET.ElementTree(root)
    # 获取根元素
    root_element = tree.getroot()
    tree_string = etree.tostring(root_element, pretty_print=True, xml_declaration=True, encoding="utf-8")
    return tree_string.decode("utf-8")


srt = '''Attributes: Application, 0x105a2f7b0, pid: 994, label: 'Phone call'
Element subtree:
Application, 0x105a2f7b0, pid: 994, label: 'Phone call'
    Window, 0x105a2fd90, {{0.0, 0.0}, {414.0, 736.0}}
      Other, 0x105a2feb0, {{0.0, 0.0}, {414.0, 736.0}}
        Other, 0x105a30270, {{0.0, 0.0}, {414.0, 736.0}}
          Other, 0x105a2ffd0, {{0.0, 0.0}, {414.0, 736.0}}
            Other, 0x105a300f0, {{0.0, 0.0}, {414.0, 736.0}}
              Other, 0x105a30810, {{0.0, 0.0}, {414.0, 736.0}}
    Window (Main), 0x105a30390, {{0.0, 0.0}, {414.0, 736.0}}
      Other, 0x105a304b0, {{0.0, 0.0}, {414.0, 736.0}}
        Other, 0x105a305d0, {{0.0, 0.0}, {414.0, 736.0}}
          Other, 0x105a306f0, {{0.0, 0.0}, {414.0, 736.0}}
            Other, 0x105a30930, {{0.0, 0.0}, {414.0, 736.0}}
              Other, 0x105a30a50, {{0.0, 0.0}, {414.0, 736.0}}
                Other, 0x105a30b70, {{0.0, 0.0}, {414.0, 736.0}}
                  Other, 0x105a30c90, {{0.0, 0.0}, {414.0, 736.0}}
                    Other, 0x105a30db0, {{0.0, 0.0}, {414.0, 736.0}}
                      Other, 0x105a30f90, {{20.0, 64.0}, {374.0, 69.0}}
                        Other, 0x105a310b0, {{20.0, 64.0}, {374.0, 69.0}}, identifier: 'PHSingleCallParticipantLabelView'
                          StaticText, 0x105a311d0, {{88.0, 64.0}, {238.3, 40.7}}, identifier: 'PHMarqueeView', label: '‪158 8020 6986‬'
                          Other, 0x105a312f0, {{138.0, 106.7}, {138.0, 26.3}}
                            StaticText, 0x105a31410, {{138.0, 106.7}, {138.0, 26.3}}, identifier: 'PHSingleCallParticipantLabelView_StatusLabel', label: 'Xiamen, Fujian'
                      Other, 0x105a31530, {{0.0, 463.7}, {414.0, 272.3}}
                        Button, 0x105a31650, {{52.0, 463.7}, {82.0, 82.0}}, label: 'Remind Me'
                          StaticText, 0x105a31770, {{52.0, 495.7}, {82.0, 19.1}}, label: 'Remind Me'
                        Button, 0x105a31890, {{52.0, 575.7}, {82.0, 82.0}}, identifier: 'Decline', label: 'Decline'
                          StaticText, 0x105a319b0, {{66.0, 665.7}, {55.0, 20.0}}, label: 'Decline'
                        Button, 0x105a31ad0, {{280.0, 463.7}, {82.0, 82.0}}, label: 'Message'
                          StaticText, 0x105a31bf0, {{280.0, 496.0}, {82.0, 19.1}}, label: 'Message'
                        Button, 0x105a31d10, {{280.0, 575.7}, {82.0, 82.0}}, identifier: 'Accept', label: 'Answer call'
                          StaticText, 0x105a31e30, {{295.0, 665.7}, {52.0, 20.0}}, label: 'Accept'
Path to element:
 →Application, 0x105a2f7b0, pid: 994, label: 'Phone call'
Query chain:
 →Find: Application 'com.apple.InCallService'
  Output: {
    Application, 0x105637a60, pid: 994, label: 'Phone call'
  }
'''

# print(converter(srt))