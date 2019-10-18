import re

class Student:
    count = 0
    name = "haha"

    def __init__(self, name):
        Student.count = Student.count + 1
        self.name = name


s = Student("james")
# s.name = "james"
s.count = 0
print(s.count)

print(s.name)

print(Student.name)
print(Student.count)

# var_def = r'^[_a-zA-Z][_a-zA-Z0-9]*$'
# var_name = "1co"
# print(re.match(var_def, var_name))
# var_name = "co1"
# print(re.match(var_def, var_name))
# var_name = "co1 "
# print(re.match(var_def, var_name))

value_types_str = "string|"
value_types = value_types_str.split("|")
print(value_types)



