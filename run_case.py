# -*-coding:utf-8-*-
from bin import api_core

args = api_core.parse_args()
print '统计信息: %s' % api_core.main(args)