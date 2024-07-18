from collections import defaultdict

def add_xpath_att(root, current_path="", parent_class_count=None, level=0):
    """
    Traverse all nodes by level and construct XPath using the class_name attribute and its occurrence count,
    then add the XPath as an attribute to the node.

    :param root: The current XML element being processed
    :param current_path: The XPath path of the current element
    :param parent_class_count: A dictionary recording the occurrence count of each class_name attribute at the current level for the parent
    :param level: The current level
    """
    if parent_class_count is None:
        parent_class_count = defaultdict(int)

    # Get the class_name attribute of the current element
    class_name = root.attrib.get('class_name', root.tag)

    # Update the count for the current class_name attribute
    current_index = parent_class_count[class_name]
    parent_class_count[class_name] += 1

    # Construct the XPath path for the current element
    current_xpath = f"{current_path}/{str(class_name).split('.')[-1]}[{current_index}]".replace("/hierarchy[0]/","")

    # Add the XPath path as an attribute to the current element
    root.set('xpath', current_xpath)

    # Recursively process child elements
    child_class_count = defaultdict(int)
    for child in root:
        add_xpath_att(child, current_xpath, child_class_count, level + 1)
    return root