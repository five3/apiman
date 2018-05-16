#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import getopt
import json
import os
import sys

from util.DataPool import DataPool
from plugs import executor, validator, hooker
from util.Constant import HOOK_POST_ALL, HOOK_POST_REQUEST, HOOK_POST_TESTING, HOOK_PRE_ALL, HOOK_PRE_REQUEST, HOOK_PRE_TESTING

reload(sys)
sys.setdefaultencoding('utf8')


class utils(object):
    def __init__(self):
        pass


DP = DataPool()
CONTEXT = {"continue": True, "utils": utils()}
COUNT = PASS = FAIL = SKIP = 0
QUITE = False
USAGE = 'Usage: \r\n\t' \
            '%s -u http://www.baidu.com -m get' % sys.argv[0]


def parse_args():
    global QUITE
    opts, args = getopt.getopt(sys.argv[1:], "qhc:d:e:f:m:t:u:v:C:D:E:H:N:P:")
    headers = {}
    files = []
    url = method = data = encoding = expect = \
        config_file = db_str = test_name = test_priority = \
        category = tag = version = None

    for op, value in opts:
        if op == "-u":  #url
            url = value
        elif op == "-m": #method
            method = value
        elif op == '-d': #data
            try:
                data = json.loads(value)
            except Exception, ex:
                data = value
        elif op == '-H': #header
            try:
                headers.update(json.loads(value))
            except Exception, ex:
                print 'ERROR: headers format error'
                sys.exit(1)
        elif op == '-f': #file
            t = tuple(value.split(':'))
            files.append(t)
        elif op == '-e': #encoding
            encoding = value
        elif op == '-E': #expect result
            expect = value.decode('gbk')
        elif op == '-C': #config
            config_file = value
        elif op == '-D': #DB connector
            db_str = value
        elif op == '-N':
            test_name = value #Test Name
        elif op == '-P': #Test Priority
            test_priority = int(value)
        elif op == '-c': #category
            category = value
        elif op == '-t':
            tag = value
        elif op == '-v':
            version = value
        elif op == '-q':
            QUITE = True
        elif op == "-h":
            print USAGE
            sys.exit()

    return {
        'url' : url,
        'method' : method,
        'data' : data,
        'encoding' : encoding,
        'files' : files,
        'headers' : headers,
        'expect' : expect,
        'config_file' : config_file,
        'db_str' : db_str,
        'test_name' : test_name,
        'test_priority' : test_priority,
        'category' : category,
        'tag' : tag,
        'version' : version
    }


def make_db_condition(args):
    test_name = args['test_name']
    test_priority = args['test_priority']
    category = args['category']
    tag = args['tag']
    version = args['version']
    condition = {}

    if test_name:
        partten = re.compile(test_name, re.I)
        condition['name'] = partten
    if test_priority:
        if not test_priority.isdigit():
            print 'Priority Must Be a Num'
            exit(3)
        condition['priority'] = int(test_priority)
    if category:
        condition['category'] = category
    if tag:
        condition['tags'] = {"$elemMatch": {tag: 1}}
    if version:
        condition['version'] = version

    return condition


def get_db_test_data(db_str):
    if db_str.strip() == '*':
        condition = {}
        case_db = DP
    else:
        db_info = db_str.split(':')
        case_db = DataPool(*db_info)

        condition = make_db_condition(args)
        if not condition:
            raise ValueError('mongo数据库查询条件为空')

    try:
        CONTEXT['utils'].case_db = case_db
        return case_db.get_test_data(condition)
    except:
        print 'DB Connect Failure'
        exit(2)


