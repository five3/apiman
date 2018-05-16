# -*-coding:utf-8-*-
from pymongo import MongoClient
import codecs
import json
import time


class MongoData(object):
    def __init__(self, mongo_host, mongo_port, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    def _read_mongo_(self, collection='testdata', condition={}):
        client = MongoClient(self.mongo_host, self.mongo_port)
        db = client[self.mongo_db]
        coll = db[collection]
        return coll.find(condition) ##获取记录

    def _write_mongo_(self, collection='testresult', record={}):
        client = MongoClient(self.mongo_host, self.mongo_port)
        db = client[self.mongo_db]
        coll = db[collection]
        return coll.insert_one(record)  ##添加记录

    def get_db_templates(self, collection, condition):
        return self._read_mongo_(collection, condition)

    def get_test_data(self, condition):
        return self._read_mongo_(condition=condition)

    def get_task_list(self):
        return self._read_mongo_(collection='task')

    def get_result_list(self, task_name):
        condition = {'task_name': task_name}
        print condition
        return self._read_mongo_(collection='testresult', condition=condition)

    def get_condition_by_test_set(self, test_set):
        condition = {'name': test_set}
        r = self._read_mongo_(collection='testset', condition=condition)
        if r:
            return r[0]

    def add_task(self, test_data):
        task_name = test_data.get('task_name', int(time.time())),
        test_data['task_name'] = task_name
        info = {'name': task_name}
        self._write_mongo_(collection='task', record=info)

    def add_result(self, test_data):
        result_info = {
            "task_name": test_data.get('task_name'),
            "project_name": test_data.get('project_name'),
            "testcase_name": test_data.get('name'),
            "category": test_data.get('category'),
            "version": test_data.get('version'),
            "result": test_data.get('result'),
            "time": int(time.time())
        }
        self._write_mongo_(record=result_info)

    def add_log(self, test_data):
        test_log = {
            "task_name": test_data.get('task_name'),
            "project_name": test_data.get('project_name'),
            "testcase_name": test_data.get('name'),
            "resp_code": test_data.get('resp_code'),
            "resp_text": test_data.get('resp_text'),
            "expect": test_data.get('expect'),
            "checkType": test_data.get('checkType'),
            "msg": test_data.get('msg')
        }
        self._write_mongo_(collection="testlog", record=test_log)

    def add_summary(self, task_name, summary):
        info = {"task_name": task_name}
        info.update(summary)
        self._write_mongo_(collection="summary", record=info)

    def add_test_set(self, data):
        test_set = {
            "name": data.get('name'),
            "db_str": data.get('db_str'),
            "test_name": data.get('test_name'),
            "test_priority": data.get('test_priority'),
            "category": data.get('category'),
            "tag": data.get('tag'),
            "version": data.get('version')
        }
        return self._write_mongo_(collection="testset", record=test_set)


class ConfigData(object):
    def __init__(self):
        pass

    def read_config(self, fp, encoding="utf-8"):
        with codecs.open(fp, "rb", encoding) as f:
            txt = f.read()
            return json.loads(txt)


class DataPool(MongoData, ConfigData):
    def __init__(self, mongo_host="127.0.0.1", mongo_port=27017, mongo_db='apiman'):
        super(DataPool, self).__init__(mongo_host, mongo_port, mongo_db)


if __name__ == '__main__':
    dp = DataPool()
    print dp.read_config('testdata.json')
    print dp.get_task_list().count()

