from enum import Enum, unique
from typing import List
import json
import re

# 值类型，分基础值类型和值类型修饰符

# 基础值类型
sys_base_value_types = ['string', 'number', 'comment']

# 值类型修饰符
sys_value_type_specifiers = ['key', 'primary_key', 'key_value_key', 'key_value_value', 'list']

# 键值类型列表
sys_key_specifiers = ['key', 'primary_key', 'key_value_key']

# 变量命名规范，用作列名表名验证
__var_def = r'^[_a-zA-Z][_a-zA-Z0-9]*$'

reg_int = r'-?[1-9]\d*$'
reg_float = r'-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)$'


class ColumnBaseValue:
    type_string: str = "string"
    type_number: str = "number"
    type_comment: str = "comment"


class ColumnSpecifier:
    key: str = "key"
    primary_key: str = "primary_key"
    key_value_key: str = "key_value_key"
    key_value_value: str = "key_value_value"
    # 无键值对
    no_key = 'no_key'
    # list = "list"


class StructType:
    map: str = "map"
    list: str = "list"


# class Struct:
#
#     def __init__(self, struct_name: str, value_type, struct_list, parent):
#         # StructType
#         self.struct_name = struct_name
#         self.value_type = value_type
#         self.struct_list = struct_list
#         # Struct
#         self.parent = parent
#
#         if self.struct_list is None or len(self.struct_list) == 0:
#             raise TypeError("结构定义没有属性")
#
#         pass
#
#     def get_ts_define(self):
#
#         if self.struct_list is None:
#             return ''
#
#         content = 'interface {'
#
#         for struct_item in self.struct_list:
#             content += struct_item.struct_name + ':'
#             is_base_type = struct_item.value_type == ColumnBaseValue.type_number
#             is_base_type = is_base_type or struct_item.value_type == ColumnBaseValue.type_string
#
#             if is_base_type:
#                 content += struct_item.struct_name + struct_item.value_type + ';'
#             elif len(self.struct_list) == 1:
#                 content += struct_item.struct_name + ';'
#             else:
#                 content += 'Array<' + struct_item.struct_name + '>;'
#                 pass
#
#         content += '}'
#         return content


class SheetColumn:
    # 列名
    name = ""
    # 基础类型
    base_type = ""
    # 列类型修饰符列表
    type_specifier: List[str] = []
    # 列的注释
    comment = ""
    # 列在所有列中的索引
    sheet_index = 0
    # 列在值列中的索引
    value_index = 0

    # 键值列、注释列在写行数据的时候被忽略
    # ignored = False

    # def is_key_column(self):
    #     is_key_col = ColumnSpecifier.key in self.type_specifier or
    #     return is_key_col

    def is_comment_col(self):
        return self.base_type == ColumnBaseValue.type_comment

    # 列检验值是否符合定义;值符合定义，将值转成正确的数据类型返回
    def validate_cell_value_by_column_type(self, cell_value: str, row_idx: int):
        # todo 检测空单元格
        if cell_value == '' or reg_int is None:
            raise TypeError("检测到空单元格 列：" + self.name + " 行数：" + row_idx)

        # 值符合定义，将值转成正确的数据类型
        # 检测数字单元格
        if self.base_type == ColumnBaseValue.type_number:
            if re.match(reg_int, cell_value):
                cell_value = int(cell_value)
                return cell_value
            if re.match(reg_float, cell_value):
                cell_value = float(cell_value)
                return cell_value
            else:
                raise TypeError("值不是数字 列：" + self.name + " 行数：" + row_idx)

        cell_value = cell_value + ''
        return cell_value


