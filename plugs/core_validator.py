# -*-coding:utf-8-*-
import re
import json as JSON
from jsonpath import jsonpath
from util.Decorator import validator

'''此处只存放验证方法名， 启动时会自动加载这些验证器方法'''
__all__ = ['equal', 'include', 'regex', 'json']


@validator
def equal(content, expect, **kwargs):
    msg = u'期望结果为：%s， 实际结果为：%s' % (expect, content)
    return (True, None) if content == expect else (False, msg)

@validator
def include(content, expect, **kwargs):
    msg = u'期望结果为包含：%s，实际未包含' % expect
    return (True, None) if expect in content else (False, msg)

@validator
def regex(content, expect, **kwargs):
    r = re.search(expect, content, re.DOTALL)
    msg = u"期望结果为匹配：%s，实际未匹配成功" % expect
    return (True, None) if r else (False, msg)

@validator
def json(content, expect, **kwargs):
    jpath = kwargs['jsonpath']
    try:
        nodes = jsonpath(JSON.loads(content), jpath)
    except Exception, e:
        print e
        msg = u"内容不是JSON格式"
        return False, msg

    if nodes:
        if expect and nodes[0] != expect:
            msg = u'期望[%s]节点结果为：%s， 实际结果为：%s' % (jpath, expect, nodes[0])
            return False, msg
    else:
        msg = u'期望结果为存在节点：%s， 实际未找到该节点' % jpath
        return False, msg
    return True, None

