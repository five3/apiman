# -*-coding:utf-8-*-
import sys


def validator(func):
    func.plug_type = sys._getframe().f_code.co_name
    return func


def executor(func):
    func.plug_type = sys._getframe().f_code.co_name
    return func


def hooker(hook_type):
    plug_type = sys._getframe().f_code.co_name
    def real_hooker(func):
        func.plug_type = plug_type
        func.hook_type = hook_type
        return func
    return real_hooker