class Sheet:

    def __init__(self, name: str, column_names: List[str], column_types: List[str], column_comments: List[str]):
        # 表名
        self.name = name
        # 表的所有列
        self.column_type_list: List[SheetColumn] = []
        # 表的所有列除了注释列
        self.value_type_columns: List[SheetColumn] = []
        # 表的所有注释列
        self.comment_type_columns: List[SheetColumn] = []

        # 键值列的类型，在这里定义，值见ColumnSpecifier
        self.key_column_type = ColumnSpecifier.no_key

        # 表的原始行数据
        self.origin_value_rows = []

        self.struct = None

        column_types_change_comment_column_type(column_types, column_names)
        self.__init_column_structure(column_names, column_types, column_comments)

        self.__init_struct()
        pass

    def __init_column_structure(self, column_names: List[str], column_types: List[str], column_comments: List[str]):

        # print("init_column_structure")

        for i in range(0, len(column_names)):
            col_name = column_names[i]
            col_type = column_types[i]
            col_comment = column_comments[i]
            sheet_col = Sheet.get_column_value_type_data(col_name, col_type, col_comment)
            sheet_col.sheet_index = i
            sheet_col.value_index = i
            self.column_type_list.append(sheet_col)

        self.group_column_by_comment()
        self.validate_sheet_columns()

        pass

    # def __init_struct(self):
    #     if self.key_column_type == ColumnSpecifier.no_key:
    #         col_structs = []
    #         for col_item in self.value_type_columns:
    #             col_struct = Struct(col_item.name, col_item.base_type, None, None)
    #             col_structs.append(col_struct)
    #             pass
    #         pass
    #
    #         self.struct = Struct(self.name, self.name)
    #     pass

    # 解析表格列的值类型数据，int|key，int|list
    def get_column_value_type_data(col_name: str, col_type: str, col_comment: str) -> SheetColumn:
        value_type_str = col_type

        if not is_var_name_ok(col_name):
            raise TypeError("列名命名不规范，请修改：" + col_name)

        sheet_col = SheetColumn()

        sheet_col.name = col_name
        sheet_col.comment = col_comment

        prefixes = value_type_str.split('|')
        if len(prefixes) > 2 or len(prefixes) == 0:
            raise TypeError("列的值类型错误：" + col_type)

        base_type = prefixes[0]
        if base_type not in sys_base_value_types:
            raise TypeError("基础值类型错误：" + base_type)

        sheet_col.base_type = base_type

        # 值类型没有修饰
        if len(prefixes) == 1:
            return sheet_col

        if prefixes[1] == '':
            print("警告：列值类型定义不规范：" + col_type)
            return sheet_col

        type_specifier = prefixes[1].split(':')
        print("type_specifier:")
        print(type_specifier)

        if '' in type_specifier != -1:
            print("警告：列值类型修饰符定义不规范：" + prefixes[1])
            type_specifier.remove('')

        sheet_col.type_specifier = type_specifier

        Sheet.validate_column_type_specifier(sheet_col)

        return sheet_col

    # 验证列的修饰符是否合法，组合是否冲突
    def validate_column_type_specifier(sheet_col: SheetColumn):
        type_specifier = sheet_col.type_specifier
        if len(type_specifier) > 2:
            raise TypeError("数值修饰不可能超过3个：" + json.dumps(type_specifier))

        unique_prefixes_num = 0
        unique_prefixes = []
        for i in range(0, len(type_specifier)):
            v_prefix = type_specifier[i]
            if v_prefix not in sys_value_type_specifiers:
                raise TypeError("值类型修饰错误：" + v_prefix)
            if v_prefix not in unique_prefixes:
                unique_prefixes.append(v_prefix)

            if v_prefix in sys_key_specifiers:
                unique_prefixes_num += 1

        if len(unique_prefixes) != len(type_specifier):
            raise TypeError("有重复的数值修饰：" + json.dumps(type_specifier))

        if unique_prefixes_num > 1:
            raise TypeError("有多个唯一的数值修饰：" + json.dumps(type_specifier))

        if 'list' in type_specifier:
            type_specifier.remove('list')
            if type_specifier[0] in sys_key_specifiers:
                raise TypeError("同一个数值类型中，list与键修饰冲突：" + json.dumps(type_specifier))
        pass

    # 整表数值修饰检验
    # 一个表最多有一个键值 sys_key_specifiers
    # 如果键值对，必须两列且对应
    def validate_sheet_columns(self):
        # 所有列只能有一个key类型修饰

        # 非注释列数量
        uncomment_column_num = len(self.value_type_columns)

        key_prefix_num = 0

        all_prefixes = []

        for column in self.value_type_columns:
            type_specifier = column.type_specifier

            if len(type_specifier) == 0:
                continue

            # print("validate_sheet_columns type_specifier:")
            # print(type_specifier)
            # print("column.sheet_index:")
            # print(column.sheet_index)

            for prefix_item in type_specifier:
                print('prefix_item', prefix_item)
                if prefix_item in sys_key_specifiers:
                    self.key_column_type = prefix_item
                    key_prefix_num = key_prefix_num + 1
                    if key_prefix_num > 1:
                        raise TypeError("一个表所有列只能有一个key类型修饰：" + str(key_prefix_num) + " " + json.dumps(all_prefixes))
                    # if column.sheet_index != 0:
                    #     raise TypeError("key类型修饰列必须放在第一列：")
                all_prefixes.append(prefix_item)

            # print('all_prefixes', all_prefixes)
            pass

        if 'key_value_key' in all_prefixes or 'key_value_value' in all_prefixes:
            if 'key_value_key' in all_prefixes and 'key_value_value' in all_prefixes and uncomment_column_num == 2:
                pass
            else:
                prefixes_str = json.dumps(all_prefixes)
                raise TypeError("不是严格的键值对两列格式：" + prefixes_str)
        else:
            pass
        pass

    # 表格非注释列
    def group_column_by_comment(self):
        print(ColumnBaseValue.type_comment)
        print(type(ColumnBaseValue.type_comment))
        for column in self.column_type_list:
            print(column.base_type, ColumnBaseValue.type_comment)
            if column.base_type != ColumnBaseValue.type_comment:
                self.value_type_columns.append(column)
            else:
                self.comment_type_columns.append(column)

        for column in self.value_type_columns:
            for i in range(len(self.column_type_list)):
                if self.column_type_list[i].base_type == ColumnBaseValue.type_comment:
                    if column.sheet_index > self.column_type_list[i].sheet_index:
                        column.value_index = column.value_index - 1


class Workbook:
    name = ""
    sheets: List[Sheet] = []

    def print_sheets_names(self):
        print("Workbook.print_sheets_names")
        for item in self.sheets:
            print(item.name)
            print(len(item.column_type_list))
        pass


# 检测工作簿英文名、表名、列名是否符合变量的定义规范
def is_var_name_ok(var_name):
    is_ok = re.match(__var_def, var_name) is not None
    return is_ok


# 注释列的数值类型改成comment
# 列名以comment开头的列都是注释列，注释列默认填的值类型是string
def column_types_change_comment_column_type(column_types: List[str], column_names: List[str]):
    comment_idxes = []
    for column_name in column_names:
        # print('column_types_change_comment_column_type ', column_name[0:7])
        if column_name[0:7] == 'comment':
            idx = column_names.index(column_name)
            # print(idx)
            comment_idxes.append(idx)
    for comment_idx in comment_idxes:
        column_types[comment_idx] = 'comment'

    print(column_types)

    pass
