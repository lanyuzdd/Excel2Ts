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
    type_list: str = "list"


class ColumnSpecifier:
    key: str = "key"
    primary_key: str = "primary_key"
    key_value_key: str = "key_value_key"
    key_value_value: str = "key_value_value"
    # 无键值对
    no_key = 'no_key'


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

    def is_comment_col(self):
        return self.base_type == ColumnBaseValue.type_comment

    # 列检验值是否符合定义;值符合定义，将值转成正确的数据类型返回
    def validate_cell_value_by_column_type(self, cell_value, row_idx: int):
        # todo 检测空单元格
        if (cell_value == '' or cell_value is None) and self.base_type != ColumnBaseValue.type_comment:
            msg = "检测到空单元格 列：" + self.name + " 行数：" + str(row_idx)
            print(msg)
            raise TypeError(msg)

        # 有可能是<class 'float'>，转成字符串
        cell_value_str = str(cell_value)
        # 值符合定义，将值转成正确的数据类型
        # 检测数字单元格
        if self.base_type == ColumnBaseValue.type_number:
            # print("reg_int")
            # print(reg_int)
            # print(cell_value)
            # print(type(cell_value))
            if re.match(reg_int, cell_value_str):
                cell_value = int(cell_value)
                print(cell_value_str + ' 转int ' + str(cell_value))
                return cell_value
            if re.match(reg_float, cell_value_str):
                if int(cell_value) - cell_value == 0:
                    cell_value = int(cell_value)
                    print(cell_value_str + ' 转int ' + str(cell_value))
                else:
                    cell_value = float(cell_value)
                    print(cell_value_str + ' 转float ' + str(cell_value))

                return cell_value
            else:
                raise TypeError("值不是数字 列：" + self.name + " 行数：" + row_idx)

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

        # 键值列的类型在这里定义
        self.key_column_type = ColumnSpecifier.no_key
        # -1表示非键值列，0以上有效值表示键列索引
        self.key_column_idx = -1

        # 表的原始行数据
        self.origin_value_rows = []

        self.struct = []

        column_types_change_comment_column_type(column_types, column_names)
        self.__init_column_structure(column_names, column_types, column_comments)

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

    def get_ts_struct_define_of_no_key(self):
        # 无键的表转成列表
        ts_define = "export interface " + self.name + "{\n"
        for col in self.value_type_columns:
            ts_define += "/** " + col.comment + " **/\n"
            ts_define += col.name + ":" + get_ts_type_by_col_base_value_type(col.base_type) + ";\n"
            pass
        ts_define += "}\n"

        class_prop = self.name + " :Array<" + self.name + ">;\n"
        return ts_define, class_prop

    # primary_key key表的ts定义
    def get_ts_struct_define_of_key(self):
        is_key_type_sheet = self.key_column_type == ColumnSpecifier.primary_key or self.key_column_type == ColumnSpecifier.key
        if not is_key_type_sheet:
            raise TypeError("不是键值列，primary_key or key")

        if len(self.value_type_columns) == 2:
            return self.get_ts_struct_define_of_key_with_one_value_cols()

        return self.get_ts_struct_define_of_key_with_multi_value_cols()

    def get_ts_struct_define_of_key_with_multi_value_cols(self):
        # 带键的表转成字典
        ts_define = "export interface " + self.name + " {\n"

        for col in self.value_type_columns:
            if col.sheet_index == self.key_column_idx:
                continue
            ts_define += "/** " + col.comment + " **/\n"
            ts_define += col.name + ":" + get_ts_type_by_col_base_value_type(col.base_type) + ";\n"
            pass
        ts_define += "}\n"

        if self.key_column_type == ColumnSpecifier.primary_key:
            class_prop = self.name + " :{[key:string]:" + self.name + "};\n"
        else:
            class_prop = self.name + " :{[key:string]:Array<" + self.name + ">};\n"

        return ts_define, class_prop

    # primary_key key表，值列只有一列，不做包装，直接写键值对
    def get_ts_struct_define_of_key_with_one_value_cols(self):
        # 带键的表转成字典
        ts_define = ""

        value_col_idx = -1
        for col in self.value_type_columns:
            if col.sheet_index != self.key_column_idx:
                value_col_idx = col.sheet_index

        if value_col_idx == -1:
            raise TypeError("没有找到值列")

        value_col_base_type = self.column_type_list[value_col_idx].base_type
        ts_type = get_ts_type_by_col_base_value_type(value_col_base_type)

        if self.key_column_type == ColumnSpecifier.primary_key:
            class_prop = self.name + " :{[key:string]:" + ts_type + "};\n"
        else:
            class_prop = self.name + " :{[key:string]:Array<" + ts_type + ">};\n"

        return ts_define, class_prop

    def get_ts_struct_define_of_key_value(self):
        # 纯键值对列转成静态属性常量

        ts_define = "\n"
        class_prop = "\n"

        value_col_idx = -1
        for col in self.value_type_columns:
            if col.sheet_index != self.key_column_idx:
                value_col_idx = col.sheet_index

        if value_col_idx == -1:
            raise TypeError("不是纯键值对表")

        key_col = self.column_type_list[self.key_column_idx]
        value_col = self.value_type_columns[value_col_idx]
        for row_value in self.origin_value_rows:
            cell_value = row_value[value_col.sheet_index]
            cell_key = row_value[key_col.sheet_index]
            base_type = "string"
            if str_is_int(cell_value) or str_is_float(cell_value):
                base_type = "number"
            if base_type == "number":
                class_prop += "export const " + cell_key + ":" + base_type + "=" + str(cell_value) + ";\n"
            else:
                class_prop += "export const " + cell_key + ":" + base_type + "= '" + str(cell_value) + "';\n"
            pass

        return ts_define, class_prop

    def get_ts_struct_define(self):

        if self.key_column_type == ColumnSpecifier.no_key:
            return self.get_ts_struct_define_of_no_key()

        if self.key_column_type == ColumnSpecifier.primary_key or self.key_column_type == ColumnSpecifier.key:
            return self.get_ts_struct_define_of_key()

        if self.key_column_type == ColumnSpecifier.key_value_key:
            return self.get_ts_struct_define_of_key_value()

        raise TypeError("不存在的表键值类型：" + self.key_column_type)

        pass

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
                    self.key_column_idx = column.sheet_index
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

    def to_json(self):

        if self.key_column_type == ColumnSpecifier.no_key:
            return self.get_json_of_no_key()

        if self.key_column_type == ColumnSpecifier.primary_key or self.key_column_type == ColumnSpecifier.key:
            return self.get_json_of_key()

        if self.key_column_type == ColumnSpecifier.key_value_key:
            pure_key_value_data = self.get_json_of_key_value()
            return pure_key_value_data, pure_key_value_data

        raise TypeError("不存在的表键值类型：" + self.key_column_type)

        pass

    def get_json_of_no_key(self):
        json_list = []
        map_list = []
        # 无键的表转成列表
        for row_origin_data in self.origin_value_rows:
            row_data = []
            row_map_data = {}
            for i in range(0, len(self.value_type_columns)):
                cell_value = self.value_type_columns[i].sheet_index
                row_data.append(cell_value)

                row_map_data[self.value_type_columns[i].name] = cell_value
                pass
            json_list.append(row_data)
            map_list.append(row_map_data)
            pass
        return json_list, map_list

    def get_json_of_key(self):

        is_key_type_sheet = self.key_column_type == ColumnSpecifier.primary_key or self.key_column_type == ColumnSpecifier.key
        if not is_key_type_sheet:
            raise TypeError("不是键值列，primary_key or key")

        if len(self.value_type_columns) == 2:
            json_map = self.get_json_of_key_with_one_value_cols()
            json_list_map = json_map
        else:
            json_list_map, json_map = self.get_json_of_key_with_multi_value_cols()

        return json_list_map, json_map

    def get_json_of_key_with_one_value_cols(self):
        # 带键的表转成字典
        json_map = {}
        value_col_idx = -1
        for col in self.value_type_columns:
            if col.sheet_index != self.key_column_idx:
                value_col_idx = col.sheet_index

        if value_col_idx == -1:
            raise TypeError("没有找到值列")

        for row_origin_data in self.origin_value_rows:
            # for i in range(0, len(self.value_type_columns)):
            key_value = row_origin_data[self.key_column_idx]
            print(row_origin_data)
            value = row_origin_data[value_col_idx]
            if self.key_column_type == ColumnSpecifier.primary_key:
                json_map[key_value] = value
            else:
                if key_value in json_map.keys():
                    pass
                else:
                    json_map[key_value] = []
                    pass
                json_map[key_value].append(value)
            pass

        return json_map

    def get_json_of_key_with_multi_value_cols(self):
        # 带键的表转成字典
        json_list_map = {}
        json_map = {}

        for row_origin_data in self.origin_value_rows:
            row_data = []
            row_map_data = {}
            key_value = row_origin_data[self.key_column_idx]
            for i in range(0, len(self.value_type_columns)):
                value_col = self.value_type_columns[i]
                if value_col.sheet_index == self.key_column_idx:
                    continue
                cell_value = row_origin_data[value_col.sheet_index]
                row_data.append(cell_value)
                row_map_data[value_col.name] = cell_value
                pass
            if self.key_column_type == ColumnSpecifier.primary_key:
                json_list_map[key_value] = row_data
                json_map[key_value] = row_map_data
            else:
                if key_value in json_list_map.keys():
                    pass
                else:
                    json_list_map[key_value] = []
                    pass
                if key_value in json_map.keys():
                    pass
                else:
                    json_map[key_value] = []
                    pass
                pass
                json_list_map[key_value].append(row_data)
                print("json_map[key_value]")
                print(json_map[key_value])
                json_map[key_value].append(row_map_data)
            pass

        return json_list_map, json_map
        # enf of get_json_of_key_with_multi_value_cols
        pass

    def get_json_of_key_value(self):
        # 纯键值对列转成静态属性常量
        json_map = {}
        value_col_idx = -1
        for col in self.value_type_columns:
            if col.sheet_index != self.key_column_idx:
                value_col_idx = col.sheet_index

        if value_col_idx == -1:
            raise TypeError("不是纯键值对表")

        key_col = self.column_type_list[self.key_column_idx]
        value_col = self.value_type_columns[value_col_idx]
        for row_value in self.origin_value_rows:
            cell_value = row_value[value_col.sheet_index]
            cell_key = row_value[key_col.sheet_index]

            json_map[cell_key] = cell_value

        return json_map


