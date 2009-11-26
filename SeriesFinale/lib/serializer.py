from xml.etree import ElementTree as ET

def serialize(obj):
    root = ET.Element(obj.__class__)
    for var, value in var(obj):
        var_element = ET.SubElement(root, var)
        if type(value) == dict:
            sub_element = ET.SubElement(var_element, serialize(value))
            sub_element.set('class', 'object')
        else:
            sub_element = ET.SubElement(var_element, str(value))
            sub_element.set('class', 'str')
    return root

def unserialize(xml_file):
    tree = ET.parse(xml_file)
    root = tree.get_root()
    args = {}
    for child in root.getchildren():
        child_class = child.get('class')
        child_object = None
        if child_class == 'object':
            args[child.tag] = unserialize(child)
        else:
            args[child.tag] = child.text
    root_object = eval('%s(**args)') % root.tag
    return root_object
