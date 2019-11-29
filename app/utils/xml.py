# -*- coding:utf-8 -*-


def dict_to_xml(d):
    xml = '<xml>\n{data}\n</xml>'
    nodes = []
    tpl = '<{name}><![CDATA[{value}]]></{name}>'
    for k in d.keys():
        nodes.append(tpl.format(name=k, value=d[k]))
    data = '\n'.join(nodes)
    return xml.format(data=data)
