# -*-coding:utf-8-*-
from util.Decorator import executor
import requests
from util import warp_files

'''此处只存放执行方法名， 启动时会自动加载这些方法'''
__all__ = ['http_sender']


@executor
def http_sender(url=None, method='get', data=None, headers=None, files=None, encoding='utf-8', **kwargs):
    if not url:
        raise ValueError('没有指定URL参数')

    method = method.strip().lower() \
        if method and isinstance(method, str) else 'get'
    if hasattr(requests, method):
        func = getattr(requests, method)
        if method in ['post', 'put', 'patch']:
            multiple_files = []
            if files:
                multiple_files = warp_files(files)
            rsp = func(url, data, headers=headers, files=multiple_files)
        else:
            rsp = func(url, params=data, headers=headers)
    else:
        rsp = requests.get(url, params=data, headers=headers)
    rsp.encoding = encoding
    code = rsp.status_code
    txt = rsp.text
    return code, txt


