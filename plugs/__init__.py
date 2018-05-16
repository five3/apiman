# -*-coding:utf-8-*-
import os
import importlib

'''该模块只对外开放一个实例，并且会自动加载本目录下其它文件中的验证器。验证器格式参考core.py'''
__all__ = ['validator', 'executor', 'hooker']

plug_type = ['validator', 'executor', 'hooker']
plug_mapping = {}


def _func_packaging_(cur_module):
    for func in cur_module.__all__:
        func_obj = getattr(cur_module, func)

        if func_obj.plug_type not in plug_type:
            continue

        cur_plug = plug_mapping.setdefault(func_obj.plug_type, {})
        cur_plug[func] = func_obj


def main():
    for sub in os.listdir(os.path.dirname(__file__)):
        if os.path.isdir(sub):
            continue

        if '__init__.py' == sub:
            continue

        module_name, ext = sub.rsplit('.', 1)
        if 'py' != ext:
            continue

        cur_module = importlib.import_module('plugs.%s' % module_name)
        _func_packaging_(cur_module)


main()
# print plug_mapping


class Validator(object):
    def __init__(self, method_mapping):
        self.method_mapping = method_mapping

    def verify(self, name, actual, expect, **kwargs):
        actual = actual.strip()
        expect = expect.strip() if expect else ''
        func = self.method_mapping.get(name.strip())
        if func and callable(func):
            return func(actual, expect, **kwargs)
        else:
            raise ValueError("没有指定的验证器:%s" % name)


class Executor(object):
    def __init__(self, method_mapping):
        self.method_mapping = method_mapping

    def send(self, name, **kwargs):
        func = self.method_mapping.get(name)
        if func and callable(func):
            return func(**kwargs)


class Hooker(object):
    def __init__(self, method_mapping):
        self.method_mapping = method_mapping
        self.hook_mapping = {}
        self._filter_()

    def _filter_(self):
        for name, func in self.method_mapping.items():
            self.hook_mapping.setdefault(func.hook_type, []).append(func)

    def do(self, hook_type, **kwargs):
        funcs = self.hook_mapping.get(hook_type)
        for func in funcs:
            if func and callable(func):
                return func(**kwargs)


validator = Validator(plug_mapping['validator'])
executor = Executor(plug_mapping['executor'])
hooker = Hooker(plug_mapping['hooker'])
