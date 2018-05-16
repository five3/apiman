# -*-coding:utf-8-*-
from util.Decorator import hooker
from util.Constant import HOOK_POST_ALL, HOOK_POST_REQUEST, HOOK_POST_TESTING, HOOK_PRE_ALL, HOOK_PRE_REQUEST, HOOK_PRE_TESTING

'''此处只存放hook方法名， 启动时会自动加载这些方法'''
__all__ = ['set_up', 'init', 'add_header', 'deal_response', 'destroy', 'clean_up']


@hooker(HOOK_PRE_ALL)
def set_up(all_test_data, context, **kwargs):
    pass


@hooker(HOOK_PRE_TESTING)
def init(test_data, index, context, **kwargs):

    if not context['continue']:
        return

    if 'pre_case' in test_data:
        case_name = test_data['pre_case']
        pre_test_data = context['utils'].get_test_data_by_case_name(case_name)
        if pre_test_data:
            r = context['utils'].run_with_data(pre_test_data, index)
            context['continue'] = r


@hooker(HOOK_PRE_REQUEST)
def add_header(args, context, **kwargs):
    pass


@hooker(HOOK_POST_REQUEST)
def deal_response(code, txt, context, **kwargs):
    pass


@hooker(HOOK_POST_TESTING)
def destroy(flag, msg, context, **kwargs):
    pass


@hooker(HOOK_POST_ALL)
def clean_up(index, context, **kwargs):
    pass