class Workbook:

    def __init__(self):
        # 工作簿的英文名，会作为导出ts类定义的类名、ts文件名
        self.name = ""
        self.sheets: List[Sheet] = []
        pass

    def print_sheets_names(self):
        print("Workbook.print_sheets_names")
        for item in self.sheets:
            print(item.name)
            print(len(item.column_type_list))
        pass

    # 工作簿数据结构转ts类
    # 工作簿读取所有表数据后，执行此方法
    def get_ts_struct_define(self, map_json):
        # namespace的常量，保存纯键值对导出的常量
        const_define = ''
        sheet_interface = ''

        namespace_define = "export namespace  " + self.name + "_ns {\n"

        # 工作簿interface，主类
        book_define = "export interface  " + self.name + " {\n"

        for sheet in self.sheets:
            ts_define, class_prop = sheet.get_ts_struct_define()
            if sheet.key_column_type == ColumnSpecifier.key_value_key:
                const_define += class_prop
            else:
                book_define += class_prop
            sheet_interface += ts_define
            pass

        book_define += "}\n"

        namespace_define += const_define
        namespace_define += book_define
        namespace_define += sheet_interface

        namespace_define += 'export const json_data:any = ' + json.dumps(map_json, sort_keys=True, indent=4,
                                                                         separators=(',', ':'),
                                                                         ensure_ascii=False) + ";\n"
        namespace_define += 'export const instance: ' + self.name + ' = json_data;\n'

        namespace_define += "}\n"

        return namespace_define

    def check_workbook_class_name_diff_from_every_sheet_name(self):
        if len(self.sheets) == 1:
            return
        for sheet in self.sheets:
            print(self.name, sheet.name)
            if self.name == sheet.name:
                raise TypeError("excel工作簿配置的英文名与表名冲突，请修改其中一个！")

    def to_json(self):
        if len(self.sheets) == 0:
            list_json, map_json = self.sheets[0].to_json()
            return list_json, map_json
        list_json = {}
        map_json = {}
        for sheet in self.sheets:
            sheet_list_data, sheet_map_data = sheet.to_json()
            list_json[sheet.name] = sheet_list_data
            map_json[sheet.name] = sheet_map_data
            pass
        return list_json, map_json


# 检测工作簿英文名、表名、列名是否符合变量的定义规范
def is_var_name_ok(var_name):
    is_ok = re.match(__var_def, var_name) is not None
    return is_ok


# 注释列的数值类型改成comment
# 列名以comment开头的列都是注释列，注释列默认填的值类型是string
def column_types_change_comment_column_type(column_types: List[str], column_names: List[str]):
    comment_idxes = []

    for i in range(0, len(column_names)):
        print(i)
        column_name = column_names[i]
        if column_name[0:7] == 'comment':
            comment_idxes.append(i)
        pass

    for comment_idx in comment_idxes:
        column_types[comment_idx] = 'comment'

    pass


def get_ts_type_by_col_base_value_type(col_base_value_type: str):
    ts_type = ""
    if col_base_value_type == ColumnBaseValue.type_string:
        ts_type = "string"
    elif col_base_value_type == ColumnBaseValue.type_number:
        ts_type = "number"
    else:
        raise TypeError("非法的基础类型：" + col_base_value_type)
    return ts_type


def str_is_int(content):
    content = str(content)
    return re.match(reg_int, content) is not None


def str_is_float(content):
    content = str(content)
    return re.match(reg_float, content) is not None
