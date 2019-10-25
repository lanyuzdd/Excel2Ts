import re
import sys
import os
import shutil
import json


class Student:
    count = 0
    name = "haha"

    def __init__(self, name):
        Student.count = Student.count + 1
        self.name = name


# s = Student("james")
# # s.name = "james"
# s.count = 0
# print(s.count)
#
# print(s.name)
#
# print(Student.name)
# print(Student.count)

# var_def = r'^[_a-zA-Z][_a-zA-Z0-9]*$'
# var_name = "1co"
# print(re.match(var_def, var_name))
# var_name = "co1"
# print(re.match(var_def, var_name))
# var_name = "co1 "
# print(re.match(var_def, var_name))

# value_types_str = "string|"
# value_types = value_types_str.split("|")
# print(value_types)

# reg_int = r'-?[1-9]\d*$'
# num_str = '1000'
# print(re.match(reg_int, num_str))
# num_str = '1000.0'
# print(re.match(reg_int, num_str))
# num_str = '1000.01'
# print(re.match(reg_int, num_str))
# num_str = '0100'
# print(re.match(reg_int, num_str))
# num_str = 's1000.0'
# print(re.match(reg_int, num_str))


def cp_json_files2laya():
    json_path = os.path.join(sys.path[0], 'assets', 'ts_class')
    items = os.listdir(json_path)
    laya_path = '/Users/zhengxijun/Documents/Laya/TestLaya220/src'
    for item in items:
        print("item " + item)
        item_path = os.path.join(json_path, item)
        shutil.copy(item_path, laya_path)
        print("copy " + item)


cp_json_files2laya()

json_obj = {}
# 报错
# json_obj.name = 'james'
# json_obj.age = 10
json_obj['name'] = 'james'
json_obj['age'] = 10
print(json.dumps(json_obj))
