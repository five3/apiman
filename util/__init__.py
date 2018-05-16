# -*-coding:utf-8-*-
import os
import mimetypes


def warp_files(files):
    multiple_files = []
    for ft in files:
        if not isinstance(ft, tuple):
            raise TypeError, "文件子项不是元组类型"
        if len(ft) < 2 or len(ft) > 3:
            raise ValueError, "文件子项长度错误"

        field = ft[0]
        file_path = ft[1]
        file_name = os.path.basename(file_path)
        if len(ft) == 3:
            mime = ft[2]
        else:
            mime = mimetypes.guess_type(file_path)[0]

        t = (field, (file_name, open(file_path, 'rb'), mime))
        multiple_files.append(t)

    return multiple_files