def run(args):
    global CONTEXT, PASS, FAIL, SKIP
    if 'url' not in args or 'method' not in args:
        SKIP += 1
    print u'开始执行测试用例: %s' % args.get('name', u'未命名')

    [fun(args, CONTEXT) for fun in hooker.hook_mapping[HOOK_PRE_REQUEST]]
    code, txt = executor.send('http_sender', **args)
    [fun(code, txt, CONTEXT) for fun in hooker.hook_mapping[HOOK_POST_REQUEST]]

    args['resp_code'] = code
    args['resp_text'] = txt

    if not QUITE:
        print code
        print txt

    args['code'] = code
    flag, msg = validator.verify(args.get('checkType', "include"), txt, args.pop('expect'), **args)
    args['result'] = flag
    args['msg'] = msg

    DP.add_result(args)
    DP.add_log(args)

    if flag:
        PASS += 1
    else:
        FAIL += 1

    print u'测试用例执行结束: %s' % args.get('name', u'未命名')
    return flag, msg


def run_with_json(config_file):
    global CONTEXT, COUNT

    if os.path.exists(config_file):
        test_data = DP.read_config(config_file)

        [fun(test_data, CONTEXT) for fun in hooker.hook_mapping[HOOK_PRE_ALL]]

        index = 0
        COUNT = len(test_data)

        for data in test_data:
            index += 1
            run_with_data(data, index, 'json')

        [fun(index, CONTEXT) for fun in hooker.hook_mapping[HOOK_POST_ALL]]
    else:
        print 'CONFIG File Not Exist'
        exit(1)


def run_with_db(args):
    global CONTEXT, COUNT

    DP.add_task(args)
    task_name = args.get('task_name')
    db_str = args['db_str']

    if not task_name:
        task_name = int(time.time()) ##默认执行任务名

    test_data = get_db_test_data(db_str)
    [fun(test_data, CONTEXT) for fun in hooker.hook_mapping[HOOK_PRE_ALL]]

    index = 0
    COUNT = len(test_data)
    for data in test_data:
        index += 1
        data['task_name'] = task_name
        run_with_data(data, index, 'db')

    [fun(index, CONTEXT) for fun in hooker.hook_mapping[HOOK_POST_ALL]]


def run_with_data(data, index, ttype=None):
    [fun(data, index, CONTEXT) for fun in hooker.hook_mapping[HOOK_PRE_TESTING]]

    if not CONTEXT['continue']:
        return

    data = merge_template(data, ttype)
    flag, msg = run(data)

    [fun(flag, msg, CONTEXT) for fun in hooker.hook_mapping[HOOK_POST_TESTING]]


def get_json_template(name):
    templates = DP.read_config('template.json')
    if name in templates:
        return templates[name]


def get_db_template(name):
    templates = DP.get_db_templates(collection='template', condition={'name' : name})
    if templates and len(templates) > 0:
        return templates[0]


def merge_template(data, ttype):
    temp = data.get('template')
    if temp and temp.strip():
        if ttype == 'json':
            template = get_json_template(temp.strip())
        elif ttype == 'db':
            template = get_db_template(temp.strip())
        else:
            return data

        if template:
            template.update(data)
            data = template

    return data


def get_test_data_by_case_name(name):
    condition = {"name": name}
    test_data = CONTEXT['utils'].case_db.get_test_data(condition=condition)
    return test_data[0] if test_data else None


def main(args):
    start_time = time.time()
    global COUNT

    args['task_name'] = '%s_%s' % (args.get('task_name', ''), int(time.time()))
    config_file = args.get('config_file')
    db_str = args.get('db_str')

    if config_file:
        run_with_json(config_file)
    elif db_str:
        run_with_db(args)
    elif args['url'] and args['method']:
        run_with_data(args, 1)
        COUNT = 1
    else:
        print USAGE

    summary = {'count': COUNT, 'pass': PASS, 'fail': FAIL, 'skip': SKIP}
    DP.add_summary(args['task_name'], summary)

    print u'时间消耗: %d' % (time.time() - start_time)
    return summary


CONTEXT['utils'].run_with_data = run_with_data
CONTEXT['utils'].get_test_data_by_case_name = get_test_data_by_case_name


if __name__ == '__main__':
    args = parse_args()
    print u'统计信息: %s' % main(args)
